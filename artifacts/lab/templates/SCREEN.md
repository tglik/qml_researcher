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
Prior-work brief read: {yes — key items | none found}
| Ledger entry | Same mechanism? | Argument |
|---|---|---|
| {id} | {yes / no / partly} | {why — by mechanism, not by wording} |
{If no entry is brushed, say which entries were checked and why none apply.}

## Rules
| Rule / gate | Rating | Reason (with the number or precedent that decides it) |
|---|---|---|
| G1 · Input loading (rule 7) | {🟢/🟠/🔴} | |
| G1 · Readout at the precision and cadence needed (rule 6) | | |
| G2 · Classical is a real bottleneck, limit charged to both sides (rule 4) | | |
| G3 · Classical competitor, on paper (rule 1 — rate each item below) | | |
| Rule 2 · Real data available | | |
| Rule 3 · Operating point named | | |
| Rule 5 · Resource range to sweep | | |

**Rule 1 checklist** (🟢 fails, with the reason · 🟠 open · 🔴 matches the quantum method)
| Competitor | Rating | Reason |
|---|---|---|
| Twin (same input, same access) | | |
| Best classical method for the task (the input classical really has) | | |
| Direct simulation at comparable cost | | |
| Simulable structure (near-Clifford, low entanglement, free-fermion, small light cones) | | |
| Noise makes it simulable (stays 🟠 until P4) | | |
| Learned classical surrogate | | |
| Only the requested output is easy | | |
| Sign-free / diffusion warning (Monte Carlo or random walk on the same input) | | |

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
**Design constraints for pre-registration** (rules 2, 3, 5): {real dataset, operating point and ladder, resource range, open Rule 1 items to test in code}
