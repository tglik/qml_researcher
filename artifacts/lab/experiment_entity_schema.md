# Experiment Entity Schema (`VERDICT.md` frontmatter)

Version: 2.0 | Replaces: `experiment_card_schema.md` (retired 2026-09-30, decision D12) |
Used by: `/qml-verdict`, `/qml-promote`, `/qml-experiments`, `scripts/lab/registry.py`

A self-run experiment lives in the `qml_artifacts` vault at
`experiments/<thread>/<NN_name>/`, next to its code, results and figures. Its `VERDICT.md`
frontmatter **is** the experiment's entity in the knowledge graph — there is no separate
Experiment Card and no mirrored source report. Indexes (`experiment-registry.md`,
`topic-map.md`) and other cards link straight to the verdict:
`[[experiments/<thread>/<NN_name>/VERDICT|<id>]]` (inside a markdown table, escape the pipe:
`\|`).

---

## Frontmatter

```yaml
---
id: recsys-classical-twin                     # folder name, numeric prefix stripped, hyphens
type: experiment
aliases: [cards/experiments/recsys-classical-twin]   # only for experiments that had a card before 2026-09-30
title: "Recsys Classical Twin — does a classical machine reproduce the QSVT pipeline's cost?"
program: idea1-synthetic-prior-spectral-filtering-recsys
experiment_number: "04"
topics: [graph-ml, recommendation, dequantization]
verdict: NO-GO-PROVISIONAL
claim_status: observed
evaluated: 2026-07-29
thread: spectral_graph
audit: CONFIRMED
ledger: [polylog-pauli-graph-hamiltonian-recsys-ranking]
---
```

## Field definitions

| Field | Required | Notes |
|---|---|---|
| id | Yes | Kebab-case slug from the folder name with the numeric prefix stripped (`04_recsys_classical_twin` → `recsys-classical-twin`). Stable — never renamed. |
| type | Yes | Always `experiment` |
| aliases | Legacy only | `[cards/experiments/<id>]` keeps pre-2026-09-30 wiki-links resolving in Quartz. Do not add for new experiments. |
| title | Yes | Short name + the question, as on the old cards |
| program | Yes | Slug grouping every experiment that tests one claim/construction. Reuse an existing program slug. |
| experiment_number | Yes | The `NN` prefix, as a string |
| topics | Yes | Topic-map tags — reuse existing slugs (`graph-ml`, `tabular-ml`, `dequantization`, …) |
| verdict | Yes | New experiments: `GO` \| `CONDITIONAL-GO` \| `NO-GO-FINAL` \| `NO-GO-PROVISIONAL` \| `BLOCKED` (D10). Legacy experiments keep their original value (`GO`, `NO_GO`, `CLOSED_NO`, `CLOSED_YES`, `PROVISIONAL`) until ledger seeding re-reads them against N1–N5 and maps them. |
| claim_status | Yes | Ceiling `observed` — a single self-run experiment is not `supported`/`strong` until independently reproduced |
| evaluated | Yes | Date the verdict was written (`YYYY-MM-DD`) |
| thread | Yes | The thread folder (`boosting_trees`, `spectral_graph`, `fraud_aml`, …) |
| audit | Yes | `CONFIRMED` \| `OVERTURNED` \| `INSUFFICIENT` (from `/qml-audit`) \| `legacy-human` (experiments closed before the lab existed) |
| ledger | Yes | Exclusion-ledger entry ids this verdict created or is a covered case of; `[]` if none |

## Body

The body is the human-authored verdict (template: `artifacts/lab/` `VERDICT.md`, C01). It ends
with a `## Graph links` section — why it matters, caveats, and related links (program siblings,
hypotheses, papers) — which is what the old card body used to carry.

## Prohibited patterns

```
❌ Creating cards/experiments/<id>.md or sources/reports/experiments/ mirrors — retired
❌ A bare | inside a wiki-link in a markdown table — escape it as \|
❌ Committing a data file > 5 MB — list it in data/manifest.json and re-create it with data/fetch.py
❌ Setting claim_status above "observed" from a single experiment
❌ Changing a legacy verdict value during a copy or refactor — mapping to D10 happens only in ledger seeding
```
