# Research Hypothesis Schema

Version: 1.0 | Written by: `/synthesize-hypotheses`

A Research Hypothesis is a cross-paper synthesis artifact. It is never extracted — it is only created or updated by `/synthesize-hypotheses`. One card per distinct research direction that meets the promotion filter.

---

## File Location

```
{output_root}/cards/hypotheses/{slug}.md
```

Example: `cards/hypotheses/rydberg-quantum-reservoir-computing.md`

---

## Frontmatter

```yaml
---
id: rydberg-quantum-reservoir-computing
type: research-hypothesis
title: "Rydberg Quantum Reservoir Computing for Temporal/Dynamical Learning"
strategic_value: directional          # foundational | directional | actionable | incremental
support_count: 3                      # number of independent papers or deep-research runs
status: plausible                     # speculative | plausible | observed | supported | strong | published | refuted
qml_criteria_passed: [hardware_fit, geometric_difference]
qml_criteria_open: [dequantization_risk, classical_baseline]
supporting_papers: [2111.10956, 2602.00610, 2405.04799]
contradicting_papers: []
last_synthesized: 2026-06-11
synthesized_by: synthesize-hypotheses
---
```

---

## Full Schema

```markdown
# Research Hypothesis: {title}

**ID:** {slug}
**Strategic value:** {foundational | directional | actionable | incremental}
**Status:** {status}  ← claim ladder position
**Support count:** {N} independent sources
**Last synthesized:** {YYYY-MM-DD}

---

## Hypothesis Statement

{2–4 sentences. The core cross-paper claim: what phenomenon or direction is supported, by what type of evidence, and on what domain/task. Cite specific papers.}

## Why This Survives the Filters

**QML criteria passed:** {list with one-line rationale per criterion}

**Novelty score:** {why this would surprise a QML expert — not just "quantum advantage claimed"}

**What makes this non-incremental:** {specific structural or empirical argument that distinguishes this from a trivially known result}

## Evidence Summary

| Paper | Verdict | Key result | QML criteria status |
|-------|---------|-----------|---------------------|
| [[cards/paper-cards/{id}]] | {verdict} | {one-line result} | {criteria passed} |

## Open Risks

{List each unresolved QML criterion and what specifically needs to be demonstrated to resolve it.}

- **Dequantization risk:** {resolved/unresolved — specific concern}
- **Geometric difference:** {resolved/unresolved — specific concern}
- **Trainability/simulability:** {resolved/unresolved — specific concern}
- **Hardware fit:** {resolved/unresolved — specific concern}
- **Classical baseline:** {resolved/unresolved — specific concern}

## Promotion Criteria

To promote from {current status} to {next status}:
- {specific experimental result or theoretical proof required}
- {specific baseline comparison required}

## Status History

| Date | From | To | Trigger |
|------|------|----|---------|
| {YYYY-MM-DD} | — | {initial status} | synthesized from {N} papers |

---

## Links

- Supporting papers: [[cards/paper-cards/{id1}]], [[cards/paper-cards/{id2}]]
- Contradicting papers: (none)
- Related hypotheses: [[cards/hypotheses/{related-slug}]]
```

---

## strategic_value Definitions

| Value | Meaning |
|-------|---------|
| `foundational` | Already widely accepted in the field; useful as a reference but not a differentiator |
| `directional` | Points toward a promising research direction; not yet actionable without further work |
| `actionable` | Ready to be turned into an experiment, prototype, or partner pitch with current resources |
| `incremental` | Minor refinement of an existing result; unlikely to change strategic direction |

**Only `directional` and `actionable` hypotheses appear in the pareto view** (`hypothesis-ledger.md`). `foundational` and `incremental` are archived but not surfaced.

---

## Promotion Filter (enforced by `/synthesize-hypotheses`)

A hypothesis card is only created if ALL of the following pass:

1. `support_count ≥ 2` — at least two independent papers or deep-research runs
2. `qml_criteria_passed` is non-empty — passes ≥1 of the 5 QML domain criteria
3. `strategic_value ∈ [directional, actionable]`
4. Novelty check passes — synthesis agent must justify why this would surprise a QML expert

If a hypothesis candidate fails any filter, it is logged to `_synthesis_skipped.md` with the reason, not silently dropped.

---

## Claim Status Ladder (applies to Research Hypotheses)

```
speculative  — mentioned across papers but no experimental evidence
plausible    — theoretical argument or indirect evidence from multiple papers
observed     — reported results across ≥2 independent papers (may lack rigor)
supported    — well-controlled results from ≥3 papers, reproducible
strong       — multiple replications + theoretical backing
published    — peer-reviewed T1/T2 venue, multiple papers
           ↘ refuted — contradicted by subsequent dequantization or negative result
```

Status only moves **forward** via `/synthesize-hypotheses` or `/claim-promotion`. Never downgraded automatically — conflicts are logged to `_conflicts.md`.

---

## Prohibited Patterns

```
❌ Creating a Research Hypothesis card from a single paper — support_count ≥ 2 is mandatory
❌ Setting strategic_value = incremental — such candidates are skipped and logged
❌ Omitting open_risks — every hypothesis must name the unresolved QML criteria
❌ Writing a hypothesis without justifying novelty — "this is well-known" is a disqualifier
❌ Merging two hypotheses silently — log to _conflicts.md and create a note for human review
```
