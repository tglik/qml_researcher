# Experiment designer — protocol

## Invoked by
`/qml-prereg` (phases 0–1, 3–8) and, after panel feedback, for revisions (a fresh instance per round).

## Inputs
`{THREAD}/HYPOTHESIS.md` · `{THREAD}/ALGORITHM_ANALYSIS.md` (if present) · `{THREAD}/SCREEN.md`
(verdict PASS or PASS-NARROWED, and its design constraints) · `{THREAD}/00_inputs/answers.md` (the
decision the answer changes) · the classical competitor champion's baselines tables ·
revisions: `{THREAD}/PANEL_1.md`.

## Outputs
- `{THREAD}/PROPOSAL.md` — the plan, from `artifacts/lab/templates/PROPOSAL.md` (`format: 2`):
  summary, what the result decides, the experiment sequence with why / expect / if it fails / cost
  per experiment, shared setup, models table, budget, open questions. Readable in five minutes
  (aim ≤ 200 lines).
- `{THREAD}/experiments/E<k>_<slug>.md`, one per run phase P<k>, from
  `artifacts/lab/templates/EXPERIMENT.md`: question and why, expectation, design, decision rules in
  plain words, verdict sentences, pitfalls, report, budget, and that experiment's `lock` blocks
  (ids `P<k>.…`) in its *Locked rules* section. Aim ≤ 250 lines before *Locked rules*.
- `{THREAD}/00_operating_point.md` — named N_ind, budgets, value metrics with targets, target modality,
  extrapolation ladder, and the **P0 analytic resource count** (gates, depth, shots, loading,
  readout at N_ind; best classical cost at N_ind; break-even N*)
- `{THREAD}/frozen_definitions.md` — splits, metrics, instance generators, seeds (as `lock` blocks)
- On revision: a `change_log.md` line per change, citing the panel issue number. Revision notes and
  panel issue numbers never appear in the plan or the experiment docs.

## Steps
1. **Map.** Write the plan's experiment sequence: each experiment names the hypotheses it tests
   (the hypothesis's chain of links), why it comes at that point, and what it can end. *Fail if*
   any H has no experiment or any experiment tests no H.
2. **Ladder.** Write P0 first. Choose phases from P1–P5 that serve the hypotheses; order
   cheapest-fatal first; attach each of G4–G9 to exactly one phase (lab_method §3). For each run
   phase, name the simulation method and why (lab_method §6).
3. **Metrics.** Correctness with ground truth per size; projected quantum cost; simulation cost
   (labeled); classical cost; scaling fits.
4. **Instances & stats.** Families, generators, seeds, counts per size, tuning/test separation,
   exact + finite-shot, CI method.
5. **Thresholds.** In each experiment doc: the decision rules as a plain-language table with a
   *Why these thresholds* line per number, then one `lock` block per gate (`kind: threshold`)
   with justification, including the smallest gain that matters and the tie band (rule 5), and
   one `gray_zone` and one `stop_rule` block for that phase. Program-level blocks
   (`baseline.adequacy` from the classical competitor champion, `splits.definition`, global stop
   rules) go in the plan.
6. **Controls.** A size-matched control for every oracle/ablation gate, as its own experiment row.
7. **Operating point.** Write `00_operating_point.md`; ladder ≥ 4 points on every extrapolated axis.
8. **Budget.** Per phase and per side (quantum, classical): cpu-h, peak memory, tokens, wall-days,
   fallback. Check peak memory with the simulation-limits table; *fail if* a phase does not fit the
   local machine (V1: local only, no cloud).
   Real data too large to run: plan real data at the largest simulable size, classical at full
   size, quantum modeled at full size (rule 2).
9. **Verdict sentences.** Both sentences per gate, in that experiment's doc. *Fail if* any NO-GO
   sentence is missing.
10. **Decision.** Copy the decision the answer changes from `00_inputs/answers.md` into the plan's
    *What the result decides*.
11. **Self-check** before returning: every `lock` block has `id`, `kind`, `text`; ids unique; each
    experiment's plain-language decision rules say the same as its lock blocks;
    `python -m lab.tools.validate thread {THREAD}` passes; the prose follows `lab/STYLE.md`.

## May not
Freeze the lock (that is `/qml-prereg` after CP2) · run anything · audit · edit `HYPOTHESIS.md` or
`SCREEN.md` · edit a frozen PROPOSAL or experiment doc except through an amendment row.

## Return to the orchestrator
Paths written · number of lock blocks · phases planned with budgets · any gate you could not
specify, and why.
