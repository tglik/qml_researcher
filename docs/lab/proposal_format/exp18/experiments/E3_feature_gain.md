---
thread: materials_configuration_space/18_config_space_features
experiment: E3 (PROPOSAL.md phase P3)
tests: H2 (gain, incl. held-out families and precision), H3 (student), H4 at the gain level (cheap routes)
status: not started
depends_on: E1 (C0 and its tuning grid), E2.1 pilot (cost and convergence per cluster), E2.3 (names the second cheap solver), E4.1 (measured noise factor V)
budget: 1,200 core-h feature computation + 150 core-h models; 8 GB peak; 7 wall-days; halt at 2×
code: P3_real/
date: 2026-10-28
---

# E3 — Do the electron features improve ranking on unseen chemistry and MOF families?

## Question and why
**Main question (H2):** adding the 23 electron features to a baseline that already sees the same
cluster: does it raise top-k enrichment by ≥ 10 %, on held-out chemistry *and* held-out MOF
families?

**Four follow-up checks.** Each one can end the quantum claim even if the main answer is yes:
1. *Precision:* does the gain survive measurement noise of ±0.01?
2. *Cheap emulator:* can a cheap model predict the features well enough to recover the gain?
3. *Cheap solver:* can a cheaper classical method (coupled cluster) supply the features instead?
4. *Student (H3):* does the gain reach a fast model that sees atom positions only?

This is the core claim of the program. Note: at 12 orbitals a classical solver computes the
features exactly, so E3 is a classical experiment. A yes means "this physics information is useful
for screening". It does not yet mean a quantum computer is needed; that is E2 and E5.

## What we expect, and why
- **Main question: a tie.** September found the baseline's errors spread evenly across metal types,
  and a related experiment (exp 12) also tied. If E1 finds no error concentration, a tie is
  near-certain.
- **Emulator:** if there is a gain, the descriptor-based emulator recovers most of it. Electron
  occupations are smooth functions of the cheap mean-field occupations; spin correlations less so.
- **Cheap solver:** coupled cluster reproduces the features for Cu/Ni-like sites and misses them
  for high-spin Fe/Mn.
- **Student:** ties with the student trained without features.

## Design
**Feature generation (E3.0).** For each of the 1,308 pairs, we build the cluster around the metal
site (from the best-binding configuration) and run a mean-field calculation. We then select the 12
most important orbitals and solve them exactly (CASCI) to get the 23 features. The same mean field
gives the 47 cheap descriptors. A cluster that does not converge is dropped from *every* model, and
the counts are reported per group and holdout.

**Splits.** These are the same as E1. The gating holdouts are Cu-out, Fe-out and held-out MOF
families; the random split and Co/Ni/Mn-out are reported only. 3 seeds. Each model is trained at
25, 50, 75 and 100 % of the training MOF families (the training ladder).

**Models compared.** All tree heads use E1's tuning grid. The proposed method has nothing to tune,
so every classical model gets at least as much tuning.

| Short name | What it is | Role |
|---|---|---|
| C0 | baseline of record from E1 | reference; the C0 → C1 gap is reported, never gating |
| C1 | C0 + 47 cheap descriptors of the same cluster | **the comparison for every gate** |
| Q1 | C1 + 23 exact electron features | proposed method |
| R1 | C1 + 23 random functions of the C1 descriptors | "any 23 extra features" control |
| Q1n | Q1 with noise at ±0.1, ±0.01, ±0.001 added to the features | precision check |
| D1a / D1b / D1b′ | Q1 with features predicted from geometry (D1a) or from the 47 descriptors (D1b trees, D1b′ kernel ridge) | cheap-emulator check |
| Q1-T2 (+ T2′) | Q1 with features from coupled cluster (+ the best other cheap solver named in E2.3) | cheap-solver check |
| L+ | C1 trained on extra DFT labels bought with the feature budget | budget-matching check |
| S-C / S-Q / S-C1 | geometry-only students: no extra targets / features as extra training targets / cheap descriptors as extra targets | student check (H3) |
| Q2 | features alone + small head | descriptive only: is the information there at all |

**Steps.**

