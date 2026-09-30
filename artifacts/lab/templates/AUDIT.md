---
thread: {thread}
date: {YYYY-MM-DD}
auditor_model: {model id}
result: {CONFIRMED | OVERTURNED | INSUFFICIENT}
---

# Audit — {short name}

## 0. Lock diff (mechanical)
{Output of `python -m lab.tools.lock diff` — verbatim. Any moved threshold, split or stop rule;
amendment timing.}

## 1. Recomputed numbers
| Number | Verdict value | Recomputed | Method (own code, file) | Agree? |
|---|---|---|---|---|

## 2. Reproduction (one size per phase run, the largest size, the classical baseline at that size)
| Experiment | Original | Reproduced | Agree within CI? |
|---|---|---|---|

## 3. Independent correctness check
{A few instances against ground truth with a different simulator or library.}

## 4. Provenance sample
| Number id | Traced to | OK? |
|---|---|---|

## 5. Fairness
- Baselines strongest and fairly tuned: …
- Twin analysis held: …
- Simulator time used as quantum time anywhere: …

## 6. Negative Verdict Standard
| | Holds? | Evidence |
|---|---|---|
| N1 | | |
| N2 | | |
| N3 | | |
| N4 | | |
| N5 | {this audit} | |

## 7. Alternative explanations
| What else could produce this result | Checked how | Ruled out? |
|---|---|---|

## 8. Result
**{CONFIRMED | OVERTURNED | INSUFFICIENT}** — {one paragraph}. {INSUFFICIENT: the named missing
control; this converts a NO-GO into a provisional one with that control as the reopening condition.}
