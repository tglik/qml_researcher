id: qml-06
version: v2.0
path: algorithm
cutoff: 2020-11-03

## Algorithm: Pauli-feature kernel (PFK)

1. Standardize the input x ∈ ℝⁿ (each coordinate mean 0, standard deviation 1) and encode it into a
   quantum state with one of three embeddings:
   - **E1:** |x⟩ = ⊗ⱼ exp(−i xⱼ Xⱼ) |0⟩, on n qubits.
   - **E2:** |x⟩ = U_Z(x) H^⊗n U_Z(x) H^⊗n |0ⁿ⟩, with
     U_Z(x) = exp(i Σⱼ xⱼ Zⱼ + i Σ_{j<j′} xⱼ x_{j′} Zⱼ Z_{j′}), on n qubits.
   - **E3:** |x⟩ = [ Πⱼ₌₁ⁿ exp(−i (t/T) xⱼ (XⱼX_{j+1} + YⱼY_{j+1} + ZⱼZ_{j+1})) ]ᵀ ⊗ⱼ₌₁ⁿ⁺¹ |ψⱼ⟩,
     with T = 20 Trotter steps, t = n/3, and |ψⱼ⟩ fixed random single-qubit states, on n + 1 qubits.
2. Measure the single-qubit Pauli expectations ⟨Xₖ⟩, ⟨Yₖ⟩, ⟨Zₖ⟩ for every qubit k.
3. Kernel: k_PFK(x, x′) = exp(−γ Σₖ Σ_{P∈{X,Y,Z}} (⟨Pₖ⟩ₓ − ⟨Pₖ⟩ₓ′)²), with γ > 0 tuned.
4. Train a support vector machine (classification) or kernel ridge regression on k_PFK.

Also proposed, on the same embeddings: the fidelity kernel k_F(x, x′) = |⟨x|x′⟩|².

## Task

Supervised learning from a small training set (hundreds of examples) of low-dimensional inputs.
The proposer has two use cases in mind:
- Classifying images after compressing them to their first n principal components. Benchmark:
  fashion-MNIST, dress versus shirt.
- Learning a function whose values come from a quantum process applied to the encoded input, for
  example an observable measured after the encoded state evolves on a device.

## Proposer's claim

"PFK on a hard-to-simulate embedding (E2 or E3) predicts better than classical machine learning at
the same training-set size, and the gap grows with the number of qubits."

## Constraints

- Compute: one workstation, 22 CPU cores, 15 GB RAM, a few CPU-hours. Statevector simulation only;
  no quantum hardware.
- Data: the fashion-MNIST training files are available locally. No network during runs.
- No literature search. Use the prior-work packet if you are given one.
- Treat anything published after 3 November 2020 as unknown.
