---
name: qml-verdict
version: 0.1.0
description: |
  QML Lab verdict. After review-panel pass 2, a fresh verdict-writer states the outcome against
  the frozen gates: GO · CONDITIONAL-GO · NO-GO-FINAL · NO-GO-PROVISIONAL · BLOCKED, with the
  mechanism, what it licenses, "not shown in range" vs "shown absent", and what survives.
  Writes VERDICT.md (its frontmatter is the experiment's graph entity). Then /qml-audit runs.

triggers:
  - qml-verdict
  - write the lab verdict for this program

input:
  - "<thread>"

output:
  - "{THREAD}/VERDICT.md"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash]
---

# /qml-verdict

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/verdict-writer/` ·
**Template:** `artifacts/lab/templates/VERDICT.md` · **Entity schema:** `artifacts/lab/experiment_entity_schema.md`

## Setup
```
python -m lab.tools.state check {THREAD} --need lock
python -m lab.tools.state check {THREAD} --need file:PANEL_2.md
PANEL_2.md verdict must not be BLOCKED
```

## Phase 1 — Write
Spawn a **fresh** `verdict-writer` (never an instance that designed, implemented or reviewed
this program):
```
Task: write {THREAD}/VERDICT.md per your PROTOCOL. Start from the pre-written verdict sentences
in PROPOSAL.md §6. Frontmatter per artifacts/lab/experiment_entity_schema.md with audit: pending.
```

## Phase 2 — Check
```
python -m lab.tools.validate entity   {THREAD}/VERDICT.md
python -m lab.tools.validate artifact {THREAD}/VERDICT.md
```
Every gate id in the lock appears in the gate-by-gate table (grep each id). Every number has a
file:line or provenance id.

## Phase 3 — Route
- Returned `apparent-advantage` (GO / CONDITIONAL-GO) ⇒ `/qml-lab escalate {thread} apparent_advantage --to adi`
  (and tsahi); the audit still runs.
- `python -m lab.tools.state set {THREAD} --by /qml-verdict --stage audit`; next is `/qml-audit`.

## Completion message
```text
QML-VERDICT — <category> — <thread>
Failed standards: <none | N1…> · Reopening condition: <…>
Next: /qml-audit (runs automatically via /qml-lab next)
```
