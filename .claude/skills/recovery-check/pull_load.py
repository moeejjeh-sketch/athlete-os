"""
Load/ACWR computation for recovery-check. Reads Strava (28+ days), computes
acute (last 7 days) vs chronic (trailing 4-week average) load and the
resulting ACWR, plus week-over-week % change. Read-only.

Usage: python pull_load.py
"""
import os
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

def hours_in_window(activities, start, end):
    total = 0.0
    for a in activities:
        dt = datetime.fromisoformat(a["start_date"].replace("Z", "+00:00"))
        if start <= dt < end:
            total += a.get("moving_time", 0) / 3600
    return total

def main():
    lines, env = read_env()
    token = ensure_token(lines, env)

    now = datetime.now(timezone.utc)
    chronic_start = now - timedelta(days=28)
    activities = fetch_activities(token, int(chronic_start.timestamp()))

    acute_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)

    acute_hours = hours_in_window(activities, acute_start, now)
    prev_week_hours = hours_in_window(activities, prev_week_start, acute_start)
    chronic_hours_total = hours_in_window(activities, chronic_start, now)
    chronic_weekly_avg = chronic_hours_total / 4

    acwr = round(acute_hours / chronic_weekly_avg, 2) if chronic_weekly_avg > 0 else None
    wow_pct = round((acute_hours / prev_week_hours - 1) * 100, 1) if prev_week_hours > 0 else None

    result = {
        "as_of": now.date().isoformat(),
        "acute_hours_last_7d": round(acute_hours, 2),
        "prev_7d_hours": round(prev_week_hours, 2),
        "chronic_weekly_avg_hours": round(chronic_weekly_avg, 2),
        "acwr": acwr,
        "week_over_week_pct_change": wow_pct,
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
