# Claim Card Schema

Version: 1.0 | Written by: `/extract-artifacts`

One claim card per extracted claim. Keyed by `{paper_id}-claim-{NN}`. In v0, claims are scoped per paper — cross-paper merging is done manually via Research Question cards.

---

## File Location

```
{output_root}/cards/claims/{paper_id}-claim-{NN}.md
```

Example: `cards/claims/2405.12345-claim-01.md`

---

## Frontmatter

```yaml
---
id: 2405.12345-claim-01
type: claim-card
paper_id: 2405.12345
claim_index: 01
summary: "Neutral-atom quantum kernels outperform RBF kernels on molecular graph datasets"
status: plausible                    # speculative | plausible | observed | supported | strong | published | refuted
status_ceiling: observed             # max allowed by source type
source_type: skill-report            # skill-report | meeting-note | discussion | news-item | document
last_promoted: 2026-06-04
promoted_by: extract-artifacts
---
```

---

## Full Schema

```markdown
# Claim: {one-line summary}

**ID:** {paper_id}-claim-{NN}
**Source paper:** [[cards/paper-cards/{paper_id}]]
**Status:** {status}  ← claim ladder position
**Status ceiling:** {ceiling from source type}
**Extracted from:** [[{source path}]]

---

## Claim Statement

{Full claim as stated or closely paraphrased from the source. Quote where possible.}
[source: {section or quote}]

## What would support this claim

- {specific experimental result or theoretical proof that would move it up the ladder}

## What would refute this claim

- {specific result that would move it to refuted}

## Evidence

| Evidence ID | Summary | Supports/Contradicts | Source |
|-------------|---------|---------------------|--------|
| [[cards/evidence/{id}]] | {summary} | supports | [[{source}]] |

## Status history

| Date | From | To | Trigger |
|------|------|----|---------|
| {YYYY-MM-DD} | — | {initial status} | extracted from [[{source}]] |

---

## Links

- Source paper: [[cards/paper-cards/{paper_id}]]
- Evidence: [[cards/evidence/{paper_id}-claim-{NN}-ev-01]]
- Related claims (cross-paper): [[cards/claims/{related}]]
- Research question: [[cards/research-questions/{slug}]]
- Extracted from: [[{source path}]]
```

---

## Claim Status Ladder

```
speculative  — hypothesis, no experimental support
plausible    — theoretical argument or indirect evidence
observed     — reported experimental result (may lack rigor)
supported    — well-controlled experiment, reproducible
strong       — multiple independent replications + theoretical backing
published    — peer-reviewed T1/T2 venue
           ↘ refuted — contradicted by subsequent evidence
```

Status only moves **forward** via `/claim-promotion`. `/extract-artifacts` sets initial status, never upgrades an existing status.

## Source ceiling rules

| Source type | Max initial status |
|-------------|-------------------|
| skill-report | `observed` |
| document | `plausible` |
| meeting-note | `speculative` |
| discussion | `speculative` |
| news-item | `speculative` |
