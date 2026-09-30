---
name: qml-screen
version: 0.1.0
description: |
  QML Lab paper screen (gates G0–G3 + the six rules + the five QML criteria), run on a completed
  HYPOTHESIS.md before any experiment is designed. Produces SCREEN.md with PASS, PASS-NARROWED,
  KILLED-ON-PAPER or ASK-HUMAN, then opens human checkpoint CP1. Normally invoked by
  `/qml-lab next`, not directly.

triggers:
  - qml-screen
  - run the lab screen on this program

input:
  - "<thread>"

output:
  - "{THREAD}/SCREEN.md"
  - "{THREAD}/00_inputs/research_request.md (only when literature is needed)"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash]
---

# /qml-screen

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/screen-analyst/` ·
**Template:** `artifacts/lab/templates/SCREEN.md`

## Setup
```
OUTPUT_ROOT, THREAD as in /qml-lab
python -m lab.tools.state check {THREAD} --need stage:screen
python -m lab.tools.state check {THREAD} --need file:HYPOTHESIS.md
python -m lab.tools.ledger validate           # the ledger must parse before G0 can engage it
```

## Phase 1 — Screen
Spawn a **fresh** `screen-analyst` (never the instance that ran intake):
```
Task: screen the program at {THREAD}. Inputs per your PROTOCOL. Write {THREAD}/SCREEN.md from
artifacts/lab/templates/SCREEN.md. Ledger: {OUTPUT_ROOT}/indexes/exclusion-ledger.md.
Related verdicts: {OUTPUT_ROOT}/experiments/**/VERDICT.md whose `topics` overlap HYPOTHESIS topics.
```
Return values: `done` · `under-specified` · `needs-research`.

## Phase 2 — Handle the return
- `under-specified` ⇒ `python -m lab.tools.state set {THREAD} --by /qml-screen --stage intake`;
  tell the user the question the screen needs answered; stop.
- `needs-research` (C12 I4) ⇒ run `/qml-deep-research` with the question in
  `{THREAD}/00_inputs/research_request.md` (`--return-to {THREAD}`); record the report path in
  SCREEN.md frontmatter `deep_research`; re-run Phase 1 once. A second `needs-research` ⇒ ASK-HUMAN.
- `done` ⇒ Phase 3.

## Phase 3 — Check and open CP1
1. `python -m lab.tools.validate artifact {THREAD}/SCREEN.md` must pass (G0 section present).
2. Hand back to `/qml-lab`, which opens **CP1** with author `agent:screen-analyst` and a brief whose
   recommendation is the verdict. On CP1 approval: PASS / PASS-NARROWED ⇒ stage `prereg`;
   KILLED-ON-PAPER ⇒ stage `variants` (then promote — the mechanism is a ledger entry);
   ASK-HUMAN ⇒ the signer's note decides.

## Completion message
```text
QML-SCREEN — <verdict> — <thread>
Decisive rules: <…> · Ledger entries engaged: <n>
Narrowest licensed claim / mechanism: <one line>
CP1 opened — waiting for <people> — brief: <path>
```
