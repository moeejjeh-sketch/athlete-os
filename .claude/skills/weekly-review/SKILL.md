---
name: weekly-review
description: Qualitative, decision-focused review of last week — execution quality (volume, vert, easy/hard discipline, aerobic decoupling in the long run), judged against the current training phase's intent, then reconciled against how the week actually felt. Complements review-my-week (which grades A-F and weighs fatigue/HRV) rather than duplicating it. Run with /weekly-review.
---

# Weekly Review

**How this differs from `review-my-week`**: that skill grades a week
A-F, weighted heavily toward sleep/HRV fatigue signals, and watches for
overtraining trends. This skill doesn't grade — it judges **execution
quality against the current phase's actual intent** (not just raw
compliance), and it's built around **reconciling subjective feel against
the data**, which `review-my-week` doesn't do at all. Run both; they answer
different questions. If this skill's scope drifts to duplicate
`review-my-week`, that's a bug — keep them distinct.

## The science this is grounded in

**Aerobic decoupling (HR drift within a single long effort) is a real,
measurable durability marker.** As fatigue, rising core temperature, and
dehydration accumulate during a steady-effort session, heart rate climbs
even though pace/output hasn't changed — the ratio of heart rate to pace
"decouples" over the course of the run. A well-developed aerobic base keeps
this small; **trained endurance athletes typically hold under 5%
decoupling over 60-90 minutes, recreational athletes typically land in the
5-10% range, and drift above ~10% is a real signal** (heat, dehydration,
inadequate aerobic base, or accumulated fatigue) rather than noise.
Dehydration specifically has a quantified effect — ~4% body-mass fluid
loss has been shown to drop stroke volume ~21% and cardiac output ~13%
even in trained athletes exercising in heat.
[Aerobic decoupling guide — TrainingPeaks](https://www.trainingpeaks.com/coach-blog/aerobic-endurance-and-decoupling/) ·
[Cardiac drift explained](https://www.tymewear.com/blogs/performance-science/cardiac-drift-explained)

This also draws on the polarized-training (80/20) and ACWR research
already established in `plan-my-week`, applied here as a **weekly
execution audit** rather than a forward-looking plan.

## Data sources

- **Strava execution data**: `pull_week.py` in this skill's folder — volume
  by sport, total vertical gain, easy/mid/hard run-intensity distribution,
  and aerobic decoupling % inside the week's longest run (via Strava's
  heart-rate/distance/time streams, not just summary data).
- **Past reviews**: read `reviews/*.md` **first**, before pulling new data,
  so trend context is already in mind, not bolted on after.
- **Phase context**: `training/plan.md` (current phase's actual intent —
  what this week was *for*, not just what was scheduled) and the matching
  `training/*-week.md` if one exists.
- **Subjective feel**: asked directly, every run — this isn't inferred from
  wearables.

## Procedure

1. **Read past reviews in `reviews/` first** (most recent 3-4) — build
   trend context before looking at this week's numbers, so this week gets
   read in light of the pattern, not in isolation.
2. **Run `pull_week.py`** for last complete week (Mon-Sun). Note the
   easy/mid/hard run-intensity split against the 80/20 target, total vert,
   and the aerobic decoupling read on the week's longest run.
3. **Read `training/plan.md`** and identify the current phase's actual
   intent (e.g., "Phase 0: gentle rebuild off a taper" has a completely
   different bar for success than "Phase 3: marathon-specific build").
   **Judge the week against that intent, not against raw numbers in a
   vacuum** — a light week can be exactly right in a rebuild phase and
   wrong in a build phase.
4. **Ask how the week actually felt** — one pass, not interrogation-style:
   energy, sleep, soreness/injury signals (check what's actually on record
   in `athlete-profile.md`'s injury history before asking about anything
   specific — don't assume a concern that isn't confirmed there), life
   stress, and which specific sessions felt great vs. rough.
5. **Reconcile feel vs. data explicitly.** Where they agree, say so briefly.
   **Where they disagree, that disagreement is itself the most important
   finding** — e.g., low decoupling and full plan compliance but the
   athlete reports feeling wrecked (life stress/sleep debt not visible in
   Strava), or the reverse (data shows strain but the athlete feels great,
   meaning the thresholds may be tuned too sensitively for them right now).
6. **Write the review** to `reviews/YYYY-MM-DD.md`, using **last week's
   Monday date** as the filename. Never overwrite a past review. Format:

```
# Week of {date} — Weekly Review

## Planned vs. Actual
{brief}

## How it really went
{execution-quality read: volume/vert/intensity-discipline/decoupling,
judged against the phase's actual intent}

## Feel vs. Data
{the athlete's own report, then explicit agreement/disagreement with the
data — disagreements get emphasis, not footnotes}

## Flags that matter
{only real ones — hip/back signals, decoupling >10%, intensity distribution
badly off 80/20, anything that showed up in both feel AND data}

## Wins
{genuine, specific — not filler}

## 1-2 Adjustments
{each with a one-line reason tied to this week's specific evidence}

## Trend watch
{what this week adds to the pattern from past reviews — building,
resolving, or worsening}
```
