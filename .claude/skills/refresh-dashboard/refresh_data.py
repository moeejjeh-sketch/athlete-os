"""
Refresh the data-driven parts of dashboard.html and docs/index.html:
- Weekly volume trend (last 8 weeks)
- Session-level data (Training History, Discipline Mix, Easy/Hard Split, Longest Session)
- Sleep/HRV/RHR (last 7 nights with data)
- Race countdowns (days remaining, recalculated from today)

Does NOT touch: Planned Training (comes from training/*-week.md via
plan-my-week), Coach's Read (authored analysis), today's readiness call
(recovery-check's job). Read-only against Strava/Garmin.

Usage: python refresh_data.py
"""
import os
import re
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone, date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ENV_PATH = os.path.join(ROOT, ".env")

def read_env():
    values = {}
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        values[k.strip()] = v.strip()
    return lines, values

def write_env(lines, updates):
    new_lines = []
    seen = set()
    for line in lines:
        s = line.strip()
        if "=" in s and not s.startswith("#"):
            k = s.split("=", 1)[0].strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}\n")
                seen.add(k)
                continue
        new_lines.append(line)
    for k, v in updates.items():
        if k not in seen:
            new_lines.append(f"{k}={v}\n")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def ensure_strava_token(lines, env):
    exp = int(env.get("STRAVA_TOKEN_EXPIRES_AT", "0") or "0")
    if time.time() < exp - 120:
        return env["STRAVA_ACCESS_TOKEN"]
    data = urllib.parse.urlencode({
        "client_id": env["STRAVA_CLIENT_ID"], "client_secret": env["STRAVA_CLIENT_SECRET"],
        "grant_type": "refresh_token", "refresh_token": env["STRAVA_REFRESH_TOKEN"],
    }).encode()
    req = urllib.request.Request("https://www.strava.com/oauth/token", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode())
    write_env(lines, {
        "STRAVA_ACCESS_TOKEN": body["access_token"], "STRAVA_REFRESH_TOKEN": body["refresh_token"],
        "STRAVA_TOKEN_EXPIRES_AT": str(body["expires_at"]),
    })
    return body["access_token"]

def fetch_strava_activities(token, after_epoch):
    all_acts, page = [], 1
    while True:
        url = "https://www.strava.com/api/v3/athlete/activities?" + urllib.parse.urlencode(
            {"after": after_epoch, "per_page": 200, "page": page})
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

def build_session_weeks(acts, n_weeks=9):
    today = datetime.now(timezone.utc)
    last_monday = (today - timedelta(days=today.weekday())).date()

    def consolidate(day_acts):
        groups, order = {}, []
        for a in day_acts:
            t = a.get("type")
            if t == "VirtualRide":
                t = "Ride"
            d = a["start_date_local"][:10]
            key = (d, t)
            if key not in groups:
                groups[key] = {"date": d, "day": datetime.fromisoformat(d).strftime("%a"), "type": t,
                               "distance_km": 0.0, "duration_min": 0.0, "hr_w": 0.0, "hr_d": 0.0,
                               "watts_w": 0.0, "watts_d": 0.0}
                order.append(key)
            g = groups[key]
            g["distance_km"] += a.get("distance", 0) / 1000
            dur = a.get("moving_time", 0) / 60
            g["duration_min"] += dur
            if a.get("average_heartrate"):
                g["hr_w"] += a["average_heartrate"] * dur
                g["hr_d"] += dur
            if a.get("average_watts"):
                g["watts_w"] += a["average_watts"] * dur
                g["watts_d"] += dur
        out = []
        for key in order:
            g = groups[key]
            out.append({"date": g["date"], "day": g["day"], "type": g["type"],
                        "distance_km": round(g["distance_km"], 2),
                        "duration_min": round(g["duration_min"], 1),
                        "avg_hr": round(g["hr_w"] / g["hr_d"]) if g["hr_d"] > 0 else None,
                        "avg_watts": round(g["watts_w"] / g["watts_d"]) if g["watts_d"] > 0 else None})
        return out

    weeks = []
    for i in range(n_weeks):
        wk_start = last_monday - timedelta(weeks=(n_weeks - 1 - i))
        wk_end = wk_start + timedelta(weeks=1)
        day_acts = [a for a in acts if wk_start <= datetime.fromisoformat(a["start_date_local"][:10]).date() < wk_end]
        sessions = consolidate(day_acts)
        total_hours = round(sum(s["duration_min"] for s in sessions) / 60, 1)
        label = wk_start.strftime("%b ") + str(wk_start.day)
        weeks.append({"week": label, "week_start": wk_start.isoformat(), "total_hours": total_hours,
                      "sessions": sessions, "partial": wk_start == last_monday})
    return weeks

def js_bool(v):
    return "true" if v else "false"

def session_weeks_js(weeks):
    parts = []
    for w in weeks:
        sess = ",".join(
            f'{{"type":"{s["type"]}","distance_km":{s["distance_km"]},"duration_min":{s["duration_min"]},"avg_hr":{s["avg_hr"] if s["avg_hr"] is not None else "null"}}}'
            for s in w["sessions"])
        entry = f'{{week:"{w["week"]}", sessions:[{sess}]{", partial:true" if w["partial"] else ""}}}'
        parts.append(entry)
    return "[\n    " + ",\n    ".join(parts) + "\n  ]"

def hist_weeks_js(weeks):
    parts = []
    for w in weeks:
        sess = ",".join(
            f'{{"date":"{s["date"]}","day":"{s["day"]}","type":"{s["type"]}","distance_km":{s["distance_km"]},"duration_min":{s["duration_min"]},"avg_hr":{s["avg_hr"] if s["avg_hr"] is not None else "null"},"avg_watts":{s["avg_watts"] if s["avg_watts"] is not None else "null"}}}'
            for s in w["sessions"])
        entry = f'{{"week_start":"{w["week_start"]}","total_hours":{w["total_hours"]},"sessions":[{sess}]}}'
        parts.append(entry)
    return "[" + ",".join(parts) + "]"

