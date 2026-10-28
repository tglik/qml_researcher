---
thread: materials_configuration_space/18_config_space_features
status: draft (format rewrite of PROPOSAL.md draft-r4, frozen 2026-10-25; science unchanged)
hypothesis: ../../hypothesis_format/exp18_HYPOTHESIS_v1.md
date: 2026-10-28
---

# Plan — quantum electron features for MOF/CO₂ screening

## Summary
We test whether adding ~23 numbers that describe the electrons at a MOF's metal site improves
the ranking of CO₂-capture candidates (see the hypothesis). The program runs six experiments, the
cheapest one that can end the program first. Experiments 1 and 3 ask whether the features help;
both are classical, because at every size we can run, a classical solver computes the features
exactly. Experiments 2, 4 and 5 ask whether a quantum computer is needed. Two results are already
in. The paper cost count (E0) puts the quantum pipeline **~4,200× over budget** under the central
hardware scenario. The September run found **no error concentration** at the metal sites, using a
weaker baseline. **Most likely outcome, stated in advance:** a classical result (the features help
or not, and are cheap to compute classically) and a NO-GO for the quantum claim.

**Status (2026-10-28):** E1 is running. The strong baselines (UMA, eSEN-ODAC25) are not yet
accessible to our account, and model tuning costs 30–100× the estimate. See
[before spending](#before-spending-open-questions-for-the-owner).

## What the result decides
| Verdict | Meaning | What we do |
|---|---|---|
| GO / CONDITIONAL-GO | features help, are hard to compute classically, and a quantum computer wins on cost under stated conditions | fund the fault-tolerant resource model and the partner proof package; approach CuspAI-class partners |
| NO-GO-FINAL | the mechanism fails, with an adequate baseline and enough statistical power | drop quantum electron features for MOF screening from the roadmap; keep any classical result; redirect to quantum-corrected labels (Q-LABEL) or another direction |
| NO-GO-PROVISIONAL | stopped, but the test was not strong enough to be final | no quantum spend until the stated reopening condition is met |

The best verdict this program can reach is **CONDITIONAL-GO**. At every size we can run, the
features come from a classical solver, so any quantum advantage is a projection, never a
measurement.

## Experiment sequence
```
E0 paper cost count ──► E1 baseline + headroom ──► E2 classical hardness ──► E3 feature gain
      (done)              (running; can end         (can end the quantum      (the core result)
                           the whole program)        claim)                          │
                                                                                     ▼
                                        E5 cost crossover (model) ◄── E4 precision + noise
```

**E0 — Can a quantum computer produce the features within a campaign budget? (done, paper only)**
- *Tests:* H5, first pass.
- *Why first:* it costs nothing to run and can end the quantum claim before any compute.
- *Result:* under the central scenario, the counted quantum runtime for one core set is
  1.08 × 10¹⁰ s against a 2.6 × 10⁶ s budget: **4,200× over**. The best corner (400 structures,
  ±0.1 precision, 18 orbitals) is still ~1,230× over at matched cost. The quantum claim narrows to
  a paper count; the classical experiments continue.
- *Details:* [`00_operating_point.md`](../../../../../qml_artifacts/experiments/materials_configuration_space/18_config_space_features/00_operating_point.md) §3.

**E1 — Is the baseline strong enough, and are its errors concentrated at the metal sites?**
- *Tests:* the precondition (baseline MAE ≤ 0.1275 eV) and H1 (error on open-shell metal pairs
  ≥ 2× the rest).
- *Why now:* it is classical, cheap, and can end the whole program. If errors are not concentrated
  where the features act, there is nothing for them to fix. It is also the test September could not
  finish.
- *Expect:* the precondition passes with a stronger backbone. H1 is unknown; September measured
  0.91–1.16.
- *If it fails:* precondition missed → BLOCKED, no verdict. H1 shown absent → program stops.
- *Cost:* 700 core-h, 8 days. *Details:* [E1_baseline_and_headroom.md](experiments/E1_baseline_and_headroom.md)

**E2 — Can classical solvers compute the features cheaply at every meaningful size?**
- *Tests:* H4.
- *Why here:* if a classical solver reaches ~1 % feature accuracy cheaply at every physically
  meaningful size, no quantum claim survives, whatever E3 shows.
- *Expect:* yes, the classical solvers win. DMRG should reach the features at small bond dimension
  up to 44 orbitals, and selected CI at every size. So H4 fails.
- *If it fails:* the quantum claim ends; the classical program continues.
- *Cost:* 2,790 core-h, 23 days (half the program). *Details:* [E2_classical_hardness.md](experiments/E2_classical_hardness.md)

**E3 — Do the features improve ranking on unseen chemistry and MOF families?**
- *Tests:* H2 (gain over the same-input baseline, beyond a random-feature control, on Cu-out,
  Fe-out and held-out MOF families) and H3 (the gain survives in a geometry-only student). Also
  checks whether a learned emulator or a cheap correlated solver recovers the gain.
- *Why here:* this is the core claim, and it needs the adequate baseline from E1.
- *Expect:* a tie is the prior (September found errors spread evenly), and the emulator recovers
  most of any gain.
- *If it fails:* no classical feature result; the quantum claim also ends (nothing to accelerate).
- *Cost:* 1,350 core-h, 7 days. *Details:* [E3_feature_gain.md](experiments/E3_feature_gain.md)

**E4 — Does the gain survive realistic measurement noise?**
- *Tests:* the precision part of H2 (gain at ±0.01). It checks the noise model E3 used against real
  finite-shot sampling at 24 qubits, and measures the shot and error-rate inputs that E5 needs.
- *Why here:* E3 uses a simple noise model, and E5's cost depends on the measured shot count.
- *If it fails:* the gain is precision-fragile, and the quantum claim ends.
- *Cost:* 805 core-h, 6 days. *Details:* [E4_precision_and_noise.md](experiments/E4_precision_and_noise.md)

**E5 — Does a quantum pipeline beat the best classical pipeline on cost?**
- *Tests:* H5 (quality per dollar against the full classical alternatives under three hardware
  scenarios).
- *Why last:* it is modelling only, and it needs measured inputs from E2–E4.
- *Expect:* fail. E0 already fails, and the proposal shows that no measured value can close the gap
  within the cost model.
- *Cost:* 15 core-h, 3 days. *Details:* [E5_cost_crossover.md](experiments/E5_cost_crossover.md) (also covers E0)

## Why this order
1. **Cheapest experiment that can end the program goes first.** E0 is free; E1 is classical and
   is the only experiment that can end the *whole* program.
2. **No quantum-side work before E1 passes.** Features are worthless if the baseline is weak or
   has no errors to fix.
3. **E2 before E3** (the screen's order): E2 can end the quantum claim without any ML.
4. **E4 and E5 last:** they refine and price a result that E3 must first produce.

## Shared setup (every experiment)
- **Data:** 1,308 MOF–adsorbate pairs from 98 MOF families (ODAC25 validation split). The label is
  the strongest-binding adsorption energy of each pair (PBE+D3 DFT). The hard group is 527 pairs
  (40 families) whose binding site is an open-shell metal (Fe, Co, Ni, Cu, Mn).
- **Splits:** September's `splits.json`, reused byte-identical. The random split is reported, never
  gating. The gating holdouts are Cu-out, Fe-out and held-out MOF families. 3 seeds.
- **Main metric:** top-k enrichment, with k = 20 % of the test pool (42–85 pairs). One pair in
  the top k is worth 4–8 % relative, so the 10 % bar is 1.3–2.5 pairs.
- **Statistics:** 95 % CI by cluster bootstrap over MOF families; tuning only inside the training
  split; each test pool touched once per model.
- **Machine:** one Windows workstation, 8 cores, 16.9 GB RAM, no GPU.
- **Exact definitions:** [`frozen_definitions.md`](../../../../../qml_artifacts/experiments/materials_configuration_space/18_config_space_features/frozen_definitions.md) (`def.*`).

Models compared (short names used in the experiment docs):

| Short name | What it is | Used in |
|---|---|---|
| **C0** baseline of record | best ML-potential baseline that passes the precondition | E1, E3 |
| **C1** same-input baseline | C0 + 47 cheap classical descriptors of the same cluster | E3 (the comparison for H2) |
| **Q1** proposed method | C1 + the 23 electron features (computed exactly) | E3 |
| **Q1n** | Q1 with measurement noise at ±0.1, ±0.01, ±0.001 | E3, E4 |
| **R1** random-feature control | C1 + 23 random features | E3 |
| **L+** more-DFT baseline | C1 trained on extra DFT labels bought with the same budget | E3, E5 |
| **D1** feature emulator | Q1 with the features predicted by a cheap model instead | E3 |
| **Q1-T2** cheap-solver variant | Q1 with features from coupled-cluster (and one more cheap solver) | E3 |
| **S-Q / S-C / S-C1** students | geometry-only students with features / without / with cheap targets | E3 |
| **Twin** | exact diagonalization / DMRG computing the same features | E2, E5 |

## Budget
| Experiment | Core-hours | Wall-days | Agent tokens (M) |
|---|---|---|---|
| E0 | 0 | 0 (done) | — |
| E1 | 700 | 8 | 1.8 |
| E2 | 2,790 | 23 | 3.7 |
| E3 | 1,350 | 7 | 4.3 |
| E4 | 805 | 6 | 1.3 |
| E5 | 15 | 3 | 2.5 |
| **Total** | **≈ 5,660** | **≈ 47** | **≈ 15.9** |

Any experiment that passes 2× its plan, or would exceed 16.9 GB memory, halts and asks the owner.

## Before spending: open questions for the owner
*Review notes from the format rewrite (2026-10-28), not part of the locked design.*
1. **The rerun's reason is not met yet.** The program reopened because a UMA/eSEN-class baseline
   became available. Our account is not authorised for either model (checked 2026-10-25), so E1
   runs on ungated MACE models. Even if E1 then finds no error concentration, that can only give a
   PROVISIONAL stop, so this rerun could end where September did. Get access first?
2. **E2 cannot change the quantum verdict.** E0 is already 4,200× over, and the proposal itself
   says no measured value can close the gap. E2 is half the budget (2,790 core-h, 23 days) and is
   expected to fail. Recommendation: run only its pilot (E2.1, needed for E3's cost inputs) and
   reduce E5 to the sensitivity table.
3. **If E2 stays, run E3 first.** A no-gain result in E3 ends the quantum question too, at half
   E2's cost. The screen's order would put the more expensive check first.
4. **Tuning cost is badly underestimated.** E1 measured 400–1,300 core-h for two baseline tunings,
   against 12.5 core-h planned. E3 uses the same tuning grid on ~10 models, so its 150 core-h
   classical estimate is likely off by the same factor.

## Where the rest lives
- Each experiment's design, decision rules and pitfalls: `experiments/E*.md`.
- Locked rule text (hashed at freeze): `PROPOSAL.md` lock blocks and `frozen_definitions.md`.
  Experiment docs cite lock ids; they never restate the hashed text.
- Revision history and review-panel responses: `change_log.md`, `PANEL_1*.md`.
- An agent implementing experiment k reads: this plan, `experiments/Ek_*.md` and
  `frozen_definitions.md`. Nothing else.
