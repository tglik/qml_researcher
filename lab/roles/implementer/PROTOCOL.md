# Implementer — protocol

## Invoked by
`/qml-run <thread> <phase>`. The slot may be filled by a person (typically Meir) with agent
assistance; the rules below bind either way.

## Inputs
`{THREAD}/STATE.json` · `PREREG.lock.json` · `PROPOSAL.md` (this phase's section and its lock
blocks) · `frozen_definitions.md` · `00_operating_point.md` · the classical arm's outputs for
this phase (produced by the twin champion) · `{OUTPUT_ROOT}/experiments/.venv`.

## Outputs (all under `{THREAD}/{phase}/`)
`src/` (quantum-arm and harness code) · `raw/` (per instance/seed/size, CSV/JSON/Parquet) ·
`figures/` · `RUN_LOG.md` · `provenance.json` · `results/gates.md` (via `lab.tools.gates`) ·
`PHASE_REPORT.md` (from template) · appended `{THREAD}/env.md` and `{THREAD}/change_log.md`.

## Steps
1. **Re-anchor.** Write the frozen question and this phase's gate ids at the top of `RUN_LOG.md`.
   `python -m lab.tools.lock verify {THREAD}` must pass.
2. **Environment & budget.** Record `env.md` (python, packages, hardware). If the thread has
   `data/fetch.py`, run it with `--verify`. Estimate memory for the largest size; *escalate* if over budget.
3. **Splits.** `python -m lab.tools.splits create|verify {THREAD}`; run the pre-registered leakage checks.
4. **Unit tests** on 2–4 qubit analytic cases; baseline sanity on small cases; exact vs finite-shot convergence.
5. **Dry run** at the smallest size; record time and memory.
6. **Full run.** Every material number recorded with `python -m lab.tools.provenance record …`.
   Deviations → `change_log.md`. Fallbacks only as pre-written.
7. **Gates.** `python -m lab.tools.gates {THREAD} {phase}` writes `results/gates.md`.
8. **Phase report** from the template: every number with a provenance id; gate-decision proposal.
9. **Close.** `python -m lab.tools.guard {THREAD}` (no protected file touched) and
   `python -m lab.tools.lock verify {THREAD}` must both pass.

## May not
Write `PREREG.lock.json`, `PROPOSAL.md`, `frozen_definitions.md`, `VERDICT.md`, `AUDIT.md` ·
put interpretation in `gates.md` · use the network during evaluation · spend beyond 2× the phase
budget without escalation.

## Return to the orchestrator
Gate table summary (pass/fail/blocked per gate) · gate-decision proposal · blockers with exact
commands · budget spent vs planned.
