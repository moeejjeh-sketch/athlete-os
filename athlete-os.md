# My Athlete OS

A one-page map of what this system is and how to use each piece. Built over
one week, on top of two live data connections and five reusable skills.

## The data connections

- **Strava** — read-only, source of truth for all actual training (runs,
  rides, swims). Never written to.
- **Garmin** — sleep, HRV, resting HR. Uses an unofficial library (no
  official individual API exists) with credentials in `.env`, never in chat.

Both auto-refresh their own tokens. Credentials live only in `.env`
(git-ignored, never committed, never pasted into conversation).

## The skills — run any of these with `/<name>`

| Skill | What it does | When to run it |
|---|---|---|
| **plan-my-week** | Builds the coming 7 days from real Strava data, your profile, and the current training phase. Auto-adjusts if 2+ key sessions were missed the week before. | Weekly, ideally before the week starts (scheduled Sundays) |
| **review-my-week** | Grades the last 7 days A–F, weighted heavily toward fatigue (sleep/HRV) over raw compliance. Watches for overtraining trends across recent reviews. | Weekly (scheduled Mondays) |
| **weekly-review** | A different lens on the same week: execution quality (volume, vert, easy/hard discipline, aerobic decoupling) judged against the current phase's intent, reconciled against how the week actually *felt*. | Weekly, alongside review-my-week |
| **recovery-check** | Daily GO HARD / GO EASY / REST call from real acute:chronic load plus Garmin sleep/HRV/resting HR. Silent when normal, only writes to `health/` when something's actually worth flagging. | Daily (scheduled mornings) |
| **fuel-and-pace** | Builds a race-day fueling (carbs/fluid/sodium per hour) and pacing plan from a race dossier, your known/estimated physiology, and course conditions. | Once per goal race, rerun as real data (FTP test, sweat test) replaces estimates |

## The folders

- **athlete-profile.md** — who I am: goals, zones, injury history, coaching
  philosophy (researched and synthesized from real coaching methodology, an
  interview, and my own Strava data)
- **training/** — `plan.md` (the master phase plan, Munich → Hamburg) plus
  dated weekly plans from plan-my-week
- **reviews/** — dated weekly reviews from review-my-week and weekly-review,
  append-only, never overwritten
- **races/** — race dossiers (course, conditions, real finisher warnings,
  logistics, all cited) and fuel-and-pace plans for each goal race
- **health/** — only appears when recovery-check actually flags something;
  empty is a good sign, not a gap
- **.claude/skills/** — the five skills above, each with its own SKILL.md
  (research citations included) and any data-pull scripts it needs

## dashboard.html

A visual, single-file dashboard — double-click it, opens in any browser,
no internet needed. Shows: race countdowns, today's readiness call, the
current and upcoming week's sessions (with real interval/set breakdowns,
gym merged into whatever cardio is that day), training history you can
page through, load/HR/elevation trends, and a coaching read tied to named
research (Gabbett's ACWR, Seiler's polarized training) plus your own data
patterns. Ask for changes anytime in plain English — it gets rebuilt, not
patched blindly.

## Automation

Three jobs were scheduled: `recovery-check` daily, `weekly-review` Mondays,
`plan-my-week` Sundays. **Important limit**: these are session-only and
auto-expire after 7 days regardless — they are not durable background
automation. For that, this project would need real OS-level scheduling
(Windows Task Scheduler calling the Claude Code CLI directly) — not set up
yet, ask if wanted.

## Remote access

The project is on a **private** GitHub repo
(`github.com/moeejjeh-sketch/athlete-os`) — `.env` credentials are excluded.
Open it at claude.ai/code from any device to keep working on it away from
this machine. Push again whenever you want the remote copy to catch up —
it doesn't happen automatically.

## How this all fits together

Strava/Garmin feed real data in → `plan-my-week` turns it into next week's
sessions → training happens → `review-my-week` / `weekly-review` grade what
actually occurred and feed forward → `recovery-check` runs the daily
go/no-go call in between → `fuel-and-pace` and the race dossiers handle
race-day specifics when a goal race approaches → `dashboard.html` is the
single place to see all of it at a glance. Nothing here is static: profile,
plans, and even the skills themselves get corrected and rebuilt as real
data proves something wrong — that's the system, not a bug in it.
