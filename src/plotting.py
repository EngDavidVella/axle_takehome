from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from models import CombinedState
from utils import get_current_time_to_nearest_30_minutes

# These set the resampling period for graphing
PERIOD = timedelta(minutes=30)
PERIOD_STR = "30min"


def _convert_states_to_dataframe(states: list[CombinedState]) -> pd.DataFrame:
    """Convert to dataframe for ease of plotting with Plotly, and resample to 30mins"""
    # TODO: Replace this with your logic - it should take the list of CombinedState objects and return a DataFrame
    rounded_time = get_current_time_to_nearest_30_minutes()

    times = [rounded_time + i * PERIOD for i in range(9)]
    socs = [0.5, 0.55, 0.6, 0.6, 0.6, 0.65, 0.7, 0.75, 0.8]
    car_is_charging = [True, True, False, False, True, True, True, True, False]
    charge_is_override = [True, True, False, False, False, False, False, False, False]

    df = pd.DataFrame(
        {
            "Time": times,
            "State of Charge": socs,
            "Car is Charging": car_is_charging,
            "Charge is Override": charge_is_override,
        }
    )

    return df.reset_index()


def plot_upcoming_charges(
    states: list[CombinedState], current_time: datetime
) -> Figure:
    """Plot the upcoming charges for the car"""
    df = _convert_states_to_dataframe(states)
    fig = px.line(df, x="Time", y="State of Charge")

    # Add a vertical line at the current time
    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="white",
        label=dict(text="Now", textposition="top center"),
    )

    # Add vertical rectangles for charging periods
    for i, row in df.iterrows():
        if not row["Car is Charging"]:
            continue
        fig.add_vrect(
            x0=row["Time"],
            x1=row["Time"] + PERIOD,
            fillcolor="red" if row["Charge is Override"] else "green",
            opacity=0.1,
            layer="below",
            label=dict(
                text="Override" if row["Charge is Override"] else "Scheduled",
                font=dict(
                    color="red" if row["Charge is Override"] else "green",
                ),
                textposition="top center",
            ),
        )

    fig.update_traces(mode="markers+lines")
    return fig
