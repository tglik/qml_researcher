# C13 — Candidate backlog and ingest gate

**Date:** 2026-11-05 · **Status:** minimal version built (tool, gate skill, role modes); sources
A–D and the portfolio director not built yet · **Background:** the review "Is ideation the
bottleneck?" (Claude Doc, 2026-11-05)

## Why
The lab had no shared list of ideas, no common check on them, and no record of which source an idea
came from or how far it got. So nobody could tell whether ideation was weak, or which way of
producing ideas works. This component is that list and that check.

## Shape
```
sources A–E ──add──► candidates.jsonl ──/qml-ingest──► gated ──human pick──► /qml-lab new --from-backlog
                    (dedupe at add)     novelty · triage screen · value        │
                                                                               ▼
                          directions.json ◄── outcome (furthest stage, rung) ◄── program closes
```

Three levels, the way a lab director thinks:

| Level | File | Key fields |
|---|---|---|
| Direction | `indexes/backlog/directions.json` | thesis, target rung, status open/paused/closed, effort share, close criteria fixed at creation, linked hypothesis cards, history |
| Candidate | `indexes/backlog/candidates.jsonl` | title, claim (≥ 8 words, testable), source A–E, base, direction (or unassigned), region, gate record, stage, explore flag, thread, outcome |
| Program | the lab thread | linked by `backlog link`; its `STATE.json` and verdict stay the record |

Sources: **A** build on a base paper or result · **B** open problems · **C** combination grid ·
**D** programmatic search · **E** scout, Adi's algorithms, variants.

Rungs (publishable steps, smallest first): 1 sharp negative · 2 quantum-inspired classical method ·
3 measured mechanism · 4 small-scale separation on quantum-native data · 5 crossover estimate ·
6 advantage on real data and hardware.

## The ingest gate
One gate for every source, so scores are comparable. Four checks, kept separate:

| Check | Where | Hard stop? |
|---|---|---|
| Dedupe | `backlog add` — word-set Jaccard ≥ 0.6 against candidates and past programs | yes (override with `--force`) |
| Novelty | lab archivist, novelty mode, arXiv search | only for exact prior work, with its id |
| Triage screen G0–G3 | screen analyst, triage mode | only for a 🔴 rule with its mechanism |
| Value | screen analyst, triage mode: rung × p | no — a score |

Rank = rung × p × (0.5 + novelty). About 10% of candidates (a deterministic hash of the id) are
flagged `explore` and shown in the queue whatever their score, gate kills included, so the gate's
false kills can be measured (`backlog report`).

Roles stay separate: sources generate, the gate scores, a human selects. The gate never picks and the
selector never re-scores.

## Not built yet
- Source adapters: A (widen `qml-variants` to any base), B (`/qml-open-problems` over card
  limitations and `open_questions.md`), C (extend `qml-primitive-transfer`), D (search job in the
  experiments venv), E (backlog writes from the scout and intake).
- Portfolio director role and its weekly checkpoint: designed after the first ~64 candidates have
  run through the gate.
- Directions seeding from the hypothesis ledger.
