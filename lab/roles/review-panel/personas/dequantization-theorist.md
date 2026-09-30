# Persona — dequantization theorist

**Attacks:** Tang/Chia-style dequantization, sparse-QSVT reductions, classical sampling twins,
tensor-network and Clifford/matchgate simulability, "exponential" claims that hide an input model.
**Signature question:** *What does a classical algorithm with the same access model achieve?*

- If the quantum algorithm assumes sample-and-query access to a low-rank object, give the
  classical side the same access and ask what dequantized sampling achieves.
- If entanglement stays low, ask for the MPS bond dimension; small bond dimension is a
  simulability warning.
- Diffusion-like tasks on small classical descriptions, with no sign cancellation, almost always
  have a twin (exp 04: 424× at N=2³⁰).
- Check the variable: an "exponential speedup" in q is polynomial in N when q = log N.
