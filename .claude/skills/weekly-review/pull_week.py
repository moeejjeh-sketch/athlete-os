"""
Execution-analysis pull for weekly-review. Reads Strava for a target Mon-Sun
week (defaults to the last complete one), reports volume, vertical gain,
easy-vs-hard intensity discipline, and aerobic decoupling (HR drift) inside
that week's longest run. Read-only.

Usage: python pull_week.py [YYYY-MM-DD]   (Monday of the target week; omit for last complete week)
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

def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def fetch_activities(token, after_epoch, before_epoch):
    all_acts = []
    page = 1
    while True:
        url = ("https://www.strava.com/api/v3/athlete/activities?"
               + urllib.parse.urlencode({"after": after_epoch, "before": before_epoch, "per_page": 200, "page": page}))
        batch = api_get(url, token)
        if not batch:
            break
        all_acts.extend(batch)
        if len(batch) < 200:
            break
        page += 1
    return all_acts

def main():
    lines, env = read_env()
    token = ensure_token(lines, env)

    if len(sys.argv) > 1:
        week_start = datetime.fromisoformat(sys.argv[1]).replace(tzinfo=timezone.utc)
    else:
        today = datetime.now(timezone.utc)
        last_monday = today - timedelta(days=today.weekday())
        week_start = last_monday - timedelta(weeks=1)
    week_end = week_start + timedelta(weeks=1)

    # reference window for max HR (90 days) to classify easy/mid/hard
    ref_start = week_end - timedelta(days=90)
    ref_activities = fetch_activities(token, int(ref_start.timestamp()), int(week_end.timestamp()))
    max_hr_observed = max([a.get("max_heartrate", 0) or 0 for a in ref_activities], default=0)

    week_activities = [a for a in ref_activities
                        if week_start <= datetime.fromisoformat(a["start_date"].replace("Z", "+00:00")) < week_end]

    by_sport = {}
    total_elev = 0.0
    run_hr_minutes = {"easy": 0.0, "mid": 0.0, "hard": 0.0, "no_hr": 0.0}
    longest_run = None
    for a in week_activities:
        t = a.get("type", "Other")
        d = by_sport.setdefault(t, {"count": 0, "distance_km": 0.0, "hours": 0.0})
        d["count"] += 1
        d["distance_km"] += a.get("distance", 0) / 1000
        d["hours"] += a.get("moving_time", 0) / 3600
        total_elev += a.get("total_elevation_gain", 0) or 0

        if t == "Run":
            dur_min = a.get("moving_time", 0) / 60
            hr = a.get("average_heartrate")
            if hr and max_hr_observed:
                pct = hr / max_hr_observed
                bucket = "easy" if pct < 0.78 else ("hard" if pct >= 0.87 else "mid")
                run_hr_minutes[bucket] += dur_min
            else:
                run_hr_minutes["no_hr"] += dur_min
            if longest_run is None or a.get("distance", 0) > longest_run.get("distance", 0):
                longest_run = a

    for v in by_sport.values():
        v["distance_km"] = round(v["distance_km"], 1)
        v["hours"] = round(v["hours"], 2)

    total_run_min = sum(run_hr_minutes.values())
    intensity_pct = {k: (round(100 * v / total_run_min, 0) if total_run_min else None) for k, v in run_hr_minutes.items()}

    decoupling = None
    longest_run_summary = None
    if longest_run and longest_run.get("moving_time", 0) >= 25 * 60:  # only meaningful for 25min+
        try:
            streams_url = (f"https://www.strava.com/api/v3/activities/{longest_run['id']}/streams?"
                            + urllib.parse.urlencode({"keys": "heartrate,distance,time", "key_by_type": "true"}))
            streams = api_get(streams_url, token)
            hr_data = streams.get("heartrate", {}).get("data", [])
            dist_data = streams.get("distance", {}).get("data", [])
            time_data = streams.get("time", {}).get("data", [])
            if hr_data and dist_data and time_data and len(hr_data) == len(dist_data) == len(time_data):
                n = len(hr_data)
                mid = n // 2
                def half_stats(lo, hi):
                    hrs = hr_data[lo:hi]
                    d0, d1 = dist_data[lo], dist_data[hi - 1]
                    t0, t1 = time_data[lo], time_data[hi - 1]
                    avg_hr = sum(hrs) / len(hrs)
                    dist_m = d1 - d0
                    dur_s = t1 - t0
                    pace_s_per_km = (dur_s / (dist_m / 1000)) if dist_m > 0 else None
                    return avg_hr, pace_s_per_km
                hr1, pace1 = half_stats(0, mid)
                hr2, pace2 = half_stats(mid, n)
                if pace1 and pace2:
                    ratio1 = hr1 * pace1  # HR * sec/km ~ proxy for HR per unit speed
                    ratio2 = hr2 * pace2
                    decoupling = round((ratio2 / ratio1 - 1) * 100, 1)
                longest_run_summary = {
                    "name": longest_run.get("name"),
                    "distance_km": round(longest_run.get("distance", 0) / 1000, 1),
                    "duration_min": round(longest_run.get("moving_time", 0) / 60, 1),
                    "first_half_avg_hr": round(hr1, 1),
                    "second_half_avg_hr": round(hr2, 1),
                    "first_half_pace_per_km_sec": round(pace1, 0) if pace1 else None,
                    "second_half_pace_per_km_sec": round(pace2, 0) if pace2 else None,
                }
        except Exception as e:
            longest_run_summary = {"error": str(e)}

    result = {
        "week_start": week_start.date().isoformat(),
        "week_end": (week_end - timedelta(days=1)).date().isoformat(),
        "max_hr_reference_90d": max_hr_observed,
        "by_sport": by_sport,
        "total_elevation_gain_m": round(total_elev, 0),
        "run_intensity_distribution_pct": intensity_pct,
        "longest_run": longest_run_summary,
        "aerobic_decoupling_pct": decoupling,
        "decoupling_interpretation": (
            "well-developed aerobic base (<5%)" if decoupling is not None and decoupling < 5 else
            "typical/moderate (5-10%)" if decoupling is not None and decoupling < 10 else
            "notable drift — fatigue/heat/dehydration signal (>10%)" if decoupling is not None else
            "not computed (no long-enough run with HR+distance+time streams this week)"
        ),
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
