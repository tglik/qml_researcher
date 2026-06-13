---
name: qml-primitive-transfer
version: 1.0.0
description: |
  Given a quantum primitive (e.g., neutral-atom MIS solver), maps it to equivalent
  NP-hard / combinatorial problem reductions, identifies classical ML workloads that
  can use the primitive as an accelerator block, and rates each workload by
  multi-dimensional business value. Produces a ranked Primitive Transfer Card.

  Use after a deep-research or paper-review run surfaces a promising quantum primitive,
  or whenever the team wants to systematically ask "what classical ML can we accelerate
  with this building block, and which of those opportunities is worth chasing?"

triggers:
  - what can we transfer from this primitive
  - what classical ML problems map to
  - business potential of this primitive
  - what ML workloads can we accelerate with
  - equivalent problems to
  - transfer analysis for
  - what other problems can we solve with
  - map this quantum primitive
  - quantum to ml bridge
  - what can we do with this solver

input:
  - Quantum primitive description (required) — name, native structure, hardware modality, regime.
    May be given as: (a) a plain prompt describing the primitive, or (b) a path to a
    /qml-deep-research or /qml-paper-review workspace — skill will extract the primitive from it.
  - Optional --no-business: skip Phase 2 (business rating); produce problem+workload map only.
  - Optional --from-report <path>: explicitly point to a prior research workspace to extract the primitive from.

output:
  - Transfer card workspace: {output_root}/sources/transfer-cards/{slug}_{YYYY-MM-DD}/
    - 00_primitive.md           — structured primitive profile
    - 01_equivalent_problems.md — equivalent NP-hard / combinatorial problem map
    - 02_ml_workloads.md        — ML workload map per equivalent problem
    - 03_business_ratings.md    — multi-dimensional business value ratings (skipped with --no-business)
    - 04_transfer_card.md       — final ranked Primitive Transfer Card
    - 04_transfer_card.docx     — Word export
    - session_memory.md
    - state.json

allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - WebSearch
  - WebFetch
  - Bash
---

# /qml-primitive-transfer

Quantum primitive in → equivalent problems mapped → ML workloads identified → business value rated → ranked Transfer Card out.

> **Infrastructure:** Read `.agents/shared/protocol.md` once during Setup. It provides the
> Agent Spawn Convention, Hermes I/O policy, progress update format, Word export instructions,
> session memory format, and completion message format.

---

## Hermes Platform Notes

- Use `clarify` instead of `AskUserQuestion` for primitive framing clarifications.
- Progress updates go to the current DM/thread.
- Do NOT use `execute_code` for file reads/writes — use Hermes file tools.

---

## Iron Rules

```
❌ Do NOT conflate problem reduction direction — track which way the reduction runs
❌ Do NOT rate business value without naming a specific paying customer or market
❌ Do NOT write the Transfer Card yourself — delegate to opportunity-writer
❌ Do NOT skip Phase 0 primitive framing — a vague primitive produces a useless map
❌ Do NOT suggest ML workloads without tracing the reduction chain explicitly
❌ Do NOT rate every workload HIGH — differentiation is the point of the rating
```

---

## Setup

**Config** — read once at start:
```
Read: config/workspace.json → CONFIG
OUTPUT_ROOT    = resolve(CONFIG.output_root)
ANALYTICS_PATH = CONFIG.analytics_folder + "/events.jsonl"
```

**Analytics — write start event** (append to ANALYTICS_PATH via `write_file` mode=append):
```
RUN_ID = "pt-{YYYYMMDD-HHMMSS}"
MODE   = "no-business" if --no-business else "full"
```
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_start","skill":"qml-primitive-transfer","version":"1.0.0","mode":"{MODE}","input_summary":"{primitive_slug}"}
```
If ANALYTICS_PATH does not exist yet, create it (empty file) before appending.

**Workspace:**
```
WORKSPACE = {OUTPUT_ROOT}/sources/transfer-cards/{slug}_{YYYY-MM-DD}/
```
`slug` = primitive name → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json`:
`current_phase`, `no_business_mode`, `primitive_name`, `hardware`, `regime`,
`source_report` (path or null), `equivalent_problems_count`, `ml_workloads_count`,
`high_opportunities_count`, `final_docx_path`.

**Agents directory:**
```
AGENTS_DIR = .agents/skills/qml-primitive-transfer/agents/
```

**Read domain criteria** — inject into agents that need them:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

**Read artifact schema** — inject into opportunity-writer:
```
Read: artifacts/primitive_transfer_card_schema.md → TRANSFER_SCHEMA
```

