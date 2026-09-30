# Pre-experiment framing — serving cost of the QSVT recommendation filter

The patent's recommendation pipeline fits a synthetic graph Hamiltonian — a restricted sum of
polylog(N) commuting Pauli strings — to the item co-occurrence graph offline. At query time, a
QSVT circuit applies a low-pass spectral filter g(L) to the user's history state and samples
recommended items. The fitted description has only polylog(N) parameters, and the filter is a
smoothing (diffusion-like) polynomial of L with non-negative weights.

Claim: per-query cost polylog(N), versus classical spectral filtering that scales with the number of
edges — an exponential serving-cost advantage at catalog sizes up to 10⁹ items, with a 10 ms per-query
target.
