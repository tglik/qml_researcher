---
name: qml-lab
version: 0.1.0
description: |
  Entry point of the QML Lab — the experiment half of the researcher. Starts a program
  (algorithm or use-case), shows what is waiting and for whom, advances a program to its next
  allowed step, opens human checkpoints with one-page decision briefs, records sign-offs, raises
  escalations, and computes when a checkpoint may need less supervision. All other lab skills
  (/qml-screen, /qml-prereg, /qml-run, …) are normally reached through `/qml-lab next`.
  Read ESSENCE.md for what it is for; this file is the protocol.

triggers:
  - qml-lab
  - start a lab program
  - new experiment program
  - what is waiting for me in the lab
  - lab status
  - next step for program
  - sign checkpoint
  - approve the screen / freeze / verdict

input:
  - "new <thread> --owner <person> --path algorithm|use-case [--from <card or report path>]"
  - "status [<thread>]"
  - "next <thread>"
  - "sign <thread> <CP> --by <person> --decision approve|reject --outcome unchanged|minor|material --minutes N [--note …]"
  - "escalate <thread> <type> --to <person>"
  - "amend <thread>"
  - "stats"
  - "step-down <CP> --by tsahi"
  - "ledger-review"

output:
  - "{OUTPUT_ROOT}/experiments/<thread>/ — program folder, STATE.json, briefs/"
  - "{OUTPUT_ROOT}/indexes/autonomy-log.md — one row per human decision"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# /qml-lab

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/lab-director/` (the director runs in
this conversation; it does not spawn itself) · **Conventions:** `lab/README.md`

## Setup
```
Read config/workspace.json          → OUTPUT_ROOT
EXPERIMENTS = {OUTPUT_ROOT}/experiments
THREAD      = {EXPERIMENTS}/<thread>          # e.g. materials/14_feature_tolerance
Read lab/roles/lab-director/ESSENCE.md and PROTOCOL.md   (adopt them for this session)
Read config/lab_autonomy.json       → checkpoint modes
```
All state changes go through `python -m lab.tools.state` / `lab.tools.autonomy` (run from the
`qml_researcher` repo root). Never edit `STATE.json` by hand.

## `new <thread> --owner <p> --path algorithm|use-case [--from <path>]`
1. `<thread>` must be `<topic_thread>/<NN_short_name>`; NN = next free number in that thread
   (list `{EXPERIMENTS}/<topic_thread>/`). *Fail if* the folder exists.
2. In `{OUTPUT_ROOT}`: `git checkout -b lab/<topic_thread>-<NN_short_name>` from the default branch.
3. `python -m lab.tools.state new {THREAD} --owner <p> --path <path>`.
4. Put the input in `{THREAD}/00_inputs/` (copy the paper/notes/code, or write `source.md` linking
   the card/report given by `--from`).
5. Write `{THREAD}/README.md`: one paragraph — the input, owner, entry path, and "stage: intake".
6. Hand off: run `/qml-intake {thread}`.

## `status [<thread>]`
Without a thread: for every `{EXPERIMENTS}/*/*/STATE.json` print one row —
`thread · owner · stage · phase · open checkpoint (mode, waiting for) · budget % · open escalations`.
Then **Waiting for you** grouped by person (eligible signers of each open checkpoint = people ≠ author),
then the **Backlog** (C12 I5): `{OUTPUT_ROOT}/cards/hypotheses/*.md` with `strategic_value: actionable`
that no `HYPOTHESIS.md` names as `source_hypothesis_card`.
With a thread: `python -m lab.tools.state show {THREAD}` plus the path of the open brief.

## `next <thread>`
1. `python -m lab.tools.state validate {THREAD}`; read STATE.
2. Look up the stage machine in `lab/roles/lab-director/PROTOCOL.md`; check the precondition with
   `python -m lab.tools.state check {THREAD} --need …`. If it fails, print the refusal and stop.
3. **Open checkpoint?** If a checkpoint is open and its mode is `HUMAN_APPROVE`, print the brief
   path and who may sign; stop.
4. **Before a run phase:** decision-relevance — list the lock ids of this phase's gates
   (`python -m lab.tools.lock show {THREAD}`); if none, refuse ("no locked gate depends on this phase").
5. Invoke the next skill: `/qml-screen`, `/qml-prereg`, `/qml-review-panel --pass 2`, `/qml-run <phase>`,
   `/qml-verdict`, `/qml-audit`, `/qml-variants`, `/qml-promote`.
6. When that skill returns and its checkpoint is due, **open the checkpoint** (below).

## Opening a checkpoint
1. Write `{THREAD}/briefs/DECISION_BRIEF_<CP>_<n>.md` from `artifacts/lab/templates/DECISION_BRIEF.md`:
   ≤ 1 page, recommendation, 3–5 evidence bullets with links, cost to continue, options, the exact
   reply command, and **the human's job at this checkpoint**:
   CP1 "is this the right question; did G0 engage honestly?" · CP2 "right question, real operating
   point, defensible thresholds?" · CP3 "does the gate decision follow the pre-registered policy?" ·
   CP4 "does the verdict mean what it says; is any exclusion the narrowest one?" · CP5 "merge?".
2. `python -m lab.tools.state open-cp {THREAD} <CP> --author <agent:role|person:name> --brief briefs/…`
3. Mode from STATE: `HUMAN_APPROVE` → stop and tell the user who can sign.
   `HUMAN_SPOTCHECK` or `AGENT` → `python -m lab.tools.autonomy auto {THREAD} <CP> --decision <the
   brief's recommendation> --note "<one line>"` and continue. A sampled spot-check (rate in config;
   always for GO/CONDITIONAL-GO verdicts) shows under "Waiting for you" with a 48 h deadline; the
   reviewer records it with `python -m lab.tools.autonomy spotcheck {THREAD} <CP> --by <p> --outcome …
   --minutes N`. A material spot-check finding restores HUMAN_APPROVE for that checkpoint.
4. Under Hermes, also send the brief to the eligible signers (Slack DM) with the reply command.

## `sign …`
`python -m lab.tools.autonomy sign {THREAD} <CP> --by <p> --decision … --outcome … --minutes N --note …`
(enforces signer ≠ author, logs the autonomy row, restores supervision on a material finding).
Then: CP2 approve → `python -m lab.tools.lock freeze {THREAD} --by <p>` and
`python -m lab.tools.state set {THREAD} --by /qml-lab --stage run --frozen-question "<claim from HYPOTHESIS.md>"`.
Other approvals → advance `stage` per the stage machine. Reject → stage stays; the brief's
note goes to the responsible skill on its next run.
Outcome guidance for signers: **unchanged** — approved as written; **minor** — wording or small
fixes, no decision changed; **material** — a verdict, number, scope, gate, or framing changed.

## `escalate <thread> <type> --to <person>`
Types: `unplanned_failure`, `budget_2x`, `compute_request`, `apparent_advantage`, `blocked_twice`,
`panel_blocked_twice`, `signer_conflict`. Write a brief, then
`python -m lab.tools.state escalate {THREAD} --type <type> --to <p> --brief briefs/…`. Routing
(`lab/roles/lab-director/PROTOCOL.md`, docs C03): budget → adi + tsahi; compute → adi + tsahi;
apparent advantage → adi + tsahi; unplanned failure / blocked / panel → adi; literature gap → run
`/qml-deep-research` (C12 I4) instead of escalating.

## `amend <thread>`
For a post-freeze change: the designer edits the lock block(s) in `PROPOSAL.md` and adds an
Amendments row; a person ≠ designer approves; then
`python -m lab.tools.lock amend {THREAD} --touches <ids> --reason "…" --phase <P> --by <person>`
(refused automatically if that phase already has data).

## `stats` · `step-down` · `ledger-review`
- `python -m lab.tools.autonomy stats` — regenerates the stats table in `autonomy-log.md`.
- `python -m lab.tools.autonomy step-down <CP> --by tsahi` — only when stats says eligible; then
  open a PR for `config/lab_autonomy.json` in `qml_researcher`.
- `python -m lab.tools.ledger list` and print entries whose `review_by` is past, for a human to
  renew, reopen or retire (quarterly).

## Completion message
```text
QML-LAB — <subcommand> — <thread>
Stage: <stage> · Phase: <phase>
Open checkpoint: <CP> (<mode>) — waiting for <people> — brief: <path>
Escalations: <none | list>
Next: <exact next command>
```
