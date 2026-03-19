"""Health analysis module.

Generates insights and computed metrics from processed Garmin data.
"""

import pandas as pd


def analyze_sleep(processed: dict) -> list[str]:
    """Generate sleep-related insights."""
    insights = []
    sleep_df = processed["sleep_summaries"]
    if sleep_df.empty:
        return insights

    # Sleep score trend
    scores = sleep_df.dropna(subset=["overall_score"])
    if len(scores) >= 7:
        recent_7 = scores.tail(7)["overall_score"].mean()
        prior_7 = scores.tail(14).head(7)["overall_score"].mean() if len(scores) >= 14 else None
        avg_score = scores["overall_score"].mean()
        insights.append(
            f"Average sleep score: **{avg_score:.0f}** "
            f"(last 7 nights: **{recent_7:.0f}**)"
        )
        if prior_7 is not None:
            diff = recent_7 - prior_7
            direction = "improved" if diff > 0 else "declined"
            if abs(diff) >= 2:
                insights.append(
                    f"Sleep score has {direction} by {abs(diff):.0f} points vs the prior week"
                )

    # Deep sleep below optimal
    deep = sleep_df.dropna(subset=["deep_pct"])
    if not deep.empty:
        below_optimal = deep[deep["deep_pct"] < 16]
        recent_7_deep = deep.tail(7)
        recent_below = recent_7_deep[recent_7_deep["deep_pct"] < 16]
        if len(recent_below) > 0:
            insights.append(
                f"Deep sleep has been below optimal (<16%) for "
                f"**{len(recent_below)}** of the last {len(recent_7_deep)} nights"
            )

    # Body battery recharge trend
    bb_change = sleep_df.dropna(subset=["body_battery_change"])
    if not bb_change.empty:
        avg_recharge = bb_change["body_battery_change"].mean()
        recent_recharge = bb_change.tail(7)["body_battery_change"].mean()
        insights.append(
            f"Average body battery recharge per night: **{avg_recharge:.0f}** "
            f"(last 7: **{recent_recharge:.0f}**)"
        )

    # Sleep efficiency
    eff = sleep_df.dropna(subset=["efficiency"])
    if not eff.empty:
        avg_eff = eff["efficiency"].mean() * 100
        insights.append(f"Average sleep efficiency: **{avg_eff:.0f}%**")

    return insights


def analyze_cardiovascular(processed: dict) -> list[str]:
    """Generate cardiovascular health insights."""
    insights = []
    rhr_df = processed["rhr"]
    hrv_df = processed["hrv_summaries"]

    # RHR trend
    if not rhr_df.empty and len(rhr_df) >= 7:
        first_week = rhr_df.head(7)["rhr"].mean()
        last_week = rhr_df.tail(7)["rhr"].mean()
        diff = last_week - first_week
        current_rhr = rhr_df.tail(1)["rhr"].values[0]
        insights.append(f"Current resting heart rate: **{current_rhr:.0f} bpm**")
        if abs(diff) >= 1:
            direction = "decreased" if diff < 0 else "increased"
            fitness_note = (
                " — cardiovascular fitness is improving"
                if diff < 0
                else " — may indicate stress or reduced fitness"
            )
            insights.append(
                f"RHR has {direction} by **{abs(diff):.1f} bpm** over the past month{fitness_note}"
            )

    # HRV status distribution
    if not hrv_df.empty:
        status_counts = hrv_df["status"].value_counts()
        total = len(hrv_df)
        status_parts = []
        for status, count in status_counts.items():
            if status:
                status_parts.append(f"{status}: {count}/{total}")
        if status_parts:
            insights.append(f"HRV status distribution: {', '.join(status_parts)}")

        # Latest HRV status
        latest = hrv_df.iloc[-1]
        if latest.get("status"):
            insights.append(f"Current HRV status: **{latest['status']}**")

        # Weekly average trend
        weekly = hrv_df.dropna(subset=["weekly_avg"])
        if len(weekly) >= 7:
            recent_avg = weekly.tail(7)["weekly_avg"].mean()
            insights.append(f"HRV weekly average (last 7 days): **{recent_avg:.0f} ms**")

    return insights


