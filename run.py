#!/usr/bin/env python3
"""Garmin Health Dashboard — CLI launcher.

Handles first-time setup (credentials) and launches the Streamlit dashboard.
"""

import os
import subprocess
import sys
from getpass import getpass
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"


def _env_exists() -> bool:
    """Check if .env exists and has both credentials."""
    if not ENV_PATH.exists():
        return False
    content = ENV_PATH.read_text()
    return "GARMIN_EMAIL" in content and "GARMIN_PASSWORD" in content


def _read_env() -> dict:
    """Read existing .env values."""
    values = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def _save_env(email: str, password: str, timezone: str):
    """Save credentials and timezone to .env file."""
    ENV_PATH.write_text(
        f'GARMIN_EMAIL="{email}"\n'
        f'GARMIN_PASSWORD="{password}"\n'
        f'TIMEZONE="{timezone}"\n'
    )
    print(f"\n  Configuration saved to {ENV_PATH}")
    print("  This file is in .gitignore and will not be shared.\n")


def setup():
    """Interactive first-time setup."""
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║     Garmin Health Dashboard Setup     ║")
    print("  ╚══════════════════════════════════════╝\n")

    existing = _read_env()

    # Email
    default_email = existing.get("GARMIN_EMAIL", "")
    if default_email:
        email = input(f"  Garmin email [{default_email}]: ").strip()
        if not email:
            email = default_email
    else:
        email = input("  Garmin email: ").strip()

    while not email or "@" not in email:
        print("  Please enter a valid email address.")
        email = input("  Garmin email: ").strip()

    # Password
    password = getpass("  Garmin password: ")
    while not password:
        print("  Password cannot be empty.")
        password = getpass("  Garmin password: ")

    # Timezone
    default_tz = existing.get("TIMEZONE", "America/Mexico_City")
    print(f"\n  Timezone is used for all displayed timestamps.")
    print(f"  Examples: America/New_York, Europe/London, Asia/Tokyo")
    tz_input = input(f"  Timezone [{default_tz}]: ").strip()
    timezone = tz_input or default_tz

    # Validate
    from zoneinfo import available_timezones
    while timezone not in available_timezones():
        print(f"  '{timezone}' is not a valid timezone.")
        tz_input = input(f"  Timezone [{default_tz}]: ").strip()
        timezone = tz_input or default_tz

    _save_env(email, password, timezone)


def _find_python() -> str:
    """Find the correct Python executable (prefer .venv, then uv run)."""
    project_dir = Path(__file__).parent
    # Check for .venv created by uv sync
    venv_python = project_dir / ".venv" / "bin" / "python"
    if not venv_python.exists():
        # Windows
        venv_python = project_dir / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def launch(days: int = 30):
    """Launch the Streamlit dashboard."""
    python = _find_python()

    # Check that streamlit is importable from the target python
    check = subprocess.run(
        [python, "-c", "import streamlit"],
        capture_output=True,
    )
    if check.returncode != 0:
        print("  Error: Streamlit is not installed.")
        print("  Run 'uv sync' first to install dependencies.\n")
        sys.exit(1)

    print(f"  Launching dashboard (last {days} days of data)...")
    print("  Press Ctrl+C to stop.\n")

    streamlit_cmd = [
        python, "-m", "streamlit", "run", "main.py",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]

    os.chdir(Path(__file__).parent)
    subprocess.run(streamlit_cmd)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Garmin Health Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="  Examples:\n"
               "    python run.py            # Setup + launch\n"
               "    python run.py --days 14  # Launch with 14 days\n"
               "    python run.py --setup    # Re-enter credentials\n",
    )
    parser.add_argument("--days", type=int, default=30,
                        help="days of history to fetch (default: 30)")
    parser.add_argument("--setup", action="store_true",
                        help="re-run credential setup")

    args = parser.parse_args()

    # First-time setup or explicit --setup
    if args.setup or not _env_exists():
        setup()

    launch(args.days)


if __name__ == "__main__":
    main()