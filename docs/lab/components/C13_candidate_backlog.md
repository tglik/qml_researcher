# C13 — Candidate backlog and ingest gate

**Date:** 2026-11-05 · **Status:** built and seeded 2026-11-05 (tool, gate skill, role modes, sources
A–E, 7 directions, 62 gated candidates); the portfolio director is not built yet · **Background:** the review "Is ideation the
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
One gate for every source, so scores are comparable. Five checks, kept separate:

| Check | Where | Hard stop? |
|---|---|---|
| Dedupe | `backlog add` — word-set Jaccard ≥ 0.6 against candidates and past programs | yes (override with `--force`) |
| Novelty | lab archivist, novelty mode, arXiv search | only for exact prior work, with its id |
| Triage screen G0–G3 | screen analyst, triage mode | only for a 🔴 rule with its mechanism |
| Potential profile | screen analyst, triage mode: seven questions (0/1/2 each) and an evidence class, per `criteria/advantage_potential.md` | no — recorded for calibration only |
| Value | screen analyst, triage mode: rung × p | no — a score |

Rank = rung × p × (0.5 + novelty). About 10% of candidates (a deterministic hash of the id) are
flagged `explore` and shown in the queue whatever their score, gate kills included, so the gate's
false kills can be measured (`backlog report`).

The potential profile (added 2026-11-11, from arXiv:2610.32595) asks why an advantage should exist
at all: mechanism, middle-band structure, hard-but-solvable window, instance ensemble, classical
work above input size, small checkable output, tested baseline. It is shown in the queue and
tabulated by band in `backlog report`, and it is deliberately outside the rank: adopt it only if
candidates in the high band reach a rung more often than those in the low band after 10 scored
candidates have closed, and delete it otherwise.

Roles stay separate: sources generate, the gate scores, a human selects. The gate never picks and the
selector never re-scores.

## Sources, where they live
| Source | Component | Writes with |
|---|---|---|
| A build on a base | `/qml-build-on` (variant-generator, build-on mode); run on each STRONG_INTEREST card and weekly on the open directions' bases | `backlog add --source A` |
| B open problems | `/qml-open-problems` over `open_questions.md`, card Limitations and hypothesis-card open risks | `backlog add --source B` |
| C combination grid | `/qml-primitive-transfer` completion step and its grid mode (hypothesis-ledger primitives and the known advantage mechanisms of `criteria/advantage_potential.md` × directions) | `backlog add --source C` |
| D programmatic search | a search job in `{OUTPUT_ROOT}/experiments/search/<name>/` with a signal check (fitness spread vs seed noise) and an honest classical twin; first job: `rydberg_graph_kernels` | `backlog add --source D` |
| E scout, algorithms, variants | `/qml-daily-scout` (claims; STRONG_INTEREST papers go to A), `/qml-variants` Phase 3, new algorithms before `/qml-intake` | `backlog add --source E` |

## First run (2026-11-05)
62 candidates (A 20, B 13, C 13, D 5, E 11), gated by fresh archivist and screen-analyst agents in
batches. Findings about the gate itself:
- Word-set dedupe at `add` caught none of the near-duplicates of our own closed programs (e.g. a
  Szegedy-walk variant of exp 08). The archivist's check against our verdicts did catch them, and
  triage killed the one that restated a ledger entry. Keep dedupe cheap; rely on the novelty step.
- The archivist caught two generator errors (a mis-described base paper, a base whose reported
  edge does not exist). Sources write from cards; stub cards make this worse.
- Batching (7 per novelty agent, 10 per triage agent) instead of one agent per candidate kept the
  cost reasonable; no sign of cross-candidate contamination, but not tested.
- Source D's first job found a fitness signal 20× seed noise, and an honest twin (the exact
  independence polynomial) that matches it.

## Second input (2026-11-11): the super-quadratic compendium
arXiv:2610.32595 was mined as a source B review: one new direction (`planted-inference-kikuchi`)
and nine candidates, gated the usual way. The paper's main lesson for the sources is that
starting from an application and looking for a quantum method rarely works; starting from a known
mechanism and looking for problems that fit it does better. Source C's grid mode now takes the
mechanisms table as rows. The 68 candidates gated before this date have no potential profile;
backfilling them is one triage pass.

## Not built yet
- Portfolio director role and its weekly checkpoint: designed after these candidates have run.
- Semantic dedupe (embedding or LLM) if the word-set check keeps missing near-duplicates.
