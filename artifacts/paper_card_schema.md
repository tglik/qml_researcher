# Paper Card Schema

Version: 4.0 | Used by: `/extract-artifacts` (from paper review source files)

A Paper Card is the structured entity card for one evaluated paper. It lives in `cards/paper-cards/` in the artifact repo, keyed by arXiv ID. It is produced by `/extract-artifacts`, not written directly by research skills.

---

## File Location

```
{output_root}/cards/paper-cards/{arxiv_id}.md
```

Example: `cards/paper-cards/2405.12345.md`

---

## Frontmatter (required — used by index builders and skill context loaders)

```yaml
---
id: 2405.12345
type: paper-card
title: "Quantum Kernels for Graph ML with Neutral Atoms"
arxiv_id: 2405.12345
persons: [farhi-edward, goldstone-jeffrey]            # person-card slugs (all authors)
organizations: [mit-center-for-quantum, caltech-iqim] # org-card slugs (from author affiliations)
topics: [graph-ml, neutral-atom, quantum-kernels]     # used by topic-map
verdict: STRONG_INTEREST                              # STRONG_INTEREST | CONDITIONAL | WEAK | REJECT
claim_status: plausible                               # main claim status for this paper
evaluated: 2026-06-04
source: sources/reports/paper-reviews/2405.12345-review-2026-06-04.md
extracted: true
---
```

**Note:** `claims` and `evidence` fields are retired (v4). Claims and evidence are embedded inline in the paper card body (`## Main Claim` and `## Evidence` sections). Cross-paper synthesis uses `cards/hypotheses/` cards created by `/synthesize-hypotheses`.

---

## Full Schema

```markdown
# Paper Card: {Full Paper Title}

**arXiv ID:** {arxiv_id}
**Authors:** [[cards/persons/{slug1}]], [[cards/persons/{slug2}]]
**Organizations:** [[cards/organizations/{org1}]], [[cards/organizations/{org2}]]
**Published:** {YYYY-MM-DD}
**Venue:** {venue name | "arXiv preprint"}
**Venue Tier:** {T1 | T2 | T3 | T4 | T5}
**Evaluated:** {YYYY-MM-DD}
**Source:** [[{source path}]]

---

## Problem

{1-2 sentences: What problem does this paper solve? What is the input and output?}
[source: abstract]

## Main Claim

{The paper's primary quantum advantage claim, quoted or closely paraphrased.}
[source: abstract, section {N}]

**Claim status:** {speculative | plausible | observed | supported | strong | published | refuted}

## Method

{2-4 sentences: What quantum primitive/circuit/approach is used? What makes it quantum?}
[source: section {N}]

## Evidence

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
**Note:** {One specific sentence citing paper section or quote.}

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
**Classical methods used:** {list}
**Missing baselines:** {list}
**Note:** {TabPFN/XGBoost/GNN/SOAP present? Hyperparameter tuning described?}

**Evaluation scope:** {full | partial}

---

## Overall Verdict

**QML verdict:** STRONG_INTEREST | CONDITIONAL | WEAK | REJECT
**Rationale:** {2-3 sentences.}

---

## Assumptions

- {assumption 1, with section citation}
- {assumption 2, with section citation}

## Limitations

Authors acknowledged:
- {limitation 1}

Not acknowledged, identified by evaluation:
- {unacknowledged limitation 1}

## Open Questions

1. {question 1}
2. {question 2}

## Follow-up Actions

- [ ] {concrete next step}

## Belief Update

**Prior belief:** {before reading}
**Posterior belief:** {after reading}
**Strength of update:** STRONG | MODERATE | WEAK | NONE

---

## Links

- Source: [[{source path}]]
- Persons: [[cards/persons/{slug1}]], [[cards/persons/{slug2}]]
- Organizations: [[cards/organizations/{org1}]], [[cards/organizations/{org2}]]
- Related hypotheses: [[cards/hypotheses/{slug}]]
- Related papers: [[cards/paper-cards/{related_id}]]
```

---

## Field Definitions

| Field | Required | Notes |
|-------|----------|-------|
| id | Yes | arXiv ID — canonical dedup key |
| type | Yes | Always `paper-card` |
| persons | Yes | List of person-card slugs (lastname-firstname) for all authors |
| organizations | Yes | List of org-card slugs derived from author affiliations |
| topics | Yes | Used by topic-map index builder |
| verdict | Yes | One of four values only |
| claim_status | Yes | Main claim status for this paper |
| source | Yes | Path to the Layer 1 source file this was extracted from |
| extracted | Yes | `true` after extraction; `false` in source frontmatter |

**Retired fields (v4):**
- `claims` — removed. Claims are embedded inline in `## Main Claim` section.
- `evidence` — removed. Evidence is embedded inline in `## Evidence` section.

## Prohibited Patterns

```
❌ Writing paper card directly from a skill — always go through /extract-artifacts
❌ Filling criteria notes from memory — only use fetched text from source
❌ Setting claim_status beyond source ceiling (skill-report max: observed before audit)
❌ Setting overall_verdict = STRONG_INTEREST when any criterion is WARN
❌ Omitting the Links section — every card must link to its persons and orgs
❌ Using "authors" or "institute" fields — superseded by "persons" and "organizations"
❌ Adding "claims" or "evidence" fields to frontmatter — those are retired in v4
❌ Linking to cards/claims/ or cards/evidence/ — those directories are retired
```
