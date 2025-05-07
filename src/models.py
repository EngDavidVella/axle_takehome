import streamlit as st
from datetime import datetime, timedelta
from utils import get_standard_schedule

class SystemStateManager:
    def __init__(self):
        # In deployment, these would come from the charger/vehicle, potentially through a database or API
        self.system_state_attr = {
            "system_date": datetime.now().date(),
            "system_time": datetime.now().time(),
            "car_is_plugged_in": False,
            "car_is_charging": False,
            "charge_is_override": False,
            "override_start_time": None,
            "override_start_date": None,
            "schedule_charge_enabled": True,
            "schedule_charge_disable_date": None,
            "current_soc": 60
        }
        self._init_session_system_state()
        
        self._check_schedule_reset()
        self._update_charging_state()
        self._render_sidebar_controls_for_demo() # Add a flag  setting (in .env?) to be able to tell whether in demo mode or not before running this.

    def _init_session_system_state(self):
        """Initialize top-level session keys with default values."""
        for key, value in self.system_state_attr.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def _render_sidebar_controls_for_demo(self): 
        # For demo only Tjsi would usually be hooked to the car/charger and/or database isntead
        # Might be worth considering a '.env' setting to auntoamtically switch between use-cases
        """Render Streamlit widgets bound to top-level session keys."""
        with st.sidebar:
            st.subheader("Demo Admin Controls")

            st.date_input("Current Date", key="system_date")
            st.time_input("Current Time", key="system_time")

            st.toggle("Car is Plugged In", key="car_is_plugged_in")
            st.slider("Current Battery SOC (%)", 0, 100, key="current_soc")
    
    def _update_charging_state(self):
        """Automatically determine whether the car should be charging."""
        now = datetime.combine(st.session_state["system_date"], st.session_state["system_time"])

        # Check if an override session has expired
        if st.session_state.get("charge_is_override", False):
            override_start_date = st.session_state.get("override_start_date")
            override_start_time = st.session_state.get("override_start_time")

            if override_start_date and override_start_time:
                override_start = datetime.combine(override_start_date, override_start_time)
                if now >= override_start + timedelta(hours=1):
                    st.session_state["charge_is_override"] = False
                    st.session_state["car_is_charging"] = False
                    st.toast("Override charging session ended.", icon="⏹️")
                    return
                else:
                    # Override is still active
                    st.session_state["car_is_charging"] = True
                    return

        if not st.session_state.get("schedule_charge_enabled", True):
            st.session_state["car_is_charging"] = False
            return
        
        if not st.session_state.get("car_is_plugged_in", True):
            st.session_state["car_is_charging"] = False
            return


        schedule_start, schedule_end = get_standard_schedule(now)

        if schedule_start <= now < schedule_end:
            st.session_state["car_is_charging"] = True
        else:
            st.session_state["car_is_charging"] = False

    def _check_schedule_reset(self):
        """
        Re-enable scheduled charging if a new day has started.
        Clears the 'schedule_charge_disable_date' flag if reset.
        """
        current_date = st.session_state["system_date"]
        disable_date = st.session_state.get("schedule_charge_disable_date")

        if disable_date and current_date > disable_date:
            st.session_state["schedule_charge_enabled"] = True
            st.session_state["schedule_charge_disable_date"] = None

    def get_state(self):
        """Build and return a copy of the current system state from top-level session keys."""
        return {
            key: st.session_state.get(key)
            for key in self.system_state_attr
        }
