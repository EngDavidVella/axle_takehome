from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils import get_standard_schedule, get_override_schedule

CHARGE_RATE_PER_30MIN = 100 / 6  # ~16.67% every 30 min
PERIOD = timedelta(minutes=30)
WINDOW_BLOCKS = 48  # Plot 4.5 hours of timeline

def get_override_window():
    if st.session_state.get("charge_is_override"):
        system_date = st.session_state["system_date"]
        system_time = st.session_state["system_time"]
        start = datetime.combine(system_date, system_time)
        end = start + timedelta(hours=1)
        return start, end
    return None

def generate_flat_soc_series(min_time: datetime, max_time: datetime) -> pd.DataFrame:
    """
    Generate a DataFrame with 1-minute time steps from min_time to max_time.
    Each row has the current battery SOC as a flat value.
    """
    if "current_soc" not in st.session_state:
        raise ValueError("current_soc not set in session state.")

    soc = st.session_state["current_soc"]

    # Generate 1-minute interval time series
    time_series = pd.date_range(start=min_time, end=max_time, freq="1min")

    df = pd.DataFrame({
        "Time": time_series,
        "State of Charge": [soc] * len(time_series)
    })

    return df

def generate_soc_series(min_time: datetime, max_time: datetime) -> pd.DataFrame:
    """
    Generate a 1-minute SoC projection from min_time to max_time.
    SoC climbs steadily from battery_soc to 100% during scheduled/override charging windows.
    Outside the window, SoC remains flat.
    """
    if "current_soc" not in st.session_state:
        raise ValueError("current_soc not set in session state.")
    
    if st.session_state["car_is_plugged_in"] == False:
        return generate_flat_soc_series(min_time, max_time)

    base_soc = st.session_state["current_soc"]
    time_series = pd.date_range(start=min_time, end=max_time, freq="1min")
    soc_series = []

    # Determine charge window
    if st.session_state.get("charge_is_override", False):
        charging_start, charging_end = get_override_schedule()
        is_override_mode = True
    else:
        # Use system_datetime to base the scheduled window
        charging_start, charging_end = get_standard_schedule(min_time)
        is_override_mode = False

    total_minutes = (charging_end - charging_start).total_seconds() / 60
    charging_occurred = False
    for t in time_series:
        is_today = t.date() == st.session_state["system_date"]
        schedule_enabled = st.session_state.get("schedule_charge_enabled", True) if is_today else True

        should_charge = (
            charging_start <= t < charging_end
            and (is_override_mode or schedule_enabled)
        )
        
        if should_charge:
            minutes_into_charge = (t - charging_start).total_seconds() / 60
            progress = minutes_into_charge / total_minutes
            soc = min(base_soc + progress * (100 - base_soc), 100)
            charging_occurred = True

        elif t >= charging_end and charging_occurred:
            soc = 100  # assume full charge is reached by end
        else:
            soc = base_soc
        soc_series.append(soc)

    return pd.DataFrame({
        "Time": time_series,
        "State of Charge": soc_series
    })
    
def add_charge_window_annotations(fig):
    """Adds vertical shaded regions to the SoC plot for scheduled or override charge windows."""
    from utils import get_standard_schedule, get_override_schedule

    system_datetime = datetime.combine(st.session_state["system_date"], st.session_state["system_time"])

    if st.session_state.get("charge_is_override"):
        # Override charging window
        override_start, override_end = get_override_schedule()
        fig.add_vrect(
            x0=override_start, x1=override_end,
            fillcolor="orange", opacity=0.2,
            layer="below", line_width=0,
            annotation_text="Override Charging", annotation_position="top left"
        )


    sched_start, sched_end = get_standard_schedule(system_datetime)


    fig.add_vrect(
        x0=sched_start,
        x1=sched_end,
        fillcolor="green",
        opacity=0.2,
        layer="below",
        line_width=0,
        annotation_text="Scheduled Charging",
        annotation_position="top left"
    )


def render_soc_plot_area():
    """
    Create a SOC plot area: Y axis from 0–100, X axis from
    30 mins before system time to 24 hours after that.
    Generate and include a SoC trace using the 'generate_soc_series' function.
    """
    system_datetime = datetime.combine(st.session_state["system_date"], st.session_state["system_time"])
    x_min = system_datetime - PERIOD
    x_max = x_min + (WINDOW_BLOCKS * PERIOD)

    # Generate actual flat SOC data
    df = generate_soc_series(x_min, x_max)
    
    fig = go.Figure()

    # Add flat SoC trace
    
    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df["State of Charge"],
        mode="lines",
        name="Flat SOC",
        line=dict(color="gray", dash="dash")
    ))

    fig.update_layout(
        title="Projected Battery SOC",
        xaxis=dict(
            range=[x_min, x_max],
            title="Time",
            tickformat="%H:%M",
        ),
        yaxis=dict(
            range=[0, 100],
            title="State of Charge (%)",
        ),
    )

    add_charge_window_annotations(fig)
    st.plotly_chart(fig, use_container_width=True)