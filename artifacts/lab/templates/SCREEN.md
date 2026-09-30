---
thread: {thread}
date: {YYYY-MM-DD}
verdict: {PASS | PASS-NARROWED | KILLED-ON-PAPER | ASK-HUMAN}
decisive_rules: [{e.g. G1, G3}]
deep_research: {path to report if one was requested | none}
---

# Screen — {short name}

> **Warnings** (from ALGORITHM_ANALYSIS.md, verbatim; "none" if none)

## G0 — Exclusion ledger engagement
| Ledger entry | Same mechanism? | Argument |
|---|---|---|
| {id} | {yes / no / partly} | {why — by mechanism, not by wording} |
{If no entry is brushed, say which entries were checked and why none apply.}

## The six rules
| Rule / gate | Rating | Reason (with the number or precedent that decides it) |
|---|---|---|
| G1 · Readout shape & cadence (rule 6) | {🟢/🟠/🔴} | |
| G2 · Resource cap, both arms (rule 4) | | |
| G3 · Classical twin, on paper (rule 1) | | |
| Rule 2 · Real data available | | |
| Rule 3 · Operating point & ladder | | |
| Rule 5 · Frontier, not a point | | |

## Five QML criteria (qml_domain.md)
| Criterion | Assessment |
|---|---|
| 1 Strong classical baseline | |
| 2 Dequantization risk | |
| 3 Quantum-native data fit | |
| 4 Trainability / simulability | |
| 5 Hardware context & feasibility | |

## Deployment architectures
| Architecture | Where the quantum step sits | Screen outcome | Killing rule (if any) |
|---|---|---|---|

## Verdict
**{PASS | PASS-NARROWED | KILLED-ON-PAPER | ASK-HUMAN}** — {one paragraph}.
**Narrowest claim the screen licenses:** {…}
**If killed — mechanism:** {structural reason, the narrowest class it generalizes to}
**Design constraints for pre-registration** (rules 2, 3, 5): {what the prereg must include}