**Read shared/protocol.md** — load Agent Spawn Convention, progress format, completion format.

---

## Phase 0 — Primitive Framing

**Goal:** Produce a structured primitive profile before any mapping begins. A vague primitive
produces a useless map.

**Runs in the main session — no agent delegation.**

### 0.1 Parse input

**Case A — plain prompt:**
Extract from the user's description:
- Primitive name (e.g., "Maximum Independent Set solver")
- Native combinatorial structure (e.g., "graph: find largest subset of vertices with no adjacent pair")
- Hardware modality (e.g., "neutral-atom Rydberg blockade")
- Regime: NISQ | FT | ANALOG
- Advantage mechanism (what makes this primitive natural on the hardware)
- Source (paper title / arXiv ID if mentioned)

**Case B — `--from-report <path>` or path provided:**
```
Read: {path}/06_final_report.md  (or 04_final_report.md for paper-review)
```
Scan for: quantum primitive mentions, hardware modality, combinatorial structure.
Extract the primary primitive the report centers on. If multiple primitives found, list them
and ask: "I found N quantum primitives in this report. Which should I transfer-map?"

### 0.2 Primitive framing gate

If ANY of the following are missing, ask (one question, all missing fields combined):
- Primitive name
- Native combinatorial structure
- Hardware modality
- Regime

Offer defaults derived from context where available. Do not ask for fields you can infer.

### 0.3 Write `{WORKSPACE}/00_primitive.md`

```markdown
# Primitive Profile: {name}

**Primitive name:** {name}
**Native combinatorial structure:** {description}
**Hardware modality:** {hardware}
**Regime:** {NISQ | ANALOG | FT}
**Advantage mechanism:** {why this is natural on the hardware}
**Key constraint:** {what currently limits scale or fidelity}
**Source:** {paper/report or "user description"}

---
## Links
- Equivalent problems: [[01_equivalent_problems.md]]
- ML workloads: [[02_ml_workloads.md]]
- Transfer card: [[04_transfer_card.md]]
```

**Gate:** primitive name, native structure, hardware, regime all present in `00_primitive.md` ✓

Progress update:
```
Progress: Phase 0 — Primitive framing complete.
- Primitive: {name}  |  Hardware: {hardware}  |  Regime: {regime}
Next: Phase 1 — map to equivalent problems and ML workloads.
```

---

## Phase 1 — Problem Equivalence + ML Workload Mapping

**Goal:** Map the primitive to equivalent NP-hard / combinatorial problem classes via known
reductions, then forward-map each equivalent problem to classical ML workloads that face
the same structure.

**Agent:** `problem-mapper`

```
Read: {AGENTS_DIR}/problem-mapper.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Map {primitive_name} to equivalent problems and ML workloads",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria
{QML_DOMAIN}

---

## Task for this invocation

workspace: {WORKSPACE}
primitive_profile: {WORKSPACE}/00_primitive.md

Read 00_primitive.md first.

Write two output files:
  {WORKSPACE}/01_equivalent_problems.md
  {WORKSPACE}/02_ml_workloads.md

See your role definition for the output format required in each file.
"""
)
```

**Gate:**
- `01_equivalent_problems.md` exists with ≥ 3 equivalent problems ✓
- `02_ml_workloads.md` exists with ≥ 3 ML workloads ✓
- Each workload traces its reduction chain to the primitive explicitly ✓

Update `state.json`: `equivalent_problems_count`, `ml_workloads_count`.

Progress update:
```
Progress: Phase 1 — Problem + ML workload mapping complete.
- Equivalent problems: {N}  |  ML workloads: {N}
Next: Phase 2 — business value rating.
```

If `--no-business`: skip Phase 2 entirely. Go to Phase 3 with `03_business_ratings.md` absent.

---

## Phase 2 — Business Value Rating

**Skip if `--no-business`. Note in transfer card and completion: "Business rating skipped (--no-business)."**

**Goal:** Rate each ML workload on four business value dimensions. Force differentiation —
not every workload can be HIGH.

**Agent:** `business-rater`

```
Read: {AGENTS_DIR}/business-rater.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Rate business value of ML workloads derived from {primitive_name}",
  prompt="""
{AGENT_DEF}

---

## Task for this invocation

workspace: {WORKSPACE}
primitive_profile: {WORKSPACE}/00_primitive.md
equivalent_problems: {WORKSPACE}/01_equivalent_problems.md
ml_workloads: {WORKSPACE}/02_ml_workloads.md

Read all three files first.

Write: {WORKSPACE}/03_business_ratings.md

See your role definition for the 4-dimension scoring rubric and output format.
"""
)
```

