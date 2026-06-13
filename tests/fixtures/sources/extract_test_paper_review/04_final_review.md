---
source_type: skill-report
source_date: 2026-06-01
skill: qml-paper-review
version: 1.2.0
paper_id: "2605.21346"
paper_title: "Evidence of Quantum Machine Learning Advantage with Tens of Noisy Qubits"
verdict: CREDIBLE
---

# Final Review — Danaci et al., "Evidence of Quantum Machine Learning Advantage with Tens of Noisy Qubits"

**arXiv:** 2605.21346  
**Venue:** arXiv preprint, 2026-05-28  
**Authors:** Bayraktar Danaci, Nana Liu, others  
**Affiliation:** University of New South Wales; Shanghai Jiao Tong University

---

## Verdict

**CREDIBLE**

This paper provides experimental evidence that quantum-coherent data processing (using
coherent multi-qubit measurements on quantum-native data) achieves a separation from
fixed-measurement classical strategies at approximately 30–40 noisy qubits. The
separation is demonstrated in a theoretically grounded setting with quantum-native data
where the input states are quantum mechanical objects, not classical feature vectors.

**Falsification condition:** This verdict would change to MARGINAL if an RFF approximation
of the coherent measurement strategy achieves equivalent performance on the same quantum-native
data benchmark, or if the qubit/noise regime required is shown to be beyond what NISQ hardware
can achieve within the next 2 years.

**Key strength:** Uses quantum-native data (quantum state inputs), sidestepping the
dequantization risk that applies to classical-data quantum kernel papers.

**Key limitation:** Quantum-native data means the result does not directly translate to
classical-data ML tasks; near-term hardware access to 30–40 high-fidelity qubits remains a
practical constraint.

---

## QML Criteria Summary

| Criterion | Verdict | Note |
|---|---|---|
| Classical Baseline | PASS | Coherent vs fixed-measurement is the right comparison for quantum-native data; no tabular baseline required |
| Dequantization Risk | PASS | Quantum-native data inputs make classical approximation inapplicable by construction |
| Quantum-Native Data Fit | PASS | Inputs are quantum states; structure is genuinely quantum |
| Trainability | WARN | Fixed-parameter measurements used (avoids training); but circuit complexity analysis limited |
| Hardware Context | WARN | 30–40 noisy qubits required; within 1–3 year neutral-atom roadmap but not available today |

---

## Consensus Evidence Summary

Supporting papers: 2 (quantum learning advantage theory, quantum-native data separations)  
Contradicting papers: 0 found in search  
Evidence weight: MODERATE — theoretical backing strong; independent experimental replication absent

---

## Workspace

| File | Link |
|---|---|
| Paper content | 00_paper_content.md |
| Claim registry | 01_claim_registry.md |
| Analysis | 02_analysis.md |
| Consensus evidence | 03_consensus_evidence.md |
| This review | 04_final_review.md |
