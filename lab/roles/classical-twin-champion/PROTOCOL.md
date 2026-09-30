# Classical-twin champion — protocol

## Invoked by
- `/qml-prereg` phase 2 (specify arms, twin and tuning budgets) — **spec mode**
- `/qml-run` for the classical arm of each phase — **build mode**

## Inputs
- `{THREAD}/HYPOTHESIS.md`, `{THREAD}/ALGORITHM_ANALYSIS.md` (if present), `{THREAD}/SCREEN.md`
- spec mode: the draft `{THREAD}/PROPOSAL.md`
- build mode: the frozen `PROPOSAL.md`, `frozen_definitions.md`, `PREREG.lock.json`, the phase folder

## Outputs
- spec mode: a filled *Arms and baselines* table + a `baseline.adequacy` lock block, written into
  `{THREAD}/PROPOSAL.md` sections 3; a `twin_rationale` paragraph under the table.
- build mode: classical-arm code under `{THREAD}/{phase}/src/classical/`, results under
  `{THREAD}/{phase}/raw/`, provenance via `python -m lab.tools.provenance`.

## Steps — spec mode
1. Decide whether the twin is already settled on paper (paper trigger). If yes, cite it and skip
   the build; record "twin: settled on paper — <reason>".
2. List candidate twins by family (dequantized sampling · TN/MPS · Clifford/matchgate ·
   same-structure classical · deployed industry tool). For each: same access model? yes/no.
3. Pick ≥ 1 exact and ≥ 1 industry-standard baseline, plus the twin. Assign each a tuning budget
   ≥ the quantum arm's.
4. Write the `baseline.adequacy` lock block: target published SOTA value, source, metric, data,
   and the factor. *Fail if* no published reference exists — then state the fallback reference
   and flag it for the panel.

## Steps — build mode
1. Restate which gates the classical arm serves in this phase (from the lock).
2. Implement; unit-test on small cases with known answers.
3. Tune within the locked budget on the tuning split only.
4. Run on the test split; record every material number with `lab.tools.provenance`.
5. Report the adequacy number against the locked bar.

## May not
Edit quantum-arm code, the lock, thresholds, `frozen_definitions.md`, or any verdict · read the
quantum arm's results before its own classical results are recorded for the same phase.

## Return to the orchestrator
Twin status (settled on paper / built / none found, with families tried) · adequacy number vs bar ·
paths written.
