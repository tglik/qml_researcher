---
thread: {thread}
format: 2
date: {YYYY-MM-DD}
status: {draft | panel-reviewed | frozen}
lock_sha256: {filled by lock.py at freeze}
---

# Plan — {short name}

<!-- The plan is the overview: a reader should get the program in five minutes. Each experiment's
design lives in experiments/E<k>_<slug>.md (template: EXPERIMENT.md); experiment k runs as tool
phase P<k> and its lock ids start with "P<k>.". Revision history and panel responses go to
change_log.md, never here. Plain words, one term per concept, models named by the short names in
the table below (lab/STYLE.md). -->

## Summary
{5–7 sentences: what we test (link HYPOTHESIS.md), how many experiments and in what spirit
(cheapest fatal first), which parts are classical and which ask whether a quantum computer is
needed, what is already known, and the most likely outcome stated in advance. One status line once
the program runs.}

## What the result decides
| Verdict | Meaning | What we do |
|---|---|---|
| GO / CONDITIONAL-GO | | {what gets funded, pitched or built} |
| NO-GO-FINAL | | {what gets dropped; what is kept} |
| NO-GO-PROVISIONAL | | {no spend until the reopening condition} |

{The best verdict this program can reach (the screen's ceiling) and why, in one sentence.}

## Experiment sequence
```
{E0 ──► E1 ──► … diagram, with one word per box on what each can end}
```

**E{k} — {the experiment's question}**
- *Tests:* {hypothesis ids, in plain words}
- *Why here:* {what it can end, and why it comes at this point}
- *Expect:* {prediction and the evidence for it}
- *If it fails:* {what stops, what continues}
- *Cost:* {core-h, wall-days}. *Details:* [E{k}_{slug}.md](experiments/E{k}_{slug}.md)

## Why this order
1. {The cheapest experiment that can end the program goes first; say which can end the whole
   program and which only the quantum claim.}

## Shared setup
- **Data and splits:** {data, holdouts that gate vs report, seeds}
- **Main metric:** {metric, its resolution, the smallest gain that matters and why}
- **Statistics:** {CI method; tuning only inside the training split; each test pool touched once}
- **Costs reported:** {correctness against ground truth per size; projected quantum cost (always
  labelled projected); simulation cost (never reported as quantum time); classical cost on the same
  hardware}
- **Machine:** {local machine and limits}
- **Exact definitions:** `frozen_definitions.md` (`def.*`).

Models compared (the classical competitor champion fills the classical rows):

| Short name | What it is | Tuning budget | Used in |
|---|---|---|---|
| {Q1} proposed method | | none on the quantum part | |
| {C0} best classical for the task | | ≥ the proposed method's | |
| {C1} same-input baseline | | ≥ the proposed method's | |
| {R1} size-matched control | | same grid | |

```lock
id: baseline.adequacy
kind: baseline
text: The best classical baseline must reach within {factor} of published SOTA ({value, source}) on {metric, data}; otherwise every NO-GO is provisional (G5/N1).
```
```lock
id: splits.definition
kind: split
text: {exact split definition — created and hashed before any modeling}
```

## Budget
| Experiment | Side | Core-hours | Peak memory | Tokens (M) | Wall-days | Fallback |
|---|---|---|---|---|---|---|
| E1 | quantum | | | | | |
| E1 | classical | | | | | |

```lock
id: global.budget_halt
kind: stop_rule
text: An experiment whose spend passes 2× its plan, or whose peak memory would exceed the machine, halts and asks a human with options (lab_method global rule 8).
```

## Before spending: open questions
- {Anything the owner must decide before compute is spent: access, feasibility, sequencing,
  estimates that look wrong. "None" if none.}

## Amendments (append-only after freeze)
| # | Date | Touches | Reason | Precedes data access for | Approved by |
|---|---|---|---|---|---|
