---
source_type: skill-report
source_date: 2026-06-01
arxiv_id: "2605.21346"
fetch_method: arxiv_api + ar5iv
partial_fetch: false
fetch_date: 2026-06-01
---

# Paper Content — Danaci et al. 2605.21346

**Title:** Evidence of Quantum Machine Learning Advantage with Tens of Noisy Qubits  
**Authors:** Bayraktar Danaci, Nana Liu, et al.  
**Affiliations:** University of New South Wales (Sydney); Shanghai Jiao Tong University  
**arXiv:** 2605.21346  
**Submitted:** 2026-05-28  
**Venue:** arXiv preprint (quant-ph + cs.LG)

## Abstract

We provide evidence for a quantum machine learning advantage using coherent multi-qubit
measurements on quantum-native data. We demonstrate a separation between coherent quantum
processing strategies and fixed-measurement classical strategies at approximately 30 to 40
noisy qubits. The advantage is established theoretically in a learning model where the data
is encoded in quantum states, and confirmed numerically in circuit simulations under realistic
noise. This regime is within reach of near-term neutral-atom and superconducting hardware.

## Introduction

Quantum machine learning (QML) has long promised advantages over classical methods, but
most demonstrations have relied on classical-data inputs processed through quantum feature
maps — a setting where dequantization arguments and strong classical baselines often close
the gap. This work takes a different approach: we study QML in the quantum-native data regime,
where inputs are quantum mechanical objects (quantum states) arising from physical measurements,
quantum sensors, or quantum communication protocols.

In this regime, the question of dequantization does not arise in the same form: there is no
classical representation of the input states to which an RFF approximation can be applied.
The relevant comparison is between coherent multi-qubit measurements (quantum processing) and
single-qubit or fixed-basis measurements followed by classical post-processing.

## Methods

We define a binary classification task over quantum-state inputs drawn from two separable
quantum distributions that are indistinguishable under any fixed-measurement strategy but
distinguishable under coherent processing. The coherent learner applies a parameterized
quantum circuit of depth O(1) followed by a multi-qubit measurement; the fixed-measurement
baseline applies independent single-qubit measurements in a fixed basis followed by a
classical SVM or MLP.

Circuit family: hardware-efficient ansatz with nearest-neighbor CZ gates on a 1D chain.  
Qubit range: 10 to 50 qubits.  
Noise model: depolarizing noise at p = 0.1% to 1% per two-qubit gate.  
Shot count: 1000 shots per classification instance.

## Results

At 30 qubits with p = 0.3% two-qubit gate error, the coherent classifier achieves 92%
test accuracy vs 67% for the best fixed-measurement baseline (SVM with RBF kernel applied
to bitstring frequencies). The gap widens with system size up to ~40 qubits, then narrows
due to noise accumulation. At p = 1% the advantage disappears above 20 qubits.

The separation is statistically significant (p < 0.01, 50 random instances).

## Conclusions

We demonstrate that coherent processing of quantum-native data achieves a measurable,
statistically significant advantage over fixed-measurement classical strategies in the
30–40 qubit regime under realistic noise assumptions. This advantage is grounded in a
theoretically sound separation between the two processing classes and does not rely on
weak classical baselines.

Near-term feasibility: the required circuit depth (O(1)) and qubit count (30–40) are within
the roadmap of current neutral-atom and superconducting hardware platforms within 1–3 years.

## Related Work

- Huang et al. (2022), Nature Communications — quantum kernel geometric difference framework  
  [[cards/paper-cards/2112.00778]]
- Chen et al. (2021) — quantum advantage for learning quantum processes  
  [[cards/paper-cards/2112.00778]]

## Links

- [[01_claim_registry.md]]
- [[02_analysis.md]]
- [[04_final_review.md]]
