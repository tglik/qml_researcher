# C04 — Intake & screen (`/qml-intake`, `/qml-screen`)

## Purpose
Turn a vague input — an algorithm or a use-case idea — into numbered, falsifiable hypotheses
(D1), then kill it on paper if it can be killed on paper. Historically G1–G3 killed more ideas,
more cheaply, than any experiment; this is the highest-leverage hour in the lab.

## Owner role(s) and human touchpoints
- `/qml-intake`: `scoping-interviewer` (use-case) or `algorithm-analyst` (algorithm). Often
  **Meir** drives it interactively; the idea's proposer (e.g. Adi for the pilot) answers.
- `/qml-screen`: `screen-analyst`. Human: **CP1** sign-off (V1 `HUMAN_APPROVE`).

## Inputs / outputs
| Skill | Input | Output |
|---|---|---|
| `/qml-intake` | algorithm (paper / notes / code in `00_inputs/`) **or** direction / deep-research report / triage card / Primitive Transfer Card / hypothesis card | `HYPOTHESIS.md`; algorithm path also `ALGORITHM_ANALYSIS.md`; new thread folder + branch + `STATE.json` (via `/qml-lab new`) |
| `/qml-screen` | `HYPOTHESIS.md` (+ analysis), `lab_method.md`, `qml_domain.md`, exclusion ledger | `SCREEN.md`; CP1 decision brief |

## Artifact schemas
Templates in C01: `HYPOTHESIS.md`, `ALGORITHM_ANALYSIS.md`, `SCREEN.md`, `DECISION_BRIEF.md`.

## Procedure

### `/qml-intake`
| Phase | Use-case path | Algorithm path | Pass/fail |
|---|---|---|---|
| 0 Ingest | Read input + exclusion ledger + related cards (no web search) | Read all of `00_inputs/`; mark vague points **[ASSUMPTION]** | Inputs listed in `HYPOTHESIS.md` §Sources |
| 1 Interrogate | One question per turn: quantifier, counterfactual, output shape, tolerance, kill condition | Adi S0 A–B: task formal I/O, correctness notion, N↔q, encoding + loading cost, circuits, depth/gates/T-count, measurement, shots(ε,δ), output form, hyperparameters, trainability | All questions answered or marked open |
| 2 Competition | Name the arm that wins if false | Adi S0 C: classical table, quantum table, **twin** (dequantization, TN/MPS, Clifford/matchgate, same-structure methods) — cite or **[UNVERIFIED]** | Both tables non-empty |
| 3 Resources | Name the operating point (in the design, not the discussion) | Adi S0 D: resource tables in q *and* N, plus brute-force simulation cost; E: claimed source of advantage, trade-offs, **break-even N*** | Same variable for both arms |
| 4 Hypotheses | Write disproof sentence + kill criteria | Write warning boxes (Adi S0 §3 table) | **H1..Hn** each has predicted value/scaling + metric |
| 5 Write | `HYPOTHESIS.md` | `ALGORITHM_ANALYSIS.md` + `HYPOTHESIS.md` | Checklist 5/5 (claim, operating point, disproof, false-arm, decision changed) |

Iron rule: no literature search, no experiment proposal, until 5/5. The failure mode is
politeness. It may conclude "this is a topic, not a hypothesis" and hand back — a valid output.
Literature gaps route to `/qml-deep-research`, never done inside intake.

### `/qml-screen`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 G0 ledger | Query ledger; for each brushed entry argue same/different **by mechanism** | Section present, each entry engaged |
| 1 Six rules | Green/amber/red + reason per rule, in ladder order: G1 readout (rule 6), G2 resource cap both arms incl. mandatory preprocessing (rule 4), G3 twin on paper (rule 1), then rules 2, 3, 5 as design constraints for prereg | ≥1 rule answered decisively, else → back to intake |
| 2 Algorithm warnings | Carry Adi's warning boxes; any exponential quantum resource or simulability → at least amber | Warnings copied verbatim to top of `SCREEN.md` |
| 3 5 QML criteria | From `qml_domain.md` | All 5 scored |
| 4 Architectures | Enumerate deployment architectures; screen each (the Q-FEAT-screen / core / label pattern) | ≥2 enumerated or a reason why only one exists |
| 5 Verdict | `PASS` / `PASS-NARROWED` (+ the narrowed claim) / `KILLED-ON-PAPER` (+ mechanism) / `ASK-HUMAN` (warnings with no decisive rule) | Narrowest licensed claim stated |
| 6 Brief | `DECISION_BRIEF_CP1_1.md`; `/qml-lab` opens CP1 | Brief ≤ 1 page |

Cost target: < 2 h agent time, zero code. `KILLED-ON-PAPER` still goes to `/qml-variants`
(mechanism is known) and `/qml-promote`.

## Checkpoints and autonomy
| CP | V1 | Target | Step-down evidence |
|---|---|---|---|
| CP1 screen | HUMAN_APPROVE | AGENT | 5 consecutive 0-material sign-offs + evals 1, 4, 5 green |

Human's job at CP1: *is this the right question* and *did G0 engage honestly*. Not: re-derive
the rules.

## Separation / permission rules
Screen-analyst ≠ scoping-interviewer instance (fresh agent, artifact handoff). The person who
proposed the idea cannot sign its CP1.

## Failure modes and controls
| Failure | Control |
|---|---|
| Accepting a topic as a hypothesis | 5/5 checklist; eval 4 |
| All-amber screen | Gate: ≥1 decisive rule or return to intake |
| Ledger lookup without engagement | Required section, C10 structural check |
| Algorithm analysis trusts the paper's own resource claims | Adi's end-to-end rule: loading + readout + shots in the quantum cost; **[UNVERIFIED]** tags; twin check mandatory |
| Screen kills a good idea (over-kill) | CP1 human review in V1; eval 3; `does_not_exclude` |

## Evals that cover it
Eval 1 (screen replay), eval 4 (scoping refusal), eval 5 (algorithm-path known answers) — C10.

## Build tasks
- [ ] `/qml-intake` SKILL.md with two paths + 2 agent defs (M, 2 days)
- [ ] `/qml-screen` SKILL.md + `screen-analyst` def (M, 1.5 days)
- [ ] Eval fixtures for 1/4/5 (C10)

## Acceptance criteria
Eval 1 ≥ 60% gate-earliness with the three known-answer checks (fraud/AML empty with the
anti-correlation reason; Q-FEAT-screen dies at G2; exp 07 wrong-object flagged by rule 1);
eval 4 refuses 3/3 and produces a specific question on ≥ 2; eval 5 passes 3/3.

## Open questions
- Does intake need the pilot proposer present live, or can Adi answer asynchronously in a file?
  Default: async answers in `00_inputs/answers.md`, one question per round.
