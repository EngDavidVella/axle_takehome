import streamlit as st

import backend
from models import SystemStateManager
from plotting import render_soc_plot_area #plot_upcoming_charges
from utils import get_current_time_to_nearest_30_minutes


    
if __name__ == "__main__":
    print ('in main')    
    # Check for and nitialize session manager and models if needed
    # Ensure that one Instance is created per session (probably needs a singleton pattern later on)

    
    system_state_manager = SystemStateManager()
    
    # for debugging:
    for key, value in system_state_manager.get_state().items():
        print(f"{key}: {value}")
    
    backend.render_user_dashboard()
    st.subheader("Controls")
    backend.render_charge_controls()
    
    st.subheader("Charging Schedule")
    render_soc_plot_area()

    
    
    

