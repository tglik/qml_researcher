---
thread: materials_configuration_space/18_config_space_features
entry_path: use-case
source: 00_inputs/Materials_Configuration_Space_ML_Experiment_Guidelines.docx (Meir's brief) + 00_inputs/source.md + answers.md
source_hypothesis_card: none
format: 2
status: draft (format rewrite of HYPOTHESIS.md, 2026-10-21; science unchanged)
date: 2026-10-27
---

# Hypothesis — do quantum-computed electron features improve MOF screening for CO₂ capture?

## In one paragraph
Materials companies screen millions of candidate MOFs (porous crystals) to find ones that bind CO₂
strongly. The best screening models today are machine-learned from atom positions. We propose
adding a few numbers that describe **how the electrons at the metal site where CO₂ binds are
arranged**. These numbers come from a small quantum-chemistry problem that a future quantum
computer could solve. We compute them for a few thousand structures only, then train a fast model
that screens the millions without them. The claim: this improves the ranking of the best
candidates by **at least 10 %** on families of materials the model has not seen. **Key point:** at
every size we can run today, a classical computer computes these numbers exactly. So the first
question (do the features help?) is a classical experiment. Whether a quantum computer is
*needed* is a separate, second question.

## Background the reader needs
- **MOF (metal–organic framework).** A porous crystal made of metal atoms joined by organic
  linkers. CO₂ often binds at an exposed metal atom (an *open metal site*). (Moghadam, Chung &
  Snurr, Nature Energy 2024.)
- **Adsorption energy.** How strongly a molecule sticks to the material, in eV. More negative means
  stronger binding. This is the label we predict.
- **DFT (density functional theory).** The standard quantum-chemistry approximation for computing
  energies. Our labels are DFT values (PBE+D3). DFT is known to be least reliable for metals whose
  electrons are strongly correlated (next bullet).
- **Open-shell transition metal / strong correlation.** Metals like Cu, Fe, Co, Ni and Mn have
  partly filled d orbitals. Their electrons can sit in several arrangements with nearly the same
  energy, and simple models that assume one arrangement go wrong there. Computing these systems
  well is a classic target for quantum computers (Reiher et al., PNAS 2017).
- **Active space.** To make the problem small, keep only the ~12 most important orbitals around the
  metal and CO₂ and solve those exactly. This gives a Hamiltonian on 2 × 12 = 24 qubits.
- **Classical solvers for the same problem.** Exact diagonalization (exact up to ~16 orbitals) and
  DMRG (very accurate when correlation is mostly local; Chan & Sharma, Annu. Rev. Phys. Chem.
  2011). These are the classical route to the same numbers.
- **ODAC25.** Meta FAIR's public dataset of DFT calculations for CO₂, H₂O, N₂ and O₂ in about
  15,000 MOFs (2025).
- **UMA / eSEN.** Meta FAIR's machine-learned models that predict energies from atom positions,
  trained on very large DFT datasets (2025). The state of the art and our main baseline.
- **Top-k enrichment.** Of the k materials the model ranks best, the fraction that are truly in the
  top k. This is what a screening campaign cares about: which candidates get sent to expensive
  simulation and the lab.
- **Distillation.** Train a cheap "student" model to reproduce a stronger "teacher" model
  (Hinton, Vinyals & Dean, 2015).

## The algorithm
```
OFFLINE, once, on a core set of 10³–10⁴ MOF + CO₂ structures
  structure ─► cut out the local cluster: metal site + nearby framework atoms + CO₂
            ─► cheap classical quantum chemistry: pick the ~12 most important orbitals
            ─► [quantum computer] prepare the lowest-energy electron state of that cluster
            ─► measure ~23 numbers (the features)
            ─► train the teacher: baseline model + features ─► adsorption energy

SCREENING, 10⁶–10⁸ candidates, ~1 ms each, no quantum computer
  structure ─► student model (atom positions only, trained to mimic the teacher) ─► ranked list
```
The ~23 features, each a simple expectation value on the cluster's electron state:
- how many electrons sit in each active orbital (metal d, CO₂, ligand),
- how often a metal orbital holds two electrons at once (a measure of correlation),
- how strongly the metal's spin is aligned with the spins on CO₂ and on the linkers,
- the total spin of the cluster.

The exact list is fixed in the pre-registration (`def.feature_family`).

## Why this approach, and why built this way
**The proposer's reason:** CO₂ binding at an open metal site depends on how the metal's electrons
are arranged. For open-shell metals that arrangement is strongly correlated, which neither DFT nor
a geometry-based ML model captures directly. Features that describe it directly should carry
information the baseline lacks.

**Design choices and why:**
- **Physically grounded features, not a generic quantum circuit.** A generic variational circuit
  applied to ordinary descriptors has no reason to know anything about binding. The brief rules it
  out.
- **A small local cluster.** Binding happens at the site, and a small cluster fits on early
  fault-tolerant hardware.
- **Quantum features only on a core set, then a student.** The September screen showed that
  computing features for *every* candidate fails: preparing each cluster classically costs about
  as much as the DFT label itself, so a quantum step per candidate can never be cheaper than just
  running DFT. A core set keeps the quantum cost fixed while the screened set grows.
- **The baseline gets the same cluster.** It also receives cheap classical descriptors of that
  cluster. Any gain must then come from the expensive correlated calculation, not from showing the
  model extra information.
- **Held-out chemistry and held-out MOF families.** Random splits leak near-duplicate MOFs between
  training and test.

**What we already know.** The same brief ran in September with a weaker baseline (MAE 0.216 eV).
Its errors were spread evenly: no larger on open-shell metal sites than elsewhere (ratio
0.91–1.16). The stop was provisional because that baseline was not good enough to judge. A stronger
baseline (UMA/eSEN) is now available, which is the reason for this rerun.

**What must be true for the claim to hold.** Each link is tested by the hypothesis in brackets:
1. The best classical model's errors concentrate at open-shell metal sites. (H1)
2. The electron features fix part of those errors, beyond cheap descriptors of the same site, on
   unseen chemistry and MOF families. (H2)
3. The gain carries over to a fast student that screens from atom positions alone. (H3)
4. No classical solver computes the same features cheaply at the size where the gain appears. (H4)
5. An early fault-tolerant quantum computer computes them at a total cost that beats the classical
   alternatives. (H5)

Links 1–3 ask whether the features help; they are classical experiments. Links 4–5 ask whether a
quantum computer is needed.

## Hypotheses
**Precondition — the baseline is good enough.** A UMA/eSEN-class model fine-tuned on our ODAC25
subset reaches MAE ≤ **0.1275 eV** (1.5 × the published 0.085 eV) on a random split.
- *Why:* claims of "headroom" against a weak baseline mean nothing. This is the gap that left
  September's result provisional.
- *If it fails:* no verdict either way. We record the failing setup and pause.

**H1 — Errors concentrate where the features act.** With an adequate baseline, its error on
open-shell metal pairs is at least **2×** its error on the other pairs (95 % CI lower bound > 1.5×)
on at least 2 of 3 holdouts.
- *Why we expect it:* a weak baseline makes generic geometry errors everywhere, which can hide the
  site-specific ones. A stronger baseline removes the generic errors and may expose the
  site-specific ones.
- *Why test it:* it is the cheapest test that can end the program. If the errors are not
  concentrated at the site, there is nothing for the features to fix.
- *Disproof:* the ratio stays near 1.0, as in September.

**H2 — The features improve ranking.** Adding the electron features raises top-k enrichment by
**≥ 10 % relative** (95 % CI excluding 0, ≥ 3 seeds) over the same-input baseline. This must hold
on held-out chemistry (all Cu MOFs out, all Fe MOFs out) *and* on held-out MOF families, with the
features measured at realistic precision (±0.01, about 10⁴ shots each).
- *Why we expect it:* the features describe the electron arrangement that controls binding
  strength. The baseline sees only atom positions and cheap summaries.
- *Why test it:* this is the core claim. +10 % is about 3 more true hits per 100 candidates sent to
  DFT, the smallest gain the proposer says changes a campaign.
- *Disproof:* gain < 10 % or CI includes 0 on either holdout type; or the same number of random
  features gives the same gain; or the gain disappears at ±0.01 precision.

**H3 — The gain survives in the fast student.** A student trained with the teacher's features
ranks better than a student trained without them, by the same 10 % bar, using only atom positions
at test time.
- *Why we expect it:* the features act as extra training signal on the core set, and the student
  can absorb part of it.
- *Why test it:* screening millions of candidates needs a ~1 ms model. If the gain needs features
  for every candidate, we are back to the per-candidate design that was ruled out.
- *Disproof:* the two students tie.

**H4 — The features are hard to compute classically.** At some active-space size that is still
physically meaningful, no classical solver (exact diagonalization, DMRG, coupled cluster,
perturbation theory, ligand-field models, a learned emulator) reaches ~1 % feature accuracy within
the pre-registered budget, and classical cost grows faster than polynomially with size.
- *Why we expect it to fail:* at pore-site sizes, exact diagonalization and DMRG are cheap. An ML
  feature needs only ~1 % accuracy, far looser than the accuracy chemistry usually needs, and
  hardness at chemical accuracy does not imply hardness at 1 %.
- *Why test it anyway:* if it fails, H1–H3 still give a classical result, but no quantum claim
  survives.
- *Disproof:* a classical route reproduces the features to ~1 % at ≤ 1 % of the modelled quantum
  cost, at every size where the gain appears.

**H5 — A quantum computer wins on total cost.** Under the central hardware scenario (≤ 10³ logical
qubits, ≤ 10⁹ logical operations per circuit), the projected quantum pipeline gives better ranking
per dollar than the best classical pipeline. A crossover under the optimistic scenario alone does
not count.
- *Why we expect it:* the proposer's premise that early fault-tolerant machines can prepare these
  states and measure ~23 numbers for a few thousand structures within a campaign budget.
- *Why test it:* a partner needs a crossover curve (quality against total cost), not a qubit
  count.
- *Disproof:* no crossover inside the hardware envelope and campaign budget.

## Classical baselines
- **Main baseline:** UMA/eSEN-class model fine-tuned on ODAC25.
- **Same-input baseline (the comparison for H2):** the main baseline plus 47 cheap descriptors of
  the same cluster (mean-field occupations, charges and spins, second-order perturbation-theory
  occupations, a 5-orbital ligand-field calculation). The quantum features are added on top of
  this.
- **Random-feature control:** the same-input baseline plus 23 random numbers.
- **More DFT instead:** the same offline budget spent on more DFT labels.
- **Classical computation of the same features (for H4):** the solvers listed in H4, and a model
  trained to predict the features from cheap descriptors.

Fairness rule: whatever physical input the quantum features get, the classical baselines get too.

## Where the claim must hold
| | Tested here | Industrial target |
|---|---|---|
| Candidates screened | 10³–10⁴ (ODAC25 subset: ~1,300 labelled pairs, 98 MOF families) | 10⁶–10⁸ |
| Structures given quantum features | 10²–10³ | 10³–10⁴ (core set) |
| Active space | 12 orbitals (24 qubits), computed exactly on a classical machine | whatever size the gain needs, within 10²–10³ logical qubits |
| Features | ~23 numbers per structure, measured once, ±0.01 | same |
| Screening cost | ~1 ms per candidate, both sides | same |
| Offline budget | one 8-core workstation, no GPU | ~10⁴ GPU-hours + ~10⁵ DFT calculations per campaign, spendable on either side |
| Main metric | top-k enrichment on held-out chemistry and MOF families | same |
| Hardware | hardware-agnostic; three scenarios in the proposal | same |

## Known risks (raised before any data)
- **The labels are DFT, and DFT is weakest exactly at these sites.** The features describe the
  true electron arrangement, but the model is scored against DFT's answer. If DFT gets these sites
  wrong, better physics cannot raise the score. Correcting the labels themselves is a separate
  idea (quantum-corrected labels, the Q-LABEL track), not claimed here.
- **Classical solvers likely compute the features cheaply** at physically meaningful sizes (see
  H4). The most likely outcome is "the features help or not, and are classically free": a
  classical result and no quantum claim.
- **September found no headroom.** A stronger baseline may remove the remaining errors rather
  than concentrate them.
- **Little data in the group that matters.** Only 527 pairs from 40 MOF families have open-shell
  metal sites, so a true 2× effect clears the H1 bar only about half the time.

## Open points
- [UNVERIFIED] UMA access is granted, but the model has not been pulled on this machine.
  Fine-tuning it on ~1,300 pairs with 8 CPU cores is unmeasured.
- [ASSUMPTION] "Held-out MOF families" stands in for held-out topology. Topology labels are not in
  ODAC25, and joining another database costs about a week.
- [ASSUMPTION] The published 0.085 eV is per configuration; ours is per MOF–molecule pair (best
  binding frame). The 1.5× allowance absorbs part of this difference.

## Hypothesis IDs in the locked proposal
The locked `PROPOSAL.md` uses the September IDs: precondition = H0, H1 = H1, H2 = H2 + H6 + H4
(precision), H3 = H2d, H4 = H3, H5 = H5. The H1 threshold above is the gate of record (2×); the
earlier draft's 1.5× is reported but does not gate.

## Sources
- `00_inputs/Materials_Configuration_Space_ML_Experiment_Guidelines.docx`: Meir's brief
- `00_inputs/source.md`, `00_inputs/answers.md`: intake record
- `../SCREEN.md`, `../01_headroom_anatomy/VERDICT.md`: September screen and result
- `frozen_definitions.md` (`def.feature_family`, `def.c1_descriptors`): feature and descriptor lists
