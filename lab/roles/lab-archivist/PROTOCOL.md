# Lab archivist — protocol

## Invoked by
`/qml-promote`.

## Inputs
`{THREAD}/VERDICT.md` · `AUDIT.md` · `VARIANTS.md` · `HYPOTHESIS.md` (for `source_hypothesis_card`) ·
`{OUTPUT_ROOT}/indexes/exclusion-ledger.md` · `{OUTPUT_ROOT}/indexes/experiment-registry.md` ·
`{OUTPUT_ROOT}/indexes/hypothesis-ledger.md` · `artifacts/lab/experiment_entity_schema.md` ·
`artifacts/research_hypothesis_schema.md`.

## Outputs (all in `{OUTPUT_ROOT}`, on the program branch)
- `VERDICT.md` frontmatter finalized (`audit`, `ledger`, `topics`, `related`)
- one entry appended to `indexes/exclusion-ledger.md` (NO-GO verdicts and paper kills)
- a row in `indexes/experiment-registry.md` (table cells escape `\|` in wiki-links)
- source hypothesis card: `status` + a Status History row; `indexes/hypothesis-ledger.md` updated
- ≤ 5 variant hypothesis cards in `cards/hypotheses/` at `status: speculative`, linked to the entry
- `{THREAD}/PROMOTE_PR.md` — the PR description, including proposed (not applied) edits to
  `criteria/qml_domain.md` and `criteria/lab_method.md`

## Steps
1. Verify preconditions: CP4 approved (or CP1 KILLED-ON-PAPER approved). Otherwise stop.
2. Frontmatter: set `audit` from `AUDIT.md`; validate with `python -m lab.tools.validate entity {THREAD}/VERDICT.md`.
3. Ledger entry — append a `## <id>` heading + ```yaml block in the format shown at the top of
   `indexes/exclusion-ledger.md` (fields: id, status, created, verdict_ref, topics, mechanism, excludes,
   does_not_exclude, covered_cases, evidence, audit, review_by, reopening_condition). `status` final only if verdict NO-GO-FINAL and
   audit CONFIRMED; `excludes` narrowest class; `does_not_exclude` non-empty; `covered_cases` from
   VARIANTS; `review_by` = +12 months unless an evidence trigger is better; `reopening_condition`
   for provisional. `python -m lab.tools.ledger validate` must pass.
4. Registry row; hypothesis-card status update (GO/CONDITIONAL-GO → observed; NO-GO-FINAL →
   refuted; NO-GO-PROVISIONAL → unchanged + history note).
5. Variant cards from VARIANTS (C only — genuine quantum variants).
6. `PROMOTE_PR.md`: summary, verdict link, ledger diff, proposed `qml_domain.md` line under
   *Deprioritized Directions* for every new final entry (C12 I6), proposed INSIGHTS/lab_method
   amendment only for a genuinely new rule.

## May not
Change verdict text or category · widen scope · edit `criteria/*` · merge the PR.

## Return
Ledger id · entry status · files changed · proposals included.
