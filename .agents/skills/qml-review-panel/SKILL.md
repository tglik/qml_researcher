---
name: qml-review-panel
version: 0.1.0
description: |
  QML Lab adversarial review panel: five personas (methodologist, dequantization theorist,
  hardware realist, baseline champion, value translator) spawned in parallel on fresh contexts.
  Pass 1 reviews the pre-registration before freeze; pass 2 reviews raw results before any
  verdict exists. Writes PANEL_1.md / PANEL_2.md. Invoked by /qml-prereg and /qml-lab.

triggers:
  - qml-review-panel
  - run the lab review panel

input:
  - "<thread> --pass 1|2"

output:
  - "{THREAD}/panel/<pass>/<persona>.md (one per persona)"
  - "{THREAD}/PANEL_<pass>.md (merged)"

allowed-tools: [Agent, Read, Write, Glob, Grep, Bash]
---

# /qml-review-panel

**Essence:** [ESSENCE.md](ESSENCE.md) · **Role:** `lab/roles/review-panel/` (panel ESSENCE +
PROTOCOL + one of `personas/*.md`) · **Template:** `artifacts/lab/templates/PANEL.md`

## Setup
```
Pass 1: python -m lab.tools.state check {THREAD} --need file:PROPOSAL.md
Pass 2: python -m lab.tools.state check {THREAD} --need lock
        and VERDICT.md must NOT exist (if it does: stop — pass 2 must precede verdict language)
PERSONAS = methodologist, dequantization-theorist, hardware-realist, baseline-champion, value-translator
```

## Phase 1 — Five parallel reviews
For each persona, in one message (parallel), spawn a fresh agent whose prompt is:
`lab/roles/review-panel/ESSENCE.md` + `personas/<persona>.md` + `PROTOCOL.md` + LAB_METHOD + task:
```
Task: review {THREAD}, pass {n}. Inputs per the PROTOCOL for this pass. Write your issues to
{THREAD}/panel/{n}/<persona>.md. Do not read other personas' files.
```
**Gate:** five files exist; each is either a table of issues or "No issues in <lane>."

## Phase 2 — Merge
Write `{THREAD}/PANEL_<n>.md` from the template: all issues renumbered, grouped BLOCKING first;
the methodologist's checklist (pass 1) or drift check (pass 2) copied in; frontmatter
`blocking: <count>` and `verdict`: BLOCKED if any BLOCKING, else APPROVED-WITH-CHANGES if any
NON-BLOCKING, else APPROVED. Do not edit, soften or drop any persona's issue.
**Gate:** `python -m lab.tools.validate artifact {THREAD}/PANEL_<n>.md`.

## Phase 3 — Record
Append a line to `{THREAD}/decision_log.md`: panel pass, verdict, blocking count.
Pass 2 with BLOCKING issues: return to `/qml-lab`, which escalates to adi (`unplanned_failure`) —
a pass-2 block means the results cannot yet support any verdict.

## Completion message
```text
QML-REVIEW-PANEL — pass <n> — <APPROVED | APPROVED-WITH-CHANGES | BLOCKED> — <thread>
Blocking: <k> · Non-blocking: <m> · By persona: <…>
Path: {THREAD}/PANEL_<n>.md
```
