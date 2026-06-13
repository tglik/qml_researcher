---
workspace_type: paper-review
source_date: 2026-06-01
processing_plan:
  - file: 00_paper_content.md
    role: Paper metadata and cited papers
  - file: 01_claim_registry.md
    role: Structured claims
  - file: 04_final_review.md
    role: Synthesis and QML criteria verdicts
---

# Test Fixture — extract-artifacts paper-review workspace

This is a minimal paper-review workspace used by the `extract-artifacts-paper-review-dir` test case.

Paper: Danaci et al. 2605.21346 — "Evidence of Quantum Machine Learning Advantage with Tens of Noisy Qubits"

Expected extractions:
- 1 paper card (arXiv 2605.21346)
- 1 person card (Bayraktar Danaci — should MERGE with pre-seeded card, triggering affiliation conflict)
- 1 organization card (University of New South Wales)
