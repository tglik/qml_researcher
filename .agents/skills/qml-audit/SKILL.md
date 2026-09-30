---
name: qml-audit
version: 0.1.0
description: |
  QML Lab independent audit of a verdict. Fresh context, artifacts only, different model where
  available: mechanical lock diff, ≥2 recomputed numbers, a reproduction subset (one size per
  phase, the largest size, the classical baseline there), provenance sampling, fairness,
  the Negative Verdict Standard N1–N5, alternative explanations. Writes AUDIT.md:
  CONFIRMED · OVERTURNED · INSUFFICIENT. Then opens CP4 (verdict + audit). Local only.

triggers:
  - qml-audit
  - audit the lab verdict

input:
  - "<thread>"

output:
  - "{THREAD}/AUDIT.md, {THREAD}/audit/ (recomputation code and logs)"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash]
---

# /qml-audit

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/verdict-auditor/` ·
**Template:** `artifacts/lab/templates/AUDIT.md`

## Setup
```
python -m lab.tools.state check {THREAD} --need stage:audit
python -m lab.tools.state check {THREAD} --need file:VERDICT.md
AUDITOR_MODEL = a different model from the verdict-writer's if the runtime offers one
                (Claude Code: Agent(model=…); Hermes: the alternate provider); else same model, fresh context
```

## Phase 1 — Mechanical checks (run here, pasted into the auditor's task verbatim)
```
python -m lab.tools.lock verify {THREAD}        ; python -m lab.tools.lock diff {THREAD}
python -m lab.tools.provenance check {THREAD}
python -m lab.tools.splits verify {THREAD}
```

## Phase 2 — Audit
Spawn `verdict-auditor` on AUDITOR_MODEL with **only** the inputs listed in its PROTOCOL (paths),
plus the Phase 1 outputs:
```
Task: audit {THREAD} per your PROTOCOL. Write {THREAD}/AUDIT.md from the template and your
recomputation code/logs under {THREAD}/audit/. Record your model id in the frontmatter.
```
**Gate:** `python -m lab.tools.validate artifact {THREAD}/AUDIT.md`; the recomputed-numbers table
has ≥ 2 rows; the reproduction table covers every phase run.

## Phase 3 — Reflect into the verdict entity (mechanical only)
Set `audit: <result>` in `VERDICT.md` frontmatter and fill the N5 row — nothing else in the verdict
changes. If INSUFFICIENT and the verdict is NO-GO-FINAL: the category becomes NO-GO-PROVISIONAL with
the audit's reopening condition (the only verdict edit the audit may cause; log it in `change_log.md`).
OVERTURNED ⇒ `/qml-lab escalate {thread} unplanned_failure --to adi`; a fresh verdict-writer revises.

## Phase 4 — CP4
`python -m lab.tools.state set {THREAD} --by /qml-audit --stage variants` happens only after CP4.
`/qml-lab` opens **CP4** (author `agent:verdict-writer`; brief: category, audit result, failed
standards, and the proposed exclusion scope). GO/CONDITIONAL-GO verdicts are always reviewed by a
person, whatever the CP4 mode.

## Completion message
```text
QML-AUDIT — <CONFIRMED | OVERTURNED | INSUFFICIENT> — <thread>
Lock diff: <clean | n changes> · Recomputed: <k> agree / <m> · Reproduced: <…>
Standards failing: <none | …> · Verdict now: <category>
CP4 opened — waiting for <people> — brief: <path>
```
