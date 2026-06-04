---
name: extract-artifacts
version: 2.0.0
description: |
  Reads any Layer 1 source file (skill report, meeting note, news item, discussion, or
  document) and extracts structured Layer 2 cards into the artifact knowledge base.
  Deduplicates by canonical ID, merges additive fields, logs conflicts, and updates
  all Layer 3 indexes. Run after any skill that produces a source, or drop a raw input
  (meeting note, WhatsApp summary, news item) and run manually.

triggers:
  - extract artifacts
  - extract cards
  - process this source
  - ingest this meeting
  - ingest this paper review
  - update the knowledge base

input:
  - source_file_path: path to the Layer 1 source file (required)
  - --dry-run: print what would be written without writing (optional)
  - --force: re-extract even if source is already marked extracted: true (optional)

output:
  - cards/ — new and updated entity cards in the artifact repo
  - indexes/ — paper-registry, claim-ledger, author-index, topic-map updated
  - _conflicts.md — any conflicts appended for human review
  - source file — Extracted Cards section added, frontmatter marked extracted: true
  - extractions/{slug}_{date}/ — phase workspace with intermediate artifacts

allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /extract-artifacts

Any Layer 1 source file → entity cards extracted → knowledge base updated → indexes current.

---

## Agent Spawn Convention

All agent definitions live in `agents/` alongside this SKILL.md.
Always `subagent_type="claude"`. Inject the agent definition and all required context into the prompt.

```
[Orchestrator]
Read: .claude/skills/extract-artifacts/agents/<agent-name>.md → AGENT_DEF

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

Read `config/workspace.json` → `OUTPUT_ROOT = resolve(config.output_root)`.

Resolve `source_path` to an absolute path. If the path does not exist, stop with:
```
Error: source file not found: {source_path}
```

Read `source_path` frontmatter only (first ~20 lines). Check:
- `source_type` present? If not → stop: "source_type missing from frontmatter. Add it and retry."
- `extracted: true` present? If yes and `--force` not set → stop: "Already extracted. Use --force to re-extract."

Set:
```
SOURCE_TYPE  = frontmatter.source_type
SOURCE_DATE  = frontmatter.source_date
CLAIM_CEILING = {
  skill-report  → observed,
  document      → plausible,
  meeting-note  → speculative,
  discussion    → speculative,
  news-item     → speculative
}[SOURCE_TYPE]

SOURCE_SLUG = {first 4 significant words of filename, hyphens, lowercase}
WORKSPACE   = {OUTPUT_ROOT}/extractions/{SOURCE_SLUG}_{SOURCE_DATE}/
```

Create `WORKSPACE` directory. Write `state.json`:
```json
{
  "source_path": "...",
  "source_type": "...",
  "source_date": "...",
  "claim_ceiling": "...",
  "workspace": "...",
  "output_root": "...",
  "phase": "setup",
  "dry_run": false,
  "force": false
}
```

Print: `Source: {source_path} | Type: {SOURCE_TYPE} | Ceiling: {CLAIM_CEILING}`

---

## Phase 1 — Source Classification

**Goal:** Parse the source file and extract all raw entities into a structured document.

**Agent:** `agents/source-classifier.md`

```
Read: .claude/skills/extract-artifacts/agents/source-classifier.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Parse source file and extract all raw entities",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

source_path: {source_path}
source_type: {SOURCE_TYPE}
claim_status_ceiling: {CLAIM_CEILING}
workspace: {WORKSPACE}

