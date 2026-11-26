---
name: qml-study
version: 0.1.0
description: |
  QML Lab small study (C16): one falsifiable claim from the lab agenda, run in hours by one author
  agent in the shared workspace. Announce, get one peer critique before running, lock the plan,
  run, bind every number to a file in the ledger, run major objections as scripts, clean-context
  code audit, release a frozen bundle. No human checkpoint before release; a person reads the
  debrief. Use for "run the next study", "start a study on <candidate>", or the pilot lab.
triggers:
  - qml-study
  - run the next study
  - start a study
input:
  - "optional: a candidate id on the lab agenda (default: the next one)"
output:
  - "{OUTPUT_ROOT}/workspace/studies/<sid>/ (STUDY.md, code/, outputs/, ledger, AUDIT.md, frozen bundle)"
  - "{OUTPUT_ROOT}/workspace/log/ posts (announce, critique, response, correction, result)"
allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash]
---

# /qml-study

**Essence:** [ESSENCE.md](ESSENCE.md) · **Design:** `docs/lab/components/C16_study_workspace.md` ·
**Roles:** `lab/roles/implementer/` (author), `lab/roles/review-panel/` (critic, objections),
`lab/roles/verdict-auditor/` (audit) · **Template:** `artifacts/lab/templates/STUDY_AUDIT.md`

`WS = python -m lab.tools.workspace`. Every state change goes through `WS`; the lab guard hook
blocks hand edits to the log, the ledger, the state and any released study.

**Names.** The author is `author-<sid>`. The critic, objector and auditor are separate subagents
on fresh contexts, named `critic-<sid>`, `objector-<sid>`, `auditor-<sid>`. Where a different
model family is available (GPT via Codex on the Mac, see C15), use it for the critic and the
auditor and add the family to the name, e.g. `critic-gpt-<sid>`.

**Budget.** `lab.json` sets `budget.max_hours` and `budget.max_usd` per study. If a study will
exceed either, stop, post a `result` saying what was learned so far, and release it as `null` or
`mixed` if the audit passes; otherwise leave it locked and post a `note`. Never raise the budget.

**What the author never reads while designing:** `indexes/backlog/panel/`, candidate gate scores,
direction scores, the queue, or other studies' outcomes ranked against each other. Read other
studies' posts and bundles for methods and pitfalls, not for which design is winning.

## Phase 0 — Read the room (author)
```
WS read --last 50                 # what earlier studies found, corrected and warned about
WS next                           # or the candidate the person named; it must be on the agenda
WS new --from <CID> --by author-<sid>     # prints the new study id; use it below
```
Read the source candidate's base card and any released study on the same direction.
**Gate:** the candidate is on the agenda and has no study in progress (the tool refuses otherwise).

## Phase 1 — Design and announce (author)
Fill `STUDY.md`: Prediction (a number at a named operating point), Disproof (written now), Plan
(cheapest fatal step first, the classical baseline and its tuning budget), Budget. For a bet, the
study is the bet sheet's fatal test, not the full claim.
```
WS post announce --study <sid> --by author-<sid> --body-file <short announce: claim, prediction, disproof, plan, budget>
```
**Gate:** Prediction, Disproof and Plan are no longer template text.

## Phase 2 — Critique before running (critic subagent, fresh context)
Spawn the critic with only `STUDY.md`, the announce post and the five QML criteria
(`criteria/qml_domain.md`). Its task: find the one or two flaws most likely to make the result
wrong or uninformative (weak or untuned baseline, leakage, wrong operating point, a control that
does not control, dequantization, a prediction that cannot fail), each with the concrete change
that fixes it. It posts:
```
WS post critique --study <sid> --by critic-<sid> --body-file <critique>
```
The author decides, edits `STUDY.md` if it agrees, and answers every point:
```
WS post response --study <sid> --by author-<sid> --changed yes|no --body-file <response>
WS lock <sid> --by author-<sid>
```
**Gate:** `lock` succeeds (announce, a critique from another agent, a response).

