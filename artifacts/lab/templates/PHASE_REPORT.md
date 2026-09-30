---
thread: {thread}
phase: {P1 | P2 | P3 | P4 | P5}
date: {YYYY-MM-DD}
gate_proposal: {PROCEED | STOP-PREREGISTERED | ESCALATE}
---

# Phase report — {phase}

## 1. What was run, and deviations from the design
{Every deviation also in change_log.md: what, why, effect on conclusions.}

## 2. Results
{Tables and figures, each with a one-sentence caption stating what it shows. Every number
carries a provenance id.}

## 3. Expected vs observed
| Hypothesis | Predicted | Observed | Confirmed / Partial / Not confirmed |
|---|---|---|---|

## 4. Baselines side by side (equal budget)

## 5. Surprises and possible bugs
- Too-good results, suspiciously low variance, input-independent outputs: {…}
- Simulability signs (small MPS bond dimension, low entanglement): {…}

## 6. Gate decision proposal
{PROCEED — all key hypotheses confirmed · STOP-PREREGISTERED — a locked stop rule fired ·
ESCALATE — failure or partial with no pre-registered policy: which assumption failed, evidence,
likely cause (bug / hyperparameters / real limitation / noise), options with cost.}