def volume_data_js(weeks):
    parts = []
    for w in weeks:
        entry = f'{{week: "{w["week"]}", hours: {w["total_hours"]}' + (", partial: true" if w["partial"] else "") + "}"
        parts.append(entry)
    return "[\n    " + ", ".join(parts) + "\n  ]"

def fetch_garmin_nights(days=10):
    from garminconnect import Garmin
    _, env = read_env()
    client = Garmin(env["GARMIN_EMAIL"], env["GARMIN_PASSWORD"])
    client.login()
    out = []
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        try:
            sleep = client.get_sleep_data(d.isoformat())
            dto = sleep.get("dailySleepDTO", {}) if isinstance(sleep, dict) else {}
            deep = dto.get("deepSleepSeconds") or 0
            light = dto.get("lightSleepSeconds") or 0
            rem = dto.get("remSleepSeconds") or 0
            awake = dto.get("awakeSleepSeconds") or 0
            score = dto.get("sleepScores", {}).get("overall", {}).get("value")
            rhr = sleep.get("restingHeartRate")
            hrv = sleep.get("avgOvernightHrv")
            hrv_status = sleep.get("hrvStatus")
            has_data = (deep + light + rem) > 0
            out.append({
                "date": d.strftime("%b ") + str(d.day),
                "deep": round(deep / 60, 1) if has_data else 0,
                "light": round(light / 60, 1) if has_data else 0,
                "rem": round(rem / 60, 1) if has_data else 0,
                "awake": round(awake / 60, 1) if has_data else 0,
                "score": score, "rhr": rhr, "hrv": hrv, "hrvStatus": hrv_status,
                "noData": not has_data,
            })
        except Exception:
            out.append({"date": d.strftime("%b ") + str(d.day), "deep": 0, "light": 0, "rem": 0, "awake": 0,
                        "score": None, "rhr": None, "hrv": None, "hrvStatus": None, "noData": True})
    out.reverse()
    # keep most recent 7 nights that have ANY data, or last 7 calendar nights if fewer
    with_data = [n for n in out if not n["noData"]]
    return out[-7:] if len(with_data) >= 5 else out[-7:]

def nights_js(nights):
    parts = []
    for n in nights:
        score = n["score"] if n["score"] is not None else "null"
        rhr = n["rhr"] if n["rhr"] is not None else "null"
        hrv = n["hrv"] if n["hrv"] is not None else "null"
        hrv_status = f'"{n["hrvStatus"]}"' if n["hrvStatus"] else "null"
        entry = (f'{{date:"{n["date"]}", deep:{n["deep"]}, light:{n["light"]}, rem:{n["rem"]}, '
                  f'awake:{n["awake"]}, score:{score}, rhr:{rhr}, hrv:{hrv}, hrvStatus:{hrv_status}'
                  + (", noData:true" if n["noData"] else "") + "}")
        parts.append(entry)
    return "[\n    " + ",\n    ".join(parts) + ",\n  ]"

def replace_block(content, var_name, new_value_js):
    marker = f"const {var_name} = "
    start = content.find(marker)
    if start == -1:
        raise ValueError(f"Could not find `{marker}` in file")
    bracket_start = content.find("[", start)
    depth = 0
    i = bracket_start
    while i < len(content):
        if content[i] == "[":
            depth += 1
        elif content[i] == "]":
            depth -= 1
            if depth == 0:
                break
        i += 1
    end = i + 1
    # consume trailing semicolon if present
    if end < len(content) and content[end] == ";":
        end += 1
    return content[:bracket_start] + new_value_js.rstrip().rstrip(";") + ";" + content[end:]

def days_between(target_iso):
    today = date.today()
    target = date.fromisoformat(target_iso)
    return (target - today).days

def refresh_file(path, data_js, session_weeks_js_str, hist_js, nights_js_str, munich_days, hamburg_days):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = replace_block(content, "data", data_js)
    content = replace_block(content, "sessionWeeks", session_weeks_js_str)
    content = replace_block(content, "weeks", hist_js)
    content = replace_block(content, "nights", nights_js_str)
    # race countdown numbers (first two "value">N<span occurrences correspond to Munich, Hamburg)
    content = re.sub(r'(Munich Marathon</div>\s*<div class="value">)\d+', rf"\g<1>{munich_days}", content)
    content = re.sub(r'(Ironman Hamburg</div>\s*<div class="value">)\d+', rf"\g<1>{hamburg_days}", content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    lines, env = read_env()
    token = ensure_strava_token(lines, env)
    now = datetime.now(timezone.utc)
    acts = fetch_strava_activities(token, int((now - timedelta(weeks=9)).timestamp()))
    weeks = build_session_weeks(acts, n_weeks=9)

    nights = fetch_garmin_nights(days=10)

    data_js = volume_data_js(weeks[-8:])
    sw_js = session_weeks_js(weeks)
    hw_js = hist_weeks_js(weeks)
    n_js = nights_js(nights)

    munich_days = days_between("2026-10-11")
    hamburg_days = days_between("2027-06-06")

    for fname in ["dashboard.html", os.path.join("docs", "index.html")]:
        path = os.path.join(ROOT, fname)
        refresh_file(path, data_js, sw_js, hw_js, n_js, munich_days, hamburg_days)
        print(f"Refreshed {fname}")

    print(f"Munich: {munich_days} days, Hamburg: {hamburg_days} days")

if __name__ == "__main__":
    main()
