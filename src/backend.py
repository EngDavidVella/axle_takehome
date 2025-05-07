# TODO: this file returns dummy data: everything should be replaced by calls to your logic
# Feel free to implement your logic within this process, or make calls to an external service

import streamlit as st

from models import ChargerState, DemoAdminState, CombinedState


def get_future_states() -> list[CombinedState]:
    """Return a list of future states for the system. This is used for plotting the charge trajectory."""
    # TODO: replace this with your logic
    return []


def get_car_state(demo_state: DemoAdminState) -> ChargerState:
    # TODO: replace this with your logic. Feel free to rewrite to combine with the function above if necessary.
    # When you're done, we shouldn't have these toggles in the frontend; they should be determined by the backend.
    with st.sidebar:
        car_is_charging = st.toggle(
            "Currently Charging", value=True, disabled=not demo_state.car_is_plugged_in
        )
        charge_is_override = st.toggle(
            "Charging is Override", value=True, disabled=not demo_state.car_is_plugged_in
        )

    return ChargerState(
        car_is_charging=car_is_charging, charge_is_override=charge_is_override
    )


def handle_start_charge():
    # TODO: handle when the user presses the "Start Charge" button
    st.toast("Starting charge!", icon="🚀")


def handle_stop_charge():
    # TODO: handle when the user presses the "Stop Charge" button
    st.toast("Stopping charge", icon="⚠️")
