# Axle Tech Take-Home: EV Charge Control Pannel

## Running the App
To launch the app locally, make sure you have Docker installed. Then, in terminal,  run:

`docker compose up`

You can then access the frontend at http://localhost:8501/

### You can interact with the system by:

- **Mimicing the live system feed through the 'Demo Admin Controls' sidebar:**
  - Plugging/unplugging the car via the sidebar
  - Adjusting system time, battery SoC, and schedule toggles in the Demo Admin Controls (sidebar)

- **Interact like an end user through the main user interface 'Controls' and 'Dashboard' and a plot for 'Chraging Schedule':**
  - Using the “Start Charging” and “Stop Charging” buttons to stop and start charging

## Design Decisions

- **Centralised Session State:**  
  I used Streamlit’s `st.session_state` to simulate a persistent system state across user interactions. A single `SystemStateManager` class was introduced to centralise initialisation, automatic updates, and admin control rendering. This makes the system traceable, easily extensible, and mockable.

- **Modular Architecture:**  
  The code is structured by responsibility:
  - `models.py` holds session state management
  - `backend.py` handles event-driven UI logic
  - `plotting.py` manages visualisation
  - `utils.py` contains shared helper logic  
  This separation allows each piece to evolve independently, and could support unit testing or backend decoupling in future.

- **Visual Feedback:**  
  I used `st.toast()` for real-time user feedback, and dynamically coloured UI elements to reflect car status and charging logic — helping simulate a live system.

- **Schedule vs Override Windows:**  
  Both scheduled and override charging windows are handled as time-bound states. The SoC plot annotates these with colour-coded overlays (green for scheduled, orange for override) for clarity.

## Assumptions Made

- The system does not connect to a real car or charging engine. All values (SoC, plugged-in status, system time) are controlled via admin inputs for demonstration.

- **Charge rate is fixed:**  
  Charging increases SoC by ~16.67% per 30 minutes, assuming linearity and no tapering effects.

- **Override duration is fixed at 60 minutes.**

- Scheduled charging (2–5am) applies only when the car is plugged in and the schedule is enabled.

- The “disable schedule until tomorrow” rule is based on a per-day flag. There's no persistence across days beyond the session.

## Time Prioritisation

### Prioritised
- Functional correctness (e.g. override expiry, schedule disable after stop)
- Robust state handling and clear user feedback
- Modular structure for clarity and maintainability
- Time-series projection logic for SoC
- Visual annotation of charge windows on the plot

### Deprioritised
- UI polish (Streamlit default styling was used)
- Error handling for edge-edge cases (e.g. leap seconds, overlapping charge windows)
- Test coverage or CI
- Config-driven scheduling or i18n/localisation

## System Design Thinking

- I treated this as a real-world prototype where state changes need to be transparent, explainable, and user-friendly.

- I relied on 'user stories' I deduced from the original breif (see user user_stories_dv.txt)

- The charge schedule logic is handled declaratively and can easily be made dynamic or user-configurable.

- The design supports evolution into a full app:
  - SystemStateManager could be connected to an API
  - The frontend already separates display from logic
  - Sidebars could be hidden in production

- I chose not to over-engineer it (e.g. no DI pattern or external state manager) but left clear extension points if needed.

- While the original guidance suggested routing everything through backend.py, I chose to initialise SystemStateManager and call render_soc_plot_area() directly in app.py to preserve clear ownership boundaries. 	
  - These calls are structural (state setup and plotting), and separating them from button-driven event logic kept backend.py focused on user interaction.

## Self-Critique

- A few methods could arguably be split for single responsibility (e.g. `_update_charging_state` in `SystemStateManager`), but in the context of a small, throwaway project, I opted to keep the logic inline for readability.

- Some logic relies on session state being correctly initialised, which would benefit from stricter encapsulation or validation in a production setup.

- If I had more time, I would introduce basic unit tests for the core schedule logic and override expiry handling.

## Known Issues

- There is a minor display issue which I opted not to fix due to time constraints. It does not affect the core functionality or logic, but I would revisit this in a real-world implementation.
  - When a scheduled charge is interrupted, the next shceduled charge only gets displayed porperly on the plot half an hour after the end of the current sheduled charge window.


## Summary

This submission is structured with extensibility and real-world clarity in mind, while being pragmatic about polish and scope. I believe that all brief criteria have been implemented, with additional affordances like annotated plots and admin controls to facilitate interactive review and demo.
