# Garmin Health Dashboard — Setup Guide

A personal health dashboard that connects to your Garmin watch data and displays interactive charts with health insights. Built with Streamlit, Plotly, and the `garminconnect` Python library.

![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue)

## What you'll get

A local dashboard with five pages:

- **Overview** — KPI cards (resting HR, HRV status, sleep score, body battery, steps), 30-day trend sparklines, and AI-generated health insights
- **Sleep** — Sleep stage breakdown per night, sleep score trend, body battery recharge, and detailed per-night view (HR, HRV, body battery during sleep)
- **Heart & HRV** — Resting heart rate trend, HRV with baseline bands, heart rate distribution, intraday HR explorer
- **Stress & Energy** — Average stress by hour of day, daily stress trend, body battery daily curve
- **Activity** — Activity log table, steps vs goal, VO2 max trend, HR zone distribution per activity

## Prerequisites

- A **Garmin watch** that syncs to Garmin Connect
- A **Garmin Connect account** (the email and password you use at connect.garmin.com)
- **Python 3.13 or newer** installed on your computer
- **uv** (Python package manager) — install instructions below

### Installing Python 3.13

If you don't have Python 3.13+, the easiest way to get it:

- **macOS**: `brew install python@3.13`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3.13` (Ubuntu 24.04+) or use [pyenv](https://github.com/pyenv/pyenv)

Verify with: `python3 --version`

### Installing uv

uv is a fast Python package manager that this project uses.

- **macOS/Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Windows**: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

Verify with: `uv --version`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/dcpadilla01/garmin-health-dashboard.git
cd garmin-health-dashboard
```

### 2. Install dependencies

```bash
uv sync
```

This creates a virtual environment and installs everything the dashboard needs.

### 3. Run the dashboard

```bash
python run.py
```

On first run, the CLI will:
1. Ask for your **Garmin Connect email** and **password**
2. Save them to a `.env` file (private — listed in `.gitignore`, never uploaded)
3. Log in to Garmin and fetch 30 days of health data (takes a few minutes — the API is rate-limited)
4. Cache the data locally in an `output/` folder so future runs are fast
5. Open the dashboard in your browser at `http://localhost:8501`

**Options:**

```bash
# Fetch a different number of days
python run.py --days 14

# Re-enter your credentials
python run.py --setup
```

> You can also run the dashboard directly with `streamlit run main.py` if you prefer to create the `.env` file manually.

## Timezone

The CLI asks for your timezone during setup. It defaults to **America/Mexico_City**. All chart timestamps and time-based analysis use this setting.

To change it later, run:

```bash
python run.py --setup
```

This will re-prompt for your email, password, and timezone. After changing the timezone, delete the `output/` folder so cached data gets reprocessed:

```bash
rm -rf output/
python run.py
```

Common timezone values: `America/New_York`, `America/Chicago`, `America/Denver`, `America/Los_Angeles`, `Europe/London`, `Europe/Berlin`, `Asia/Tokyo`.

## Using the dashboard

- Use the **sidebar** to navigate between pages
- Adjust the **"Days of history"** slider to change how far back the data goes (7–90 days)
- Click **"Refresh Data"** to re-fetch from Garmin (useful after a new day of data comes in)
- Charts are interactive — hover for details, click-drag to zoom, double-click to reset

## Troubleshooting

### "Login failed" or authentication errors

- Double-check your email and password in `.env`
- If you use Google/Apple sign-in for Garmin Connect, you'll need to set a password directly at [connect.garmin.com](https://connect.garmin.com) under account settings
- Garmin may temporarily block logins if you try too many times — wait a few minutes and try again

### Empty charts or missing data

- Some metrics require specific Garmin watch models. If your watch doesn't track SpO2 or Body Battery, those sections will be empty
- The first day of data may be incomplete (today's data is still being recorded)
- If a specific day failed to fetch, delete its file from `output/` (e.g., `output/garmin_2026-03-15.json`) and refresh

### "No module named 'data'" or import errors

Make sure you're running from the project root directory:

```bash
cd garmin-health-dashboard
streamlit run main.py
```

### Port already in use

If port 8501 is taken, Streamlit will automatically try the next available port. You can also specify one:

```bash
streamlit run main.py --server.port 8502
```

## Privacy

- All data stays on your computer. Nothing is sent to any server other than Garmin's own API.
- Your cached health data is stored in the `output/` folder. This folder is in `.gitignore` and will not be uploaded if you fork this repo.
- Your credentials in `.env` are also in `.gitignore`.

## Project structure

```
garmin-health-dashboard/
├── run.py               # CLI launcher (start here)
├── main.py              # Streamlit dashboard
├── data/
│   ├── fetch.py         # Garmin API data fetching with caching
│   └── process.py       # Data normalization and timezone conversion
├── analysis/
│   └── health.py        # Health insights generation
├── dashboard/
│   ├── overview.py      # Overview page
│   ├── sleep.py         # Sleep analysis page
│   ├── heart.py         # Heart rate & HRV page
│   ├── stress.py        # Stress & energy page
│   ├── activity.py      # Activity & fitness page
│   └── charts.py        # Shared Plotly chart helpers
├── pyproject.toml       # Python dependencies
└── .env                 # Your Garmin credentials (you create this)
```