"""
Reusable Strava fetch helper for the plan-my-week skill.
Reads/refreshes credentials from the project .env, pulls activities from the
last N days (default 14), and prints a compact per-day + weekly-totals JSON
summary to stdout. Read-only: never writes to Strava.

Usage: python fetch_recent_training.py [days]
"""
import os
import sys
import time
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta, timezone

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

def read_env():
    values = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        values[key.strip()] = val.strip()
    return lines, values

def write_env(lines, updates):
    new_lines = []
    seen = set()
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}\n")
                seen.add(key)
                continue
        new_lines.append(line)
    for key, val in updates.items():
        if key not in seen:
            new_lines.append(f"{key}={val}\n")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def ensure_token(lines, env):
    expires_at = int(env.get("STRAVA_TOKEN_EXPIRES_AT", "0") or "0")
    if time.time() < expires_at - 120:
        return env["STRAVA_ACCESS_TOKEN"]
    data = urllib.parse.urlencode({
        "client_id": env["STRAVA_CLIENT_ID"],
        "client_secret": env["STRAVA_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": env["STRAVA_REFRESH_TOKEN"],
    }).encode()
    req = urllib.request.Request("https://www.strava.com/oauth/token", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())
    write_env(lines, {
        "STRAVA_ACCESS_TOKEN": body["access_token"],
        "STRAVA_REFRESH_TOKEN": body["refresh_token"],
        "STRAVA_TOKEN_EXPIRES_AT": str(body["expires_at"]),
    })
    return body["access_token"]

def fetch_activities(token, after_epoch):
    all_acts = []
    page = 1
    while True:
        url = ("https://www.strava.com/api/v3/athlete/activities?"
               + urllib.parse.urlencode({"after": after_epoch, "per_page": 200, "page": page}))
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as resp:
            batch = json.loads(resp.read().decode())
        if not batch:
            break
        all_acts.extend(batch)
        if len(batch) < 200:
            break
        page += 1
    return all_acts

def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    lines, env = read_env()
    token = ensure_token(lines, env)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    activities = fetch_activities(token, int(start.timestamp()))

    daily = []
    for a in sorted(activities, key=lambda x: x["start_date_local"]):
        daily.append({
            "date": a["start_date_local"][:10],
            "day_of_week": datetime.fromisoformat(a["start_date_local"].replace("Z", "")).strftime("%A"),
            "type": a.get("type"),
            "name": a.get("name"),
            "distance_km": round(a.get("distance", 0) / 1000, 2),
            "duration_min": round(a.get("moving_time", 0) / 60, 1),
            "avg_hr": a.get("average_heartrate"),
            "max_hr": a.get("max_heartrate"),
            "avg_watts": a.get("average_watts"),
            "elev_gain_m": a.get("total_elevation_gain"),
        })

    by_sport_totals = {}
    for a in activities:
        t = a.get("type", "Other")
        d = by_sport_totals.setdefault(t, {"count": 0, "distance_km": 0.0, "hours": 0.0})
        d["count"] += 1
        d["distance_km"] += a.get("distance", 0) / 1000
        d["hours"] += a.get("moving_time", 0) / 3600
    for v in by_sport_totals.values():
        v["distance_km"] = round(v["distance_km"], 1)
        v["hours"] = round(v["hours"], 2)

    total_hours = round(sum(a.get("moving_time", 0) for a in activities) / 3600, 2)

    result = {
        "range_days": days,
        "date_from": start.date().isoformat(),
        "date_to": now.date().isoformat(),
        "total_hours": total_hours,
        "total_activities": len(activities),
        "by_sport_totals": by_sport_totals,
        "activities": daily,
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
