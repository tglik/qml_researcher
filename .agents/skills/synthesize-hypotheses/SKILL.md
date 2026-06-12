---
name: synthesize-hypotheses
version: 1.0.0
description: |
  Reads all paper cards grouped by topic, identifies cross-paper claim patterns, and
  creates or updates Research Hypothesis cards in cards/hypotheses/. Applies the
  Pareto filter: only hypotheses with support_count ≥ 2, passing ≥1 QML criterion,
  and strategic_value in [directional, actionable] are promoted.
  Updates hypothesis-ledger.md index.

triggers:
  - synthesize hypotheses
  - run hypothesis synthesis
  - update hypothesis ledger
  - synthesize research directions

input:
  - --topic: optional topic slug to scope synthesis (e.g., neutral-atom, qcnn); if omitted, runs over all topics
  - --dry-run: print what would be created/updated without writing

output:
  - cards/hypotheses/ — new and updated Research Hypothesis cards
  - indexes/hypothesis-ledger.md — updated with all directional/actionable hypotheses
  - indexes/_synthesis_skipped.md — candidates that failed the promotion filter with reasons

allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /synthesize-hypotheses

Paper cards → claim patterns detected → Pareto filter applied → Research Hypothesis cards written → hypothesis-ledger updated.

---

## Agent Spawn Convention

All agent definitions live in `agents/` alongside this SKILL.md.
Always `subagent_type="claude"`. Inject the agent definition and all required context into the prompt.

```
[Orchestrator]
Read: .agents/skills/synthesize-hypotheses/agents/<agent-name>.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="<short description>",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

<task-specific variables and paths>
"""
)
```

---

## Setup

Read `config/workspace.json` → CONFIG.
```
OUTPUT_ROOT    = resolve(CONFIG.output_root)
ANALYTICS_PATH = CONFIG.analytics_folder + "/events.jsonl"
```

**Analytics — write start event** (append to ANALYTICS_PATH via `write_file` mode=append):
```
RUN_ID = "sh-{YYYYMMDD-HHMMSS}"
SCOPE  = "--topic {topic}" if --topic else "all"
```
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_start","skill":"synthesize-hypotheses","version":"1.0.0","mode":"{SCOPE}","input_summary":"hypothesis synthesis"}
```
If ANALYTICS_PATH does not exist yet, create it (empty file) before appending.

```
HYPOTHESES_DIR = {OUTPUT_ROOT}/cards/hypotheses/
PAPER_CARDS_DIR = {OUTPUT_ROOT}/cards/paper-cards/
HYPOTHESIS_LEDGER = {OUTPUT_ROOT}/indexes/hypothesis-ledger.md
SKIPPED_LOG = {OUTPUT_ROOT}/indexes/_synthesis_skipped.md
TOPIC_MAP = {OUTPUT_ROOT}/indexes/topic-map.md
```

Read `artifacts/research_hypothesis_schema.md` → `HYPOTHESIS_SCHEMA`
Read `criteria/qml_domain.md` → `QML_CRITERIA`

If `--topic` is set, scope synthesis to that topic only. Otherwise synthesize all topics from `topic-map.md`.

Print: `Synthesizing hypotheses | Topic scope: {topic or "all"} | Output: {OUTPUT_ROOT}`

---

## Phase 1 — Paper Card Inventory

**Goal:** Build a structured inventory of all paper cards, grouped by topic, with verdict and inline claim content.

For each topic in scope (from `topic-map.md`):
1. List all paper cards linked under that topic section
2. For each paper card, read:
   - `verdict` from frontmatter
   - `claim_status` from frontmatter
   - `## Main Claim` section body
   - `## QML Criteria Evaluation` section body
   - `## Overall Verdict` rationale
3. Filter to cards with `verdict ∈ [STRONG_INTEREST, CONDITIONAL]` — skip WEAK and REJECT

Write `{OUTPUT_ROOT}/extractions/synthesis_{date}/00_paper_inventory.md`:
```markdown
# Paper Inventory for Synthesis

**Date:** {YYYY-MM-DD}
**Topics scoped:** {list}
**Total paper cards found:** {N}
**Filtered to STRONG_INTEREST/CONDITIONAL:** {N}

## By Topic

### {topic-slug}
| arXiv ID | Verdict | Claim status | Main claim summary |
|----------|---------|-------------|-------------------|
| {id} | {verdict} | {status} | {one-line summary} |
```

**Gate:** inventory has ≥1 paper cards.

