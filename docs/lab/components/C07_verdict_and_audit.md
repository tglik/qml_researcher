# C07 — Verdict & audit (`/qml-verdict`, `/qml-audit`)

## Purpose
State what was measured against the frozen gates, at the right strength, and then have an
independent agent try to break that statement. In a kill-oriented lab the cheap failure is
**over-killing** — a NO-GO that is really a bug, a weak baseline, or an underpowered test — so
the audit bar for a binding negative is higher than for a go.

## Owner role(s) and human touchpoints
`verdict-writer`, `verdict-auditor` (fresh context, artifacts only, different model where
available). Human: **CP4** signs the verdict + audit pair — V1 `HUMAN_APPROVE`; default signer
Adi. Any GO / CONDITIONAL-GO also triggers the "apparent advantage" escalation to Adi + Tsahi.

## Inputs / outputs
| Skill | Input | Output |
|---|---|---|
| `/qml-verdict` | lock, `PROPOSAL.md`, all `results/gates.md`, phase reports, `PANEL_2.md` | `VERDICT.md` |
| `/qml-audit` | `VERDICT.md`, lock, raw artifacts, provenance, code — **no transcripts, no phase-report prose beyond numbers** | `AUDIT.md` |

## Artifact schemas
C01: `VERDICT.md`, `AUDIT.md`. Verdict vocabulary (D10):

| Verdict | Meaning | Requires |
|---|---|---|
| **GO** | Correct, and credible advantage of a named type (provable / heuristic / practical) survives twin, baselines, loading/readout/shots, and noise or an FT path | Advantage type + resource + confidence; escalation to Adi + Tsahi |
| **CONDITIONAL-GO** | Correct, advantage plausible under stated conditions (p < p*, N > N*, instance class, complexity assumption) | Conditions explicit and testable |
| **NO-GO-FINAL** | No advantage / incorrect / simulable / overheads cancel it | N1–N5 all hold |
| **NO-GO-PROVISIONAL** | As above but ≥1 of N1–N5 fails | Named reopening condition; blocks quantum spend, not the reopening experiment |
| **BLOCKED** | Could not evaluate | Blocker with failing command |

Mandatory in every verdict: **"not shown in tested range" vs "shown to be absent"** — which one
applies, per hypothesis.

## Procedure

### `/qml-verdict`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Read | Lock + gates tables + phase reports + panel #2 | Lock verify green |
| 1 Gate-by-gate | Outcome per gate by reference to lock ids (not restated) | Every locked gate has an outcome |
| 2 Mechanism | Structural reason it held or failed + narrowest class it generalizes to (N4) | One paragraph; no "it just didn't work" |
| 3 Licenses | What this licenses / does not license; tested-range statement | Wording ≤ claim-ladder status (`SOUL.md`) |
| 4 Category | Apply D10 + N1–N5 self-check (auditor re-checks independently) | Category justified |
| 5 Survives regardless | Classical results, instruments, datasets that transfer | Section non-empty or explicit "none" |
| 6 Reopening | Condition (PROVISIONAL) or next step | Present when required |

Iron rule: no number without a `file:line` or provenance id. Written by a different agent than
the implementer; pre-written verdict sentences from the prereg are the starting point.

### `/qml-audit`
| Phase | Work | Pass/fail |
|---|---|---|
| 0 Lock diff | `lock.py diff` verdict claims vs lock; any threshold / split / stop-rule moved; amendment timing | Mechanical — zero judgment |
| 1 Recompute | ≥ 2 headline numbers from raw artifacts with own code (`fit_scaling.py` for fits) | Match within reported CI |
| 2 Reproduce | Adi S5 subset: ≥ 1 size per phase run, the largest size reached, the classical baseline at that size — rerun from stored code/env/seeds, with data re-created by `fetch.py --verify` (via `/qml-experiments rerun` mechanics, repointed at `qml_artifacts/experiments/` by C11) | Agree within CI |
| 3 Independent correctness | A few instances checked against ground truth with a different simulator / library | Match |
| 4 Provenance sample | Sample ≥ 5 material numbers → trace to provenance → file | All trace |
| 5 Fairness | Baselines strongest + fairly tuned? twin held? simulator time used as quantum time anywhere? | No violations |
| 6 N1–N5 | Baseline adequacy · gate integrity · discriminating power (point estimates at null; size-matched controls present) · mechanism named · (this audit) | Each marked |
| 7 Alternatives | What non-mechanism could produce this result (bug, leakage, underpowering, instance selection) | Considered and addressed |
| 8 Verdict on verdict | **CONFIRMED** / **OVERTURNED** / **INSUFFICIENT** (+ named missing control) | — |

`INSUFFICIENT` with a named missing control is a success: it converts a NO-GO into a
provisional one with a reopening condition. Only `CONFIRMED` lets a FINAL NO-GO enter the ledger
as binding. `OVERTURNED` → escalation to Adi; verdict-writer revises (new instance), auditor
re-runs.

## Checkpoints and autonomy
| CP | V1 | Target | Step-down evidence |
|---|---|---|---|
| CP4 verdict + audit | HUMAN_APPROVE | HUMAN_SPOTCHECK — 1 in 3 sampled, **every GO / CONDITIONAL-GO always reviewed** | 5 consecutive 0-material; evals 2 and 3 green |

Human's job at CP4 (~30 min): does the verdict mean what it says? Is the scope of any exclusion
the narrowest one? Spot-read the diff of the implementation for plausible-wrong-code.

## Separation / permission rules
Auditor has never designed or run anything in this program; fresh context; artifacts only;
different model where available. Implementer never writes the verdict.

## Failure modes and controls
| Failure | Control |
|---|---|
| Overclaiming a GO | Advantage-type field; escalation; CP4 always human for GO |
| Over-killing | N1, N3, N5; provisional-by-default when baseline is weak; eval 3 |
| Auditor agrees by default | Mechanical phases 0–2 don't depend on judgment; C10 tracks CONFIRMED rate (100% over many runs is a smell) |
| Tool-call hacking / cited-but-unused evidence | Provenance sample |

## Evals that cover it
**Eval 2** (M01 audit replay): auditor must independently flag H2's formal pass as a
size-matched-control artifact and H0's failure → PROVISIONAL. **Eval 3** (false-kill): classical
survivors kept in "survives regardless".

## Build tasks
- [ ] `/qml-verdict` SKILL.md + `verdict-writer` def (M, 1.5 days)
- [ ] `/qml-audit` SKILL.md + `verdict-auditor` def (M, 2 days)
- [ ] `lock.py diff` human-readable output (S, C06)

## Acceptance criteria
Eval 2 passes both known answers; a seeded moved threshold is caught at phase 0; a seeded
fabricated number fails provenance sampling.

## Open questions
- Different model availability for the auditor (`00` open question 2).
