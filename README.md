# Garmin Health Dashboard

A personal health dashboard that pulls data from your Garmin watch and displays interactive charts with health insights — all running locally on your machine.

Built with **Streamlit**, **Plotly**, and the [`garminconnect`](https://github.com/cyberjunky/python-garminconnect) Python library.

## Dashboard Pages

| Page | What it shows |
|------|---------------|
| **Overview** | KPI cards (resting HR, HRV, sleep score, body battery, steps), 30-day sparklines, health insights |
| **Sleep** | Sleep stage breakdown, score trend, body battery recharge, per-night detail (HR, HRV curves) |
| **Heart & HRV** | RHR trend, HRV with baseline bands, HR distribution, intraday HR explorer |
| **Stress & Energy** | Stress by hour of day, daily stress trend, body battery daily curve |
| **Activity** | Activity log, steps vs goal, VO2 max trend, HR zone distribution |

## Quick Start

```bash
git clone https://github.com/dcpadilla01/garmin-health-dashboard.git
cd garmin-health-dashboard
uv sync
python run.py
```

The CLI will prompt for your Garmin email and password on first run, save them locally, and launch the dashboard at `http://localhost:8501`.

```bash
# Fetch only 14 days of data
python run.py --days 14

# Re-enter credentials
python run.py --setup
```

## Timezone

All timestamps default to **America/Mexico_City**. The CLI asks for your timezone during setup. To change it later, run `python run.py --setup` — see the [Setup Guide](SETUP.md#timezone) for details.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- A Garmin watch that syncs to Garmin Connect

## Full Setup Guide

For detailed installation instructions, troubleshooting, and OS-specific steps, see the **[Setup Guide](SETUP.md)**.

## Privacy

All data stays on your computer. Credentials and health data are in `.gitignore` and never leave your machine.