---

## Phase 2 — Pattern Detection

**Goal:** Identify cross-paper claim clusters and score each candidate hypothesis against the Pareto filter.

**Agent:** `agents/hypothesis-synthesizer.md`

```
Read: .agents/skills/synthesize-hypotheses/agents/hypothesis-synthesizer.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Detect cross-paper claim clusters and score hypothesis candidates",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

workspace: {OUTPUT_ROOT}/extractions/synthesis_{date}/
qml_criteria: {QML_CRITERIA}
hypothesis_schema: {HYPOTHESIS_SCHEMA}

Read: {OUTPUT_ROOT}/extractions/synthesis_{date}/00_paper_inventory.md
Also read: {OUTPUT_ROOT}/cards/hypotheses/ (existing hypothesis cards — check for updates vs new)

Detect claim clusters. For each candidate, apply the promotion filter.
Write output to: {OUTPUT_ROOT}/extractions/synthesis_{date}/01_hypothesis_candidates.md
"""
)
```

**Gate:** `01_hypothesis_candidates.md` exists with at least one PROMOTED or SKIPPED entry.

---

## Phase 3 — Hypothesis Card Writing

**Goal:** Write new hypothesis cards and update existing ones. Log skipped candidates.

For each PROMOTED candidate in `01_hypothesis_candidates.md`:

1. Check if `{HYPOTHESES_DIR}/{slug}.md` exists:
   - **New:** write full card per `HYPOTHESIS_SCHEMA`
   - **Update:** read existing card, update `support_count`, `supporting_papers`, `status` if warranted, `last_synthesized`
   - **Status downgrade never happens** — log to `_conflicts.md` if new evidence contradicts

2. Write or update `{HYPOTHESES_DIR}/{slug}.md`

For each SKIPPED candidate:
- Append to `{SKIPPED_LOG}`:
```markdown
| {YYYY-MM-DD} | {candidate title} | {filter that failed} | {reason} |
```

If `--dry-run`: print what would be written, do not write files.

**Gate:** all PROMOTED candidates have a file written or verified updated.

---

## Phase 4 — Hypothesis Ledger Update

**Goal:** Rebuild `hypothesis-ledger.md` to reflect all current hypothesis cards.

Scan `{HYPOTHESES_DIR}/*.md`. For each card with `strategic_value ∈ [directional, actionable]`:

Rebuild `{HYPOTHESIS_LEDGER}`:
```markdown
---
title: Hypothesis Ledger
description: All Research Hypotheses — cross-paper synthesis, Pareto-filtered
updated: {YYYY-MM-DD}
---

# Hypothesis Ledger

Pareto view: directional + actionable hypotheses only. `foundational` and `incremental` hypotheses are archived but not shown here.

Status ladder: `speculative → plausible → observed → supported → strong → published ↘ refuted`

| Hypothesis | Status | Support count | Strategic value | QML criteria passed | Last synthesized |
|-----------|--------|--------------|-----------------|---------------------|-----------------|
| [[cards/hypotheses/{slug}]] | {status} | {N} papers | {strategic_value} | {criteria list} | {date} |
```

Sort rows by: `strategic_value` (actionable first, then directional) then `support_count` descending.

---

## Completion

**Analytics — write end event** (append to ANALYTICS_PATH):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_end","skill":"synthesize-hypotheses","version":"1.0.0","outcome":"success","duration_s":{elapsed},"output_path":"{HYPOTHESIS_LEDGER}"}
```

Print:
```
✓ /synthesize-hypotheses complete

Topics:     {N} scoped
Papers:     {N} inventoried, {N} STRONG_INTEREST/CONDITIONAL

Hypotheses:
  Created:   {N}
  Updated:   {N}
  Skipped:   {N}  →  {SKIPPED_LOG}

Hypothesis ledger: {HYPOTHESIS_LEDGER}
```

If any were skipped: list them with the failing filter.

---

## Failure Modes to Avoid

```
❌ Promoting a hypothesis with support_count = 1 — minimum is 2 independent sources
❌ Setting strategic_value = incremental — log to skipped, do not create card
❌ Omitting open_risks — every hypothesis must document unresolved QML criteria
❌ Downgrading existing hypothesis status — log conflict, preserve current status
❌ Including per-paper claim text that belongs in the paper card — synthesis is cross-paper patterns only
❌ Creating a hypothesis for a direction explicitly deprioritized in qml_domain.md — log skip with reason
```
