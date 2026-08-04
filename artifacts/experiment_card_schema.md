# Experiment Card Schema

Version: 1.0 | Used by: `/extract-artifacts` (from `experiment-report` source files)

An Experiment Card is the structured entity card for one self-run, pre-registered
falsifiable experiment from `qml_experiments`. It lives in `cards/experiments/` in the
artifact repo, keyed by a program-scoped slug. It is produced by `/extract-artifacts`,
not written directly by research skills.

Experiment Cards are the empirical counterpart to Paper Cards: a Paper Card records what
the literature claims, an Experiment Card records what the team itself measured against
an honest classical baseline. They are deliberately kept separate — never merged into
`cards/paper-cards/` — because the claim ceiling and evidence standard differ (see
`Field Definitions` below).

---

## Why this exists

`qml_experiments` is a separate git repo with its own code/data lifecycle (Python, venvs,
figures) — it is intentionally **not** merged into this markdown-only, Quartz-served vault.
An Experiment Card is the lightweight bridge: it carries the verdict, gates, and key
numbers into the knowledge graph so skills and the team can discover and link to
self-run evidence the same way they discover paper evidence, without qml_artifacts
absorbing code or data files. The full record (code, data, figures, VERDICT.md) always
stays in `qml_experiments` — the card links out to it via `canonical_source`.

---

## File Location

```
{output_root}/cards/experiments/{slug}.md
```

Example: `cards/experiments/recsys-classical-twin.md`

---

## Frontmatter (required — used by index builders and skill context loaders)

```yaml
---
id: recsys-classical-twin
type: experiment-card
title: "Recsys Classical Twin — does a classical machine reproduce the QSVT pipeline's cost?"
program: idea1-synthetic-prior-spectral-filtering-recsys   # program slug — groups experiments run against one claim
experiment_number: "04"                                     # numbering within the program, as string (may be non-numeric)
topics: [graph-ml, recommendation, dequantization]          # used by topic-map
verdict: CLOSED_NO                                          # GO | NO_GO | CLOSED_NO | CLOSED_YES | PROVISIONAL
claim_status: observed                                       # see Field Definitions — ceiling is "observed" until independently reproduced
evaluated: 2026-07-29
canonical_source: qml_experiments/experiments/spectral_graph/04_recsys_classical_twin/VERDICT.md
source: sources/reports/experiments/recsys-classical-twin_2026-07-29.md
extracted: true
---
```

---

## Full Schema

```markdown
# Experiment Card: {Full Experiment Title}

**Program:** [[cards/experiments/{other cards in same program}]] (or plain text program name if no program index card exists)
**Experiment #:** {experiment_number} within {program}
**Evaluated:** {YYYY-MM-DD}
**Canonical source:** `{canonical_source}` (qml_experiments repo — code, data, figures, full VERDICT.md)
**Source:** [[{source path}]]

---

## Question

{1-2 sentences: the falsifiable question this experiment was pre-registered to answer, in the same terms as the experiment's own README/VERDICT.}

## Method

{2-4 sentences: what was measured, on what real data/benchmarks, against what classical baseline, at what matched budget. Name the datasets.}

## Verdict

**{GO | NO_GO | CLOSED_NO | CLOSED_YES | PROVISIONAL}** — {one-sentence verdict, close to verbatim from the experiment's own VERDICT.md}

**Key numbers:**
- {metric}: {quantum/synthetic-construction result} vs {classical baseline result}
- Gate: {pre-registered pass bar} → {N}/{M} checks cleared

## Why It Matters

{1-2 sentences: what this experiment rules in or out for the broader program/hypothesis, and what it would take to overturn it.}

## Caveats

- {any explicitly flagged scope limitation — e.g. "modeled quantum cost, no hardware run" or "restricted Pauli family, general construction untested"}

---

## Links

- Canonical source (code + full verdict): `{canonical_source}`
- Program siblings: [[cards/experiments/{sibling-slug-1}]], [[cards/experiments/{sibling-slug-2}]]
- Related hypotheses: [[cards/hypotheses/{slug}]] (only if the experiment bears directly on an existing hypothesis card — do not force a link)
- Related papers: [[cards/paper-cards/{id}]] (only if the experiment was designed to test a specific paper's claim)
```

---

## Field Definitions

| Field | Required | Notes |
|-------|----------|-------|
| id | Yes | Program-relative slug, kebab-case, derived from the experiment folder name with the numeric prefix stripped (`04_recsys_classical_twin` → `recsys-classical-twin`) |
| type | Yes | Always `experiment-card` |
| program | Yes | Slug grouping all experiments testing one claim/construction. Reuse an existing program slug if one exists — do not create a new program per experiment. |
| experiment_number | Yes | The number/id used in the source repo's own folder naming, as a string |
| topics | Yes | Used by topic-map index builder — reuse existing topic slugs where they apply (e.g. `graph-ml`, `tabular-ml`, `dequantization`) rather than inventing new ones |
| verdict | Yes | `GO` (quantum arm wins at matched budget) \| `NO_GO` (fails the pre-registered gate) \| `CLOSED_NO` (question closed, no advantage found) \| `CLOSED_YES` (question closed, advantage confirmed) \| `PROVISIONAL` (result stands but a named condition is unmet — see source) |
| claim_status | Yes | Ceiling is `observed` — a single self-run experiment, however rigorous, is not `supported`/`strong` until independently reproduced. Never set higher without a second, independent replication. |
| canonical_source | Yes | Path (relative to the `qml_experiments` repo root) to the full VERDICT.md/README this card summarizes. This is a plain-text path, not a wikilink — it points outside the vault. |
| source | Yes | Path to the Layer 1 source file (the mirrored summary) this was extracted from |
| extracted | Yes | `true` after extraction |

## Prohibited Patterns

```
❌ Writing an experiment card directly from a skill — always go through /extract-artifacts
❌ Copying code, data, or figures into qml_artifacts — this repo stays markdown-only; link to qml_experiments instead
❌ Setting claim_status above "observed" from a single experiment — independent reproduction is required first
❌ Inventing numbers not present in the mirrored source or canonical_source — if a figure isn't in the source, omit it, don't estimate
❌ Force-linking to a hypothesis or paper card that isn't actually about the same claim — an empty "Related hypotheses" section is correct when no real link exists
❌ Creating a new program slug when an existing one already covers this experiment's claim — check indexes/experiment-registry.md first
```
