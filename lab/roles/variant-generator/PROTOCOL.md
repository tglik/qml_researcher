# Variant generator — protocol

## Invoked by
`/qml-variants`, after CP4 (or after CP1 approved a KILLED-ON-PAPER screen).

## Inputs
`{THREAD}/VERDICT.md` + `AUDIT.md` (or `SCREEN.md` for a paper kill) · `HYPOTHESIS.md` ·
`SCREEN.md` · `{OUTPUT_ROOT}/indexes/exclusion-ledger.md` · `criteria/lab_method.md` (injected).

## Output
`{THREAD}/VARIANTS.md` from `artifacts/lab/templates/VARIANTS.md`. Variant hypothesis cards are
written by `/qml-promote`, not by you.

## Steps
1. **When to generate.** Read the verdict category. GO or BLOCKED ⇒ write "Variants not generated —
   <reason>", fill Salvage only, skip to step 7. NO-GO-PROVISIONAL ⇒ variants allowed, but state that
   they do not replace the reopening condition. CONDITIONAL-GO ⇒ variants loosen the conditions.
2. **Mechanism.** Pick the primary cause from the template list; state it as a precondition.
3. **Candidates.** Change one or a few things (task, input or access, output, resource competed on,
   precision, instance class, hardware, scale only with a real scaling gap). For each, write what
   changed and why it escapes the failure.
4. **Check each candidate** against G0–G3 (not only the failed rule). A new input ⇒ redo the Rule 1
   checklist. A new resource ⇒ name the limit where classical suffers, charged to both sides, over a
   range. A resource trade-off ⇒ state it. Same gate + same mechanism ⇒ move to *Covered cases*.
   Inside an existing ledger entry ⇒ drop it.
5. **Rank** by potential, best first; keep ≤ 10. Fill every column, including the cheapest kill test.
   None viable ⇒ "No viable variant — <reason>".
6. **Salvage** (a), (b), (c); a useful classical competitor goes under (a), unranked.
7. **Pivot questions** Q1–Q3 with ratings · **Paper / IP** section with the disclosure warning
   verbatim · **Recommendation**; for `new-cycle`, a one-sentence draft claim for the chosen variant.

## May not
Re-argue the verdict (a stronger baseline or a bug fix goes to `/qml-audit`) · write ledger entries
or hypothesis cards · run experiments beyond a small check ≤ 16 qubits · give legal advice ·
rate or screen its own variants beyond the step 4 quick check.

## Return
Number of variants · recommendation · covered cases (for the ledger entry) · salvage list.
