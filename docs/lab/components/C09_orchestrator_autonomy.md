# C09 — Orchestrator & autonomy controller (`/qml-lab`)

## Purpose
The lab's single user-facing entry point (C12): people drive the lab through `/qml-lab`
(plus `/qml-intake` for the interactive interrogation); stage skills are reached through
`/qml-lab next`. Under Hermes, `status`, `sign`, briefs and escalations are available in Slack;
execution subcommands run locally. The program loop: keeps each program on its frozen question, enforces order, tracks budget,
opens and closes human checkpoints, routes escalations — and implements the **autonomy ladder**
(D4/D5), so supervision drops only when the data says it can.

## Owner role(s) and human touchpoints
`lab-director` agent. Humans interact with the lab almost entirely through `/qml-lab`: they
receive decision briefs, sign checkpoints, and (Tsahi) approve step-downs.

## Inputs / outputs
Input: `STATE.json`, `config/lab_autonomy.json`, `indexes/autonomy-log.md`.
Output: updated `STATE.json`, `briefs/*.md`, autonomy-log rows, `decision_log.md` rows, program
`README.md`, step-down proposals.

## Artifact schemas

### `qml_researcher/config/lab_autonomy.json`
```json
{
  "schema": "qml-lab/autonomy@1",
  "retire_rule": {"consecutive_runs": 5, "max_material": 0, "requires_evals": true},
  "restore_rule": "any material finding restores previous mode",
  "spotcheck": {"sample_rate": 0.33, "review_within_hours": 48, "always_review": ["GO", "CONDITIONAL-GO"]},
  "checkpoints": {
    "CP1": {"mode": "HUMAN_APPROVE", "target": "AGENT",           "evals": ["eval1", "eval4", "eval5"]},
    "CP2": {"mode": "HUMAN_APPROVE", "target": "HUMAN_APPROVE",   "evals": []},
    "CP3": {"mode": "HUMAN_APPROVE", "target": "AGENT",           "evals": ["lock_integrity", "guard"]},
    "CP4": {"mode": "HUMAN_APPROVE", "target": "HUMAN_SPOTCHECK", "evals": ["eval2", "eval3"]},
    "CP5": {"mode": "HUMAN_APPROVE", "target": "HUMAN_APPROVE",   "evals": []}
  },
  "history": [{"date": "2026-10-01", "cp": "*", "from": null, "to": "HUMAN_APPROVE", "by": "tsahi", "evidence": "W0 init"}]
}
```

## Procedure — subcommands
| Command | Does | Pass/fail |
|---|---|---|
| `new <thread> --owner <p> --path algorithm\|use-case` | Create `qml_artifacts/experiments/<thread>/` from template on branch `lab/<thread>` of `qml_artifacts`, `STATE.json`, `README.md`; hand to `/qml-intake` | Validator green |
| `status [<thread>]` | Table of programs: owner, stage, phase, open CP, budget %, blockers, escalations; plus the **backlog** — `strategic_value: actionable` hypothesis cards with no program yet (C12 I5) | — |
| `next <thread>` | Read STATE; run the next allowed skill; **refuse out of order** (no prereg without CP1, no run without lock, no verdict before panel #2, no promote before CP4) | Refusal message names missing precondition |
| `sign <thread> <CP> --by <p> --outcome unchanged\|minor\|material --minutes N [--note]` | Enforce signer ≠ author; record in STATE + autonomy-log + decision_log; advance stage | signer ≠ author |
| `escalate <thread> <type>` | Write brief; set escalation in STATE; pause | — |
| `amend <thread>` | Post-lock amendment flow → human approval → `lock.py amend` | Timing rule holds |
| `stats` | Recompute per-CP streaks and eval status; regenerate autonomy-log footer; **propose step-downs** | — |
| `step-down <CP> --approve` | Tsahi only; writes `lab_autonomy.json.history`; PR | Evidence attached |
| `ledger-review` | List ledger entries past `review_by` | — |

**Decision-relevance test** (before every `/qml-run` phase): can this phase change the outcome
of any locked gate? If not, it is not run. **Stop rule:** phase cost > 2× planned → halt + budget
escalation.

**Decision brief** (every CP and escalation, ≤ 1 page): what is decided · the agent's
recommendation · evidence links (artifact paths, gate table rows) · cost to continue · 2–5
options · exact reply (`/qml-lab sign …`). Never a transcript.

### Checkpoint handling by mode
| Mode | At checkpoint | After |
|---|---|---|
| HUMAN_APPROVE | Brief → pause until `sign` | Log row with outcome |
| HUMAN_SPOTCHECK | Brief written; proceed; sampled at `sample_rate` (always for listed categories) → human reviews within 48 h | Material finding → restore HUMAN_APPROVE for that CP lab-wide |
| AGENT | Proceed; brief written for the record | Escalations still fire |

Mode is copied into the program's STATE when a checkpoint opens and stays fixed for that
instance.

### Step-down math (D5)
For each CP: streak = consecutive most-recent logged rows with outcome ≠ material (minor edits
allowed). Eligible when streak ≥ 5 **and** all `evals` for that CP pass on the current skill
version. `stats` writes a proposal; Tsahi approves; history records evidence. Restore is
automatic on a material finding (including a spot-check finding) and logged.

## Checkpoints and autonomy
This component *implements* all of them; see the table in `01` §5.

## Separation / permission rules
`lab-director` never changes gates and never writes results. Only Tsahi can `step-down`.
`sign` refuses author = signer. `--takeover` of another owner's program is logged.

## Failure modes and controls
| Failure | Control |
|---|---|
| Drift into interesting-but-irrelevant work | Re-anchor + decision-relevance test |
| Runaway spend | Budget in STATE + 2× halt |
| Rubber-stamping (approve without reading) | `minutes` field; a CP with median < 3 min flagged in stats; restore rule |
| Premature autonomy | Eval gate + streak; restore on first material miss |
| Escalation flood | Only C03-listed triggers; pre-registered stops don't escalate |

## Evals that cover it
C10 order-enforcement fixture (call `/qml-run` without a lock → refusal); step-down math unit
tests on synthetic logs; signer ≠ author test.

## Build tasks
- [ ] W1 minimal: `new`, `status`, `next` (intake→screen→promote), `sign`, autonomy-log writing (M, 2 days)
- [ ] W3 full: run/verdict/audit routing, budget, `escalate`, `amend`, `stats`, `step-down`, `ledger-review` (M, 3 days)
- [ ] `lab_autonomy.json` + `lab/tools/autonomy.py` (streak + eligibility) (S, 1 day)
- [ ] Hermes: use `clarify` for checkpoint pauses (S)

## Acceptance criteria
Pilot runs start to finish through `/qml-lab next` only; every CP logged with outcome and
minutes; `stats` produces correct eligibility on a synthetic 10-row log.

## Open questions
- Where do briefs get delivered — file only, or also Slack DM via Hermes? Default: file +
  Hermes DM to the target person when running under Hermes.
