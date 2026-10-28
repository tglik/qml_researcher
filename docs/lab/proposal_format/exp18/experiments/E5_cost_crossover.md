---
thread: materials_configuration_space/18_config_space_features
experiment: E5 (PROPOSAL.md phases P0 and P5)
tests: H5 (a quantum pipeline beats the best classical pipeline on total cost)
status: E0 done (paper count, 00_operating_point.md §3); E5 not started
depends_on: E2 (wall size n_b; λ, gap, γ per size), E3 (gain vs size, budget curves), E4 (B, V, a, p_L*)
budget: 15 core-h; 2 GB; 3 wall-days; 2.5 M tokens
code: P5_hardware/
date: 2026-10-28
---

# E5 — Does a quantum pipeline beat the best classical pipeline on total cost?

## Question and why
Take the gain measured in E3 and the costs measured in E2–E4. Does a quantum pipeline give better
ranking per dollar than the best classical pipeline, under realistic early fault-tolerant hardware?
A partner needs this as a curve, quality against total cost, not as a qubit count.

E5 is modelling only; no quantum hardware or circuit is run. It comes last because it needs every
measured input from the earlier experiments.

## What we already know (E0, paper count)
Under the central scenario, one core set of 1,000 structures at 12 orbitals and ±0.01 precision
needs **1.08 × 10¹⁰ s** of quantum runtime. The budget is 2.6 × 10⁶ s (30 days), so that is 4,200×
over. The best corner (400 structures, ±0.1, 18 orbitals) is still 69× over in runtime, and
**~1,230× over at matched dollars**. Only three measured values can lower the count. Two of them
(the overlap γ and the number of measurement groups B) give at most ~5× together. The pass
therefore rests on the third, the Hamiltonian norm λ, which at 18 orbitals would need to be
≤ 0.3 Ha; ≥ 10 Ha is typical for a transition-metal active space of that size. **Expected: H5
fails.**

## Design
**Hardware scenarios** (logical qubits, operations per circuit, logical operations per second):

| Scenario | Qubits | Ops per circuit | Clock |
|---|---|---|---|
| Pessimistic | 100 | 10⁶ | 10³ /s |
| Central | 316 | 3.16 × 10⁷ | 3.16 × 10⁴ /s |
| Optimistic | 1,000 | 10⁹ | 10⁶ /s |

- A circuit counts under a scenario only if it fits that scenario's qubit and operation caps.
- The central clock assumes superconducting-class hardware. Trapped-ion and neutral-atom machines
  (including the Q-Factor track) sit in the pessimistic clock bucket until the roadmap refresh says
  otherwise.

**Cost axis.**
- Dollars per campaign. Quantum time is priced at $10⁴ per QPU-hour; $10³ and $10⁵ are also
  reported.
- The classical campaign costs $0.405 M.

| Step | What | Output |
|---|---|---|
| E5.1 crossover | quantum pipeline quality vs total dollars, against the classical front at ≥ 5 budgets (including $0.405 M) under all three scenarios. The quantum quality is E3's gain: measured up to 16 orbitals, held flat above. The quantum cost is classical preparation + runtime at the wall size n_b from E2 | crossover table and curve per scenario; measured and projected rows kept apart |
| E5.2 sensitivity and value per run | recount E0 with measured inputs; table of precision × core-set size × readout corners; break-even QPU price against (i) the classical campaign and (ii) computing the same features classically | produced in **every** outcome, so the partner sentence always has its dollar figure |
| E5.3 hardware map | logical qubits, operations, p_L* and shots mapped to each vendor row in `criteria/hardware_roadmaps.md`: code distance, physical qubits, factory allowance | per-vendor table, labelled projected |

**The classical front** (what the quantum pipeline must beat at equal dollars):
- the same-input baseline (C1);
- the more-DFT baseline (L+);
- the cheap-solver variant (Q1-T2);
- the *same features computed classically* at 12 and 16 orbitals, and at n_b (projected from E2's
  fit).

The last one matters most: at matched quality, the real competitor is the classical solver
producing the identical features.

## Decision rules
**A crossover exists only if all of these hold under the central scenario:**
1. E2 found a confirmed wall, and n_b is set.
2. The circuit actually run fits: ≤ 316 logical qubits and ≤ 3.16 × 10⁷ operations.
3. The recounted runtime fits the 30-day budget.
4. Quantum ranking at matched dollars beats the whole classical front by more than one pair
   (CI lower bound > 0) at ≥ 3 of ≥ 5 budgets, including the $0.405 M operating point.
5. The quantum cost at n_b is below the projected cost of computing the same features classically
   at n_b.
6. E3's gain still rises from 12 to 16 orbitals.

**Outcomes:**

| Outcome | What happens |
|---|---|
| Pass | quantum claim at most CONDITIONAL-GO, with the wall size, feature set, scenario, readout and required logical error p_L* as stated conditions |
| Fail | quantum claim NO-GO (final or provisional per the verdict standard); E3's classical result is reported on its own |
| E2 found no wall | E5.1 is run at a hypothetical 18 orbitals, labelled so; H5 fails without further work |
| Passes only on the optimistic scenario | reported, never counts |

**Why these thresholds.**
- **Matched dollars:** this is the axis a partner decides on.
- **≥ 3 of 5 budgets, including the operating point:** one lucky budget is not a crossover.
- **Central scenario:** it is the geometric midpoint of the frozen hardware band. The optimistic end
  is a hope, not a plan.

## Pitfalls and controls
- **Projected vs measured.** Every quantum number is projected, and every classical number is
  measured or cited. Rows are never mixed.
- **Circuits that do not fit.** A runtime quoted for a readout whose circuit exceeds the operation
  cap is an inconsistent count and enters no gate.
- **Encoding claims.** Detection-only or small-distance demonstrations (Helios 2:1, Sqale distance
  2) are not surface-code logical qubits at the needed error rate. They are reported as what they
  are.
- **Roadmap ≠ delivery date.** The hardware map shows what each roadmap would need to deliver, not
  when it will.
- **Cherry-picked parameters.** The quantum route is priced at the median of the wall clusters, not
  of the easier full set.
- **Quality above 16 orbitals is assumed.** It is held flat beyond the measured range, and labelled
  so.

## Budget and fallbacks
15 core-h, 2 GB, 3 wall-days, 2.5 M tokens. If the quantum claim ended earlier, only E5.2 is
produced.

## Do not
- Use the optimistic scenario alone.
- Mix projected and measured rows.
- Price shots at any precision other than the one E3/E4 settled.
- Change the budget, the scenarios, the dollar rates or the form of the resource model. Only
  measured parameters are substituted.
- Present a hardware mapping as a delivery date.

## Locked rules this experiment reads
Rule text lives in `PROPOSAL.md` (P0 and P5 sections) and `frozen_definitions.md`; it is never
restated here. `P0.qpu_time_central` · `P0.envelope_fit` · `P0.gray_zone` · `P0.stop_rule` ·
`P5.H5.threshold` · `P5.H5.not_optimistic_alone` · `P5.gray_zone` · `P5.stop_rule` ·
`def.cost_axis` · `def.ftqc_scenarios` · `def.resource_model` · `def.qpu_budget` ·
`def.core_set_of_record`
