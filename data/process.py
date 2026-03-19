"""Data processing module.

Converts raw Garmin API responses into clean pandas DataFrames
with proper timezone handling (all times in America/Mexico_City).
"""

import pandas as pd
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Mexico_City")


def _ts_to_datetime(ts_ms: int | float) -> pd.Timestamp:
    """Convert UNIX timestamp in milliseconds to Mexico City datetime."""
    return pd.Timestamp(ts_ms, unit="ms", tz="UTC").tz_convert(TZ)


def _gmt_str_to_datetime(gmt_str: str) -> pd.Timestamp:
    """Convert GMT string like '2026-03-17T06:00:00.0' to Mexico City datetime."""
    return pd.Timestamp(gmt_str, tz="UTC").tz_convert(TZ)


# ── Heart Rate ──────────────────────────────────────────────────────

def process_heart_rate(day_data: dict) -> pd.DataFrame:
    """Process heart rate time series into a DataFrame.

    Returns DataFrame with columns: [datetime, heart_rate]
    """
    hr_data = day_data.get("heart_rate")
    if not hr_data or not hr_data.get("heartRateValues"):
        return pd.DataFrame(columns=["datetime", "heart_rate"])

    records = []
    for ts_ms, hr in hr_data["heartRateValues"]:
        if hr is not None:
            records.append({
                "datetime": _ts_to_datetime(ts_ms),
                "heart_rate": hr,
            })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("datetime").reset_index(drop=True)
    return df


# ── Stress ──────────────────────────────────────────────────────────

def process_stress(day_data: dict) -> pd.DataFrame:
    """Process stress time series into a DataFrame.

    Returns DataFrame with columns: [datetime, stress]
    Filters out negative stress values (Garmin uses -1/-2 for unmeasured).
    """
    stress_data = day_data.get("stress")
    if not stress_data or not stress_data.get("stressValuesArray"):
        return pd.DataFrame(columns=["datetime", "stress"])

    records = []
    for ts_ms, stress in stress_data["stressValuesArray"]:
        if stress is not None and stress >= 0:
            records.append({
                "datetime": _ts_to_datetime(ts_ms),
                "stress": stress,
            })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("datetime").reset_index(drop=True)
    return df


# ── Steps ───────────────────────────────────────────────────────────

