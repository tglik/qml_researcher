id: qml-07
title: Rigorous supervised speedup
paper: Liu, Arunachalam & Temme, A rigorous and robust quantum speed-up in supervised machine learning (arXiv Oct 2020; Nature Physics 17, 1013, 2021)
link: https://arxiv.org/abs/2010.02174
type: Theory
cutoff: 2020-10-05
domain: qml
profile: formal

## expected_verdict
Supported (conditional theorem); no practical advantage claimed. Under the classical hardness of discrete log, no efficient classical learner beats random guessing by 1/poly, while SVM with quantum kernel estimation reaches 0.99 accuracy and is robust to additive sampling error. It needs a fault-tolerant computer running Shor-type circuits. The authors say the task "is not practically motivated". No independent proof check was found (tier C).

## I0
Can a kernel learner solve a discrete-log-based task efficiently under a stated hardness assumption?

## evidence
- Concept class C = {f_s} on x ∈ Z_p*: label depends on whether log_g x lies in an interval starting at s (Fig. 1).
- Theorem 1: assuming classical hardness of DLP, no efficient classical algorithm achieves 1/2 + 1/poly(n) test accuracy (reduction via Blum–Micali hardness of the most significant bit of log_g x).
- Theorem 2: SVM-QKE learns C with test accuracy ≥ 0.99, robust to i.i.d. additive noise in kernel entries from finite sampling.
- Feature map |φ(x)⟩ = 2^(−k/2) Σ |x·g^i⟩, k = n − t log n, prepared with a circuit using Shor's algorithm as a subroutine (Eq. 3, App. D.1).
- Access model: classical data only (no qRAM).
- Conclusion: "not practically motivated"; near-term relevance would need shallow, error-mitigated feature maps.

## intake
- Scope: an end-to-end exponential separation for a constructed classification task, with classical data access.
- Regime: fault-tolerant quantum computer; asymptotic in n = log2 p.
- Assumptions: DLP is classically hard; kernel entries estimated to additive error with polynomially many shots; the SVM margin argument holds under that noise.
- Falsifiers: a classical algorithm for DLP (refutes the assumption); an error in the reduction from learning to DLP; noise robustness failing at realistic shot budgets.

## screen
- Must flag: the separation is conditional on DLP; the task is artificial; implementation needs Shor-scale fault-tolerant circuits, not NISQ.
- Must not flag as a flaw: impracticality alone (the paper's claim is formal).

## retrieval
- Pre-cutoff must-finds: Havlíček et al. 2018 and Schuld & Killoran (heuristic quantum kernels); Kearns 1990 (cryptographic hardness of learning); Blum & Micali 1984; Servedio & Gortler 2004 (quantum vs classical learnability). Power of data (Nov 2020) is after the cutoff and must not appear in historical mode.
- Current mode: no claim-level adjudication in the inventory; 2406.07072 discusses trainability vs dequantization but does not test the theorem.

## designer
- A proof audit, not an experiment: verify the reduction (Theorem 1), the margin/robustness argument (Theorem 2), and end-to-end resources (circuit depth incl. Shor subroutine, shots for 0.99 accuracy).

## champion
- The best classical learner is bounded by Theorem 1; the meaningful comparator is a classical algorithm for DLP at the relevant n (number field sieve) to show the assumption's regime.

## panel
- Accept as a positive formal result. Request an explicit resource estimate; do not demand a NISQ demonstration.

## run
- Proof check only. Optional toy: small p, simulate the ideal kernel and confirm the SVM separates C; this cannot certify hardness.

## verdict
- Label: Supported (scoped, conditional); tier C (no external adjudication).
- Must say: conditional on DLP hardness; fault-tolerant only; not practical.
- Must not say: this shows near-term or practical quantum ML advantage; or the result is invalid because hardware cannot run it.

## audit
- Check: the 1/2 + 1/poly(n) bound; 0.99 accuracy; Blum–Micali citation; k = n − t log n; "not practically motivated" quote.

## variants
- Resource estimate for a cryptographically meaningful n; search for shallow feature maps with a similar hardness reduction (the paper's own outlook).
