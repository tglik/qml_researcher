# Explanation checker — protocol

## Invoked by
`/qml-ingest` phase 4 (Explain), after the explainer: one fresh instance per batch, never the
instance that wrote the pages.

## Inputs
- The explainer files of the batch (`{OUTPUT_ROOT}/indexes/backlog/explainers/...`).
- Each entity's gate record (`candidates.jsonl`) or entry (`directions.json`).
- The sources the page cites (open them: `/fetch-arxiv` or WebFetch on `arxiv.org/abs/<id>`).
- `criteria/advantage_potential.md` and the explainer's PROTOCOL (the rules the page must follow).

## Checks, per page
1. **Lint.** `python -m lab.tools.backlog validate --explainers` passes for the file.
2. **Bet and verdict.** `bet` matches the value rung. `quantum_case` respects the caps in the
   explainer PROTOCOL. If in doubt, lower it.
3. **Facts.** Every number, name, date and paper claim traces to the gate record or a cited source
   you opened. Remove or correct anything that does not.
4. **Candor.** "The real motivation" names the real kind of result. "Why quantum, honestly" opens
   with a verdict that matches `quantum_case`. No sentence implies an advantage the verdict does not
   support. The strongest classical competitor is named.
5. **Readability.** Each concept is defined before use. A smart non-specialist can follow it.

## Outcome, per page
- **Sign:** apply small fixes in place, then set `check_status: signed`, add
  `checked_by: explanation-checker` and `checked_at: <YYYY-MM-DD>`.
- **Return:** set `check_status: draft`, add `check_notes: <one line naming each problem>`. The
  explainer gets one revise round; a page that still fails stays draft and is shown with a draft
  badge.

Report one line per page: id · signed or returned · what you changed or why you returned it.

## May not
- Raise `quantum_case`, change `bet` upward, or add a motivation the writer did not have evidence for.
- Sign without opening at least the first cited source.
