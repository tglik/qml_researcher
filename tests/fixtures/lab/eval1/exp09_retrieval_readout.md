# Pre-experiment framing — the polylog-Pauli construction at the candidate-retrieval stage

Every recommendation stage except candidate retrieval has been tested. Retrieval is "where
production value lives": from a catalog of N items, return the top ~500 candidates per user for
the ranker, within a few milliseconds, at billions of items.

Proposed quantum routes:
1. Prepare the user's filtered state with the fitted operator and extract the top-K items with
   amplitude amplification (√(KN) queries).
2. Sample candidates directly by measuring the filtered state (shot sampling).
3. Use a Grover-style mixing step to concentrate amplitude on high-score items, then sample.
4. Alternatively, use the operator's block partition as a compressed on-device candidate index.

Claim: at matched candidate budget and serving bytes, the quantum route matches classical recall
at lower cost.
