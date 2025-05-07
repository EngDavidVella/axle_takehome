import streamlit as st
from datetime import timedelta

def start_charge():
    if st.session_state["car_is_plugged_in"]:
        st.session_state["car_is_charging"] = True
        st.session_state["charge_is_override"] = True
        st.session_state["charge_start_date"] = st.session_state["system_date"]
        st.toast("Started charging!", icon="🚀")

        # Store the override start time
        st.session_state["override_start_time"] = st.session_state["system_time"]
        st.session_state["override_start_date"] = st.session_state["system_date"]
    else:
        st.toast("Cannot start charging: car is unplugged.", icon="⚡")

def stop_charge():
    if st.session_state["car_is_charging"]:
        if not st.session_state["charge_is_override"]:
            # If this was a scheduled charge, disable schedule until tomorrow
            st.session_state["schedule_charge_enabled"] = False
            st.session_state["schedule_charge_disable_date"] = st.session_state["system_date"]
        st.session_state["car_is_charging"] = False
        st.session_state["charge_is_override"] = False
        st.toast("Stopped charging.", icon="⚠️")

def render_charge_controls():
    """Render Start/Stop Charging buttons based on current session state."""
    car_is_charging = st.session_state.get("car_is_charging")
    car_is_plugged_in = st.session_state.get("car_is_plugged_in")
    start_disabled = car_is_charging or not car_is_plugged_in
    stop_disabled = not car_is_charging

    c1, c2 = st.columns([1, 1])

    c1.button(
        "Start Charging",
        disabled=start_disabled,
        on_click=start_charge,
    )

    c2.button(
        "Stop Charging",
        disabled=stop_disabled,
        on_click=stop_charge,
    )


def render_user_dashboard():
    with st.container():
        st.markdown("## 🚘 Car Status Dashboard")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("📅 Date", str(st.session_state["system_date"]))
            st.metric("⏰ Time", str(st.session_state["system_time"]))
            if st.session_state['current_soc'] > 15:
                st.metric("🔋 State of Charge", f"{st.session_state['current_soc']}%")
            else:
                st.metric("⚠️🔋 State of Charge", f"{st.session_state['current_soc']}%")
            
        with col2:
            plugged = st.session_state["car_is_plugged_in"]
            charging = st.session_state["car_is_charging"]
            override = st.session_state["charge_is_override"]

            st.markdown(f"**🔌 Plugged In:** {'<span style=\"color:green\">Yes</span>' if plugged else '<span style=\"color:red\">No</span>'}", unsafe_allow_html=True)
            st.markdown(f"**⚡ Charging:** {'<span style=\"color:green\">Yes</span>' if charging else '<span style=\"color:red\">No</span>'}", unsafe_allow_html=True)
            st.markdown(f"**🚦 Override:** {'<span style=\"color:orange\">Active</span>' if override else '<span style=\"color:grey\">Off</span>'}", unsafe_allow_html=True)

        st.markdown("---")

        schedule_enabled = st.session_state.get("schedule_charge_enabled", True)
        car_plugged_in = st.session_state.get("car_is_plugged_in", True)
        disable_date = st.session_state.get("schedule_charge_disable_date")

        st.markdown(
            f"**📋 Schedule Charging:** "
            f"{'<span style=\"color:green\">Enabled</span>' if schedule_enabled else '<span style=\"color:red\">Disabled</span>'}",
            unsafe_allow_html=True,
        )

        # 🚫 Warning if charging is scheduled but car is unplugged
        if schedule_enabled and not car_plugged_in:
            st.markdown(
                "<span style='color:orange'>⚠️ Scheduled charging is active, but the car is not plugged in.</span>",
                unsafe_allow_html=True,
            )

        # 📅 Note if charging is disabled
        if not schedule_enabled and disable_date:
            st.markdown(
                f"<span style='color:gray'>ℹ️ Scheduled charging will be re-enabled at 00:00 on {disable_date + timedelta(days=1)}.</span>",
                unsafe_allow_html=True,
            )


