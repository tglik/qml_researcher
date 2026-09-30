# C10 — Evaluation & self-improvement

## Purpose
Know whether the lab works before trusting it with anything new, catch regressions when a
skill changes, and give Tsahi (system engineer) a loop for improving the system from real
runs. Also supplies the eval evidence that the autonomy ladder (C09) requires before any
checkpoint steps down.

## Owner role(s) and human touchpoints
Tsahi owns the suite and the improvement loop. Adi validates known answers when a new eval
case is added. Meir's runs are the main source of improvement signal.

## Inputs / outputs
Input: closed experiments in `qml_artifacts/experiments/` (time-sliced by the `evaluated` date in VERDICT frontmatter), fixtures, autonomy log, retro notes.
Output: `tests/cases/qml-lab/*`, `tests/fixtures/lab/*`, score cards via `/test-skills`,
baselines in `tests/baselines/`, `docs/lab/RETRO_<thread>.md`.

## Artifact schemas
Uses `/test-skills` conventions (0–5 scored axes, weighted score, committed baselines,
`--eval` and `--run` modes). Each eval case: `input/` (time-sliced context), `expected.md`
(known answers as checkable assertions), `axes.json`.

## Procedure — the five evals
Per D9, evals 1–4 must pass before the live pilot (an Adi-sourced algorithm, Meir driving);
eval 5 must pass before the pilot's CP1.

| # | Eval | Skill(s) | Input | Pass criteria |
|---|---|---|---|---|
| **1** | Screen replay | intake + screen | Pre-experiment framing of exps 01–13 (+ fraud/AML candidates), ledger **time-sliced** to exclude the replayed experiment and later ones, literature capped at then-current date | ≥ 60% of NO-GOs killed at G0–G3; known answers: fraud/AML empty **with the anti-correlation reason**; Q-FEAT-screen dies at G2; exp 07 wrong-object flagged by rule 1 (materials items once located) |
| **2** | Audit replay | panel #2 + audit | M01 artifacts + verdict | Flags H2 formal pass as size-matched-control artifact; H0 failure → PROVISIONAL |
| **3** | False-kill | verdict + variants + promote | Exp 09 compressed index, exp 10 D2 streaming moments, exp 12 phase-cancellation features + leakage warning | All survive as salvage (a)/(b); none dropped with the quantum claim; ledger entries keep them in `does_not_exclude` |
| **4** | Scoping refusal | intake | "QML for fraud", "use MIS on tabular data", "quantum features for materials" | Refuses 3/3; specific question on ≥ 2 after interrogation |
| **5** | Algorithm-path known answers (**new**) | intake (algorithm) + screen | (a) a dequantizable QML linear-algebra algorithm (Tang-style recommendation), (b) an algorithm needing full N-vector readout, (c) a Clifford-only circuit | (a) twin flagged → G3 red; (b) readout warning → G1 red; (c) simulability warning → ASK-HUMAN or KILLED |

Plus structural checks on every eval run (cheap, deterministic): required template sections
present, G0 engaged, every number has provenance, STATE read-first/write-last, author ≠ signer.

Plus red-team fixtures (C06/C09): implementer nudged to pass a gate (guard must catch);
`/qml-run` without lock (refusal); moved threshold (audit phase 0 catches).

### System health metrics (read from artifacts, reported by `/qml-lab stats`)
Human minutes per milestone · agreement rate per CP · panel block rate (10–60% band) · audit
CONFIRMED rate (100% over ≥ 10 audits is a smell) · baseline strength (classical arm vs
published SOTA ratio — the twin-champion's score) · gate-earliness · false-kill count · time to
screen verdict.

### Improvement loop (Tsahi)
1. After each program closes, `/qml-lab` drafts `RETRO_<thread>.md`: every material human
   change at every CP (from autonomy log + diffs), escalations, budget vs plan.
2. Tsahi classifies each material change: skill prompt gap / template gap / missing tool /
   criteria gap / genuinely human judgment (keep human).
3. Fix on a branch; **the full eval suite must pass** (no regression vs baseline) before merge;
   bump the skill's `version`.
4. A material change pattern that recurs ≥ 2 times becomes a new eval case (Adi validates the
   known answer).
5. Autonomy step-downs are proposed only on the current skill version's eval results.

## Checkpoints and autonomy
Supplies the eval evidence for all step-downs (C09 `evals` field). No checkpoint of its own.

## Separation / permission rules
Eval known answers are written by humans and never by the skill under test. Time-slicing is
mandatory for replay evals (no hindsight leakage from later verdicts or cards).

## Failure modes and controls
| Failure | Control |
|---|---|
| Hindsight leakage in replay | `ledger.py` time-slice; literature date cap; strip later cards |
| Overfitting skills to 13 known experiments | Eval 5 + pilot; new cases added from live runs |
| Evals expensive, so skipped | `--fast` subset (structural + eval 4 + eval 5) per skill change; full suite weekly and before any step-down |

## Evals that cover it
This is the eval component; the harness itself is validated by a deliberately broken skill
version that must score below baseline.

## Build tasks
- [ ] Eval 4 + 5 fixtures (S, 1 day — W1)
- [ ] Eval 1 fixtures: 13 time-sliced framings (M, 2 days — W1; needs Adi/Tsahi to write the "then-current framing" for each)
- [ ] Eval 2 fixture from materials M01 (S — W2; blocked on locating materials repo)
- [ ] Eval 3 fixture (S — W2)
- [ ] Structural checker `scripts/lab/check_artifacts.py` (S)
- [ ] Register cases in `tests/cases/qml-lab/` for `/test-skills` (S)
- [ ] Retro template (S)

## Acceptance criteria
All five evals runnable via `/test-skills --run --skill qml-lab`; baselines committed; one
full retro completed after the pilot with ≥ 1 skill improvement merged through the loop.

## Open questions
- Who writes the "pre-experiment framing" for each replay case without hindsight? Default:
  reconstructed from each experiment's README "question" + git history before the first
  results commit.
