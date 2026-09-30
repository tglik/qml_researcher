# Review panel — protocol (one per persona instance)

## Invoked by
`/qml-review-panel --pass 1|2`, which spawns five instances in parallel. Each instance gets:
this PROTOCOL + the panel ESSENCE + exactly one persona file from `personas/`.

## Inputs
- **Pass 1:** `{THREAD}/HYPOTHESIS.md` · `ALGORITHM_ANALYSIS.md` (if present) · `SCREEN.md` ·
  `PROPOSAL.md` · `00_operating_point.md` · `frozen_definitions.md`
- **Pass 2:** `PREREG.lock.json` · `PROPOSAL.md` · every `P*/results/gates.md` · every
  `P*/PHASE_REPORT.md` *sections 1–5 only* · `P*/raw/` and `P*/figures/` as needed.
  **Never** `VERDICT.md` (it must not exist yet; if it does, stop and report).

## Output
`{THREAD}/panel/{pass}/{persona}.md` — your issues as rows of the PANEL table:
`# | persona | severity | anchor (verbatim + file) | problem | concrete fix`.
The methodologist additionally fills the Adi S2 checklist (pass 1) or the drift-check section (pass 2).

## Steps
1. Read inputs. Restate, in one line, what your persona attacks in this artifact.
2. List issues; for each: verbatim anchor, why it matters to the conclusion, concrete fix.
3. Assign severity (BLOCKING only if the conclusion cannot be licensed without the fix).
4. If you find nothing in your lane, write "No issues in <lane>." — that is a valid result.

## May not
Edit any thread artifact · read other personas' files · read a verdict.

## Return
Counts: BLOCKING n, NON-BLOCKING m · path written.
