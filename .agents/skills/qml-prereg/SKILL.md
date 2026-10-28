---
name: qml-prereg
version: 0.1.0
description: |
  QML Lab pre-registration. After CP1 approves a PASS / PASS-NARROWED screen, writes PROPOSAL.md
  (a short plan: what the result decides, experiments in cheapest-fatal order with why / expect /
  if it fails / cost, shared setup, classical baselines, budget), one experiments/E<k>_<slug>.md per
  phase (design, plain-language decision rules, verdict sentences, that phase's lock blocks),
  00_operating_point.md (with the P0 resource count) and frozen_definitions.md; runs review-panel
  pass 1; opens CP2 (freeze). On CP2 approval /qml-lab freezes PREREG.lock.json. Normally invoked
  by `/qml-lab next`.

triggers:
  - qml-prereg
  - write the pre-registration for this program

input:
  - "<thread>"

output:
  - "{THREAD}/PROPOSAL.md, experiments/E<k>_<slug>.md, 00_operating_point.md, frozen_definitions.md"
  - "{THREAD}/PANEL_1.md (via /qml-review-panel)"
  - "PREREG.lock.json is written only at freeze (CP2 approval), by lab.tools.lock"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash]
---

# /qml-prereg

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/experiment-designer/`,
`lab/roles/classical-competitor-champion/` (spec mode) · **Templates:** `artifacts/lab/templates/{PROPOSAL,EXPERIMENT}.md`

## Setup
```
python -m lab.tools.state check {THREAD} --need cp:CP1
python -m lab.tools.state check {THREAD} --need stage:prereg
Read SCREEN.md frontmatter: verdict must be PASS or PASS-NARROWED
```

## Phase 1 — Design draft
Spawn `experiment-designer`:
```
Task: write the pre-registration for {THREAD} — PROPOSAL.md (the plan, from the template), one
experiments/E<k>_<slug>.md per phase (from EXPERIMENT.md), 00_operating_point.md,
frozen_definitions.md. Every threshold, split, stop rule, gray zone and the baseline adequacy bar
goes in a ```lock block (id, kind, text; op/value where the gate is numeric): a phase's blocks in
its experiment doc, program-level blocks in the plan. Leave the classical rows of the models
tables to the classical competitor champion. Write for a reader outside the field (lab/STYLE.md).
```
**Gate:** `python -m lab.tools.lock show {THREAD}` lists ≥ 1 block of each kind threshold, split,
stop_rule; every planned phase has a stop_rule and a gray_zone.

## Phase 2 — Classical baselines
Spawn `classical-competitor-champion` in **spec mode** on the draft. **Gate:** classical rows of the models tables filled;
`competitor_rationale` covers every Rule 1 checklist item; twin row present (built or "settled on
paper" with reason); `baseline.adequacy` lock block present; classical budget rows filled.

## Phase 3 — Budget and phases into STATE
For each planned phase: `python -m lab.tools.state budget {THREAD} --phase Pk --planned cpu_h=…,wall_days=…,tokens_m=…`;
`python -m lab.tools.state set {THREAD} --by /qml-prereg --phases P1,P2,…`.
**Gate:** every phase's peak memory, quantum and classical side, fits the local machine (lab_method §6); else revise.

## Phase 4 — Panel pass 1
Run `/qml-review-panel {thread} --pass 1`. If `PANEL_1.md` has BLOCKING issues: spawn a **fresh**
`experiment-designer` with `PANEL_1.md` to revise (log each change in `change_log.md` with the issue
number), then re-run the panel. Max 2 rounds; a second BLOCKED ⇒ `/qml-lab escalate {thread}
panel_blocked_twice --to adi`.

## Phase 5 — Hand to CP2
`python -m lab.tools.validate thread {THREAD}` must pass (plan and every experiment doc). `/qml-lab` opens **CP2**
(author `agent:experiment-designer`; the brief lists the gates in plain language, the operating
point, each panel BLOCKING issue and its resolution, and "physics-bearing thresholds: yes/no").
On approval `/qml-lab sign` freezes the lock and sets stage `run`.

## Completion message
```text
QML-PREREG — READY FOR FREEZE — <thread>
Phases: <P1…> · Lock blocks: <n> · Panel: <APPROVED | APPROVED-WITH-CHANGES> after <k> round(s)
Operating point: <one line> · Budget: <total cpu-h, wall-days>
CP2 opened — waiting for <people> — brief: <path>
```
