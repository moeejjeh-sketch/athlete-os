---
name: recovery-check
description: Daily readiness call (GO HARD / GO EASY / REST) from real load (ACWR), Garmin sleep/HRV/resting HR, and today's planned session — tuned conservative for this athlete's spike risk, current life stress, and hip/back watch. Run with /recovery-check.
---

# Recovery Check

A daily signal, not a daily report. Most days this should be one line. Only
write a file when something's actually worth flagging.

## The science this is grounded in

This reuses the ACWR and HRV/overtraining research already established in
`plan-my-week` and `review-my-week` (acute:chronic workload ratio,
sustained HRV drops signaling overtraining risk) — this skill is the
same-day version: a quick readiness gate before today's session, not a
retrospective grade.

**HRV-guided training is real, but only on trends, not single readings.**
Daily HRV drives real training-intensity decisions in the research (below
an athlete's normal range → lower intensity or rest; within/above → proceed)
— but HRV is noisy day to day even in well-recovered athletes (hydration,
alcohol, sleep environment all move it), so a single automated pull should
never be the final word on its own. **Application: if this check's
automated data is borderline or conflicting, tell the athlete to glance at
their Garmin app's own HRV status (which is trend-based) and morning RHR
directly, rather than trusting one script-pulled number in isolation.**
[Monitoring recovery via HRV — narrative review](https://www.mdpi.com/1424-8220/26/1/3) ·
[HRV-guided training methodology](https://www.kubios.com/blog/hrv-guided-training/)

## This athlete's tuning (2026-07-15 — read live from `athlete-profile.md`,
update thresholds if this context changes)

- **#1 risk is piling on load too fast.** Standard ACWR guidance treats
  0.8-1.3 as the safe build zone and ≥1.5 as a clear red flag. **This
  athlete's thresholds are pulled in tighter**: caution starts at **ACWR ≥
  1.2** (not 1.3), and 1.5+ is still the hard stop. This is a deliberate,
  named adjustment for his risk profile, not a different reading of the
  same research.
- **Moderate life stress, ~7h/night fairly consistent sleep** (confirmed
  2026-07-15 via direct interview, standing context in `athlete-profile.md`
  — not asked fresh each day). Stress is present but manageable, not a
  reason to lower the flagging bar on its own — treat sleep/HRV/RHR signals
  at standard sensitivity rather than the extra-cautious reading a
  high-stress context would warrant. Re-tune if this context changes.
- Confirmed 2026-07-15: no injury history beyond the left ankle (see
  `athlete-profile.md`) — no additional injury-watch items currently.

## Data sources

- **Strava load**: `plan-my-week/fetch_recent_training.py` (reuse — pull
  28+ days for chronic load, last 7 for acute).
- **Garmin wellness**: `review-my-week/fetch_garmin_wellness.py` (reuse —
  last 3-7 nights: sleep score/hours, resting HR, HRV value/status).
- **Today's planned session**: `training/plan.md` for phase context, plus
  the most recent `training/*-week.md` for what today specifically is.

## Procedure

1. Pull Strava (28-day window) and compute: **acute load** (last 7 days
   total hours), **chronic load** (trailing 4-week average), **ACWR**
   (acute ÷ chronic), and **week-over-week % change** vs. the prior 7 days.
2. Pull Garmin: last night's sleep score/hours, resting HR, HRV value and
   status, plus the last 2-3 nights for a short trend read (not just last
   night in isolation).
3. Read `training/plan.md` and the current week's plan file for what today
   was supposed to be (session type, hard/easy/rest).
4. **Make the call** — GO HARD / GO EASY / REST — weighing, in this order:
   - ACWR ≥ 1.5, or HRV status LOW/UNBALANCED combined with a poor-sleep
     night (<6h) → **REST**, regardless of what was planned.
   - ACWR ≥ 1.2 (this athlete's tightened threshold), OR one mild flag
     alone (poor sleep, elevated resting HR, non-BALANCED HRV) without
     corroboration, OR today's plan calls for a hard/quality session while
     the stress/sleep context above is active → **GO EASY** (downgrade
     intensity, keep the session, don't cancel it outright).
   - ACWR in 0.8-1.2, sleep adequate, HRV BALANCED, resting HR normal, no
     corroborating flags → **GO HARD**, plan proceeds as written.
5. **State the actual numbers** in the call — ACWR value, week-over-week %,
   last night's sleep/HRV/RHR — never just the verdict alone.
6. **If the automated read is borderline or conflicting** (e.g., HRV status
   shows "NONE"/insufficient data, or two signals disagree), say so
   explicitly and tell the athlete to glance at the Garmin app's own
   HRV-status trend and morning RHR to confirm before deciding.
7. **Output discipline — signal, not noise**:
   - **GO HARD with no flags**: one line in chat. **Do not write a file.**
   - **GO EASY or REST, or any notable flag/trend** (including an
     early-stage pattern across recent days, not just today): append to
     `health/YYYY-MM-DD-<short-flag-name>.md` with: the call, the specific
     trigger, the evidence (numbers), and the recommended adjustment. Never
     overwrite a past health file — same append-only rule as `reviews/`.