| Step | What | Answers |
|---|---|---|
| E3.0 | compute features and descriptors for all pairs; measure cost per cluster | inputs; ≤ 15 % unconverged expected |
| E3.1 | C0, C1, Q1, R1 (+ Q2) on all holdouts and training sizes | H2 main question |
| E3.2 | Q1n at each noise level (re-read later at the noise factor E4 measures) | precision |
| E3.3 | D1a, D1b, D1b′; fraction of Q1's gain each recovers, with CI | cheap emulator |
| E3.3b | Q1-T2 (+ T2′) on all pairs; fraction of gain recovered | cheap solver |
| E3.4 | three students; inference time per candidate | H3 |
| E3.5 | L+ curve; and Q1 at 50 % data vs C1 at 100 % data | budget matching |
| E3.6 | C1 vs C0 | reported, never gating |
| E3.7 | Q1 at 6, 8, 10, 12, 14, 16 orbitals | does the gain grow with size (input to E5) |
| E3.8 | gain at k = 10, 25, 50 and default; extra true hits and DFT calculations saved | translation into the partner's units |

## Decision rules
**The classical feature claim is shown only if all four hold:**
1. *Chemistry:* Q1 beats C1 by ≥ 10 % (CI lower bound > 0) on Cu-out or Fe-out, and by ≥ 5 %
   (point) on the other one.
2. *MOF families:* Q1 beats C1 by ≥ 10 % (CI lower bound > 0) on held-out families.
3. *Random control:* on each counted holdout, Q1 beats R1 (CI lower bound > 0). If R1 itself
   gains ≥ 10 % there, that holdout counts as a "capacity effect", not a feature effect.
4. *Training ladder:* on each counted holdout, the gain is ≥ 5 % at two or more of the three smaller
   training sizes.

**Then each follow-up check must pass for the quantum claim to stay open:**

| Check | Passes if | If it fails |
|---|---|---|
| Precision | Q1n at ±0.01 still ≥ 10 % (CI > 0) on every counted holdout | gain is precision-fragile; quantum claim ends. If it holds only at ±0.001, E5 prices 100× more shots |
| Cheap emulator | D1a and the better of D1b/D1b′ each recover < 50 % of the gain (CI upper bound < 50 %) | features are learnable from cheap inputs; quantum claim ends, classical result stands with the emulator |
| Cheap solver | Q1-T2 (+ T2′) recovers < 50 % (same rule) | a seconds-scale classical method carries the gain; quantum claim ends |
| Student (H3) | S-Q beats S-C by ≥ 10 % (CI > 0) on held-out families and ≥ 1 chemistry holdout, and beats S-C1 (CI > 0) | the gain needs features for every candidate, the design ruled out on cost; quantum claim ends |
| Budget matching | Q1 at 50 % data beats C1 at 100 % data | any positive verdict is capped at CONDITIONAL |

In the recovery checks, a point estimate below 50 % with a CI that crosses 50 % reads "not
shown", never "pass".

**Other outcomes:**
- **Passes on one holdout type only, or fails the ladder:** "not shown in the tested range". No
  quantum claim. E4.1 still runs for the record, and E5 shrinks to its sensitivity table.
- **Tie everywhere:**
  - With tight intervals (CI half-width ≤ 2 pairs), the result is "shown absent": the baseline
    already carries this information at 12 orbitals.
  - With wider intervals, it is "not shown". This is the expected form at this sample size.
- **More than 15 % of clusters unconverged:** BLOCKED.
- **After E3 the program ends at the verdict stage** if the quantum claim has ended *and* E2 found
  no classical wall. Nothing is left for E4/E5 to decide.

**Why these thresholds.**
- **10 %:** at the observed enrichment (~0.3), this is about 3 more true hits per 100 candidates
  sent to DFT, or ~9 % fewer DFT calculations for the same yield. The proposer named it as the
  smallest gain that changes a campaign.
- **Second chemistry holdout ≥ 5 %, not 10 %:** Fe-out has only k ≈ 42–51 pairs, so a full bar on
  both would cut power below what E1 accepts. Requiring the same direction still halves the
  false-positive rate.
