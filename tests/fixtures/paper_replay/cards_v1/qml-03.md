id: qml-03
title: Quantum recommendation
paper: Kerenidis & Prakash, Quantum Recommendation Systems (arXiv Mar 2016; ITCS 2017)
link: https://arxiv.org/abs/1603.08675
type: Theory
cutoff: 2016-03-29
domain: qml
profile: advantage

## expected_verdict
Refuted for the exponential speedup; Supported for algorithm correctness. The poly(k) polylog(mn) quantum sampler is correct, but a classical algorithm with matched ℓ2-norm sampling access achieves poly(k) log(mn), so the separation is only polynomial.

## I0
Does a quantum recommendation algorithm reduce cost under specified matrix-access assumptions?

## evidence
- Claim: sample a recommendation from a rank-k approximation of an m×n preference matrix in O(poly(k) polylog(mn)) time, vs classical matrix-reconstruction methods that run in poly(mn) (Abstract, §1).
- Assumptions: the preference matrix has a good rank-k approximation with small constant k, and users of a type agree on high-value items (§1, §4); entries are stored in a binary-tree data structure (Thm 5.1) giving quantum access to row states in polylog(mn) time, O(w log²(mn)) memory.
- Core primitive: singular value estimation in O(polylog(mn)/ε) (Thm 5.2) + projection onto the top singular subspace; output is a sample, not the full row.
- Recommendation quality: subsampling theorems (Thm 4.1–4.3) + Thm 3.3 bound bad-recommendation probability for most users.
- Authors' own caveats: HHL-style results need care about input assumptions and whether the output solves the classical problem (§1.2).
- No numerics, no hardware.

## intake
- Scope: sampling one good recommendation for a user, not reconstructing the matrix.
- Regime: low-rank preference matrices; data already in a QRAM-style tree data structure; large m, n with constant k.
- Assumptions: low-rank + agreement-on-high-values model; polylog-time quantum access to the data structure; classical comparator = full reconstruction.
- Falsifier: a classical algorithm given the same data structure (which also supports ℓ2-norm sampling) samples from the low-rank row in time polylog in m, n.

## screen
- Must flag: the speedup is measured against classical reconstruction, which solves a harder task; the data structure gives classical sampling power too; output is a sample, not the vector.
- Must request: the best classical algorithm with matched sampling/query access (FKV-style low-rank sampling).

## retrieval
- Pre-cutoff must-finds: HHL and Aaronson's "read the fine print" caveats; Frieze–Kannan–Vempala (2004) length-squared sampling for low-rank approximation (pre-cutoff but not cited by the paper: the key test of whether retrieval finds the strongest comparator); Achlioptas & McSherry subsampling (Thm 4.1 source); Drineas–Kerenidis–Raghavan competitive recommendation systems.
- Current-mode critique: Tang 2018: classical ℓ2-sampling algorithm in O(poly(k) log(mn)); "Kerenidis and Prakash's algorithm does not in fact give an exponential speedup."

## designer
- A complexity comparison, not an experiment: list each resource (data-structure build, query access, singular-value threshold, output type) for both algorithms under the same access model.
- Success criterion for an exponential separation: the classical lower bound under matched sampling access is poly(mn).

## champion
- FKV-style / Tang quantum-inspired sampler using the same tree data structure. Classical reconstruction (SVD, alternating minimization) is the wrong comparator.

## panel
- Flaw: unmatched access model. Repair: restate the claim as "exponential over reconstruction-based methods" or prove a lower bound under sampling access.

## run
- Theory: check the dependency chain Thm 5.1 → 5.2 → 4.3 → 3.3. No numerical result can certify the speedup; optional toy check that ℓ2 sampling from a small low-rank matrix matches the target distribution.

## verdict
- Label: Refuted (exponential separation); Supported (algorithm correctness and polylog quantum runtime).
- Must say: the remaining gap is polynomial (Tang's poly(k) has much higher degree); the classical result needs the same strong input assumptions.
- Must not say: the quantum algorithm is wrong; or quantum-inspired algorithms are fast in practice.

## audit
- Check the quoted complexities: quantum O(poly(k) polylog(mn)); classical O(poly(k) log(mn)); KP Thm 5.1 memory O(w log²(mn)).
- Check that Tang's Theorem 1 uses the data structure of KP (Prop. 3.2 / §3), i.e. matched access.

## variants
- Remove sampling access (e.g. data arrives as a stream with no tree) and ask whether any separation reappears; or a high-rank regime where poly(k) dominates.
