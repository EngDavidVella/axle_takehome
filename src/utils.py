from datetime import datetime, timedelta
import streamlit as st


def get_current_time_to_nearest_30_minutes():
    """Return the current time, rounded to the nearest 30 minutes"""
    now = datetime.now()
    minutes = 30 * round(now.minute / 30)
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)

def floor_to_nearest_30_minutes(dt: datetime) -> datetime:
    """Round a datetime down to the nearest 30-minute mark."""
    floored_minute = 0 if dt.minute < 30 else 30
    return dt.replace(minute=floored_minute, second=0, microsecond=0)


def get_standard_schedule(system_date_time: datetime):
    """Return the next scheduled charging window (02:00–05:00)."""
    base_date = system_date_time.date()
    start = datetime.combine(base_date, datetime.strptime("02:00", "%H:%M").time())
    end = datetime.combine(base_date, datetime.strptime("05:00", "%H:%M").time())

    if system_date_time >= end:
        # If already past today’s window, schedule for tomorrow
        start += timedelta(days=1)
        end += timedelta(days=1)

    return start, end

def get_override_schedule() -> tuple[datetime, datetime]:
    """Return a 1-hour override charging window starting from the current system time."""
    system_date = st.session_state["system_date"]
    system_time = st.session_state["system_time"]
    start = datetime.combine(system_date, system_time)
    end = start + timedelta(hours=1)
    return start, end
