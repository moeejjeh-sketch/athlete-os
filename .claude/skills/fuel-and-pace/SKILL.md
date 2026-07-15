---
name: fuel-and-pace
description: Build a race-day fueling plan (carbs/fluid/sodium per hour, exact timing) and pacing plan (effort/pace by segment, adjusted for elevation and heat) from a race dossier, athlete profile, and known-or-estimated physiological inputs. Run with /fuel-and-pace.
---

# Fuel & Pace

Build a race-specific fueling and pacing plan grounded in real exercise
science, not round-number guesses. Every formula below has a citation;
every input is either the athlete's real number or a clearly labeled
estimate with a one-line note on how to measure the real thing later.

## The science this is grounded in

**Carbohydrate oxidation has a hard ceiling — and glucose:fructose blends
raise it.** A single carbohydrate source (glucose/maltodextrin alone) is
absorbed via the SGLT1 transporter and oxidizes at a hard ceiling of
**~60g/hour**, regardless of how much more is ingested. Fructose uses a
separate transporter (GLUT5), so a glucose:fructose blend (commonly ~2:1)
uses both pathways simultaneously without competing — raising achievable
exogenous oxidation to **~90g/hour** in practice, with peak lab-observed
rates around 105g/hour at very high intake (144g/hour). ACSM guidance:
**60g/hour for the first 2.5 hours, rising toward 90g/hour beyond 2.5
hours** for events long enough to warrant it. This ceiling is gut-trained,
not automatic — someone without practiced gut tolerance at high intake
should not be defaulted to the 90g/hour number.
[Multiple transportable carbohydrates — GSSI](https://www.gssiweb.org/sports-science-exchange/article/sse-108-multiple-transportable-carbohydrates-and-their-benefits) ·
[90g/hour strategy explainer](https://thefeed.com/insider/90g-carbs-per-hour-the-endurance-fuel-strategy-that-changes-everything) ·
[Carbohydrate feeding during exercise — review](https://www.tandfonline.com/doi/full/10.1080/17461390801918971)

**Sweat rate and sodium loss are highly individual, and both are
measurable.** Endurance athletes average **1.28 ± 0.57 L/hour** whole-body
sweat loss, with most athletes losing 0.5-1.5L/hour depending on body size,
intensity, heat, humidity, and heat acclimation. Sweat sodium concentration
varies widely between individuals — commonly cited range is roughly
**500-2,000mg/L**, meaning fixed-dose sodium advice is often wrong for any
given athlete. **Real test protocol**: weigh nude immediately before and
after a set-duration run/ride, account for any fluid consumed and urine
output during the session; sweat rate (L/hr) = (pre-weight − post-weight +
fluid consumed − urine output) ÷ duration in hours. Sweat sodium
concentration requires a patch test or lab analysis to measure precisely.
[Normative sweat data — GSSI](https://www.gssiweb.org/research/article/normative-data-for-sweating-rate-sweat-sodium-concentration-and-sweat-sodium-loss-in-athletes-an-update-and-analysis-by-sport) ·
[How to measure sweat rate](https://www.precisionhydration.com/performance-advice/hydration/how-to-measure-your-sweat-rate/)

**Altitude increases fluid loss beyond sweat alone.** Above roughly 2,400m
(8,000ft), respiratory water loss increases 2-3x due to faster breathing in
thinner air, and lower air pressure increases urination (diuresis). Athletes
at altitude lose 1-3% of body weight in fluid during moderate exercise even
in cool conditions. **This is a minor-to-negligible factor for any race near
sea level or moderate elevation (below ~1,000-1,500m)** — apply the
adjustment only when the course genuinely warrants it.
[Fluid loss at altitude](https://alpineoxygen.net/altitude-dehydration/) ·
[Rehydration during endurance exercise — review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8001428/)

**Pacing: even or slightly negative splits outperform positive splits for
non-elite athletes.** Starting conservatively reduces early glycogen
depletion and lactate/hydrogen-ion accumulation, preserving muscular
efficiency and delaying central fatigue — most non-elite marathoners run
faster overall with a negative split than an even or positive one. (Elite
athletes at very high absolute speeds are the exception — glycogen
depletion there is driven by speed itself more than pacing variance.)
[Physiology and psychology of negative splits](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12307312/)

**Heat slows you down predictably, below a clear threshold.** Below ~15°C
(60°F), temperature has minimal performance impact. Above that threshold,
expect roughly **1-2 seconds/km slower per °C above 15°C in dry conditions,
roughly double that in humid conditions** (equivalently, ~0.1-0.15% pace
loss per °F above 60°F). Humidity compounds the effect independently of
temperature.
[Heat pacing adjustment](https://runningmagazine.ca/sections/training/how-to-adjust-your-pace-in-the-heat/) ·
[Temperature/pace data](https://pheidi.training/articles/heat-performance/)

**Grade changes effort non-linearly, not proportionally.** The Minetti
energy-cost formula models this precisely; the practical heuristic is that
a 5% grade adds roughly 25-30 seconds/km of effective effort, a 10% climb
adds 4+ minutes/km-equivalent, and descents recover *less* time than
equivalent climbs cost (braking cost caps the benefit) — the relationship
is asymmetric, not symmetric.
[Grade-Adjusted Pace calculator/methodology](https://apps.runningwritings.com/gap-calculator/)

## Required inputs

| Input | Source |
|---|---|
| Body weight | `athlete-profile.md` — ask if missing |
| Expected duration & intensity | The relevant `races/*-dossier.md` + goal pace/effort |
| Sweat rate | Athlete-reported measured value, or estimate (labeled) |
| Sweat sodium ("salty sweater"?) | Athlete-reported, or estimate (labeled) |
| Gut carb tolerance | Athlete-reported (products, max g/hr practiced), or conservative estimate |
| Products used | Athlete-reported |
| Heat tolerance | Athlete-reported, or neutral default |
| Past fueling disasters | Athlete-reported — directly shapes the plan's safety margins |
| Course profile (elevation, climbs) | From the race dossier |
| Altitude | From the race dossier |
| Conditions (temp, humidity, wind) | From the race dossier |

## Procedure

1. **Identify the race**: match against files in `races/*-dossier.md`. If
   more than one exists and it's ambiguous which race this run is for, ask.
   Read `athlete-profile.md` for body weight — if missing, ask directly
   (don't estimate a number this foundational).
2. **Ask what's known**, grouped in one pass (not required to be strictly
   sequential): gut carb tolerance (max g/hr practiced without GI distress,
   and with what products), salty/heavy sweater self-assessment, a measured
   sweat rate if one exists, products currently used, heat tolerance
   (self-assessed), and any past fueling disasters worth designing around.
3. **For anything unknown, estimate — never stall waiting on a number the
   athlete doesn't have.** Use these defaults, each explicitly labeled
   `ESTIMATE` in the output:
   - **Sweat rate**: default to the population average band (~0.8-1.0 L/hr
     for cool conditions <15°C, ~1.0-1.3 L/hr for 15-22°C, ~1.3-1.6+ L/hr
     above 22°C or high humidity), adjusted for the race's actual
     temperature/humidity from the dossier. One-line note: *"measure your
     real rate by weighing yourself nude before/after a same-conditions
     run — see the protocol above."*
   - **Sweat sodium**: default to population average **~1,000mg/L** absent
     other information. One-line note: *"a sweat patch test or lab
     analysis gives your real number — worth doing before Hamburg
     specifically, sodium errors compound over 9+ hours."*
   - **Gut carb tolerance**: default to the **conservative ACSM ceiling
     (60g/hr)**, not the 90g/hr multiple-transportable-carbohydrate
     ceiling, unless the athlete reports having practiced higher intakes
     without GI distress. One-line note: *"90g/hr is achievable but must be
     gut-trained in long runs first — don't debut a higher number on race
     day."*
   - **Heat tolerance**: neutral default (apply the standard heat-pacing
     formula above without extra adjustment) unless the athlete reports
     being notably heat-sensitive or heat-adapted.
4. **Build the fueling plan**: carbs/hr, fluid/hr, sodium/hr, and exact
   timing (e.g., "every 20 minutes: X"), derived from the formulas above and
   the inputs table. Cap carb recommendations at the athlete's demonstrated
   or conservative-estimated gut tolerance, not the theoretical maximum.
5. **Build the pacing plan**: goal pace/effort by course segment, starting
   from the dossier's goal pace, adjusted for (a) grade using the GAP
   heuristic at each known climb/descent, (b) heat/humidity using the
   heat-pacing formula if race conditions exceed 15°C, (c) altitude only if
   the course is meaningfully elevated. Structure toward even-to-slightly-
   negative splits per the pacing research, not a positive-split default.
6. **Show every input** in a table — athlete-reported vs. `ESTIMATE` — and
   the math behind each derived number. **Flag anything at or near a
   physiological limit** (carb intake approaching 90g/hr, unusually high
   estimated sweat/sodium loss, pace adjustments that push effort into
   risk territory). Structure the plan so that correcting one input (e.g.,
   a real sweat-rate test result) makes it obvious what to recompute.
7. **Save** to `races/YYYY-MM-DD-<race-name>-fuel-pace-plan.md`. Clearly
   mark which numbers are real vs. estimated in the saved file, not just in
   conversation.
