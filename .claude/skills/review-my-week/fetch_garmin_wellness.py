"""
Reusable Garmin Connect wellness fetch helper for review-my-week.
Reads credentials from the project .env (unofficial garminconnect library —
see SKILL.md for why). Pulls sleep score, sleep duration, resting HR, and
HRV for the last N days (default 7). Read-only: never writes to Garmin.

Usage: python fetch_garmin_wellness.py [days]
"""
import os
import sys
import json
from datetime import date, timedelta
from garminconnect import Garmin

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

def read_env():
    values = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            values[key.strip()] = val.strip()
    return values

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    env = read_env()
    client = Garmin(env["GARMIN_EMAIL"], env["GARMIN_PASSWORD"])
    client.login()

    out = []
    today = date.today()
    for i in range(days):
        d = (today - timedelta(days=i)).isoformat()
        entry = {"date": d}
        try:
            sleep = client.get_sleep_data(d)
            dto = sleep.get("dailySleepDTO", {}) if isinstance(sleep, dict) else {}
            entry["sleep_score"] = dto.get("sleepScores", {}).get("overall", {}).get("value")
            secs = dto.get("sleepTimeSeconds")
            entry["sleep_hours"] = round(secs / 3600, 2) if secs else None
            entry["resting_hr"] = sleep.get("restingHeartRate")
            entry["avg_overnight_hrv"] = sleep.get("avgOvernightHrv")
            entry["hrv_status"] = sleep.get("hrvStatus")
            entry["body_battery_change"] = sleep.get("bodyBatteryChange")
        except Exception as e:
            entry["error"] = str(e)
        out.append(entry)

    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