## Phase 3 — Run and bind (author, implementer role)
Write code under `code/`, outputs under `outputs/`. Simulation only; seeds fixed and recorded.
Every number that will appear in the result goes into the ledger before it is written in prose:
```
WS ledger <sid> --id <name> --value <v> --file outputs/<file> --command "<exact command>"
```
If an early result turns out wrong (a bug, an untuned baseline), say so at once:
`WS post correction …`. A plan change after lock needs a correction, then the edit, then
`WS amend <sid> --by author-<sid> --reason "…"` — and only before any number is in the ledger.
**Gate:** every planned number is in the ledger.

## Phase 4 — Objections as code (objector subagent, fresh context)
Give the objector `STUDY.md`, `code/`, `outputs/` and the ledger. Its task: write at most three
major objections, each as a runnable script `objections/<name>.py` that tests it on the deposited
outputs or reruns a small variant (stronger baseline, other seeds, a missing control). It runs
each and records whether the headline result flips:
```
WS objection <sid> --script objections/<name>.py --by objector-<sid> --flips yes|no --note "<one line>"
```
An objection that cannot be written as code is posted as a `note`, not recorded as an objection.
If one flips the result, the author posts a `correction` and reports the corrected result.

## Phase 5 — Audit (auditor subagent, fresh context, different family if available)
The auditor reads the code line by line against the claim, recomputes at least two ledger numbers
from the files, and checks the prose against the numbers. It writes `AUDIT.md` from
`artifacts/lab/templates/STUDY_AUDIT.md` with `auditor:` and `verdict: PASS|FAIL` in frontmatter.
**Gate:** `verdict: PASS`. A FAIL is posted as a correction; the study stays locked.

## Phase 6 — Result and release (author)
```
WS post result --study <sid> --by author-<sid> --body-file <result>
WS release <sid> --by author-<sid> --outcome supported|refuted|null|mixed [--cost-usd <x>]
```
Then, one post each, what the study taught about the domain (physics, theory, method; never the
lab process) and the follow-ups or what-ifs it raised, each with its honest prior and novelty status:
```
WS post learning --study <sid> --by author-<sid> --body-file <one learning, bold one-line headline first>
WS post idea --study <sid> --by author-<sid> --body-file <one idea>
```
Each idea that states a testable claim (not tooling) then goes into the backlog with the study as
its source, and waits for the next `/qml-ingest` like any other candidate:
```
python -m lab.tools.backlog add --source S --base "study:<sid>" --title "<idea headline>" \
    --claim "<what, against which baseline, at what size>" --direction <direction> --by author-<sid>
```
The result post states the outcome, the ledger numbers it rests on, what it does and does not
show, and what it means for the source candidate (next step, kill, or narrow). Pass `--cost-usd`
when the runtime reports spend. Then feed the verdict into the backlog (C17,
`docs/lab/components/C17_learning_updates.md`): rules, not a score formula.
```
python -m lab.tools.backlog learn <sid>        # closes the candidate; a refutation is a strike on its line
```
`learn` prints the siblings and the direction that now have a review due. The next `/qml-ingest`
portfolio step records them (`backlog review`, `direction score`). Then the lab's agenda is
re-derived, and a person applies it:
```
python -m lab.tools.workspace agenda           # derived order vs lab.json; --apply --by <person> --reason …
```
Then commit the study folder, the new log posts and the backlog changes in qml_artifacts on the lab
branch, and open or update the lab PR.

## Debrief (person + agent, after each batch the lab sets)
```
WS report
```
Read with the person: how often critique changed a design, objections that flipped a result,
corrections, audit failures, hours and cost per study, and, for each released study, whether it
moved its direction toward an algorithm we would own. Changes to this skill come from the debrief.

## Failure modes to check
- A baseline tuned less than the quantum arm (the most common flip in the source study).
- Prose that turns "not significant" into "no effect".
- A verifier or scorer that reads the answer; a prompt or input that leaks the target.
- Failed runs silently retried or overwritten.
- Simulating at a size where the classical arm is trivially exact, then claiming a regime.
- Hash or number retyped from memory instead of pasted from tool output.
