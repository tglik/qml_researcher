---
name: qml-ingest
version: 0.2.0
description: |
  The common ingest gate of the candidate backlog. For every candidate that a source added with
  `lab.tools.backlog add` and the gate has not finished: novelty check against the lab and arXiv
  (lab archivist, novelty mode), then a batch triage screen G0–G3, the seven-question advantage-potential
  profile and a value estimate (screen analyst, triage mode). Records results with `lab.tools.backlog score`; never picks or opens a
  program. Then writes a plain-language explainer page per candidate and changed direction (explainer),
  signed by a separate explanation checker. Then the portfolio step: direction scores (plausibility ×
  impact), the independence check with merge proposals, and candidate prerequisites that set the start
  order inside each direction. Run nightly, or after a source adds a batch.

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
  - "{OUTPUT_ROOT}/indexes/backlog/explainers/{candidates,directions}/<id>.md — explainer pages"
  - "{OUTPUT_ROOT}/indexes/backlog/directions.json (assessment), relations.json, candidates.jsonl (requires)"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash, WebFetch]
---

# /qml-ingest

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/lab-archivist/` (novelty mode),
`lab/roles/screen-analyst/` (triage mode), `lab/roles/explainer/`, `lab/roles/explanation-checker/` · **Design:** `docs/lab/components/C13_candidate_backlog.md`

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

## Phase 2 — Triage screen, potential profile and value
Batch the candidates that are not `prior_exists` (≤ 10 per spawn). Spawn a **fresh** `screen-analyst`
in **triage mode** (never the instance that wrote or checked the candidate):
```
Task: triage-screen these backlog candidates per the triage mode of your PROTOCOL: <CID: title — claim>…
```
Record per candidate:
```
python -m lab.tools.backlog score <CID> --gate screen --verdict pass|narrowed|killed --gates G1,G3 --note "…"
python -m lab.tools.backlog score <CID> --gate potential --answers m,b,w,e,k,o,a --evidence-class none|heuristic|stage1|stage2 --note "…"
python -m lab.tools.backlog score <CID> --gate value --rung N --p P --note "…"
```
The potential answers are the seven questions of `criteria/advantage_potential.md`, in its order,
each 0 / 1 / 2. They are recorded for calibration (`backlog report`); they are not part of the gate
decision or the rank.
For each candidate that returns a bet sheet (step 6 of triage mode), save it to
`{OUTPUT_ROOT}/indexes/backlog/bet_sheets/<CID>.json` and record it:
```
python -m lab.tools.backlog bet <CID> --sheet {OUTPUT_ROOT}/indexes/backlog/bet_sheets/<CID>.json --by screen-analyst
```
Upside 4–5 puts the candidate in the bets lane; below 4 it goes to the steps lane (C14). If the
multi-model panel has run (`lab.tools.panel`), import its scores before Phase 5:
`python -m lab.tools.backlog panel <panel out>/scores.jsonl`. Panel medians replace the single
agent's rung, p and upside; a champion or a split panel marks a bet contested.
**Gate:** `killed` only with a 🔴 rule and its mechanism in the note; anything 🟠 is `pass` or
`narrowed`. Every candidate has a potential record and a value record; every rung 4 or 6 candidate
has a bet sheet.

## Phase 3 — Log
Write `{OUTPUT_ROOT}/indexes/backlog/gate_runs/<YYYY-MM-DD>.md`: one line per candidate —
id · novelty (score, evidence) · screen (verdict, deciding gate) · potential (total of 14, evidence
class, weakest answer) · value (rung × p). Then print
`python -m lab.tools.backlog queue`. Commit both backlog files and the log in `{OUTPUT_ROOT}` (phase 4 commits the explainers after it).

## Phase 4 — Explain
The team reads the backlog as a site (overview plus one page per direction and candidate,
rendered by `scripts/render_backlog.py` in qml_artifacts). Each page comes from an explainer file.
```
python -m lab.tools.backlog explain-status     # missing / stale / draft pages: the work list
```
Batch the listed entities: at most 6 candidates of one direction, or at most 3 directions, per spawn.
Killed candidates get a page too; their "Why quantum, honestly" is the kill reason.
1. Spawn a **fresh** `explainer` per batch:
   ```
   Task: write explainer pages for <ids> per your PROTOCOL. OUTPUT_ROOT=<path>.
   ```
2. Then a **fresh** `explanation-checker` per batch (never the instance that wrote it):
   ```
   Task: check and sign or return the explainer pages for <ids> per your PROTOCOL. OUTPUT_ROOT=<path>.
   ```
3. Returned pages: one more explainer round with the checker's notes, then one more check. A page
   still failing stays `draft` and the site shows it with a draft badge.

**Gate:** `python -m lab.tools.backlog validate --explainers` passes, and `explain-status` lists no
missing or stale entity. Drafts are allowed and reported.

## Phase 5 — Portfolio: direction score, independence, start order
The team funds one direction at a time; the page ranks directions by score. Run when a direction or any
of its candidates changed this run, and on every direction that has no `assessment`.
Spawn a **fresh** `screen-analyst` in **portfolio mode** with the directions, their candidates' gate
records and `python -m lab.tools.backlog independence`. Record what it returns:
```
python -m lab.tools.backlog direction score <ID> --plausibility P --impact I --confidence low|medium|high \
       --plausibility-note "… cites c-… / arXiv:… / experiments/…" --impact-note "…" --by screen-analyst
