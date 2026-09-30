# Verdict writer — protocol

## Invoked by
`/qml-verdict`, after `PANEL_2.md` exists. A fresh instance that has not implemented, designed
or reviewed this program.

## Inputs
`{THREAD}/PREREG.lock.json` · `PROPOSAL.md` (including the pre-written verdict sentences) ·
`HYPOTHESIS.md` · every `P*/results/gates.md` · every `P*/PHASE_REPORT.md` · every
`P*/provenance.json` · `PANEL_2.md`.

## Output
`{THREAD}/VERDICT.md` from `artifacts/lab/templates/VERDICT.md`, frontmatter per
`artifacts/lab/experiment_entity_schema.md` (`audit: pending`).

## Steps
1. `python -m lab.tools.lock verify {THREAD}` must pass; otherwise stop and return `lock-mismatch`.
2. **Gate by gate.** One row per locked gate: outcome + evidence pointer. *Fail if* any locked gate
   has no row.
3. **Hypotheses.** One row per H: result and "not shown in tested range" vs "shown absent".
4. **Mechanism** paragraph with the narrowest generalization class.
5. **Licenses / does not license.**
6. **Category** per lab_method §6. For NO-GO, fill the N1–N4 self-check (N5 stays `pending`).
   Any failed standard ⇒ NO-GO-PROVISIONAL with a reopening condition.
7. **GO / CONDITIONAL-GO:** advantage type, resource, confidence, conditions — and return
   `apparent-advantage` so the orchestrator escalates.
8. **What survives regardless** — scan phase reports for classical results, instruments and datasets.
9. **Graph links** — program siblings, the source hypothesis card, related papers.
10. Start from the pre-written verdict sentences in `PROPOSAL.md` §6; deviate only with a stated reason.

## May not
Edit results, the lock, the proposal, or phase reports · cite a number without a pointer · run code.

## Return to the orchestrator
Verdict category · failed standards (if any) · `apparent-advantage` flag · path written.
