---
name: qml-variants
version: 0.1.0
description: |
  QML Lab variant mining and pivot analysis after a verdict (or a paper kill): mechanism
  inversion, one-axis relaxation, salvage (classical results / instruments / quantum variants),
  Adi's pivot questions, paper and IP flags. ≤ 5 pre-screened variants. Writes VARIANTS.md.
  Normally invoked by `/qml-lab next`.

triggers:
  - qml-variants
  - mine variants from this verdict

input:
  - "<thread>"

output:
  - "{THREAD}/VARIANTS.md"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash]
---

# /qml-variants

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/variant-generator/` ·
**Template:** `artifacts/lab/templates/VARIANTS.md`

## Setup
```
Either: python -m lab.tools.state check {THREAD} --need cp:CP4
Or (paper kill): cp:CP1 approved and SCREEN.md verdict KILLED-ON-PAPER
```

## Phase 1 — Generate
Spawn `variant-generator`:
```
Task: write {THREAD}/VARIANTS.md per your PROTOCOL. Mechanism source: VERDICT.md + AUDIT.md
(or SCREEN.md for a paper kill). Ledger: {OUTPUT_ROOT}/indexes/exclusion-ledger.md.
```

## Phase 2 — Check
`python -m lab.tools.validate artifact {THREAD}/VARIANTS.md`; ≤ 5 variant rows; every row has a
newly-passes and a newly-faces gate; the disclosure warning is present verbatim.

## Phase 3 — Route
`python -m lab.tools.state set {THREAD} --by /qml-variants --stage promote`. If the recommendation
is `ip-first`, add a line to the CP5 brief so the promotion PR is not merged publicly before a
decision on filing.

## Completion message
```text
QML-VARIANTS — <recommendation> — <thread>
Variants: <n> (top: <one line>) · Covered cases: <k> · Salvage: <a/b counts>
Next: /qml-promote
```
