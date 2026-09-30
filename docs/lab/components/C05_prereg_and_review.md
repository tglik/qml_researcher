# C05 — Pre-registration & review panel (`/qml-prereg`, `/qml-review-panel`)

## Purpose
Freeze what counts as success before any data is opened, in a form a machine can diff later
(`PREREG.lock.json`), and have it attacked by five adversarial reviewers before a human freezes
it. Merges Tsahi's registered-report discipline with Adi's S1 phase design and S2 checklist.

## Owner role(s) and human touchpoints
`experiment-designer` (prereg), `classical-twin-champion` (baseline + twin spec), `review-panel`
(5 personas). Human: **CP2 freeze** — permanent `HUMAN_APPROVE`. Default signer Adi
(physics-bearing thresholds), any of the 3 otherwise; never the designer-of-record.

## Inputs / outputs
| Skill | Input | Output |
|---|---|---|
| `/qml-prereg` | `HYPOTHESIS.md`, `ALGORITHM_ANALYSIS.md`, `SCREEN.md` (PASS*), `lab_method.md` | `PROPOSAL.md`, `00_operating_point.md`, `frozen_definitions.md`, `PREREG.lock.json` (on freeze) |
| `/qml-review-panel` | pass 1: proposal set; pass 2: `results/gates.md` + phase reports, **no verdict** | `PANEL_1.md` / `PANEL_2.md` |

## Artifact schemas
C01: `PROPOSAL.md`, `PANEL_n.md`, `PREREG.lock.json`.

## Procedure

### `/qml-prereg`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Map | H→experiment table: hypothesis · experiment IDs · metric · predicted · pass-if · fail-if (Adi S1 §1.1) | Every H tested; every experiment tests an H |
| 1 Ladder | Phases P1–P5 per D3/D7; order **cheapest-fatal first** inside the phase set (a P3 real-data headroom check may be pulled ahead of P2 if cheaper and more fatal); attach G4–G9 | Each gate attached to exactly one phase |
| 2 Arms | Quantum arm; classical twin; strongest classical baselines (≥1 exact, ≥1 industry tool); size-matched controls for every oracle / ablation gate; tuning budget classical ≥ quantum | Twin present or on-paper reason it's unnecessary |
| 3 Metrics | Correctness (ground truth per size), projected quantum cost (formula + assumed clock), **simulation cost labeled separately**, classical cost same hardware, scaling fits (poly vs exp, AIC/BIC, CIs) | Simulation cost never used as quantum time |
| 4 Instances & stats | Families, generators + seeds, ≥ 20–50 per size small, tuning vs test split, exact + finite-shot, CI method | Split definitions hashed in `frozen_definitions.md` |
| 5 Thresholds | Numeric threshold + justification + **gray-zone policy** per gate ("a second failure stops the program" written now); baseline-adequacy bar (N1, factor of published SOTA) | Every threshold has a justification line |
| 6 Operating point | `00_operating_point.md`: named industrial N_ind, KPI translation, extrapolation ladder ≥ 4 points | Present |
| 7 Budget | Per phase: cpu-h, peak memory (checked against `sim_budget.py`), tokens, wall days; fallback per phase ("stop at 24q, MPS for checks only") | Fits D7 limits |
| 8 Verdict sentences | Both the GO and NO-GO sentence per gate, in advance | Both present; if NO-GO sentence can't be written, gate is not specified |
| 9 Panel #1 | Invoke `/qml-review-panel` pass 1; designer revises; ≤ 2 rounds | 0 unresolved BLOCKING |
| 10 Freeze | Brief → **CP2**; on approval `lock.py freeze` writes the lock, commits, records sha in `STATE.json` | Lock validates |

Iron rule: after the lock, thresholds are immutable. Amendments: `/qml-lab amend` → append-only,
dated, human-approved, and must precede data access for the phase they touch (`lock.py`
enforces with provenance timestamps).

### `/qml-review-panel`
Five personas spawned in parallel, fresh contexts, artifacts only:

| Persona | Attacks | Signature question |
|---|---|---|
| methodologist | leakage, splits, power, missing controls, gate drift | What would make this result appear without the mechanism? |
| dequantization-theorist | Tang/Chia reductions, sparse-QSVT, sampling twins, TN/Clifford simulability | What does a classical algorithm with the same access model achieve? |
| hardware-realist | shots, cadence, qubit/depth envelope, noise, modality fit, P4/P5 realism | How many times is this circuit run, and who pays? |
| baseline-champion | SOTA adequacy, tuning parity, budget parity | Is this baseline strong enough to license the conclusion? |
| value-translator | operating point, KPI, customer value | Which number on a customer's dashboard moves? |

Plus **Adi's S2 checklist** as the mandatory floor — run by the methodologist, marked
✅/⚠️/❌ per item. Output: severity-ranked issues anchored to verbatim text with a concrete fix.
Verdict: APPROVED / APPROVED-WITH-CHANGES / BLOCKED. Small fixes are *suggested*, never applied
by the panel (it may not rewrite what it reviews); the designer applies and logs in
`change_log.md`.

**Pass 2** (after the last phase, before `/qml-verdict`): same personas, inputs are
`results/gates.md`, phase reports, lock — explicitly no draft verdict. Focus: gate drift,
leakage, artifact explanations, size-matched controls. This is where M01's H2 would have been
caught prospectively.

## Checkpoints and autonomy
| CP | V1 | Target | Note |
|---|---|---|---|
| CP2 freeze | HUMAN_APPROVE | **HUMAN_APPROVE (permanent)** | Framing errors pass every automated check; this is the only place they're caught |

Human's job at CP2 (~30 min): right question? operating point real? thresholds defensible?
Brief lists the panel's BLOCKING issues and how each was resolved.

## Separation / permission rules
Designer never audits. Panel never edits. Classical-twin-champion never touches the quantum
arm spec. Panel is a different agent instance per pass.

## Failure modes and controls
| Failure | Control |
|---|---|
| Post-hoc redefinition of success | Lock + amendment timing rule + audit lock diff |
| Weak / untuned baseline | baseline-champion + N1 bar + tuning-budget parity in lock |
| Panel is decoration (never blocks) or noise (always blocks) | Block rate tracked; target band 10–60% (C10) |
| Budget blowup at P2 26q | `sim_budget.py` check in phase 7; fallback pre-written |

## Evals that cover it
Eval 2 (M01 replay — panel pass 2 should flag the H2 size-matched artifact before the auditor
does); C10 panel block-rate metric.

## Build tasks
- [ ] `/qml-prereg` SKILL.md + `experiment-designer`, `classical-twin-champion` defs (M, 2 days)
- [ ] `/qml-review-panel` SKILL.md + 5 persona defs + S2 checklist (M, 1.5 days)
- [ ] `lock.py freeze|verify|amend` (C06, needed here in W2)

## Acceptance criteria
On the M01 replay, prereg reconstruction produces a lock that `lock.py verify` accepts; panel
pass 2 raises the H2 size-matched-control issue as BLOCKING; a seeded post-freeze threshold
edit is caught.

## Open questions
- Should Adi countersign physics-bearing thresholds even when Tsahi signs CP2? D6 says any
  of the 3; recommended as a soft default in the brief ("physics-bearing: yes/no").
