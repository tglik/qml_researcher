---
thread: materials_configuration_space/18_config_space_features
experiment: E1 (PROPOSAL.md phase P1)
tests: precondition (baseline adequacy), H1 (error concentration)
status: running since 2026-10-25
budget: 700 core-h classical, 0 quantum; 10 GB peak; 8 wall-days; halt at 1,400 core-h
code: P1_toy/
date: 2026-10-28
---

# E1 — Is the baseline strong enough, and are its errors concentrated at the metal sites?

## Question and why
Two questions, both classical:
1. **Precondition:** does a strong ML-potential baseline predict adsorption energy well enough
   (MAE ≤ 0.1275 eV) that its mistakes mean something?
2. **H1:** with that baseline, is its error on the open-shell metal pairs at least twice its error
   on the other pairs?

The electron features can only help where the baseline is wrong. If the errors are spread evenly,
there is nothing for the features to fix, and the program stops here, before any quantum
chemistry is run. September asked the same question but could not answer it: its baseline
(MAE 0.216 eV) was too weak to judge.

## What we expect, and why
- **Precondition:** pass. The published eSEN model reaches 0.085 eV on ODAC25. The bar is 1.5× that,
  to allow for our per-pair label (see pitfalls).
- **H1:** unknown. September measured ratios of 0.91–1.16 (no concentration). The argument for a
  different answer now: a weak baseline makes generic geometry errors everywhere, which can hide
  site-specific ones, and a stronger baseline removes the generic errors first.

## Design
**Data.** 1,308 MOF–adsorbate pairs from 98 MOF families. The label is the strongest-binding
adsorption energy over each pair's configurations. The hard group is 527 pairs (40 families)
whose binding site is Fe, Co, Ni, Cu or Mn.

**Splits.** September's splits, byte-identical. The random split selects the baseline. The H1
gating holdouts are Cu-out, Fe-out and held-out MOF families, which contain only 16, 6 and 8 hard
families. Co/Ni/Mn-out is reported only. 3 seeds.

**Baseline candidates.** Each backbone is a pretrained ML potential, used in up to four ways:

| Variant | How it predicts adsorption energy |
|---|---|
| B0 zero-shot | E(MOF + molecule) − E(empty MOF) − E(molecule), straight from the potential |
| B1 | gradient-boosted trees on simple descriptors + the B0 energy + pooled atom embeddings |
| B2-head | a small readout trained on the frozen backbone's per-atom features |
| B2-full | full fine-tune, 5 epochs; only if the probe (E1.0) allows it |

The backbones are tried in order, best first:
1. eSEN-ODAC25 or UMA. Not accessible to our account yet.
2. MACE-MPA-0 (MIT licence; in use).
3. MACE-OMAT-0. Blocked until the owner accepts its licence.
4. MatterSim, if the others miss.

September's baseline (MACE-MP-0 + trees) is re-run unchanged as an anchor. It must reproduce
0.216 eV within ±0.005 eV, or E1 stops on reproducibility.

**Steps.**

| Step | What | Output |
|---|---|---|
| E1.0 probe | time a forward and backward pass on 10 structures; check whether our 98 MOFs were in each backbone's training data | whether B2-full runs (≤ 5 s per structure); a per-MOF exposure flag |
| E1.0b power table | before any real result: simulate how often the H1 test passes at a true ratio of 1.0×, 2.0× and 2.5×, at the real hard-family counts | probability of pass per holdout; printed before E1.1 |
| E1.1 precondition | all candidates on the random split | pair-level MAE; the best one becomes **C0** |
| E1.2 H1 | C0 (and every other passing candidate) on the three gating holdouts | hard/soft MAE ratio with a bootstrap CI over MOF families |
| E1.3 oracle repair | replace the hard group's predictions with the true labels; compare with repairing a random same-size group, and a group matched on top-k membership | gain in top-k enrichment, minus the larger control gain |
| E1.4 data ladder | the H1 ratio at 25, 50, 75 and 100 % of the training data | trend only (descriptive) |

E1.3 asks a narrower question: if we fixed the hard group perfectly, would ranking improve more
than by fixing any group of that size? If yes, quantum treatment can later be limited to the hard
group (400 structures instead of 1,000).

**Tuning.** One grid for every tree model (144 configurations), chosen by grouped 5-fold
cross-validation inside the training split. The same grid is reused for every model in E3.

