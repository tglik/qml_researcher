---
name: qml-open-problems
version: 0.1.0
description: |
  Source B of the candidate backlog. Mines open questions — the team's open-questions notes, the
  Limitations / Open Questions / Follow-up Actions sections of fully reviewed paper cards, and the
  open-problems sections of recent reviews — and turns each into up to 3 testable claims added with
  `lab.tools.backlog add --source B`. Weekly.

triggers:
  - qml-open-problems
  - mine open problems
  - turn open questions into candidates

input:
  - "[--from <notes file>] [--cards all|<glob>]"

output:
  - "{OUTPUT_ROOT}/indexes/backlog/candidates.jsonl — new rows (source B)"
  - "{OUTPUT_ROOT}/indexes/backlog/open_problems_<date>.md — every question and what became of it"

allowed-tools: [Read, Glob, Grep, Bash, WebFetch, WebSearch]
---

# /qml-open-problems

**Essence:** [ESSENCE.md](ESSENCE.md) · runs in this conversation (no spawn) ·
**Design:** `docs/lab/components/C13_candidate_backlog.md`

## Phase 1 — Collect
Read, in order: the notes file given by `--from` (default: the team's `open_questions.md` in the
vault, read-only); the Limitations, Open Questions and Follow-up Actions of every paper card that is
not a stub (`grep -L "report-level extraction" {OUTPUT_ROOT}/cards/paper-cards/*.md`); the open
questions of each hypothesis card. One row per question in the log, with its source.
**Gate:** every question has a source line.

## Phase 2 — Sharpen
Per question: still open? (one search; if answered, name the paper and stop). Otherwise write up to
3 claims, each with model family, size, baseline and measurement, the direction it serves (or
"new direction: <name>"), and the rung it aims at.
**Gate:** every claim is ≥ 8 words and names a baseline and a size.

## Phase 3 — Add
`python -m lab.tools.backlog add --source B --base "<question source>" --direction <ID> --region <R> --title "…" --claim "…"`
Write the log; it records questions that produced nothing, and why.

## Failure modes to check
- A claim that is the question with a question mark removed.
- Treating a question as open without one search.
