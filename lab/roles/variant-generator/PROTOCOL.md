# Variant generator — protocol

## Invoked by
`/qml-variants`, after CP4 (or after CP1 approved a KILLED-ON-PAPER screen).

## Inputs
`{THREAD}/VERDICT.md` + `AUDIT.md` (or `SCREEN.md` for a paper kill) · `HYPOTHESIS.md` ·
`{OUTPUT_ROOT}/indexes/exclusion-ledger.md` · `criteria/lab_method.md` (injected).

## Output
`{THREAD}/VARIANTS.md` from `artifacts/lab/templates/VARIANTS.md`. Draft hypothesis cards are
written by `/qml-promote`, not by you.

## Steps
1. **Mechanism.** Pick the primary cause from the template list; state it as a precondition.
2. **Inversion.** ≥ 1 candidate or an explicit "none" with the reason.
3. **One-axis relaxation.** For each failed gate, the axes it has; candidates relaxing exactly one.
4. **Pre-screen** every candidate with the six rules: newly-passed gate, newly-faced gate,
   predicted kill gate. Same gate + same mechanism ⇒ move to *Covered cases*.
5. **Rank** and keep ≤ 5.
6. **Salvage** (a), (b), (c) — every (a)/(b) listed explicitly.
7. **Pivot questions** Q1–Q3 with ratings.
8. **Paper / IP** section with the disclosure warning verbatim.
9. **Recommendation**; for `new-cycle`, a one-sentence draft claim for the chosen variant.

## May not
Write ledger entries or hypothesis cards · run experiments beyond a small check ≤ 16 qubits ·
give legal advice.

## Return
Number of variants · recommendation · covered cases (for the ledger entry) · salvage list.
