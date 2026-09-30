---
name: qml-intake
version: 0.1.0
description: |
  QML Lab intake. Turns a proposed quantum algorithm or a use-case idea (or a hypothesis card /
  transfer card / deep-research report) into HYPOTHESIS.md — numbered testable hypotheses with
  predicted values, a named operating point, and a disproof written before any data. Algorithm
  path first runs Adi's Stage 0 analysis (ALGORITHM_ANALYSIS.md). Interactive: asks one question
  per turn until the 5-item falsifiability checklist is complete. Usually started by `/qml-lab new`.

triggers:
  - qml-intake
  - scope this hypothesis
  - turn this idea into a testable hypothesis
  - analyze this quantum algorithm for the lab

input:
  - "<thread>  (created by /qml-lab new; inputs in 00_inputs/)"

output:
  - "{THREAD}/ALGORITHM_ANALYSIS.md (algorithm path)"
  - "{THREAD}/HYPOTHESIS.md"
  - "{THREAD}/00_inputs/answers.md"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, WebSearch, WebFetch]
---

# /qml-intake

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/algorithm-analyst/`,
`lab/roles/scoping-interviewer/` · **Templates:** `artifacts/lab/templates/{ALGORITHM_ANALYSIS,HYPOTHESIS}.md`

## Setup
```
OUTPUT_ROOT from config/workspace.json;  THREAD = {OUTPUT_ROOT}/experiments/<thread>
python -m lab.tools.state check {THREAD} --need stage:intake       # else stop
Read STATE.json → ENTRY_PATH (algorithm | use-case)
Read criteria/lab_method.md → LAB_METHOD
```

## Phase 1 — Algorithm analysis (algorithm path only)
Spawn `algorithm-analyst` (convention in `lab/README.md`: ESSENCE + PROTOCOL + LAB_METHOD + task):
```
Task: analyze the algorithm in {THREAD}/00_inputs/ and write {THREAD}/ALGORITHM_ANALYSIS.md
from artifacts/lab/templates/ALGORITHM_ANALYSIS.md. Also read criteria/qml_domain.md.
```
**Gate:** `python -m lab.tools.validate artifact {THREAD}/ALGORITHM_ANALYSIS.md` passes;
recommendation present. `STOP` ⇒ write HYPOTHESIS.md with `status: not-a-hypothesis` and the
analysis's reason; return. `ASK-HUMAN` ⇒ continue, but carry the warnings into Phase 2 and the brief.

## Phase 2 — Scoping interview (both paths; runs in this conversation)
Adopt `lab/roles/scoping-interviewer/ESSENCE.md` + `PROTOCOL.md`.
- Pre-fill from the input (C12 I5): hypothesis card (`cards/hypotheses/…`) or transfer card
  (`sources/reports/{transfer-analysis,primitives-analysis}/*/04_transfer_card.md`) — mark drafts.
- Algorithm path: H1..Hn and warnings come from `ALGORITHM_ANALYSIS.md`; the interview pins the
  operating point, the disproof, the losing-arm and the decision.
- Ask **one question per turn** (AskUserQuestion, or Hermes message to the proposer). Record each
  Q/A in `{THREAD}/00_inputs/answers.md`.
**Gate:** checklist 5/5 ⇒ `status: complete`; otherwise keep asking; three failed rounds on one
item ⇒ `status: not-a-hypothesis`.

## Phase 3 — Write and hand off
1. Write `{THREAD}/HYPOTHESIS.md` from the template.
2. `python -m lab.tools.validate artifact {THREAD}/HYPOTHESIS.md` must pass.
3. `complete` ⇒ `python -m lab.tools.state set {THREAD} --by /qml-intake --stage screen`, then tell
   the user: next is `/qml-lab next <thread>` (runs the screen).
   `not-a-hypothesis` ⇒ leave stage at intake; summarize what is missing.

## Completion message
```text
QML-INTAKE — <DONE | NOT-A-HYPOTHESIS | BLOCKED> — <thread>
Path: <algorithm | use-case> · Checklist: <n>/5
Claim: <one sentence>
Warnings: <none | list from the analysis>
Next: /qml-lab next <thread>
```
