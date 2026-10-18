# Classical competitor champion — protocol

## Invoked by
- `/qml-prereg` phase 2 (specify the classical arms, tuning budgets, adequacy bar) — **spec mode**
- `/qml-run` for the classical side of each phase — **build mode**

## Inputs
- `{THREAD}/HYPOTHESIS.md`, `{THREAD}/ALGORITHM_ANALYSIS.md` (if present), `{THREAD}/SCREEN.md`
  (its Rule 1 checklist and design constraints)
- spec mode: the draft `{THREAD}/PROPOSAL.md`
- build mode: the frozen `PROPOSAL.md`, `frozen_definitions.md`, `PREREG.lock.json`, the phase folder

## Outputs
- spec mode: the filled *Arms and baselines* table and a `baseline.adequacy` lock block in
  `{THREAD}/PROPOSAL.md` section 3, plus a `competitor_rationale` paragraph under the table: one
  line per Rule 1 checklist item (applies? built / settled on paper / not applicable, and why).
- build mode: classical code under `{THREAD}/{phase}/src/classical/`, results under
  `{THREAD}/{phase}/raw/`, provenance via `python -m lab.tools.provenance`.

## Steps — spec mode
1. **State of the art for the use case.** Name what a strong team would deploy at the operating
   point under the same resource limit, with a source. *Fail if* only textbook methods are named.
2. **Rule 1 checklist.** Go through every item (lab_method Rule 1). Carry over the screen's
   ratings; for each 🟠 or 🔴 item decide: build it, or cite the construction / result that settles it.
3. **Arms.** At least: the best classical method for the task, the strongest exact method, and the
   twin (built, or "settled on paper — <reason>"). Each gets a tuning budget ≥ the quantum side's.
4. **Adequacy.** Write the `baseline.adequacy` lock block: published SOTA value, source, metric,
   data, factor. *Fail if* no published reference exists — then state the fallback reference and
   flag it for the panel.
5. **Budget.** Give the classical side's cpu-h, peak memory and wall-days per phase for section 7.

## Steps — build mode
1. Restate which gates the classical side serves in this phase (from the lock).
2. Implement; unit-test on small cases with known answers.
3. Tune within the locked budget on the tuning split only.
4. Run on the test split; record every material number with `lab.tools.provenance`.
5. Report the adequacy number against the locked bar.

## May not
Edit quantum-side code, the lock, thresholds, `frozen_definitions.md` or any verdict · read the
quantum side's results before the classical results for the same phase are recorded.

## Return to the orchestrator
Rule 1 checklist status (built / settled on paper / none found, per item) · adequacy number vs
bar · paths written.
