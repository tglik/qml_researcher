# C06 — Execution harness & run (`/qml-run`, `scripts/lab/`)

## Purpose
Execute one frozen phase faithfully, with every number traceable and no way for the executor
to move the goalposts. This is where every documented agent pathology lives (overclaiming,
reward hacking, constraint-evasive fabrication), so it is built last (W3) and leans hardest on
deterministic tools — Meir's "tools" layer.

## Owner role(s) and human touchpoints
`implementer` (often **Meir** in the slot, with agent assistance), `classical-twin-champion`
(baseline arm). Human: **CP3 phase gate** — V1 `HUMAN_APPROVE`.

## Inputs / outputs
Input: `STATE.json` (stage `run`), lock, `PROPOSAL.md` phase section, `frozen_definitions.md`.
Output per phase `Pk_*/`: `src/`, `raw/`, `figures/`, `RUN_LOG.md`, `provenance.json`,
`results/gates.md`, `PHASE_REPORT.md`; `env.md` and `change_log.md` appended.

## Artifact schemas
C01: `provenance.json`, `results/gates.md`, `PHASE_REPORT.md`.

### Deterministic tools — `qml_researcher/scripts/lab/`
| Tool | Does | Used at |
|---|---|---|
| `validate.py` | Schema-validate STATE / lock / provenance | every skill, phase 0 and last |
| `lock.py freeze\|verify\|amend\|diff` | Canonicalize PROPOSAL items → hashes; verify root; enforce amendment-before-data rule using provenance timestamps; human-readable diff | prereg, run (start + end), audit |
| `splits.py` | Create + hash splits before any modeling; refuse to re-create a hashed split | run phase 2 |
| `provenance.py` | Context manager / CLI wrapper: records command, commit, env hash (pip freeze), dataset + split sha, seeds, wall-clock, peak memory → appends `provenance.json` | every material run |
| `check_sizes.py` | Pre-commit: refuse any file > 5 MB not listed as untracked in a `manifest.json` (C11) | every commit on a program branch |
| `guard.py` | Git diff at phase end; fail if implementer touched lock / PROPOSAL / frozen_definitions / VERDICT | run last phase |
| `sim_budget.py` | Memory/time estimate from Adi's limits table (16·2^q statevector, 16·4^q density matrix, trajectories) | prereg phase 7, run phase 1 |
| `fit_scaling.py` | Fit cost vs q and N to poly and exp models, AIC/BIC, bootstrap CIs; emits scaling class | run analysis, audit recompute |
| `gates.py` | Read raw results + lock thresholds → write `results/gates.md` table (no prose possible) | run phase 5 |
| `resource_est.py` | P5: transpile to native gate sets/connectivity (Qiskit), depth after routing, SWAP overhead, optional QRE logical→physical | P5 only |

Reuse: slug resolution, freshness diagnosis and rerun mechanics come from the existing
`/qml-experiments` skill (repointed at `qml_artifacts/experiments/` by C11) — `/qml-run` calls
its `run-status` and `rerun` modes rather than re-implementing them. All code and results a
phase produces are committed on the program branch in `qml_artifacts` (D12); nothing is
written to `qml_researcher` except tool improvements.

## Procedure — `/qml-run <thread> <phase>`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Re-anchor | Read STATE + lock; restate frozen question + gates this phase serves; `lab-director` confirms decision-relevance (can this phase change any gate outcome?) | Restatement matches lock text; `lock.py verify` green |
| 1 Environment, data & budget | `env.md`; `data/fetch.py --verify` re-creates any gitignored file > 5 MB and checks sha256 against `manifest.json` (C11); `sim_budget.py` vs planned; offline mode for evaluation (no network in eval step) | Hashes match; budget fits or escalate |
| 2 Splits & sanity | `splits.py` create/hash; pre-registered leakage checks (precedent: static-graph leakage worth ≈0.51 ROC-AUC on crypto AML) | Leakage checks pass or BLOCKED |
| 3 Unit tests | Circuits on 2–4q with analytic answers; baselines correct on small cases; exact vs finite-shot converge as shots grow (Adi S3 §1) | All green |
| 4 Dry run | Smallest size end to end; measure time + memory | Within budget ×1.2 |
| 5 Full run | Execute design exactly; raw per instance/seed/size to Parquet/CSV; every deviation → `change_log.md`; no silent skipping of sizes (use pre-written fallback) | All planned cells present or explained |
| 6 Gates | `gates.py` → `results/gates.md`; `fit_scaling.py` outputs | Every gate in phase evaluated or explicitly BLOCKED |
| 7 Phase report | Adi template: what ran + deviations · results with one-sentence captions · expected vs observed per H (Confirmed / Partial / Not) · baselines side by side at equal budget · surprises + bug signs (too good, too-low variance, input-independent output) + simulability signs (small MPS bond dim) · gate decision proposal | Every number has a provenance id |
| 8 Close | `guard.py`; `lock.py verify`; write STATE; `/qml-lab` opens CP3 with brief | Guard + lock green |

