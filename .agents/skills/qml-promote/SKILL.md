---
name: qml-promote
version: 0.1.0
description: |
  QML Lab promotion (CP5). Finalizes the VERDICT.md entity frontmatter, appends a mechanism-scoped
  entry to the exclusion ledger, updates the experiment registry and the source hypothesis card's
  status, writes variant hypothesis cards, and proposes (never applies) criteria changes — all as
  one PR on the program branch in qml_artifacts, merged by a person. Normally invoked by `/qml-lab next`.

triggers:
  - qml-promote
  - promote this lab verdict

input:
  - "<thread>"

output:
  - "qml_artifacts: VERDICT.md frontmatter, indexes/exclusion-ledger.md, indexes/experiment-registry.md,"
  - "  cards/hypotheses/* (status + variants), indexes/hypothesis-ledger.md, {THREAD}/PROMOTE_PR.md"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash]
---

# /qml-promote

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/lab-archivist/` ·
**Schemas:** `artifacts/lab/experiment_entity_schema.md`, `artifacts/research_hypothesis_schema.md`

## Setup
```
python -m lab.tools.state check {THREAD} --need stage:promote
python -m lab.tools.state check {THREAD} --need file:VARIANTS.md
Precondition: CP4 approved, or CP1 approved with SCREEN.md verdict KILLED-ON-PAPER
In {OUTPUT_ROOT}: on the program branch (STATE.branch), up to date with the default branch
```

## Phase 1 — Archive
Spawn `lab-archivist`:
```
Task: promote {THREAD} per your PROTOCOL. Paper kills: the ledger entry comes from SCREEN.md's
mechanism; status provisional; audit legacy-human is NOT allowed — use INSUFFICIENT with the
reopening condition "an experiment showing the killing rule does not apply".
```

## Phase 2 — Checks
```
python -m lab.tools.validate entity {THREAD}/VERDICT.md          (not for paper kills)
python -m lab.tools.ledger validate
python -m lab.tools.check_sizes
```
Registry rows escape `\|` inside wiki-links; a hypothesis status never exceeds `observed` from one experiment.

## Phase 3 — PR and CP5
1. `git add` the changed vault files; commit on the program branch:
   `lab(<thread>): promote <verdict> — ledger <id>`.
2. Open a PR (gh) against the default branch with `{THREAD}/PROMOTE_PR.md` as the body. If the
   remote is unavailable, leave the branch and print the PR body.
3. `/qml-lab` opens **CP5** (permanent HUMAN_APPROVE) — the merge is the signature; record it with
   `/qml-lab sign {thread} CP5 --by <merger> …` after merging.
4. Proposed `criteria/qml_domain.md` / `criteria/lab_method.md` edits live in `qml_researcher`; the
   signer applies them there in a separate PR if accepted.
5. After CP5: `python -m lab.tools.state set {THREAD} --by /qml-promote --stage closed`.

## Completion message
```text
QML-PROMOTE — PR OPEN — <thread>
Ledger: <id> (<final | provisional>) · Hypothesis card: <slug> <from> → <to> | none
Variant cards: <n> · Criteria proposals: <n>
CP5: merge <PR url> and sign
```