**Gate:**
- `03_business_ratings.md` exists ✓
- Every ML workload from `02_ml_workloads.md` has a row in the ratings ✓
- Rating distribution is differentiated (not all HIGH) ✓

Update `state.json`: `high_opportunities_count`.

Progress update:
```
Progress: Phase 2 — Business value rating complete.
- Workloads rated: {N}  |  HIGH: {N}  |  MED: {N}  |  LOW: {N}
Next: Phase 3 — write Primitive Transfer Card.
```

---

## Phase 3 — Primitive Transfer Card

**Goal:** Produce the final structured, ranked Transfer Card following the artifact schema.

**Agent:** `opportunity-writer` — **MANDATORY: do NOT write the Transfer Card yourself.**

```
Read: {AGENTS_DIR}/opportunity-writer.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Write Primitive Transfer Card for {primitive_name}",
  prompt="""
{AGENT_DEF}

---

## Transfer Card Schema
{TRANSFER_SCHEMA}

---

## Task for this invocation

workspace: {WORKSPACE}
inputs:
  - {WORKSPACE}/00_primitive.md
  - {WORKSPACE}/01_equivalent_problems.md
  - {WORKSPACE}/02_ml_workloads.md
  - {WORKSPACE}/03_business_ratings.md  (may be absent if --no-business)

no_business_mode: {true | false}

Read all available input files first.

Write: {WORKSPACE}/04_transfer_card.md
Then export: {WORKSPACE}/04_transfer_card.docx  (see protocol.md → Word Export section)
"""
)
```

**Word export:** See `.agents/shared/protocol.md` → Word Export section.

**Gate:** Confirm `04_transfer_card.md` and `04_transfer_card.docx` both exist and are non-empty ✓

Update `state.json`: `final_docx_path`.

---

## Completion

1. Confirm `04_transfer_card.md` and `04_transfer_card.docx` exist and are non-empty.

2. **Analytics — write end event** (append to ANALYTICS_PATH):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_end","skill":"qml-primitive-transfer","version":"1.0.0","outcome":"success","duration_s":{elapsed},"output_path":"sources/transfer-cards/{slug}_{YYYY-MM-DD}/"}
```
If any `skill_error` event was written, set `outcome` to `"error"` instead.

3. Write `{WORKSPACE}/session_memory.md` using the format in `shared/protocol.md`.
   Skill-specific fields:
   - `primitive`, `hardware`, `regime`
   - `equivalent_problems_count`, `ml_workloads_count`
   - `high_opportunities` (list of HIGH-rated workload names)
   - `no_business_mode` (true/false)
   - Executive summary bullets (3)
   - Connector payload: `[{date}] [SOURCE: qml-primitive-transfer] Transfer map: {primitive} → {N} ML workloads. TOP: {top_opportunity}. Word card: [[{WORKSPACE}/04_transfer_card.docx]]`

4. Report to user using the completion message format in `shared/protocol.md`. Lead with the
   top 3 HIGH opportunities and their business rationale. Include what-was-done checklist.
   Attach the Word report.

   Also append at the end of the completion message:
   ```
   Next step suggestion: If any HIGH opportunity looks actionable,
   run /qml-deep-research on the specific workload to validate the quantum advantage claim.
   ```

---

## No-Business Mode

If `--no-business`:
- Run: Phase 0 → Phase 1 → Phase 3 (skip Phase 2)
- Phase 3 inputs: `00_primitive.md`, `01_equivalent_problems.md`, `02_ml_workloads.md` only
- Opportunity-writer produces the card without business ratings; ranks workloads by strategic fit instead
- Note in completion: "Business rating skipped (--no-business). Workloads ranked by strategic fit."

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Vague primitive ("some quantum solver") | Produces unmappable reduction chain | Always run Phase 0 framing before Phase 1 |
| Confuse reduction direction | "MIS reduces to X" ≠ "X reduces to MIS" | Track direction explicitly in `01_equivalent_problems.md` |
| Rate all workloads HIGH | Removes decision signal — which one do we chase? | Force differentiation; ≤40% of workloads can be HIGH |
| Name a market without naming a payer | "Healthcare is a big market" is useless | Name who pays, for what outcome, at what scale |
| Orphaned ML workload (no reduction trace) | Looks connected but isn't | Every workload must cite its equivalent problem chain |
| Skip Phase 0 when input is a research report | Report may mention many primitives; wrong one gets mapped | Always extract + confirm primitive before Phase 1 |
| Write Transfer Card as orchestrator | Removes generator/writer separation | Always delegate to opportunity-writer |
