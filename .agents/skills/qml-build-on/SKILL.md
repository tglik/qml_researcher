---
name: qml-build-on
version: 0.1.0
description: |
  Source A of the candidate backlog. Given a base — a paper card, a hypothesis card, or one of our
  own verdicts — proposes up to 5 next steps (stress-test, extend, combine, generalize), each a
  testable claim, and adds them to the backlog with `lab.tools.backlog add --source A`. Run when
  paper review writes a STRONG_INTEREST card, and weekly over the open directions' base papers.

triggers:
  - qml-build-on
  - build on this paper
  - next steps from this result

input:
  - "<base: paper card path | hypothesis card path | experiment thread> [--direction ID]"

output:
  - "{OUTPUT_ROOT}/indexes/backlog/candidates.jsonl — up to 5 new rows (source A)"

allowed-tools: [Agent, Read, Glob, Grep, Bash, WebFetch]
---

# /qml-build-on

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/variant-generator/` (build-on mode) ·
**Design:** `docs/lab/components/C13_candidate_backlog.md`

## Setup
```
Read config/workspace.json → OUTPUT_ROOT
python -m lab.tools.backlog direction list      # pick the direction the base belongs to, if any
```
If the base is a stub card (its Limitations say "report-level extraction"), read the paper itself
first (`/fetch-arxiv`), and say so in each candidate's base field.

## Phase 1 — Generate
Spawn `variant-generator` in **build-on mode**:
```
Task: propose up to 5 next steps on base <BASE> per the build-on mode of your PROTOCOL.
Direction: <ID or none>. Ledger: {OUTPUT_ROOT}/indexes/exclusion-ledger.md.
```
**Gate:** every step names its kind (stress-test | extend | combine | generalize), its rung (1–6),
and the deciding experiment; none restates the base's own result.

## Phase 2 — Add
For each step:
`python -m lab.tools.backlog add --source A --base "<base id>" --direction <ID> --region <R> --title "…" --claim "…"`
A duplicate refusal means the step exists already: drop it, do not `--force`.
Then run `/qml-ingest` (or leave the rows for the nightly gate).

## Failure modes to check
- A step whose claim a number could not contradict.
- Building on a stub card without reading the paper.
- Steps that only differ in dataset name: that is one step with a dataset sweep.
