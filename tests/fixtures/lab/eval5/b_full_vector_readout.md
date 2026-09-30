# Algorithm fixture (b) — linear-system solver for portfolio weights

HHL-style quantum linear-system solver for mean–variance portfolio optimisation. Input: an
N×N sparse, well-conditioned covariance matrix Σ (condition number κ ≤ 100, s nonzeros per row)
and the expected-return vector μ, loaded as a quantum state |μ⟩. The algorithm prepares
|w⟩ ∝ Σ⁻¹|μ⟩ in O(log N · s² κ² / ε) gates. Claimed: exponential speedup over classical
conjugate gradient, O(N s κ log(1/ε)).

Output required by the use case: the **full vector of N portfolio weights w**, to be sent to the
execution system every trading day. N = 5,000 assets. Precision needed on each weight: 10⁻⁴.
