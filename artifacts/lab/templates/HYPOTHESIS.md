---
thread: {thread}
entry_path: {algorithm | use-case}
source: {path to the input: algorithm paper/notes in 00_inputs/, hypothesis card, transfer card, deep-research report, or "direct"}
source_hypothesis_card: {cards/hypotheses/<slug> | none}   # C12 I1 — promotion updates this card's status
checklist: {n}/5
status: {draft | complete | not-a-hypothesis}
date: {YYYY-MM-DD}
---

# Hypothesis — {short name}

## Claim
{One or two sentences, stated so that a number could contradict it. Include the quantifier:
for which data regime, which problem size, which accuracy tolerance.}

## Operating point
{The named industrial setting where the claim must hold: problem size N (and qubits q with the
mapping), latency / memory / cost budget, output cadence. In the design, not the discussion.}

## Disproof
{The result that would count as disproof, written before any data. "If <measurement> shows
<value/shape>, the claim is false."}

## Arm that wins if the claim is false
{The classical method (or twin) that would be the right answer instead, and why.}

## Decision this changes
{What gets funded, dropped, or pitched depending on the answer.}

## Testable hypotheses
| # | Hypothesis | Predicted value / scaling | Metric | Source of the prediction |
|---|---|---|---|---|
| H1 | {…} | {e.g. "two-qubit gate count O(q²)", "approx. ratio ≥ 0.9 for N ≤ 20"} | {…} | {analysis section / paper / prior experiment} |

## Kill criteria
- {Condition that ends the program early, e.g. "twin reproduces the output at ≤ 1/10 modeled cost at N=2^20"}

## Open points
- {Anything the interrogation could not resolve, marked [ASSUMPTION] or [UNVERIFIED]}

## Sources
- {inputs read during intake}
