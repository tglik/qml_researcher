---
thread: {thread}
experiment: E{k}
phase: P{k}            # tool phase; folder P{k}_*/, lock ids "P{k}.…"
tests: {hypothesis ids, in plain words}
status: {not started | running | done}
depends_on: {earlier experiments and what each supplies}
feeds: {later experiments and what this one supplies}
budget: {core-h per side; peak memory; wall-days; halt at 2×}
date: {YYYY-MM-DD}
---

# E{k} — {the experiment's question, in plain words}

<!-- One experiment, complete enough that an implementer runs it without asking a question and an
auditor checks it mechanically. Plain-language rules first; the hashed lock text last. The rules
in "Decision rules" and the lock blocks in "Locked rules" must say the same thing — the review
panel checks this. -->

## Question and why
{The question(s) in one or two sentences each. Why the answer matters for the claim, and what it
can end. If the experiment is classical at every size it runs, say so.}

## What we expect, and why
- **{Hypothesis or check}:** {prediction}. {The evidence or mechanism behind it.}

## Design
**Data and instances.** {What is used, how many, how chosen; families, generators and seeds.}

**Models compared.** {Short names from the plan; what each receives; tuning grid; the proposed
method's tuning is never larger than the baselines'.}

**Simulation method.** {Exact / statevector / tensor network / trajectories, and why (lab_method
§6). "None" for classical-only experiments.}

**Steps.**

| Step | What | Output |
|---|---|---|
| E{k}.0 | {setup, probe or pilot} | |
| E{k}.1 | | |

## Decision rules
| Outcome | Condition | What happens |
|---|---|---|
| Pass | | {next experiment} |
| Shown absent | {including the tightness required} | {stop / continue; FINAL or PROVISIONAL} |
| In between | | {written now, before data} |

**Why these thresholds.** {One line per threshold: where the number comes from.}

## Verdict sentences, written in advance
| Gate | If it passes we write | If it fails we write | If not shown we write |
|---|---|---|---|

## Pitfalls and controls
- **{What could fool us.}** {The control or check that guards against it.}
{Every oracle or ablation gate has a size-matched control.}

## Report
{The tables and figures the phase report must contain.}

## Budget and fallbacks
| Side | Core-hours | Peak memory | Tokens (M) | Wall-days | Fallback |
|---|---|---|---|---|---|
| quantum | | | | | |
| classical | | | | | |

## Do not
- {What the implementer must not change or touch in this experiment.}

## Locked rules
Hashed into PREREG.lock.json at freeze; after freeze, changes are dated amendments that precede
data access. One block per threshold or gate, plus one `gray_zone` and one `stop_rule`.

```lock
id: P{k}.{name}.threshold
kind: threshold
text: {measured quantity, numeric threshold, justification}
op: ">="
value: {number}
```
```lock
id: P{k}.gray_zone
kind: gray_zone
text: {what happens on a partial or borderline result}
```
```lock
id: P{k}.stop_rule
kind: stop_rule
text: {condition under which the program stops after this experiment}
```