- **Chemistry and families both required:** we read three holdouts, so "any one passes" would
  triple the false-positive rate.
- **50 % recovery:** if a cheap route gets half the gain, the expensive computation is not what
  carries it.
- **Tie = one pair:** one pair entering or leaving the top k is the metric's resolution (4–8 %
  relative).

## Pitfalls and controls
- **Coarse metric.** One pair is worth 4–8 %, so the 10 % bar is 1.3–2.5 pairs. Realistic outcomes
  are "pass" or "not shown"; "shown absent" needs tight intervals that this sample size rarely
  gives.
- **More features, better fit.** Any 23 extra features can help a tree model. R1 separates that
  from the electron features.
- **Information already in the inputs.** The features are computed from the same geometry the
  baseline sees, so a cheap model may learn them. D1 measures how much.
- **Non-random dropouts.** Open-shell clusters fail to converge more often. If the hard group's
  dropout rate is > 2× the rest on a holdout, its result is reported "on the convergent subset (x %)".
- **Student input is chosen by the label.** Students see the best-binding configuration, which a
  real screen does not know in advance. The ~1 ms per candidate does not include finding that
  configuration, so it is not shown here. A descriptive re-run with a label-free configuration is
  reported.
- **Top 20 % is not the real use case.** A real campaign selects ≤ 0.1 % of candidates, which this
  data cannot test. The k-curve (E3.8) shows whether the gain sits in the tail or the bulk.
- **Pretrained backbone.** If C0's backbone saw these MOFs in pretraining, the held-out families
  are held out from the head only, not from the backbone. Every sentence says so.
- **Noise model.** E3.2 assumes Gaussian noise with a planning variance factor of 1. E4 measures the
  real factor per observable, and Q1n is re-read at it, without re-tuning.
- **DFT labels.** All gains are measured against DFT, which is weakest at the sites the features
  describe.

## Budget and fallbacks
- **Plan:** feature computation 1,200 core-h (6 GB); models 150 core-h (8 GB); 7 wall-days; halt at
  2×.
- **Fallbacks, in order:**
  1. If the E2 pilot projects > 2,400 core-h for all features: exact features for hard pairs only,
     mean-field features for the rest, applied identically to every model.
  2. A smaller basis set and smaller clusters.
  3. Cut E3.7 at 14 and 16 orbitals.
- **Risk:** E1 measured tree tuning at 30–100× its estimate. E3 tunes ~10 models on the same grid,
  so 150 core-h is likely too low. Re-estimate from E1's measured cost before E3 starts.
- **Dependency on E2:** the second cheap solver (T2′) is named in E2.3. If E2 is cut to its pilot,
  E2.3 must still run at 12 orbitals, or T2′ is dropped and the cheap-solver check uses coupled
  cluster alone.

## Do not
- Change k, splits, seeds, the 12-orbital size, the feature tolerance, the noise ladder or the
  tuning grid after any E3 number is seen.
- Gate anything on Q1 vs C0. Every gate is against C1.
- Score any model on a test pool more than once.
- Train emulators or students on test pairs.
- Fill in E4's measured noise factor before E4 runs.
- Interpret results. That is the verdict writer's job.

## Locked rules this experiment reads
Rule text lives in `PROPOSAL.md` (P3 section) and `frozen_definitions.md`; it is never restated
here. `P3.H2.threshold` · `P3.H6.threshold` · `P3.H2.control` · `P3.ladder_rule` ·
`P3.claim.pass` · `P3.H4.threshold` · `P3.I3.emulator` · `P3.I3.cheap_route` · `P3.H2d.student` ·
`P3.gray_zone` · `P3.stop_rule` · `def.feature_family` · `def.cluster_protocol` ·
`def.c1_descriptors` · `def.random_control_R1` · `def.emulator_D1` · `def.student_arms` ·
`def.more_dft_arm` · `def.epsilon_ladder` · `def.min_gain` · `def.tie_band` ·
`def.holdout_resolution` · `def.enrichment_metric` · `def.ci_method` · `def.training_size_ladder` ·
`def.leakage_rule`