Read the source file at source_path. Extract all entities per your protocol.
Write output to: {WORKSPACE}/00_source_parsed.md
"""
)
```

**Gate Phase 1 → Phase 2:**
- `{WORKSPACE}/00_source_parsed.md` exists and is non-empty ✓
- No validation errors reported in the parsed document ✓

Update `state.json`: `"phase": "phase-1-complete"`.

---

## Phase 2 — Entity Generation

**Goal:** Assign canonical IDs to all extracted entities and generate complete card bodies.

**Agent:** `agents/entity-extractor.md`

Read the three card schemas to inject:
```
Read: artifacts/paper_card_schema.md   → PAPER_SCHEMA
Read: artifacts/claim_card_schema.md   → CLAIM_SCHEMA
Read: artifacts/author_card_schema.md  → AUTHOR_SCHEMA
Read: artifacts/evidence_card_schema.md → EVIDENCE_SCHEMA
```

```
Read: .claude/skills/extract-artifacts/agents/entity-extractor.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Generate canonical card content for all extracted entities",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

workspace: {WORKSPACE}
source_type: {SOURCE_TYPE}
claim_status_ceiling: {CLAIM_CEILING}
source_path: {source_path}
output_root: {OUTPUT_ROOT}

## Card Schemas (use these as the template for each card type)

### Paper Card Schema
{PAPER_SCHEMA}

### Claim Card Schema
{CLAIM_SCHEMA}

### Author Card Schema
{AUTHOR_SCHEMA}

### Evidence Card Schema
{EVIDENCE_SCHEMA}

Read: {WORKSPACE}/00_source_parsed.md
Generate canonical IDs and complete card bodies for every entity.
Write output to: {WORKSPACE}/01_entities.md
"""
)
```

**Gate Phase 2 → Phase 3:**
- `{WORKSPACE}/01_entities.md` exists ✓
- ID Assignment Log section present ✓

Update `state.json`: `"phase": "phase-2-complete"`.

---

## Phase 3 — Card Writing

**Goal:** Create new cards or merge into existing ones. Log conflicts.

**Agent:** `agents/card-writer.md`

```
Read: .claude/skills/extract-artifacts/agents/card-writer.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Write or merge entity cards into the artifact repo",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

workspace: {WORKSPACE}
output_root: {OUTPUT_ROOT}
source_path: {source_path}
conflicts_path: {OUTPUT_ROOT}/_conflicts.md

Read: {WORKSPACE}/01_entities.md
For each entity: check {OUTPUT_ROOT}/cards/{type}/{id}.md, create or merge, log conflicts.
Write output to: {WORKSPACE}/02_write_report.md
"""
)
```

**Gate Phase 3 → Phase 4:**
- `{WORKSPACE}/02_write_report.md` exists ✓
- Summary counts present (created, merged, conflicts) ✓

If `--dry-run`: print the write report and stop. Do not proceed to Phase 4.

Update `state.json`: `"phase": "phase-3-complete"`.

---

## Phase 4 — Index Update

**Goal:** Update all four indexes to reflect new and updated cards. Mark source as extracted.

**Agent:** `agents/index-updater.md`

```
Read: .claude/skills/extract-artifacts/agents/index-updater.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Update knowledge base indexes and mark source as extracted",
  prompt="""
{AGENT_DEF}

---

## Context for this invocation

workspace: {WORKSPACE}
output_root: {OUTPUT_ROOT}
source_path: {source_path}
source_date: {SOURCE_DATE}

Read: {WORKSPACE}/02_write_report.md
Update indexes in {OUTPUT_ROOT}/indexes/.
Append Extracted Cards section to {source_path}.
Mark {source_path} frontmatter: extracted: true, extracted_date: {today}.
"""
)
```

**Gate Phase 4 → Completion:**
- `paper-registry.md` updated (rows added/updated) ✓
- `claim-ledger.md` updated ✓
- Source file has `## Extracted Cards` section ✓
- Source frontmatter has `extracted: true` ✓

---

## Completion

Read `{WORKSPACE}/02_write_report.md` for counts. Print:

```
✓ /extract-artifacts complete

Source:   {source_path}
Type:     {SOURCE_TYPE}
Ceiling:  {CLAIM_CEILING}

Cards written:
  Created:   {N}
  Merged:    {N}
  Conflicts: {N} — see {OUTPUT_ROOT}/_conflicts.md
  Skipped:   {N}

Indexes updated: paper-registry, claim-ledger, author-index, topic-map
Workspace: {WORKSPACE}
```

If any conflicts were logged, add:
```
⚠  {N} conflict(s) need human review → {OUTPUT_ROOT}/_conflicts.md
```

---

## Fast Mode (`--dry-run`)

Runs Phases 1–3 only. Prints the write report. Does not write any cards or update any indexes. Use to preview what would change before committing.

---

## Failure Modes to Avoid

```
❌ Running without source_type in frontmatter — always validate before spawning agents
❌ Re-extracting an already-extracted source without --force — check extracted: true
❌ Skipping conflict logging — every disagreement must be recorded
❌ Letting index-updater run if card-writer reported zero cards — nothing to index
❌ Hardcoding output_root — always read from config/workspace.json
```
