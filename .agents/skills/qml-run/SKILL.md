---
name: qml-run
version: 0.1.0
description: |
  QML Lab execution of one frozen phase (P1 toy · P2 medium · P3 real data + industrial scale ·
  P4 noise · P5 hardware plan, modeling only in V1). Classical arm by the twin champion, quantum
  arm and harness by the implementer; every material number recorded with provenance; gates
  computed by lab.tools.gates from the lock; phase report; guard + lock checks; opens CP3.
  Local only. Normally invoked by `/qml-lab next`. Not available in Slack.

triggers:
  - qml-run
  - run phase P1 / P2 / P3 / P4 / P5 of this program

input:
  - "<thread> <phase>"

output:
  - "{THREAD}/<Pk_dir>/src, raw, figures, RUN_LOG.md, provenance.json, results/gates.md, PHASE_REPORT.md"

allowed-tools: [Agent, Read, Write, Edit, Glob, Grep, Bash]
---

# /qml-run

**Essence:** [ESSENCE.md](ESSENCE.md) · **Roles:** `lab/roles/implementer/`,
`lab/roles/classical-twin-champion/` (build mode) · **Templates:** `PHASE_REPORT.md`, `gates.md`
Phase folders: P1 → `P1_toy/`, P2 → `P2_medium/`, P3 → `P3_real/`, P4 → `P4_noise/`, P5 → `P5_hardware/`.

## Setup
```
python -m lab.tools.state check {THREAD} --need lock            # frozen and unchanged
python -m lab.tools.state check {THREAD} --need stage:run
previous phase (if any): python -m lab.tools.state check {THREAD} --need cp:CP3:<prev>
python -m lab.tools.state set {THREAD} --by /qml-run --phase <Pk>     # records the start commit
Environment: {OUTPUT_ROOT}/experiments/.venv (create from experiments/requirements.txt if missing)
```
Reuse: `/qml-experiments` rerun mechanics for re-running an earlier phase's command.

## Phase 1 — Re-anchor (decision relevance)
List this phase's lock ids (`python -m lab.tools.lock show {THREAD}` filtered by `<Pk>.`). If none,
stop: "no locked gate depends on <Pk>". Write the frozen question + gate ids at the top of
`<Pk_dir>/RUN_LOG.md`.

## Phase 2 — Classical arm first
Spawn `classical-twin-champion` in **build mode** for this phase. **Gate:** classical results and
the adequacy number recorded with provenance before the quantum arm runs.

## Phase 3 — Quantum arm and harness
Spawn `implementer` (or, when Meir fills the slot, work with him under the same PROTOCOL):
```
Task: execute phase <Pk> of {THREAD} per PROPOSAL.md §5 and your PROTOCOL. Record every material
number with python -m lab.tools.provenance record. Write <Pk_dir>/results/measured.json keyed by
lock id. Then python -m lab.tools.gates {THREAD} <Pk>, then PHASE_REPORT.md from the template.
```
Budget: after each major step `python -m lab.tools.state spend {THREAD} --phase <Pk> cpu_h=…`; a
`budget_2x` error ⇒ stop and `/qml-lab escalate {thread} budget_2x --to adi`.
BLOCKED ⇒ `python -m lab.tools.state block {THREAD} --what … --command …`; second BLOCKED on the
same phase ⇒ escalate `blocked_twice`.

## Phase 4 — Checks
All must pass:
```
python -m lab.tools.guard {THREAD}
python -m lab.tools.lock verify {THREAD}
python -m lab.tools.provenance check {THREAD}
python -m lab.tools.splits verify {THREAD}
python -m lab.tools.validate artifact {THREAD}/<Pk_dir>/PHASE_REPORT.md
python -m lab.tools.check_sizes
```
A guard failure is never "fixed" by the implementer — it goes to `/qml-lab escalate … unplanned_failure`.

## Phase 5 — Hand to CP3
`/qml-lab` opens **CP3** (author `agent:implementer` or `person:<name>`) with the gate table and
the proposal: PROCEED (all key hypotheses confirmed) · STOP-PREREGISTERED (a locked stop rule
fired — stage `panel2`) · ESCALATE (anything else).

## Completion message
```text
QML-RUN — <Pk> — <PROCEED | STOP-PREREGISTERED | ESCALATE | BLOCKED> — <thread>
Gates: <n pass / m fail / k blocked> · Budget: <spent> of <planned>
Checks: guard ✓ lock ✓ provenance ✓ splits ✓ sizes ✓
CP3 opened — waiting for <people> — brief: <path>
```