def process_steps(day_data: dict) -> pd.DataFrame:
    """Process 15-min step intervals into a DataFrame.

    Returns DataFrame with columns: [datetime, steps, activity_level]
    """
    steps_data = day_data.get("steps")
    if not steps_data:
        return pd.DataFrame(columns=["datetime", "steps", "activity_level"])

    records = []
    for entry in steps_data:
        records.append({
            "datetime": _gmt_str_to_datetime(entry["startGMT"]),
            "steps": entry.get("steps", 0),
            "activity_level": entry.get("primaryActivityLevel", "unknown"),
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("datetime").reset_index(drop=True)
    return df


def process_daily_steps(daily_steps: list) -> pd.DataFrame:
    """Process daily step totals.

    Returns DataFrame with columns: [date, total_steps, step_goal, distance]
    """
    if not daily_steps:
        return pd.DataFrame(columns=["date", "total_steps", "step_goal", "distance"])

    records = []
    for entry in daily_steps:
        records.append({
            "date": pd.Timestamp(entry["calendarDate"]),
            "total_steps": entry.get("totalSteps", 0),
            "step_goal": entry.get("stepGoal", 0),
            "distance": entry.get("totalDistance", 0),
        })

    return pd.DataFrame(records).sort_values("date").reset_index(drop=True)


# ── Sleep ───────────────────────────────────────────────────────────

def process_sleep(day_data: dict) -> dict:
    """Process sleep data into a summary dict and time-series DataFrames.

    Returns dict with keys:
      - summary: dict with sleep metrics
      - heart_rate: DataFrame [datetime, heart_rate]
      - stress: DataFrame [datetime, stress]
      - body_battery: DataFrame [datetime, body_battery]
      - hrv: DataFrame [datetime, hrv]
    """
    sleep_data = day_data.get("sleep")
    if not sleep_data:
        return {
            "summary": {},
            "heart_rate": pd.DataFrame(),
            "stress": pd.DataFrame(),
            "body_battery": pd.DataFrame(),
            "hrv": pd.DataFrame(),
        }

    # Sleep summary fields live inside dailySleepDTO;
    # bodyBatteryChange, hrvStatus, and time-series arrays are top-level.
    dto = sleep_data.get("dailySleepDTO", {})
    sleep_scores = dto.get("sleepScores", {})
    summary = {
        "date": dto.get("calendarDate"),
        "sleep_time_seconds": dto.get("sleepTimeSeconds", 0),
        "deep_seconds": dto.get("deepSleepSeconds", 0),
        "light_seconds": dto.get("lightSleepSeconds", 0),
        "rem_seconds": dto.get("remSleepSeconds", 0),
        "awake_seconds": dto.get("awakeSleepSeconds", 0),
        "overall_score": sleep_scores.get("overall", {}).get("value"),
        "overall_qualifier": sleep_scores.get("overall", {}).get("qualifierKey"),
        "deep_pct": sleep_scores.get("deepPercentage", {}).get("value"),
        "deep_qualifier": sleep_scores.get("deepPercentage", {}).get("qualifierKey"),
        "deep_optimal_start": sleep_scores.get("deepPercentage", {}).get("optimalStart"),
        "deep_optimal_end": sleep_scores.get("deepPercentage", {}).get("optimalEnd"),
        "light_pct": sleep_scores.get("lightPercentage", {}).get("value"),
        "rem_pct": sleep_scores.get("remPercentage", {}).get("value"),
        "rem_optimal_start": sleep_scores.get("remPercentage", {}).get("optimalStart"),
        "rem_optimal_end": sleep_scores.get("remPercentage", {}).get("optimalEnd"),
        "body_battery_change": sleep_data.get("bodyBatteryChange"),
        "resting_hr": dto.get("restingHeartRate"),
        "hrv_status": sleep_data.get("hrvStatus"),
        "sleep_start": (
            _ts_to_datetime(dto["sleepStartTimestampGMT"])
            if dto.get("sleepStartTimestampGMT")
            else None
        ),
        "sleep_end": (
            _ts_to_datetime(dto["sleepEndTimestampGMT"])
            if dto.get("sleepEndTimestampGMT")
            else None
        ),
    }

    # Compute sleep efficiency
    if summary["sleep_start"] and summary["sleep_end"] and summary["sleep_time_seconds"]:
        total_bed_seconds = (summary["sleep_end"] - summary["sleep_start"]).total_seconds()
        if total_bed_seconds > 0:
            summary["efficiency"] = summary["sleep_time_seconds"] / total_bed_seconds
        else:
            summary["efficiency"] = None
    else:
        summary["efficiency"] = None

    # Time series from sleep data
    def _process_sleep_ts(key, value_name):
        entries = sleep_data.get(key, [])
        if not entries:
            return pd.DataFrame(columns=["datetime", value_name])
        records = [
            {"datetime": _ts_to_datetime(e["startGMT"]), value_name: e["value"]}
            for e in entries
            if e.get("value") is not None
        ]
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.sort_values("datetime").reset_index(drop=True)
        return df

    return {
        "summary": summary,
        "heart_rate": _process_sleep_ts("sleepHeartRate", "heart_rate"),
        "stress": _process_sleep_ts("sleepStress", "stress"),
        "body_battery": _process_sleep_ts("sleepBodyBattery", "body_battery"),
        "hrv": _process_sleep_ts("hrvData", "hrv"),
    }


# ── RHR ─────────────────────────────────────────────────────────────

def process_rhr(day_data: dict) -> float | None:
    """Extract resting heart rate value from day data."""
    rhr_data = day_data.get("rhr")
    if not rhr_data:
        return None
    try:
        metrics = rhr_data["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"]
        return metrics[0]["value"]
    except (KeyError, IndexError, TypeError):
        return None


# ── HRV ─────────────────────────────────────────────────────────────

def process_hrv(day_data: dict) -> dict:
    """Process HRV summary and readings.

    Returns dict with:
      - summary: dict with weekly_avg, last_night_avg, status, baseline
      - readings: DataFrame [datetime, hrv]
    """
    hrv_data = day_data.get("hrv")
    if not hrv_data:
        return {"summary": {}, "readings": pd.DataFrame()}

    hrv_summary = hrv_data.get("hrvSummary", {})
    baseline = hrv_summary.get("baseline", {})
    summary = {
        "date": hrv_summary.get("calendarDate"),
        "weekly_avg": hrv_summary.get("weeklyAvg"),
        "last_night_avg": hrv_summary.get("lastNightAvg"),
        "last_night_5min_high": hrv_summary.get("lastNight5MinHigh"),
        "status": hrv_summary.get("status"),
        "balanced_low": baseline.get("balancedLow"),
        "balanced_upper": baseline.get("balancedUpper"),
        "low_upper": baseline.get("lowUpper"),
    }

    readings = hrv_data.get("hrvReadings", [])
    if readings:
        records = []
        for r in readings:
            gmt_str = r.get("readingTimeGMT")
            if gmt_str and r.get("hrvValue") is not None:
                records.append({
                    "datetime": _gmt_str_to_datetime(gmt_str),
                    "hrv": r["hrvValue"],
                })
        readings_df = pd.DataFrame(records)
        if not readings_df.empty:
            readings_df = readings_df.sort_values("datetime").reset_index(drop=True)
    else:
        readings_df = pd.DataFrame(columns=["datetime", "hrv"])

    return {"summary": summary, "readings": readings_df}


# ── Body Battery ────────────────────────────────────────────────────

def process_body_battery(day_data: dict) -> pd.DataFrame:
    """Process body battery time series.

    Returns DataFrame with columns: [datetime, body_battery]
    """
    bb_data = day_data.get("body_battery")
    if not bb_data:
        return pd.DataFrame(columns=["datetime", "body_battery"])

    # The API returns either:
    # - A list of day-summary dicts, each with "bodyBatteryValuesArray": [[ts, val], ...]
    # - A dict with "bodyBatteryValuesArray" or "chartValueList"
    # - A flat list of [ts, val] pairs
    entries = bb_data
    if isinstance(bb_data, list) and bb_data and isinstance(bb_data[0], dict):
        # List of day-summary dicts — extract the values arrays from each
        all_values = []
        for day_dict in bb_data:
            all_values.extend(day_dict.get("bodyBatteryValuesArray", []))
        entries = all_values
    elif isinstance(bb_data, dict):
        entries = bb_data.get("bodyBatteryValuesArray", bb_data.get("chartValueList", []))

    if not entries:
        return pd.DataFrame(columns=["datetime", "body_battery"])

    records = []
    for entry in entries:
        if isinstance(entry, list) and len(entry) == 2:
            ts_ms, val = entry
            if val is not None:
                records.append({
                    "datetime": _ts_to_datetime(ts_ms),
                    "body_battery": val,
                })
        elif isinstance(entry, dict):
            ts = entry.get("timestampGMT") or entry.get("startGMT")
            val = entry.get("bodyBatteryValue") or entry.get("value")
            if ts is not None and val is not None:
                if isinstance(ts, (int, float)):
                    records.append({
                        "datetime": _ts_to_datetime(ts),
                        "body_battery": val,
                    })
                else:
                    records.append({
                        "datetime": _gmt_str_to_datetime(ts),
                        "body_battery": val,
                    })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("datetime").reset_index(drop=True)
    return df


# ── SpO2 ────────────────────────────────────────────────────────────

def process_spo2(day_data: dict) -> pd.DataFrame:
    """Process SpO2 data.

    Returns DataFrame with columns: [datetime, spo2]
    """
    spo2_data = day_data.get("spo2")
    if not spo2_data:
        return pd.DataFrame(columns=["datetime", "spo2"])

    # SpO2 can come in different formats
    entries = spo2_data
    if isinstance(spo2_data, dict):
        entries = spo2_data.get("spO2Values", spo2_data.get("spo2Readings", []))

    if not entries:
        return pd.DataFrame(columns=["datetime", "spo2"])

    records = []
    for entry in entries:
        if isinstance(entry, list) and len(entry) == 2:
            ts_ms, val = entry
            if val is not None and val > 0:
                records.append({
                    "datetime": _ts_to_datetime(ts_ms),
                    "spo2": val,
                })
        elif isinstance(entry, dict):
            ts = entry.get("timestampGMT") or entry.get("startGMT")
            val = entry.get("spO2Value") or entry.get("value") or entry.get("spo2")
            if ts is not None and val is not None and val > 0:
                if isinstance(ts, (int, float)):
                    records.append({
                        "datetime": _ts_to_datetime(ts),
                        "spo2": val,
                    })
                else:
                    records.append({
                        "datetime": _gmt_str_to_datetime(ts),
                        "spo2": val,
                    })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("datetime").reset_index(drop=True)
    return df


# ── Activities ──────────────────────────────────────────────────────

def process_activities(activities: list) -> pd.DataFrame:
    """Process activities list into a DataFrame."""
    if not activities:
        return pd.DataFrame(columns=[
            "date", "name", "type", "duration_min", "distance_km",
            "avg_hr", "max_hr", "calories", "avg_speed",
            "aerobic_te", "anaerobic_te", "vo2max", "steps",
            "hr_zone_1", "hr_zone_2", "hr_zone_3", "hr_zone_4", "hr_zone_5",
        ])

    records = []
    for a in activities:
        activity_type = a.get("activityType", {})
        records.append({
            "date": pd.Timestamp(a.get("startTimeLocal", "")),
            "name": a.get("activityName", ""),
            "type": activity_type.get("typeKey", "unknown"),
            "duration_min": round((a.get("duration", 0) or 0) / 60, 1),
            "distance_km": round((a.get("distance", 0) or 0) / 1000, 2),
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "calories": a.get("calories"),
            "avg_speed": a.get("averageSpeed"),
            "aerobic_te": a.get("aerobicTrainingEffect"),
            "anaerobic_te": a.get("anaerobicTrainingEffect"),
            "vo2max": a.get("vO2MaxValue"),
            "steps": a.get("steps"),
            "hr_zone_1": a.get("hrTimeInZone_1"),
            "hr_zone_2": a.get("hrTimeInZone_2"),
            "hr_zone_3": a.get("hrTimeInZone_3"),
            "hr_zone_4": a.get("hrTimeInZone_4"),
            "hr_zone_5": a.get("hrTimeInZone_5"),
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df = df.sort_values("date", ascending=False).reset_index(drop=True)
    return df


# ── Master Processing ──────────────────────────────────────────────

def process_all(raw_data: dict) -> dict:
    """Process all raw data into DataFrames and summaries.

    Input: output from fetch.fetch_all()
    Returns dict with all processed data ready for analysis and display.
    """
    daily = raw_data["daily"]
    dates = sorted(daily.keys())

    # Per-day time series
    all_hr = []
    all_stress = []
    all_steps = []
    all_body_battery = []
    all_spo2 = []
    sleep_summaries = []
    sleep_details = {}
    rhr_values = []
    hrv_summaries = []
    hrv_details = {}

    for d in dates:
        day = daily[d]

        hr = process_heart_rate(day)
        if not hr.empty:
            all_hr.append(hr)

        stress = process_stress(day)
        if not stress.empty:
            all_stress.append(stress)

        steps = process_steps(day)
        if not steps.empty:
            all_steps.append(steps)

        bb = process_body_battery(day)
        if not bb.empty:
            all_body_battery.append(bb)

        spo2 = process_spo2(day)
        if not spo2.empty:
            all_spo2.append(spo2)

        sleep = process_sleep(day)
        if sleep["summary"]:
            sleep_summaries.append(sleep["summary"])
            sleep_details[d] = sleep

        rhr = process_rhr(day)
        if rhr is not None:
            rhr_values.append({"date": pd.Timestamp(d), "rhr": rhr})

        hrv = process_hrv(day)
        if hrv["summary"]:
            hrv_summaries.append(hrv["summary"])
            hrv_details[d] = hrv

    return {
        "heart_rate": pd.concat(all_hr, ignore_index=True) if all_hr else pd.DataFrame(),
        "stress": pd.concat(all_stress, ignore_index=True) if all_stress else pd.DataFrame(),
        "steps_intraday": pd.concat(all_steps, ignore_index=True) if all_steps else pd.DataFrame(),
        "daily_steps": process_daily_steps(raw_data["daily_steps"]),
        "body_battery": pd.concat(all_body_battery, ignore_index=True) if all_body_battery else pd.DataFrame(),
        "spo2": pd.concat(all_spo2, ignore_index=True) if all_spo2 else pd.DataFrame(),
        "sleep_summaries": pd.DataFrame(sleep_summaries) if sleep_summaries else pd.DataFrame(),
        "sleep_details": sleep_details,
        "rhr": pd.DataFrame(rhr_values) if rhr_values else pd.DataFrame(),
        "hrv_summaries": pd.DataFrame(hrv_summaries) if hrv_summaries else pd.DataFrame(),
        "hrv_details": hrv_details,
        "activities": process_activities(raw_data["activities"]),
    }
