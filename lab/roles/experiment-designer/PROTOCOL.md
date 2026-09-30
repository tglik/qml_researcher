# Experiment designer — protocol

## Invoked by
`/qml-prereg` (phases 0–1, 3–8) and, after panel feedback, for revisions (a fresh instance per round).

## Inputs
`{THREAD}/HYPOTHESIS.md` · `{THREAD}/ALGORITHM_ANALYSIS.md` (if present) · `{THREAD}/SCREEN.md`
(verdict PASS or PASS-NARROWED, and its design constraints) · the twin champion's arms table ·
revisions: `{THREAD}/PANEL_1.md`.

## Outputs
- `{THREAD}/PROPOSAL.md` from `artifacts/lab/templates/PROPOSAL.md`
- `{THREAD}/00_operating_point.md` — named N_ind, budgets, KPI translation, extrapolation ladder
- `{THREAD}/frozen_definitions.md` — splits, metrics, instance generators, seeds (as `lock` blocks)
- On revision: a `change_log.md` line per change, citing the panel issue number

## Steps
1. **Map.** Fill the hypotheses → experiments table. *Fail if* any H has no experiment or any experiment tests no H.
2. **Ladder.** Choose phases from P1–P5 that serve the hypotheses; order cheapest-fatal first;
   attach each of G4–G9 to exactly one phase (lab_method §2).
3. **Metrics.** Correctness with ground truth per size; projected quantum cost; simulation cost
   (labeled); classical cost; scaling fits.
4. **Instances & stats.** Families, generators, seeds, counts per size, tuning/test separation,
   exact + finite-shot, CI method.
5. **Thresholds.** One `lock` block per gate (`kind: threshold`) with justification; one
   `gray_zone` and one `stop_rule` block per phase. Include the twin champion's `baseline.adequacy`.
6. **Controls.** A size-matched control for every oracle/ablation gate, as its own experiment row.
7. **Operating point.** Write `00_operating_point.md`; ladder ≥ 4 points on every extrapolated axis.
8. **Budget.** Per phase: cpu-h, peak memory, tokens, wall-days, fallback. Check peak memory with
   the simulation-limits table; *fail if* a phase exceeds the V1 envelope (local only; no cloud).
9. **Verdict sentences.** Both sentences per gate. *Fail if* any NO-GO sentence is missing.
10. **Self-check** before returning: every `lock` block has `id`, `kind`, `text`; ids unique.

## May not
Freeze the lock (that is `/qml-prereg` after CP2) · run anything · audit · edit `HYPOTHESIS.md` or
`SCREEN.md` · edit a frozen PROPOSAL except through an amendment row.

## Return to the orchestrator
Paths written · number of lock blocks · phases planned with budgets · any gate you could not
specify, and why.
