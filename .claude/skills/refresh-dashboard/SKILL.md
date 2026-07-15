---
name: refresh-dashboard
description: Re-pull real Strava/Garmin data and update dashboard.html and docs/index.html — Training History, volume trend, discipline mix, easy/hard split, longest-session charts, sleep/HRV/RHR, and race countdowns. Does not touch Planned Training (from plan-my-week's saved files) or Coach's Read (authored analysis). Commits and pushes automatically. Run with /refresh-dashboard.
---

# Refresh Dashboard

Keeps the data-driven parts of the dashboard current without a full manual
rebuild. This is intentionally scoped — it swaps out specific embedded data
blocks, it does not regenerate the page.

## What it updates
- Weekly volume trend (last 8 weeks)
- Session-level data behind Training History, Discipline Mix, Easy/Hard
  Split, and Longest Session charts (last 9 weeks)
- Sleep stages, sleep score, resting HR, HRV (last 7 nights with data)
- Race countdown numbers (recalculated from today's actual date)

## What it deliberately does NOT touch
- **Planned Training** — that section reflects `training/*-week.md`, which
  only changes when `plan-my-week` runs. Refreshing Strava data here
  wouldn't make sense of it since the plan is forward-looking, not derived
  from past activity.
- **Coach's Read** — the qualitative analysis is authored, not
  data-generated. Auto-rewriting it without a human actually looking at
  what changed risks stale or wrong reasoning presented as current.
- **Today's Readiness call** — that's `recovery-check`'s job specifically,
  run separately.

## Procedure

1. Run `python .claude/skills/refresh-dashboard/refresh_data.py` from the
   project root. It reads `.env`, refreshes the Strava token if needed,
   pulls fresh Strava (9 weeks) and Garmin (10 days, most recent 7 with
   data) data, and rewrites the specific `const data/sessionWeeks/weeks/
   nights = [...]` blocks and the two race-countdown numbers in both
   `dashboard.html` and `docs/index.html`.
2. **Check the diff before pushing** — the script does targeted block
   replacement, not free-form generation, but confirm nothing looks broken
   (`git diff --stat`, and skim the actual diff for both files).
3. Commit and push both files to the repo.
4. Note in chat what changed (new weeks in the trend, any notable shift in
   sleep/recovery data) — don't push silently without saying what moved.
