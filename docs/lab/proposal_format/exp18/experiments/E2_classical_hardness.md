---
thread: materials_configuration_space/18_config_space_features
experiment: E2 (PROPOSAL.md phase P2)
tests: H4 (the features are hard to compute classically)
status: not started (no spend before E1's precondition and H1 are recorded)
depends_on: E1 (pass or in-between)
feeds: E3 (cost per cluster, convergence rate, the second cheap solver), E5 (Hamiltonian size, gap, overlap, entanglement)
budget: 2,790 core-h classical (≤ 1,170 of it only if a candidate wall appears); 14 GB peak; 23 wall-days; halt at 2×
code: P2_medium/
date: 2026-10-28
---

# E2 — Can classical solvers compute the features cheaply at every meaningful size?

## Question and why
We grow the active space from 6 to 44 orbitals. Is there a size where no classical solver
computes the 23 features to within 0.02 (about 1 % of their range) inside the budget? And does the
classical cost grow exponentially from there on?

If a classical solver reaches the features cheaply at every physically meaningful size, a quantum
computer adds nothing, whatever E3 shows. E2 also measures inputs that E3 and E5 need: the cost
and convergence rate per cluster (E3), and the size, energy gap and entanglement of each
Hamiltonian (E5).

A size counts as **physically meaningful** if it has at least 8 orbitals, including all five metal
d orbitals, two CO₂ orbitals and one orbital of a linker atom bound to the metal. Smaller spaces
leave out part of the binding chemistry.

## What we expect, and why
**H4 fails: classical solvers win.** One metal site plus CO₂ plus a few linker orbitals is a weakly
entangled system (entanglement entropy ≲ 1.5). DMRG should reach the features at bond dimension
≤ 256 up to 44 orbitals, and selected CI should pass at every size. Classical cost should grow
polynomially. The key point is that ML features need only ~1 % accuracy, far looser than the
accuracy chemistry usually needs, so hardness at chemical accuracy does not carry over.

## Design
**Clusters.** Built the same way as in E3, from the best-binding configuration.
- *Pilot:* 10 clusters, 2 per metal (Fe, Co, Ni, Cu, Mn), chosen near each metal's median size.
- *Main set:* up to 40 clusters, 8 per metal, sized from the pilot's cost. At least 20 are
  required.

**Size ladder.** 6, 8, … 16 orbitals solved exactly (CASCI). Above 16, the reference is DMRG run
until its two largest bond dimensions agree within 0.01.

**Classical solvers tried at every size** (each on the same cluster, orbitals and Hamiltonian):

| Solver | What it is |
|---|---|
| CASCI | exact diagonalization; reference up to 16 orbitals |
| DMRG | tensor-network solver; bond dimension 32 → 2,048; the main solver for the scaling fit |
| SHCI | selected configuration interaction (keeps only the important electron configurations) |
| MP2 / NEVPT2 | perturbation theory; gives orbital occupations only |
| CCSD | coupled cluster, with its density matrices read out |
| Ligand-field model | exact solve of the five metal d orbitals only |
| Learned emulator | a model predicting the features from the 47 cheap descriptors |
| AFQMC | quantum Monte Carlo; run only to confirm a candidate wall |

**Caps.** Each (cluster, size, solver) gets 16 core-h. On up to 10 candidate wall clusters, the
cap rises to 50 core-h, about one DFT calculation, which the campaign already pays per structure.
At every point we record cost, the bond dimension needed and the entanglement entropy.

**Steps.**

| Step | What | Output |
|---|---|---|
| E2.0 | install pyscf + block2 (WSL2; failed on native Windows in September) | smoke test |
| E2.1 pilot | mean field, orbital selection, small CASCI and DMRG on 10 clusters; power check for the scaling fit | cost per cluster; convergence count; smallest detectable growth rate b_min |
| E2.2 ladder | every solver at every size on the main set | cost vs size per solver; wall counts per size |
| E2.3 cheap solvers | the cheap solvers against the reference at every size | fraction of clusters within tolerance at ≤ 1 % of the reference cost; names E3's second cheap solver at 12 orbitals |
| E2.4 inputs for E5 | Hamiltonian norm λ, energy gap, overlap with mean field γ, entanglement, all per size | medians, split by wall / non-wall clusters |

## Decision rules
**Pilot gate.**
- The median cost per cluster for the mean field and orbital selection must be ≤ 4 core-h.
  Otherwise we shrink the cluster (≤ 40 atoms) and basis set once and re-run the pilot. A second
  miss blocks both E2 and E3's features.
- If the pilot cost × 1,308 pairs exceeds 2,400 core-h, E3 automatically uses its hard-pairs-only
  fallback.

**H4 passes only if all four hold:**
1. *A wall exists.* At some meaningful size n* ≤ 44:
   - at least 10 clusters have a converged reference;
   - on ≥ 50 % of them, no solver reaches 0.02 accuracy inside its cap;
   - the wall survives an AFQMC attempt.
2. *No cheap solver gets there.* No cheap solver reaches tolerance on ≥ 90 % of clusters at ≤ 1 %
   of the reference's cost, at the wall size.
3. *Cost grows exponentially.* We fit the DMRG cost against size, pooled across clusters. The
   exponential model must beat a power law by ΔBIC ≥ 6, with a growth rate at least the b_min fixed
   before the fit. The fit needs ≥ 4 sizes with ≥ 10 clusters each. The bond dimension needed must
   also rise with size.
4. *It matters at campaign scale.* The fitted cost curve crosses 5,000 core-h per structure (100 DFT
   calculations) at some size n_b ≤ 44. E5 prices the quantum route at n_b.

**What ends the quantum claim:**
- no wall up to 44 orbitals;
- a cheap solver at every wall size;
- AFQMC removes the wall.

The classical program then continues: E3 in full, E4.1 for the record, and only E5's sensitivity
table.

**Why these thresholds.**
- **0.02 tolerance:** about 1 % of each feature's range, the same scale as the measurement
  precision (±0.01). So the classical solver is held to exactly what a quantum computer would
  deliver.
- **1 % of reference cost:** a cheap solver at that price makes the expensive route irrelevant.
- **5,000 core-h:** at 10³ core structures, this is the campaign's entire DFT budget.

## Pitfalls and controls
- **Our machine's limit is not hardness.** A wall at 16–50 core-h on an 8-core box says something
  about this box. Classical hardness may be claimed only through the scaling fit, never from the
  cap.
- **No reference, no wall.** If the reference itself does not converge, the quantum answer could not
  be checked either. That point is "unmeasured" and never counts as a wall.
- **Small sizes say nothing about hardness.** At 8–10 orbitals DMRG covers the whole space, which
  makes it an exact solver, so those points are excluded from the fit. In practice the fit runs on
  12, 14, 16 and the wall size.
- **Too few points to fit a curve.** The smallest detectable growth rate is fixed from the design
  before any cost is plotted.
- **Energy is the wrong yardstick.** Tolerance is checked on the features, not on energies.
- **Memory.** Bond dimension 2,048 at 44 orbitals needs ~11 GB. If it does not fit, it is recorded
  as "not run on this box", never as a wall.

## Budget and fallbacks
- **Plan:** 2,790 core-h:
  - pilot 40;
  - ladder ≤ 1,300;
  - small-size DMRG for the fit 40;
  - cheap solvers 160;
  - inputs for E5 60;
  - wall confirmation ≤ 1,170, spent only if a candidate wall appears.
- **Resources:** 14 GB peak, 23 wall-days.
- **Fallbacks:**
  - If WSL2 fails, try conda-forge on Windows. If neither works within 2 days, H4 is BLOCKED; E3
    can still run on pyscf alone.
  - The main set is sized from the pilot.
  - The bond-dimension ladder is cut where a run exceeds the cap or memory.
- **If the owner cuts E2** (see the plan's open question 2), keep E2.0 and E2.1, plus E2.3 at
  12 orbitals. E3 needs them.

## Do not
- Train any model on adsorption labels or touch E3's models.
- Change E3's 12-orbital size.
- Use energies as the tolerance test.
- Report a wall without running the cheap solvers at that size.
- Skip recording bond dimension and entanglement at any point.

## Locked rules this experiment reads
Rule text lives in `PROPOSAL.md` (P2 section) and `frozen_definitions.md`; it is never restated
here. `P2.pilot.gate` · `P2.H3.wall` · `P2.H3.fit` · `P2.H3.projected_bar` ·
`P2.T2.cheap_routes` · `P2.gray_zone` · `P2.stop_rule` · `def.feature_tolerance` ·
`def.active_space_ladder` · `def.n_star_meaningful` · `def.cluster_protocol` ·
`def.c1_descriptors`