## Decision rules
| Outcome | Condition | What happens |
|---|---|---|
| Precondition fails | best seed-mean MAE > 0.1275 eV on the random split | **BLOCKED**: no verdict; record the failing setup and pause |
| Near miss | 0.1275 < MAE ≤ 0.1375 eV, or a lucky pick (see pitfalls) | **BLOCKED**, ask the owner; the bar is never moved after seeing the number |
| H1 passes | ratio ≥ 2.0 and CI lower bound > 1.5 on ≥ 2 of 3 holdouts | continue to E2/E3 |
| H1 shown absent | ratio < 1.3 on all 3 holdouts and CI upper bound < 2.0 on all 3 | **program stops** (FINAL or PROVISIONAL, below) |
| H1 in between | anything else | continue to E2/E3, but limiting to the hard group is not allowed, the partner package is dropped, and H1 is reported as "not shown" |
| Hard-group limit allowed | H1 passes and E1.3's gain beats the larger control by ≥ 5 points on ≥ 2 of 3 holdouts | quantum treatment of 400 hard structures instead of 1,000 |

"Shown absent" is **FINAL** only if two things hold. First, the baseline is an eSEN/UMA-class
model run here. Second, our MOFs are verified absent from its training data. Otherwise it is
**PROVISIONAL**, with the reopening condition "re-run E1.1 and E1.2 with eSEN/UMA once access is
granted". Under current access, any stop is PROVISIONAL.

**Why these thresholds.** 2×: by September's arithmetic, a group whose error is less than twice the
rest cannot carry a 10 % ranking gain even if repaired perfectly. 1.3: below this, no holdout comes
near 2×, even with the wide intervals that 6–16 families give. So a miss is a real absence, not a
power problem.

## Pitfalls and controls
- **Small samples.** With 6–16 hard families per holdout, bootstrap intervals are wide. A true 2×
  effect would clear the CI bar only about half the time even with all 40 hard families, and less
  often per holdout. The power table (E1.0b) is printed first, so a
  "not shown" result is read correctly.
- **Memorisation.** If a backbone saw these MOFs in pretraining, a good MAE can mean memorisation.
  The exposure check (E1.0) flags this. eSEN's training manifest is behind the same access gate, so
  expect "unverifiable".
- **Lucky pick.** Choosing the best of ~10 candidates on one split flatters the winner. If the
  winning margin is < 0.01 eV and its held-out-family MAE is > 0.1375 eV, treat it as a near miss.
- **A stronger baseline found later.** If a better-scoring candidate appears after H1 is read, H1 is
  re-run on it before any E3 data.
- **Label definition.** The published 0.085 eV is per configuration; ours is per pair (the best
  configuration). The 1.5× allowance absorbs part of the difference. Report both numbers.
- **DFT labels.** Errors are measured against DFT, which is itself weakest at open-shell metals.
  E1 measures headroom against DFT, not against the true chemistry.
- **Missing empty-MOF references.** 7 of 1,308 pairs (0.5 %) use an adsorbate-removed frame
  instead of a relaxed empty MOF. Flagged; below the 10 % limit.

## Budget and fallbacks
- **Plan:** 700 core-h, 10 GB peak, 8 wall-days; halt and ask the owner at 1,400 core-h.
- **Fallbacks:** if full fine-tuning is too slow, use B2-head, then B1. If the checkpoint will not
  load, E1 is BLOCKED, not a NO-GO.
- **Measured so far:** one tree-model tuning costs 400–1,300 core-h for the two tuned baselines,
  against 12.5 core-h planned. A budget guard now projects the holdout cost from the random-split
  run and stops before the 1,400 core-h halt.

## Do not
- Build clusters or compute any electron feature (that starts in E2/E3).
- Change the splits, k, seeds or the hard-group definition.
- Gate H1 at the hypothesis draft's 1.5× (the gate of record is 2×).
- Re-run with other seeds or redefine the hard group to rescue an in-between result.

## Locked rules this experiment reads
Rule text lives in `PROPOSAL.md` (P1 section) and `frozen_definitions.md`; it is never restated
here. `P1.H0.threshold` · `P1.feasibility.finetune` · `P1.H1.threshold` · `P1.H1.absent` ·
`P1.A3.license` · `P1.gray_zone` · `P1.stop_rule` · `baseline.adequacy` · `splits.definition` ·
`def.leakage_rule` · `def.h1_ratio_procedure` · `def.holdout_resolution` · `def.random_control_R1`
