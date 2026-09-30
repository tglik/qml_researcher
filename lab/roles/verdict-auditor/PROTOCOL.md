# Verdict auditor — protocol

## Invoked by
`/qml-audit`. Always a fresh context. Use a different model from the verdict-writer where the
runtime allows it (record which in `AUDIT.md` frontmatter).

## Inputs — artifacts only
`{THREAD}/VERDICT.md` · `{THREAD}/PREREG.lock.json` · `{THREAD}/PROPOSAL.md` ·
`{THREAD}/frozen_definitions.md` · every `{THREAD}/P*/results/gates.md` ·
every `{THREAD}/P*/provenance.json` · raw data under `{THREAD}/P*/raw/` · code under
`{THREAD}/P*/src/` · `{THREAD}/PANEL_2.md`.
**Not provided, not to be requested:** RUN_LOG prose, PHASE_REPORT interpretation sections,
chat transcripts, drafts.

## Output
`{THREAD}/AUDIT.md` from `artifacts/lab/templates/AUDIT.md`; own recomputation code under
`{THREAD}/audit/`.

## Steps
1. **Lock diff.** Run `python -m lab.tools.lock verify {THREAD}` and
   `python -m lab.tools.lock diff {THREAD}`; paste output verbatim. Any unexplained change ⇒ N2 fails.
2. **Recompute ≥ 2 headline numbers** from raw files with your own code in `{THREAD}/audit/`.
   Agreement within the reported CI, else record the discrepancy.
3. **Reproduce** ≥ 1 size per phase run, the largest size reached, and the classical baseline at
   that size, from stored code, environment and seeds (data re-created with `data/fetch.py --verify`
   where present). Log commands.
4. **Independent correctness** on a few instances with a different simulator or library.
5. **Provenance sample.** ≥ 5 material numbers traced to file + command.
6. **Fairness.** Baselines adequate and tuned with ≥ the quantum budget? Twin analysis held?
   Simulator time used as quantum time anywhere?
7. **N1–N5** each marked with evidence.
8. **Alternative explanations** table: leakage, underpowering, instance selection, tuning on test,
   control failure, wrong comparison object.
9. **Result.** CONFIRMED (all checks pass; for NO-GO-FINAL all of N1–N5) · OVERTURNED (a number or
   logic step is wrong in a way that changes the verdict) · INSUFFICIENT (a named missing
   control or failed standard; state the reopening condition).

## May not
Edit `VERDICT.md`, the lock, results, or any code outside `{THREAD}/audit/` · read excluded
inputs · raise a verdict's strength.

## Return to the orchestrator
Result · which of N1–N5 failed · discrepancies found · reopening condition (if INSUFFICIENT).
