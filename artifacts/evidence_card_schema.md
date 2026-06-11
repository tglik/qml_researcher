# Evidence Card Schema

> **RETIRED as of 2026-06-11.** Evidence cards are replaced by inline `## Evidence` sections in paper cards.
> Cross-paper evidence aggregation is handled by `Research Hypothesis` cards (`artifacts/research_hypothesis_schema.md`).
>
> The `cards/evidence/` directory in `qml-artifacts` has been deleted. Do not create new evidence card files.

Version: 1.0 (retired) | Was written by: `/extract-artifacts`

One card per distinct piece of evidence that supports or contradicts a claim. Keyed by `{paper_id}-claim-{NN}-ev-{NN}`.

---

## File Location

```
{output_root}/cards/evidence/{paper_id}-claim-{NN}-ev-{NN}.md
```

Example: `cards/evidence/2405.12345-claim-01-ev-01.md`

---

## Frontmatter

```yaml
---
id: 2405.12345-claim-01-ev-01
type: evidence-card
paper_id: 2405.12345
claim_id: 2405.12345-claim-01
relation: supports                   # supports | contradicts | neutral
evidence_type: experimental          # experimental | theoretical | empirical | anecdotal
strength: moderate                   # strong | moderate | weak
source_type: skill-report
extracted: 2026-06-04
---
```

---

## Full Schema

```markdown
# Evidence: {one-line description}

**ID:** {paper_id}-claim-{NN}-ev-{NN}
**Claim:** [[cards/claims/{claim_id}]]
**Paper:** [[cards/paper-cards/{paper_id}]]
**Relation:** supports | contradicts | neutral
**Type:** experimental | theoretical | empirical | anecdotal
**Strength:** strong | moderate | weak

---

## Evidence Statement

{Exact quote or close paraphrase of the result/argument.}
[source: {section, table, figure}]

## Details

- Dataset: {name, size | N/A}
- Metric: {metric name}
- Result: {quantum: X, classical: Y | theoretical argument}
- Seeds: {N | not reported}
- Statistical test: {reported | not reported}
- Hardware: {simulated | real hardware — {backend}}

## Why this strength rating

{One sentence justifying strong/moderate/weak — e.g., "Weak: only 2 seeds, no significance test, toy dataset."}

---

## Links

- Claim: [[cards/claims/{claim_id}]]
- Paper: [[cards/paper-cards/{paper_id}]]
- Source: [[{source path}]]
```

---

## Strength guidelines

| Rating | Criteria |
|--------|----------|
| strong | Real hardware or well-controlled simulation; ≥5 seeds; significance test; strong classical baseline |
| moderate | Simulation only OR weak baseline OR <5 seeds; result is directionally correct |
| weak | No seeds reported; toy dataset; no classical baseline; or theoretical-only with no experiment |
