# Paper Card Schema

Version: 1.0 | Used by: `/qml-evaluate` (Phase 2)

A Paper Card is the structured output of a full QML paper evaluation. It is produced by
`/qml-evaluate` for papers that have passed triage. It is the primary artifact for capturing
a paper's claims, evidence quality, and QML-specific evaluation results.

---

## File Naming

```
{vault_path}/artifacts/{topic_slug}_{YYYY-MM-DD}.md
```

Where:
- `topic_slug` = first 3-4 significant words from paper title, hyphenated, lowercase
  e.g. "neutral-atom-graph-kernels" for "Neutral-Atom Quantum Kernels for Graph ML"
- `YYYY-MM-DD` = date of evaluation, not paper publication date

---

## Full Schema

```markdown
# Paper Card: {Full Paper Title}

**arXiv ID:** {arxiv_id}
**Authors:** {Author1, Author2, ...}
**Published:** {YYYY-MM-DD}
**Venue:** {venue name | "arXiv preprint"}
**Venue Tier:** {T1 | T2 | T3 | T4 | T5}  ← see criteria/qml_domain.md
**Evaluated by:** /qml-evaluate {version}
**Evaluation date:** {YYYY-MM-DD}
**Triage verdict:** PASS | TRIAGE-resolved
**Triage log ref:** triage_log.jsonl entry {arxiv_id}

---

## Problem

{1-2 sentences: What problem does this paper solve? What is the input and output?}
[source: abstract]

## Main Claim

{The paper's primary quantum advantage claim, quoted or closely paraphrased.}
[source: abstract, section {N}]

**Claim status:** {speculative | plausible | observed | supported | strong | published | refuted}
↑ Use the claim status ladder. Do not upgrade beyond what evidence supports.

## Method

{2-4 sentences: What quantum primitive/circuit/approach is used? What makes it quantum?}
[source: section {N}]

## Evidence

{What experimental or theoretical evidence is provided for the main claim?}
- Dataset(s): {names, sizes}
- Metric(s): {accuracy, MSE, F1, etc.}
- Results: {key numbers — quantum vs classical}
- Number of seeds: {N | not reported}
- Statistical significance: {reported | not reported}
[source: section {N}, Table {N}]

---

## QML Criteria Evaluation

### 1. Dequantization Risk
**Verdict:** PASS | WARN | FAIL  |  **Severity:** CRITICAL | MAJOR | MINOR | N/A
**Note:** {One specific sentence. Must cite paper section or quote.}

### 2. Geometric Difference
**Verdict:** PASS | WARN | FAIL  |  **Severity:** CRITICAL | MAJOR | MINOR | N/A
**Note:** {One specific sentence citing evidence from methods section.}

### 3. Trainability / Simulability
**Verdict:** PASS | WARN | FAIL  |  **Severity:** CRITICAL | MAJOR | MINOR | N/A
**Note:** {Gradient scaling analysis found/not found. System size range. Simulability addressed/not addressed.}

### 4. Hardware Fit — Neutral Atom / NISQ
**Verdict:** PASS | WARN | FAIL  |  **Severity:** CRITICAL | MAJOR | MINOR | N/A
**Note:** {Circuit depth, qubit count, hardware platform used. Neutral-atom analysis present/absent.}

### 5. Classical Baseline
**Verdict:** PASS | WARN | FAIL  |  **Severity:** CRITICAL | MAJOR | MINOR | N/A
**Classical methods used:** {list what was compared against}
**Missing baselines:** {list what should have been used but wasn't}
**Note:** {TabPFN/XGBoost/GNN/SOAP present? Hyperparameter tuning described?}

**Evaluation scope:** {full | partial — abstract+intro+conclusion only (fallback fetch)}

---

## Overall Verdict

**QML verdict:** STRONG_INTEREST | CONDITIONAL | WEAK | REJECT
- STRONG_INTEREST: All 5 criteria PASS; result is relevant to team's current directions
- CONDITIONAL: 1-2 criteria at WARN; paper is interesting if concerns are resolved
- WEAK: Criteria mostly PASS but result is not relevant to team's current directions
- REJECT: Any CRITICAL FAIL found (should have been SKIP at triage — flag for review)

**Rationale:** {2-3 sentences explaining the overall verdict.}

---

## Assumptions

Hidden assumptions identified in the paper that are not validated experimentally:
- {assumption 1, with section citation}
- {assumption 2, with section citation}
- {e.g., QRAM availability, oracle construction cost, noise-free simulation, infinite shots}

## Limitations

Limitations acknowledged by the authors:
- {limitation 1}
- {limitation 2}

Limitations NOT acknowledged but identified by evaluation:
- {unacknowledged limitation 1}

## Open Questions

Questions this paper raises that are relevant to our research:
1. {question 1}
2. {question 2}

## Follow-up Actions

- [ ] {Concrete next step: e.g., "Run TabPFN on their benchmark dataset to check baseline gap"}
- [ ] {e.g., "Check whether their kernel is RFF-approximable — test on datasets in their Table 2"}
- [ ] {e.g., "Ask Meir: does this circuit topology map to our Pasqal hardware?"}

## Belief Update

**Prior belief:** {What did we think about this direction before reading?}
**Posterior belief:** {How does this paper update our view?}
**Strength of update:** STRONG | MODERATE | WEAK | NONE
```

---

## Field Definitions

| Field | Required | Notes |
|-------|----------|-------|
| arxiv_id | Yes | Canonical format: YYMM.NNNNN |
| venue_tier | Yes | T1-T5 from criteria/qml_domain.md venue table |
| claim_status | Yes | Must use claim status ladder; never skip steps |
| evidence.seeds | Yes | If not reported, write "not reported" — do not omit |
| criteria.note | Yes | Must cite paper section or quote fetched text; no fabrication |
| evaluation_scope | Yes | "full" or "partial" — partial means fallback fetch was used |
| overall_verdict | Yes | One of four values only |
| follow_up_actions | Yes | At least one action item; use checkboxes |

## Prohibited Patterns

```
❌ Filling criteria notes from memory about the paper topic — only use fetched text
❌ Setting claim_status = "strong" or "published" without peer review evidence
❌ Omitting the "not reported" marker for missing fields (seeds, significance)
❌ Setting overall_verdict = STRONG_INTEREST when any criterion is WARN
❌ Writing "see paper" as a note — must quote or paraphrase the specific finding
```

## Claim Status Ladder

Claims in this Paper Card must not exceed the current evidence tier:

```
speculative  — hypothesis, no experimental support
plausible    — theoretical argument or indirect evidence
observed     — reported experimental result (may lack rigor)
supported    — well-controlled experiment, reproducible
strong       — multiple independent replications, theoretical backing
published    — peer-reviewed venue T1/T2
            ↘ refuted — contradicted by subsequent evidence
```

The Paper Card records the claim status AS OF EVALUATION DATE. If later evidence changes the status, update via `/claim-promotion`.
