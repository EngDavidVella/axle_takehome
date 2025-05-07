import streamlit as st

import backend
from models import DemoAdminState
from plotting import plot_upcoming_charges
from utils import get_current_time_to_nearest_30_minutes


def get_demo_state() -> DemoAdminState:
    rounded_time = get_current_time_to_nearest_30_minutes()
    with st.sidebar:
        st.subheader("Demo Admin Controls")
        st.write("Use these controls to simulate the car and charger state.")

        current_time = st.time_input("Current Time", rounded_time)
        # Add back in the date to the time
        current_time = rounded_time.replace(
            hour=current_time.hour, minute=current_time.minute
        )

        car_is_plugged_in = st.toggle("Plugged in", value=True)

    return DemoAdminState(
        car_is_plugged_in=car_is_plugged_in, current_time=current_time
    )


def controls(car_is_plugged_in: bool, car_is_charging: bool, charge_is_override: bool):
    st.subheader("Controls")
    c1, c2 = st.columns([1, 1])

    # TODO: Rename and enable/disable these buttons based on the car/charger state
    return (
        c1.button("Start Charging", disabled=False, on_click=backend.handle_start_charge),
        c2.button("Stop Charging", disabled=False, on_click=backend.handle_stop_charge),
    )


if __name__ == "__main__":
    demo_state = get_demo_state()
    car_state = backend.get_car_state(demo_state)
    st.subheader("Charging Schedule")
    st.plotly_chart(
        plot_upcoming_charges(
            backend.get_future_states(),
            current_time=demo_state.current_time,
        )
    )
    start_charging, stop_charging = controls(
        demo_state.car_is_plugged_in,
        car_state.car_is_charging,
        car_state.charge_is_override,
    )
