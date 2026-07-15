---
name: review-my-week
description: Grade the past 7 days against training/plan.md and the most recent plan-my-week output, weighing fatigue (sleep/HRV/resting HR) more heavily than raw compliance, and watch for overtraining trends across recent reviews. Run with /review-my-week.
---

# Review My Week

You are grading a week the way the athlete's coaching philosophy demands:
direct, blunt, tied to real data — not a participation trophy for hitting
numbers if the body was clearly struggling underneath them.

## The research this is grounded in

**A sustained drop in HRV below an individual's own baseline signals
accumulated stress and overtraining risk** — this is the core mechanism
behind HRV-guided ("day-to-day") periodization, which lets training load
adjust to the athlete's actual physiological state rather than a fixed plan.
Reduced resting HRV (specifically RMSSD) is associated with fatigue,
overtraining, and reduced performance capacity. Sleep is a primary input to
HRV and overall recovery — poor sleep degrades the same signal.
**Application: fatigue markers (sleep, HRV, resting HR) are weighted more
heavily than plan compliance in the grade below.** A week where every
planned session happened but sleep and HRV both cratered is not an A week —
it's a week where the plan was followed past what the body could recover
from.
[HRV-guided training RCT protocol](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7432021/) ·
[Does HRV detect overtraining? — Wu Tsai Human Performance Alliance](https://humanperformancealliance.org/playbook/does-heart-rate-variability-detect-overtraining/)

This builds on the injury/load research already in `plan-my-week`
(polarized training, the 10% rule's real limits, ACWR, deload cadence) —
this skill is the retrospective half of that same system: plan-my-week
decides the week going in, review-my-week grades what actually happened.

## Data sources

- **Strava** (`plan-my-week/fetch_recent_training.py 7`) — what actually
  happened: session types, durations, distances, HR.
- **Garmin wellness** (`fetch_garmin_wellness.py 7`, in this skill's
  folder) — sleep score/hours, resting HR, HRV value and status
  (BALANCED/UNBALANCED/LOW/etc.), body battery change, per night.
- **The plan** — the most recent `training/YYYY-MM-DD-week.md` covering
  the reviewed week if one exists (compliance target), plus
  `training/plan.md` for phase context. If no week-specific plan exists for
  the period being reviewed (e.g. before plan-my-week was in use), grade
  what's gradable — consistency, ramp discipline, fatigue trend — and say
  explicitly that plan-compliance isn't assessable for that week.
- **Prior reviews** (`reviews/*.md`, most recent 3-4) — for trend detection.

## Procedure

1. Pull last 7 days from Strava and Garmin (scripts above).
2. Find the matching `training/*-week.md` plan file for the period, if one
   exists. Read `athlete-profile.md` (coaching philosophy, zones) and
   `training/plan.md` (current phase) for context.
3. **Compare actual vs. planned**: which sessions happened, at what
   duration/intensity relative to target, which were skipped or cut short.
4. **Weigh fatigue explicitly**: look at the 7 nights of sleep score/hours,
   resting HR, and HRV status/value. Flag any night under ~6 hours sleep,
   any HRV status other than BALANCED, and any resting HR meaningfully above
   the recent norm. This block can cap the grade regardless of compliance.
5. **Grade the week, A-F**, and explain the grade in plain terms tied to
   specific numbers — no vague "good job":
   - **A**: plan followed closely, fatigue markers stable, no safety flags.
   - **B**: minor plan deviations, fatigue markers stable.
   - **C**: meaningful plan deviation OR mild fatigue strain (not both).
   - **D**: significant plan deviation (missed key sessions, a dangerous
     volume jump) OR sustained fatigue strain (multiple poor-sleep nights,
     HRV trending down, resting HR elevated).
   - **F**: both plan badly off track AND real fatigue strain — this is a
     "stop and address it directly" week, say so plainly.
6. **Check the last 3-4 reviews in `reviews/`** for trends the single week
   can't show: resting HR creeping up across weeks, HRV drifting away from
   BALANCED, sleep quality declining, grades declining. Warn early — 2
   consecutive weeks of a signal is worth naming, don't wait for a 4-week
   confirmed crisis. If fewer than 2-3 prior reviews exist yet, say so and
   note this is still building a baseline.
7. **Save** to `reviews/YYYY-MM-DD-week.md` (date = start of the reviewed
   week). Never overwrite a past review — this is the compounding record.
8. Walk the athlete through it: the grade, why, the fatigue picture, any
   trend warning, and what should change (if anything) for the coming week.
   Tone follows the coaching philosophy in `athlete-profile.md`: direct and
   blunt, tied to data, no cushioning.

## Output file format

```
# Week of {date} — Review — Grade: {A-F}

## Grade reasoning
{explicit, tied to specific numbers below}

## Plan vs. actual
{table or list: planned session vs. what happened}

## Fatigue picture
{sleep/HRV/resting HR per night, flagged nights, overall read}

## Trend check (last 3-4 reviews)
{any early-warning pattern, or "still building baseline"}

## What changes next week
{concrete, tied to this week's data}
```