Phase-specific notes (D7):
- **P1 toy 6–16q:** hyperparameter search on tuning set only; record how best params change with q.
- **P2 18–26q:** no new full search; extrapolation rule pre-written; ~1 GiB statevector at 26q.
- **P3 real data:** (a) real data subsampled to ≤ 26q, (b) classical at full industrial N_ind,
  (c) resource estimate at N_ind vs (b) and break-even N*. MPS beyond 26q only as a check —
  small bond dimension is flagged as a simulability warning.
- **P4 noise:** density matrix ≤ 12–14q, trajectories ≤ 20–24q; mitigation with its shot overhead; output = error threshold p* and whether any P1–P3 advantage survives at p*.
- **P5 hardware (modeling):** `resource_est.py` per modality table; NISQ vs FT; minimal
  hardware demonstration defined; **no job submission** in V1.

`BLOCKED` is first-class and non-penalized: record the exact failing command and attempts; never
fabricate a path around a constraint.

## Checkpoints and autonomy
| CP | V1 | Target | Step-down evidence |
|---|---|---|---|
| CP3 phase gate | HUMAN_APPROVE | AGENT for pre-registered pass/stop; escalate otherwise | 5 consecutive 0-material; lock diff clean on all; 0 guard violations; audits find no fabricated BLOCKED workarounds |

Decision rule at CP3 (Adi S3 §5 + gray-zone policy): all key H confirmed → next phase;
pre-registered stop condition met → stop, go to verdict (not an escalation); anything else
(partial with no pre-registered policy, suspected bug, deviation that affects conclusions) →
escalation brief with options + cost.

## Separation / permission rules
Implementer cannot write lock / PROPOSAL / frozen_definitions / VERDICT (guard). Interpretation
is not in `gates.md`. Classical-twin-champion builds the baseline arm; implementer builds the
quantum arm.

## Failure modes and controls
| Failure | Control |
|---|---|
| Training on test / leaking splits | Hashed splits before modeling; leakage checks; offline eval |
| Patching the scorer / thresholds | `gates.py` reads thresholds from lock; guard |
| Plausible wrong code → clean-looking NO-GO | Unit tests on analytic cases; size-matched controls; auditor rerun subset; human CP3 in V1 |
| Simulator time presented as quantum time | Separate metrics fields; panel pass 2; audit fairness check |
| Silent budget runaway | Budget in STATE; 2× halt → escalation |

## Evals that cover it
Eval 2 (auditor rerun subset exercises provenance), C10 red-team fixture: an implementer prompt
nudged to "make the gate pass" — guard / lock must catch the edit.

## Build tasks
- [ ] `lock.py`, `validate.py`, `guard.py` (M, 2 days — W2 because prereg needs lock)
- [ ] `splits.py`, `provenance.py`, `gates.py`, `sim_budget.py`, `fit_scaling.py` (M, 3 days)
- [ ] `resource_est.py` (M, 2 days; can slip to after pilot P3)
- [ ] `/qml-run` SKILL.md + `implementer` def (M, 2 days)
- [ ] Unit tests for all tools in `tests/lab/` (M)

## Acceptance criteria
Tools have unit tests; a toy end-to-end thread runs P1 with complete provenance; seeded
violations (threshold edit, split re-create, missing provenance) each fail loudly; pilot P1–P3
complete with CP3 logged each time.

## Open questions
- P5 tooling: Qiskit transpile + Azure QRE vs hand model first (`00` open question 4).
- GPU statevector (cuQuantum) for 26–30q locally — in or out of V1? Default: out.
