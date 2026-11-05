---
name: qml-ingest
version: 0.1.0
description: |
  The common ingest gate of the candidate backlog. For every candidate that a source added with
  `lab.tools.backlog add` and the gate has not finished: novelty check against the lab and arXiv
  (lab archivist, novelty mode), then a batch triage screen G0–G3 plus a value estimate (screen
  analyst, triage mode). Records results with `lab.tools.backlog score`; never picks or opens a
  program. Run nightly, or after a source adds a batch.

triggers:
  - qml-ingest
  - run the ingest gate
  - gate the backlog
  - score new candidates

input:
  - "[--limit N]   (default: all pending candidates)"

output:
  - "{OUTPUT_ROOT}/indexes/backlog/candidates.jsonl — gate fields filled"
  - "{OUTPUT_ROOT}/indexes/backlog/gate_runs/<date>.md — one line per candidate with evidence"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash, WebFetch]
---

# /qml-ingest

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/lab-archivist/` (novelty mode),
`lab/roles/screen-analyst/` (triage mode) · **Design:** `docs/lab/components/C13_candidate_backlog.md`

Sources (A build on a base, B open problems, C combination grid, D programmatic search, E scout /
algorithms / variants) only `add`. This skill only `score`s. The portfolio decision (pick, open,
close a direction) stays with a human.

## Setup
```
Read config/workspace.json → OUTPUT_ROOT
python -m lab.tools.backlog validate
python -m lab.tools.backlog pending          # the work list; stop if empty
```

## Phase 1 — Novelty (dedupe already ran at `add`)
For each pending candidate, spawn a **fresh** `lab-archivist` in **novelty mode**:
```
Task: novelty check for backlog candidate <CID>: "<title>" — <claim>. Base: <base>.
Per the novelty mode of your PROTOCOL. Return score, prior_exists, evidence ids, note.
```
Record: `python -m lab.tools.backlog score <CID> --gate novelty --score S [--prior-exists] --evidence <ids> --note "…"`
**Gate:** every pending candidate has a novelty record; `--prior-exists` only with an arXiv id that
states the same claim at the same or larger scope.

## Phase 2 — Triage screen and value
Batch the candidates that are not `prior_exists` (≤ 10 per spawn). Spawn a **fresh** `screen-analyst`
in **triage mode** (never the instance that wrote or checked the candidate):
```
Task: triage-screen these backlog candidates per the triage mode of your PROTOCOL: <CID: title — claim>…
```
Record per candidate:
```
python -m lab.tools.backlog score <CID> --gate screen --verdict pass|narrowed|killed --gates G1,G3 --note "…"
python -m lab.tools.backlog score <CID> --gate value --rung N --p P --note "…"
```
**Gate:** `killed` only with a 🔴 rule and its mechanism in the note; anything 🟠 is `pass` or
`narrowed`. Every candidate has a value record.

## Phase 3 — Log
Write `{OUTPUT_ROOT}/indexes/backlog/gate_runs/<YYYY-MM-DD>.md`: one line per candidate —
id · novelty (score, evidence) · screen (verdict, deciding gate) · value (rung × p). Then print
`python -m lab.tools.backlog queue`. Commit both backlog files and the log in `{OUTPUT_ROOT}`.

## Failure modes to check
- Novelty scored from memory instead of a retrieved paper: every novelty note names what was
  searched and what was found.
- Gate drift by source: the same claim worded by two sources must get the same verdict.
- A kill on a 🟠 rule: that is the full screen's job, not triage's.
- Treating the low-confidence rules as settled: a triage kill cites the rule *and* the evidence or
  precedent that decides it.