python -m lab.tools.backlog relate <A> <B> --kind dependent|overlap|shared-tooling|independent \
       --proposal merge|move|keep [--into ID] [--move CID:DIR …] --evidence c-… --note "…"
python -m lab.tools.backlog require <CID> --on <CID2> --why "…"
python -m lab.tools.backlog direction edit <ID> --summary "what it is, one sentence" \
       --payoff "what we have if it works, one sentence" \
       --target "the algorithm of ours this direction builds toward, one or two sentences" --reason "…"
python -m lab.tools.backlog path <CID> --off --why "why it is no step toward our own algorithm"   # or --on
python -m lab.tools.backlog direction rank && python -m lab.tools.backlog order
```
Candidates sit in two lanes (C14, `docs/lab/components/C14_lanes.md`): steps are banded A/B/C by
rung × p × (0.5 + novelty); bets are ordered by sheet, champion, upside and the cost of their fatal
test, never by p. `direction rank` shows each score with an error bar from its confidence and marks
ties; inside a tie the direction with the cheapest decisive bet test goes first.
Score = plausibility × impact. Plausibility is the chance the direction's thesis holds at its target
rung before its close criteria fire; impact is the 1–5 scale in `lab/tools/backlog.py` (`IMPACT`),
which measures progress toward an algorithm we own (Tsahi, 2026-11-20): each direction is a chain of
small publishable steps toward a method that becomes our IP. Refuting or reproducing other people's
work can be publishable, but it is impact 1. A direction with no target algorithm caps at impact 2.
A candidate whose only result is about someone else's method (a refutation, a crossover estimate for
an algorithm we would not own) is marked off path: it stays in the backlog, but leaves the start order.
A `dependent` pair is not two directions: it gets `merge` or `move`, never `keep`. Relations are
always recorded `proposed`; merging or moving candidates is a human decision, applied by editing the
backlog in a PR. Append a section to the run log.
The summary and payoff are the two lines the team reads in the overview table: plain words, no
jargon a non-specialist cannot follow, one sentence each (8–35 words, enforced), and the payoff as
candid as the score (say "a publishable negative" when that is the realistic win).
**Gate:** `validate` passes (it fails on a cross-direction `requires` with no relation, and on
requires cycles); every open direction has an assessment, a summary, a payoff and a target algorithm (or an impact ≤ 2
that says why it has none); every pair `independence` lists is judged.

## Failure modes to check
- Novelty scored from memory instead of a retrieved paper: every novelty note names what was
  searched and what was found.
- Gate drift by source: the same claim worded by two sources must get the same verdict.
- A kill on a 🟠 rule: that is the full screen's job, not triage's.
- A kill, or a lowered rank, justified by the potential profile alone: it is a recorded hypothesis
  until `backlog report` shows that it predicts outcomes.
- Treating the low-confidence rules as settled: a triage kill cites the rule *and* the evidence or
  precedent that decides it.
- An explainer that sells: a kill test or mechanism probe written up as a quantum-advantage story.
  The page states the real motivation; "a publishable negative" is a complete answer.
- A quantum case stronger than the potential profile allows (the lint enforces the caps).
- A direction score inflated by a kill-test direction's high plausibility: a likely negative is
  impact 1–2, whatever its plausibility.
- Impact credited for clearing the field: a refutation of someone else's method is impact 1 and off
  path, however publishable. Only steps toward our own target algorithm raise impact.
- Silent merges: the portfolio step proposes; it never changes a candidate's direction.
- Prerequisites invented to make an order look tidy: a `requires` must say what the earlier result
  decides for the later one.
