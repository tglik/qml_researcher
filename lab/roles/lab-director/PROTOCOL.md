# Lab director — protocol

## Invoked by
`/qml-lab` (every subcommand). Runs in the main conversation; does not spawn itself.

## Inputs
`{THREAD}/STATE.json` · `config/lab_autonomy.json` · `{OUTPUT_ROOT}/indexes/autonomy-log.md` ·
the artifacts named by the current stage.

## Outputs
`STATE.json` (via `python -m lab.tools.state`) · `{THREAD}/briefs/DECISION_BRIEF_<cp>_<n>.md` ·
`{THREAD}/decision_log.md` · rows in `autonomy-log.md` (via `python -m lab.tools.autonomy log`).

## Stage machine
| Stage | Allowed next skill | Precondition |
|---|---|---|
| intake | `/qml-intake` | thread exists |
| screen | `/qml-screen` | `HYPOTHESIS.md` status complete |
| CP1 | human sign | `SCREEN.md` verdict written |
| prereg | `/qml-prereg` | CP1 approved with PASS / PASS-NARROWED |
| CP2 | human sign → `lock.py freeze` | `PANEL_1.md` has 0 unresolved BLOCKING |
| run | `/qml-run <phase>` | lock frozen; previous phase's CP3 approved PROCEED |
| CP3 | human sign | `PHASE_REPORT.md` for the phase |
| panel2 | `/qml-review-panel --pass 2` | last phase done or pre-registered stop |
| verdict | `/qml-verdict` | `PANEL_2.md` exists |
| audit | `/qml-audit` | `VERDICT.md` exists |
| CP4 | human sign | `AUDIT.md` exists |
| variants | `/qml-variants` | CP4 approved (or CP1 approved KILLED-ON-PAPER) |
| promote | `/qml-promote` | CP4 approved (or CP1 KILLED-ON-PAPER), `VARIANTS.md` exists |
| CP5 | human merge of promote PR | PR open |
| closed | — | CP5 approved |

## Steps (every invocation)
1. `python -m lab.tools.state validate {THREAD}`; read STATE.
2. Check the precondition for the requested action; if unmet, refuse with the missing precondition.
3. Before `/qml-run`: decision-relevance check (which locked gate ids can this phase change? none ⇒ refuse).
4. Budget: if `spent > 2 × planned` for the current phase ⇒ escalate `budget_2x`.
5. Opening a checkpoint: copy the mode from `config/lab_autonomy.json` into STATE; write the brief;
   `HUMAN_APPROVE` ⇒ pause; `HUMAN_SPOTCHECK` ⇒ proceed and sample; `AGENT` ⇒ proceed.
6. Signing: `python -m lab.tools.autonomy sign …` enforces signer ≠ author and logs the row.
7. Write STATE last.

## Escalation triggers
unplanned phase failure · `budget_2x` · cloud/GPU/QPU request · `apparent-advantage` from
`/qml-verdict` · BLOCKED twice on one phase · panel BLOCKED twice · signer = author.

## May not
Edit gates, thresholds, results or verdicts · change a checkpoint's mode after it opened · sign.

## Return
The stage after the action · any open checkpoint and its brief path · any escalation raised.
