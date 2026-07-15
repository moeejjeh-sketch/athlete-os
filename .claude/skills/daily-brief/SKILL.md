---
name: daily-brief
description: A short, scannable morning brief — today's session, readiness call, race-plan status, race countdown, and a one-line focus — assembled from real data only, no invented numbers. Run with /daily-brief.
---

# Daily Brief

Five lines, readable on a phone in ten seconds. This skill assembles, it
doesn't invent — every number comes from an existing skill's data pull or
an existing file. If a real number isn't available, say so plainly rather
than filling the gap with something that sounds plausible.

## What it pulls, and from where

1. **Today's planned session** — find today's date in the current
   `training/*-week.md` file (the most recent one covering today). Pull the
   session name, target, and its stated "why" from that row. If today falls
   in a gap between saved weeks (no plan covers it), say that directly
   rather than guessing a session.
2. **Readiness call** — reuse the exact mechanism from `recovery-check`:
   run `plan-my-week/fetch_recent_training.py` (or `recovery-check/pull_load.py`
   for ACWR) and `review-my-week/fetch_garmin_wellness.py` for last 1-3
   nights, then apply the same tuned thresholds already documented in
   `recovery-check/SKILL.md` (ACWR ≥1.2 caution, ≥1.5 stop; sleep/HRV/RHR
   flags). Don't duplicate the threshold logic by hand — read and apply
   what's already written there.
3. **Race-plan status** — read `training/plan.md` for the current phase
   name and dates, and whether this week's actual volume (from the Strava
   pull above) is tracking with, above, or below that phase's target range.
4. **Race countdown** — read the dated dossiers in `races/` for goal
   race(s) and date(s); compute days remaining from today. Lead with the
   nearer race; mention the primary goal race too if it's different.
5. **One line of fuel/focus** — tied to today's *specific* session type,
   not generic advice: a swim day mentions the pool-gym logistics if
   relevant, a hard day mentions warm-up discipline (per the athlete's
   established risk pattern), a long run mentions hydration/fueling
   rehearsal, an easy day can be brief.

## Voice

Direct and blunt, tied to the coaching philosophy in `athlete-profile.md`
— no filler, no cushioning, no "great job!" padding. State the call and the
reason in the fewest words that are still true.

## Procedure

1. Read `athlete-profile.md` (coaching voice, goals) and `training/plan.md`
   (current phase).
2. Find today in the most recent applicable `training/*-week.md`.
3. Compute today's readiness call using the data pulls and thresholds
   described above (same logic as `recovery-check`, run fresh — don't read
   a stale cached call).
4. Read the relevant race dossier(s) in `races/` for countdown math.
5. Assemble the five lines. Keep total length to what fits on a phone
   screen without scrolling — this is a brief, not a report.
6. Output in chat. If asked to email it, hand off to the `email-me` skill
   (check it exists first — if not, that's a setup step, not a silent
   failure) with subject `Your training brief — {date}` and a short, clean
   HTML version of the same five lines.

## Output format

```
Today (Wed 7/22): {session} — {target}. {one-line why}
Readiness: {GO HARD/EASY/REST} — {reason + real numbers}
Plan status: {phase name}, {on-track/above/below} this week ({actual}h vs {target range})
{X} days to {nearer race} ({goal time}) · {Y} days to {primary goal race}
Focus: {one line, tied to today's specific session}
```
