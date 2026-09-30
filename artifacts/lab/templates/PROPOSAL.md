---
thread: {thread}
date: {YYYY-MM-DD}
status: {draft | panel-reviewed | frozen}
lock_sha256: {filled by lock.py at freeze}
---

# Pre-registration — {short name}

Every item in a fenced `lock` block below is hashed into PREREG.lock.json at freeze. After
freeze those blocks are immutable; changes are dated amendments that precede data access.

## 1. Hypotheses → experiments
| Hypothesis | Experiment IDs | Metric | Predicted | Pass if | Fail if |
|---|---|---|---|---|---|

## 2. Metrics
- **Correctness:** {metric; ground truth per size — exact / brute force / trusted solver}
- **Projected quantum cost:** {formula; assumed hardware clock}
- **Simulation cost:** {wall-clock + peak memory — reported, never used as quantum time}
- **Classical cost:** {same hardware, same budget}
- **Scaling fits:** {polynomial vs exponential, AIC/BIC, CIs}

## 3. Arms and baselines
| Arm | What it is | Tuning budget | Why it is here |
|---|---|---|---|
| Quantum | | | |
| Classical twin | | | rule 1 |
| Strongest classical (exact) | | ≥ quantum | |
| Strongest classical (industry tool) | | ≥ quantum | |
| Size-matched control(s) | | — | N3, one per oracle/ablation gate |

```lock
id: baseline.adequacy
kind: baseline
text: Classical arm must reach within {factor} of published SOTA ({value, source}) on {metric, data}; otherwise every NO-GO is provisional (G5/N1).
```

## 4. Instances, splits, statistics
- Families and generators (with seeds); easy / typical / hard / edge; ≥ 20–50 per size at small sizes.
- Tuning vs test instances kept separate.
- Exact (statevector) and finite-shot runs.
- CI method, seeds, outlier handling.

```lock
id: splits.definition
kind: split
text: {exact split definition — created and hashed before any modeling}
```

## 5. Phases (cheapest-fatal first)
### P1 — {toy, 6–16 q}
Objective · experiment table (ID, hypothesis, sizes, instances, seeds, method, metric, expected) ·
tuning plan · budget (cpu-h, peak memory, wall-days) · fallback.

```lock
id: P1.G4.threshold
kind: threshold
text: {gate, measured quantity, numeric threshold, justification}
```
```lock
id: P1.gray_zone
kind: gray_zone
text: {what happens on a partial or borderline result — written before data}
```
```lock
id: P1.stop_rule
kind: stop_rule
text: {condition under which the program stops after P1}
```

### P2 — {medium, 18–26 q} …
### P3 — {real data + classical at N_ind + resource estimate at N_ind} …
### P4 — {noise sweep} …
### P5 — {hardware plan — modeling only in V1} …

## 6. Verdict sentences, written in advance
| Gate | If it passes we will write | If it fails we will write |
|---|---|---|

## 7. Budget and fallbacks
| Phase | cpu-h | peak memory | tokens | wall-days | Fallback |
|---|---|---|---|---|---|

## 8. Analysis plan
{Figures and tables each phase report must contain.}

## 9. Risks

## Amendments (append-only after freeze)
| # | Date | Touches | Reason | Precedes data access for | Approved by |
|---|---|---|---|---|---|
