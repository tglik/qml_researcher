# Algorithm fixture (a) — quantum recommendation by low-rank sampling

A quantum recommendation system (in the style of Kerenidis–Prakash 2016). Input: an m×n
preference matrix A stored in a QRAM-style data structure that supports preparing |A_i⟩ for any
row i and the row-norm distribution in O(polylog(mn)) time. Assumption: A is close to rank k.

Algorithm: for user i, project |A_i⟩ onto the top-k singular subspace of A with quantum singular
value estimation (precision ε, cost O(poly(k, 1/ε) · polylog(mn))), then measure the projected
state in the computational basis to **sample** an item j with probability proportional to the
squared entry of the low-rank reconstruction. Claimed: exponential speedup in m, n over
classical recommendation, which needs time poly(mn).

Output: one sampled recommended item per query (repeat for more items).
Operating point claimed: 10⁹ users × 10⁸ items, 100 ms per recommendation.
