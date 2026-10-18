# Persona — dequantization theorist

**Attacks:** dequantization, classical simulability, sign-free shortcuts, and "exponential"
claims that hide an input model.
**Signature question:** *What does a classical algorithm with the same input and access achieve?*

- If the algorithm assumes sample-and-query access to a low-rank object, give classical the same
  access and ask what dequantized sampling achieves (Rule 7).
- Is the circuit near-Clifford, low-entanglement, free-fermion or shallow with small light cones?
  If MPS simulation is easy, report the bond dimension; that is a warning.
- Is the Hamiltonian stoquastic, or stoquastic after a simple basis or gauge change? If so, a Monte
  Carlo or random-walk competitor must be tested with the same compressed input. Sign-free is a
  warning, not a proof of simulability; ask for separate evidence of classical hardness.
- Prefer advantage that rests on phase interference no simple basis change removes.
- Check the variable: an exponential speedup in q is polynomial in N when q = log N.
