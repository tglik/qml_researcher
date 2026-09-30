# Pre-experiment framing — global spectral properties via the fitted Pauli operator

The review of the polylog-Pauli graph-Hamiltonian patent left one "native direction" untested:
instead of per-node recommendation (which needs node correspondence), use the quantum operator for
a **global** property of a graph, which sidesteps correspondence entirely.

Proposal: fit the restricted (abelian) polylog-Pauli synthetic operator to a real graph's low-order
spectral moments (the same fitting procedure used in experiment 04), then estimate the graph's
algebraic connectivity λ₂ on a quantum computer by phase estimation on the fitted operator. Compare
the modeled quantum cost of that estimate with classical Lanczos run on the real graph, on six real
networks (38K–1.1M nodes). The claim: λ₂ within 2× of the true value at lower modeled cost than
classical Lanczos.
