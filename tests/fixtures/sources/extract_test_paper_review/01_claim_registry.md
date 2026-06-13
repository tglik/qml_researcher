---
source_type: skill-report
source_date: 2026-06-01
paper_id: "2605.21346"
claim_counts:
  TOP: 3
  SUPPORT: 4
  GENERAL: 2
  MOTIVATIONAL: 2
  VAGUE_FLAGS: 0
---

# Claim Registry — Danaci et al. 2605.21346

## TOP Claims (primary advantage claims)

**T1 — Coherent processing advantage at 30–40 qubits**
- Crisp: Coherent multi-qubit measurement achieves 92% accuracy vs 67% fixed-measurement baseline at 30 qubits, p=0.3% noise.
- Label: EMPIRICAL_ADVANTAGE
- Quote: "At 30 qubits with p = 0.3% two-qubit gate error, the coherent classifier achieves 92% test accuracy vs 67% for the best fixed-measurement baseline"
- Status: observed (single-paper result; needs independent replication)

**T2 — Quantum-native data sidesteps dequantization**
- Crisp: Quantum-native input states remove the classical RFF approximation attack vector.
- Label: THEORETICAL_NOVELTY
- Quote: "In this regime, the question of dequantization does not arise in the same form: there is no classical representation of the input states to which an RFF approximation can be applied."
- Status: supported (established theoretical argument, consistent with prior work on quantum-native learning)

**T3 — Noise threshold for advantage: p < 1% at 30 qubits**
- Crisp: Advantage disappears above 20 qubits when two-qubit gate error exceeds 1%.
- Label: HARDWARE_CONSTRAINT
- Quote: "At p = 1% the advantage disappears above 20 qubits."
- Status: observed

## SUPPORT Claims

**S1 — Statistically significant separation**
- Crisp: Separation is p < 0.01 across 50 random instances.
- Quote: "The separation is statistically significant (p < 0.01, 50 random instances)."

**S2 — Advantage widens with qubit count up to ~40**
- Crisp: Gap grows from 30 to ~40 qubits then narrows.
- Quote: "The gap widens with system size up to ~40 qubits, then narrows due to noise accumulation."

**S3 — Circuit depth O(1) — NISQ feasible**
- Crisp: Required circuit depth is constant depth; compatible with NISQ hardware.
- Quote: "the required circuit depth (O(1)) and qubit count (30–40) are within the roadmap of current neutral-atom and superconducting hardware platforms"

**S4 — Fixed-measurement baseline: SVM with RBF on bitstring frequencies**
- Crisp: Classical baseline is an SVM with RBF kernel applied to measurement bitstring frequency vectors.
- Quote: "SVM with RBF kernel applied to bitstring frequencies"

## GENERAL Claims

**G1 — Prior QML work uses classical-data inputs**
- Crisp: Most prior QML demonstrations use classical data, enabling dequantization attacks.
- Quote: "most demonstrations have relied on classical-data inputs processed through quantum feature maps — a setting where dequantization arguments and strong classical baselines often close the gap."

**G2 — Quantum-native data arises from physical measurements and sensors**
- Crisp: Quantum-native data sources include quantum sensors, quantum communication.
- Quote: "quantum sensors, or quantum communication protocols"

## MOTIVATIONAL Claims

**M1 — QML advantage requires quantum-native data regime to survive classical competition**
- Crisp: Classical-data QML is vulnerable; quantum-native data is the defensible path.

**M2 — Near-term hardware within reach**
- Crisp: 30–40 qubit O(1) depth circuits are feasible within 1–3 year hardware roadmap.

## Links

- [[00_paper_content.md]]
- [[02_analysis.md]]
- [[04_final_review.md]]
