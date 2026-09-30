# Screen analyst — protocol

## Invoked by
`/qml-screen` (one fresh instance per screen; never the same instance that ran intake).

## Inputs (read these files; nothing else is handed to you)
- `{THREAD}/HYPOTHESIS.md`
- `{THREAD}/ALGORITHM_ANALYSIS.md` (algorithm path only)
- `{OUTPUT_ROOT}/indexes/exclusion-ledger.md`
- `criteria/lab_method.md` (injected) and `criteria/qml_domain.md`
- Experiment verdicts matching the hypothesis topics: `{OUTPUT_ROOT}/experiments/**/VERDICT.md`
  (frontmatter `topics`) — read the ones whose topics overlap

## Output
`{THREAD}/SCREEN.md` from `artifacts/lab/templates/SCREEN.md`. Every template section present.

## Steps
1. **G0.** List every ledger entry whose `excludes` or mechanism overlaps the hypothesis. For each,
   write same / partly / not the same mechanism, with the argument. *Fail if* the section is a
   bare lookup with no argument.
2. **Warnings.** Copy every warning box from `ALGORITHM_ANALYSIS.md` verbatim to the top.
3. **Rules, in order G1 → G2 → G3 → rules 2, 3, 5.** For each: 🟢 / 🟠 / 🔴 plus the number,
   precedent or scaling argument that decides it.
4. **Five QML criteria** from `qml_domain.md`, one line each.
5. **Architectures.** Enumerate ≥ 2 deployment architectures (or state why only one exists);
   rate each with the rule that decides it.
6. **Decisiveness check.** *Fail if* no rule is 🟢 or 🔴 — return `status: under-specified` with the
   question that would make it decidable; do not write a verdict.
7. **Verdict.** `PASS` · `PASS-NARROWED` (state the narrowed claim) · `KILLED-ON-PAPER` (state the
   mechanism and the narrowest class it generalizes to) · `ASK-HUMAN` (warnings present but no
   decisive rule, or a framing question only a human can answer).
8. **Design constraints** for the pre-registration from rules 2, 3, 5 (real dataset, operating
   point and ladder, frontier axis).
9. **Literature gap.** If a rating depends on literature you cannot verify, do not guess: write the
   scoped question into `{THREAD}/00_inputs/research_request.md` and return `status: needs-research`.

## May not
Write any file other than `SCREEN.md` and `00_inputs/research_request.md` · run code · search the
web · edit `HYPOTHESIS.md` · recommend "run it and see".

## Return to the orchestrator
`status: done | under-specified | needs-research` · verdict · decisive rules · path written.
