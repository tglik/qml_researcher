---
name: qml-prereg
version: 0.1.0
description: |
  QML Lab pre-registration. After CP1 approves a PASS / PASS-NARROWED screen, writes PROPOSAL.md
  (hypotheses → experiments, arms incl. the classical twin, metrics, phases P1–P5 cheapest-fatal
  first, thresholds with gray-zone policies, both verdict sentences), 00_operating_point.md and
  frozen_definitions.md; runs review-panel pass 1; opens CP2 (freeze). On CP2 approval /qml-lab
  freezes PREREG.lock.json. Normally invoked by `/qml-lab next`.

triggers:
  - qml-prereg
  - write the pre-registration for this program

input:
  - "<thread>"

output:
  - "{THREAD}/PROPOSAL.md, 00_operating_point.md, frozen_definitions.md"
  - "{THREAD}/PANEL_1.md (via /qml-review-panel)"
  - "PREREG.lock.json is written only at freeze (CP2 approval), by lab.tools.lock"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash]
---

# /qml-prereg

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/experiment-designer/`,
`lab/roles/classical-twin-champion/` (spec mode) · **Template:** `artifacts/lab/templates/PROPOSAL.md`

## Setup
```
python -m lab.tools.state check {THREAD} --need cp:CP1
python -m lab.tools.state check {THREAD} --need stage:prereg
Read SCREEN.md frontmatter: verdict must be PASS or PASS-NARROWED
```

## Phase 1 — Design draft
Spawn `experiment-designer`:
```
Task: write the pre-registration for {THREAD} — PROPOSAL.md (from the template),
00_operating_point.md, frozen_definitions.md. Every threshold, split, stop rule, gray zone and the
baseline adequacy bar goes in a ```lock block (id, kind, text; op/value where the gate is numeric).
Leave section 3 (arms) with the rows to be filled by the twin champion.
```
**Gate:** `python -m lab.tools.lock show {THREAD}` lists ≥ 1 block of each kind threshold, split,
stop_rule; every planned phase has a stop_rule and a gray_zone.

## Phase 2 — Arms and baselines
Spawn `classical-twin-champion` in **spec mode** on the draft. **Gate:** arms table filled; twin
row present (built or "settled on paper" with reason); `baseline.adequacy` lock block present.

## Phase 3 — Budget and phases into STATE
For each planned phase: `python -m lab.tools.state budget {THREAD} --phase Pk --planned cpu_h=…,wall_days=…,tokens_m=…`;
`python -m lab.tools.state set {THREAD} --by /qml-prereg --phases P1,P2,…`.
**Gate:** every phase's peak memory fits the V1 envelope (local; lab_method §5); else revise.

## Phase 4 — Panel pass 1
Run `/qml-review-panel {thread} --pass 1`. If `PANEL_1.md` has BLOCKING issues: spawn a **fresh**
`experiment-designer` with `PANEL_1.md` to revise (log each change in `change_log.md` with the issue
number), then re-run the panel. Max 2 rounds; a second BLOCKED ⇒ `/qml-lab escalate {thread}
panel_blocked_twice --to adi`.

## Phase 5 — Hand to CP2
`python -m lab.tools.validate artifact {THREAD}/PROPOSAL.md` must pass. `/qml-lab` opens **CP2**
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
