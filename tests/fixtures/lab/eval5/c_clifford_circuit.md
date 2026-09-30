# Algorithm fixture (c) — "quantum feature map" for anomaly detection

A quantum feature map for transaction anomaly detection. Each transaction's 40 binary flags
x ∈ {0,1}⁴⁰ are encoded on 40 qubits by applying X on qubit i when xᵢ = 1, followed by a fixed
entangling layer: Hadamard on every qubit, then a ladder of CNOTs (i, i+1), then S gates on even
qubits, then another layer of Hadamards. The feature vector is the expectation value of every
two-qubit Pauli ZᵢZⱼ (780 features), estimated with 10⁴ shots each, and fed to an isolation forest.

Claimed: "exponentially large Hilbert space features unavailable to classical methods," with a
proposed run on 40-qubit hardware.
