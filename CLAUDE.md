# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Personal Garmin health dashboard built with Streamlit. Pulls data from the Garmin Connect API via the `garminconnect` Python library, processes it into pandas DataFrames, and displays interactive Plotly charts with health insights.

## Commands

```bash
# Run the dashboard
streamlit run main.py

# Install/sync dependencies
uv sync

# Quick data fetch test (no UI)
python -c "from data.fetch import fetch_all; fetch_all(7)"

# Import check
python -c "from data.fetch import fetch_all; from data.process import process_all; from analysis.health import generate_all_insights; print('OK')"
```

There are no tests, linter, or CI configured yet.

## Architecture

**Data flow:** Garmin API → `data/fetch.py` (raw JSON, cached to `output/`) → `data/process.py` (pandas DataFrames) → `analysis/health.py` (text insights) → `dashboard/*.py` (Streamlit UI)

The `processed` dict is the central data structure passed through the entire dashboard. It is produced by `process_all()` and contains DataFrames keyed by metric type (`heart_rate`, `stress`, `sleep_summaries`, `rhr`, `hrv_summaries`, `body_battery`, `spo2`, `daily_steps`, `activities`) plus nested dicts for per-night detail (`sleep_details`, `hrv_details`).

### Key conventions

- **Timezone:** All timestamps are converted to `America/Mexico_City` at the processing layer (`data/process.py`). Raw Garmin data comes in two formats: UNIX milliseconds (HR, stress, body battery) and ISO strings in GMT (steps, sleep, HRV readings). Both are normalized via `_ts_to_datetime()` and `_gmt_str_to_datetime()`.
- **Caching:** `data/fetch.py` caches each day's raw API response as `output/garmin_YYYY-MM-DD.json`. Past days use cache; today is always re-fetched (incomplete data). Streamlit has a separate 1-hour TTL cache via `@st.cache_data`.
- **Garmin API rate limiting:** 0.3s delay between per-day fetches. The API can throttle or require re-auth. `_safe_call()` wraps every API call to return None on failure.
- **Stress values:** Garmin uses -1/-2 for unmeasured intervals. `process_stress()` filters these out (keeps only >= 0).
- **Charts:** All Plotly charts use `plotly_dark` template with transparent backgrounds. Color constants and layout defaults are in `dashboard/charts.py`.
- **Credentials:** `.env` file with `GARMIN_EMAIL` and `GARMIN_PASSWORD`. Never commit this file.

### Garmin API reference

The `garminconnect_functions.md` file documents each API method's call signature, return structure, and sample data. Consult this before adding new metrics — the response formats vary significantly between endpoints.

## Planned features (not yet implemented)

- Food log correlation with health metrics
- Cron job for daily 6 AM data pull
- Openclaw AI agent integration