def analyze_stress_energy(processed: dict) -> list[str]:
    """Generate stress and energy insights."""
    insights = []
    stress_df = processed["stress"]
    bb_df = processed["body_battery"]

    if not stress_df.empty:
        # Average stress by hour of day
        stress_with_hour = stress_df.copy()
        stress_with_hour["hour"] = stress_with_hour["datetime"].dt.hour
        hourly_avg = stress_with_hour.groupby("hour")["stress"].mean()

        peak_hour = hourly_avg.idxmax()
        peak_stress = hourly_avg.max()
        calm_hour = hourly_avg.idxmin()
        calm_stress = hourly_avg.min()

        insights.append(
            f"Peak stress typically at **{peak_hour}:00** (avg: {peak_stress:.0f}), "
            f"calmest at **{calm_hour}:00** (avg: {calm_stress:.0f})"
        )

        overall_avg = stress_df["stress"].mean()
        insights.append(f"30-day average stress level: **{overall_avg:.0f}**")

    if not bb_df.empty:
        # Daily min/max body battery
        bb_with_date = bb_df.copy()
        bb_with_date["date"] = bb_with_date["datetime"].dt.date
        daily_bb = bb_with_date.groupby("date")["body_battery"].agg(["min", "max"])
        avg_max = daily_bb["max"].mean()
        avg_min = daily_bb["min"].mean()
        avg_drain = avg_max - avg_min
        insights.append(
            f"Body battery: avg daily peak **{avg_max:.0f}**, "
            f"avg daily low **{avg_min:.0f}** (avg drain: {avg_drain:.0f})"
        )

    return insights


def analyze_activity(processed: dict) -> list[str]:
    """Generate activity and fitness insights."""
    insights = []
    activities_df = processed["activities"]
    steps_df = processed["daily_steps"]

    if not activities_df.empty:
        # Activity frequency
        total = len(activities_df)
        type_counts = activities_df["type"].value_counts()
        type_summary = ", ".join(f"{t}: {c}" for t, c in type_counts.head(5).items())
        insights.append(f"**{total}** activities in period ({type_summary})")

        # VO2 max trend
        vo2_data = activities_df.dropna(subset=["vo2max"])
        if not vo2_data.empty:
            latest_vo2 = vo2_data.iloc[0]["vo2max"]  # sorted desc by date
            insights.append(f"Latest VO2 max: **{latest_vo2:.0f}**")

        # Average HR during runs
        runs = activities_df[activities_df["type"] == "running"]
        if not runs.empty:
            avg_run_hr = runs["avg_hr"].mean()
            if pd.notna(avg_run_hr):
                insights.append(f"Average HR during runs: **{avg_run_hr:.0f} bpm**")

    if not steps_df.empty:
        # Step goal achievement
        with_goal = steps_df.dropna(subset=["step_goal"])
        if not with_goal.empty:
            achieved = with_goal[with_goal["total_steps"] >= with_goal["step_goal"]]
            rate = len(achieved) / len(with_goal) * 100
            avg_steps = with_goal["total_steps"].mean()
            insights.append(
                f"Step goal achieved **{rate:.0f}%** of days "
                f"(avg: {avg_steps:,.0f} steps/day)"
            )

    return insights


def analyze_spo2(processed: dict) -> list[str]:
    """Generate SpO2 insights."""
    insights = []
    spo2_df = processed["spo2"]

    if spo2_df.empty:
        return insights

    avg_spo2 = spo2_df["spo2"].mean()
    min_spo2 = spo2_df["spo2"].min()
    insights.append(f"Average SpO2: **{avg_spo2:.1f}%**, minimum recorded: **{min_spo2:.0f}%**")

    if min_spo2 < 90:
        low_readings = spo2_df[spo2_df["spo2"] < 90]
        insights.append(
            f"⚠️ **{len(low_readings)}** readings below 90% SpO2 — "
            f"consider discussing with a healthcare provider"
        )

    return insights


def generate_all_insights(processed: dict) -> dict[str, list[str]]:
    """Generate all health insights.

    Returns dict mapping category name to list of insight strings.
    """
    return {
        "Sleep": analyze_sleep(processed),
        "Cardiovascular": analyze_cardiovascular(processed),
        "Stress & Energy": analyze_stress_energy(processed),
        "Activity": analyze_activity(processed),
        "SpO2": analyze_spo2(processed),
    }
