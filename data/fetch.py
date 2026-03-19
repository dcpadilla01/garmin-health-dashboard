"""Garmin API data fetching module.

Pulls all health metrics for a given date range and caches as JSON.
"""

import json
import os
import time
from datetime import date, timedelta

from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")


def _get_client() -> Garmin:
    """Create and authenticate a Garmin client."""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin(email, password)
    client.login()
    return client


def _cache_path(cdate: str) -> str:
    """Return cache file path for a given date."""
    return os.path.join(CACHE_DIR, f"garmin_{cdate}.json")


def _load_cached(cdate: str) -> dict | None:
    """Load cached data for a date, or None if not cached."""
    path = _cache_path(cdate)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def _save_cache(cdate: str, data: dict) -> None:
    """Save data to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(_cache_path(cdate), "w") as f:
        json.dump(data, f, indent=2, default=str)


def _safe_call(fn, *args, **kwargs):
    """Call a Garmin API function, returning None on error."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


def fetch_day(client: Garmin, cdate: str, force: bool = False) -> dict:
    """Fetch all metrics for a single day.

    Uses cache unless force=True. The cache file for today is always
    re-fetched since the day's data is incomplete.
    """
    is_today = cdate == str(date.today())

    if not force and not is_today:
        cached = _load_cached(cdate)
        if cached:
            return cached

    data = {
        "date": cdate,
        "heart_rate": _safe_call(client.get_heart_rates, cdate),
        "steps": _safe_call(client.get_steps_data, cdate),
        "stress": _safe_call(client.get_all_day_stress, cdate),
        "sleep": _safe_call(client.get_sleep_data, cdate),
        "rhr": _safe_call(client.get_rhr_day, cdate),
        "hrv": _safe_call(client.get_hrv_data, cdate),
        "body_battery": _safe_call(client.get_body_battery, cdate),
        "spo2": _safe_call(client.get_spo2_data, cdate),
    }

    _save_cache(cdate, data)
    return data


def fetch_all(days: int = 30, force: bool = False) -> dict:
    """Fetch all metrics for the last N days.

    Returns a dict with:
      - "daily": dict of date_str -> day_data
      - "daily_steps": list from get_daily_steps
      - "activities": list from get_activities_by_date
    """
    client = _get_client()
    today = date.today()
    start = today - timedelta(days=days - 1)

    start_str = str(start)
    end_str = str(today)

    # Range-based calls (only need to call once)
    daily_steps = _safe_call(client.get_daily_steps, start_str, end_str)
    activities = _safe_call(client.get_activities_by_date, start_str, end_str)

    # Per-day calls
    daily = {}
    for i in range(days):
        d = start + timedelta(days=i)
        cdate = str(d)
        daily[cdate] = fetch_day(client, cdate, force=force)
        time.sleep(0.3)  # Rate limiting

    return {
        "daily": daily,
        "daily_steps": daily_steps or [],
        "activities": activities or [],
    }
