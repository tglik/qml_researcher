---
name: qml-deep-research
version: 1.1.0
description: |
  Multi-agent deep research workflow for QML topics. Decomposes a question into
  scoped sub-questions, runs parallel literature sweeps, applies the five QML criteria
  to classify every source, synthesizes evidence into a grounded draft, adversarially
  challenges it, audits every claim against its source, and writes a final report with
  a dequantization risk table and startup implications.

  Use when asked to "research X", "what does the field say about X", "literature review",
  "investigate QML topic", or any question requiring systematic evidence (not just triage).

triggers:
  - deep research
  - research this topic
  - literature review on
  - what does the field say
  - investigate qml
  - qml research
  - what do we know about
  - is this claim true
  - fact check this
  - verify this paper
  - give me a reading list
  - what papers exist on
  - annotated bibliography

input:
  - Research question or topic (required)
  - Optional --fast: skip phases 2 and 4-5 (Phase 0 → 1 → 3 → 6)
  - Optional --scope-only: stop after Phase 0 and wait for user review
  - Optional --socratic: run guided 5-question QML clarification before PICO (for vague inputs)
  - Optional --lit-review: stop after Phase 1; produce annotated bibliography instead of synthesis
  - Optional --fact-check: verify a single claim or paper (Phase 1 targeted + Phase 5 only)

output:
  - Research workspace: {vault}/research/{slug}_{YYYY-MM-DD}/
    - 00_scope.md
    - 01_literature_merged.md
    - 02_domain_classification.md
    - 03_draft_report.md
    - 04_challenges.md
    - 05_evidence_ledger.md
    - 06_final_report.md

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
---

# /qml-deep-research

Multi-agent QML literature research. Question in → grounded report out.

---

## ⚠️ IRON RULES — Read Before Starting

```
❌ Do NOT synthesize research content yourself — delegate to agents
❌ Do NOT write the final report prose yourself — delegate to synthesis-writer
❌ Do NOT skip Phase 4 (devil's advocate) in standard mode even if draft looks clean
❌ Do NOT merge adjacent phases to save time
❌ Do NOT let synthesis-writer run until evidence-auditor clears the draft
❌ Do NOT treat abstract-only synthesis as valid research output
```

---

## Setup

**Workspace directory** — all phase outputs go here:
```
WORKSPACE = C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup\research\{slug}_{YYYY-MM-DD}\
```

Where `slug` = parent question → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json` and update after each phase with: `current_phase`, `fast_mode`, `coverage_retry_per_subq`, `blocking_issues_count`, `revision_cycle` (max 2).

**Agent definitions directory** — all agents for this skill live here:
```
AGENTS_DIR = .claude/skills/qml-deep-research/agents/
```

**Domain criteria** — read once during Setup, before Phase 1. Inject into every agent that needs domain knowledge. This ensures all agents use the team's current criteria, not stale inline copies:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

The `QML_DOMAIN` variable is passed as a labelled section inside every relevant agent prompt (see Agent Spawn Convention and each phase below).

---

## Agent Spawn Convention

**This skill owns its agents.** All agent definitions live in `agents/` alongside this file.
Do NOT use named subagent types — always use `subagent_type="claude"` and inject the
agent definition into the prompt.

Before every Agent call in this skill:
1. Read the agent file: `Read AGENTS_DIR/<agent-name>.md`
2. Capture its full contents as `AGENT_DEF`
3. Spawn with `subagent_type="claude"`, prompt starting with `AGENT_DEF` followed by a `---` separator and the task

```
[You, the orchestrator]
Read: .claude/skills/qml-deep-research/agents/<agent-name>.md  → AGENT_DEF

Agent(
  subagent_type="claude",
  description="<short description>",
  prompt="""
{AGENT_DEF}

---

## Task for this invocation

<task-specific instructions>
"""
)
```

This pattern ensures: agents are self-contained within this skill, and changing an agent
here cannot affect any other skill.

---

## Phase 0 — Scope

**Goal:** Decompose the research question into 3-7 bounded sub-questions with explicit criteria. Confirm with user before launching literature sweep.

**This phase runs in the main session — no agent delegation.**

### Steps

**0.0 Socratic Clarification (only if `--socratic` flag is set or input is clearly vague)**

Trigger conditions: user provides a direction rather than a question ("something about reservoirs", "we should look at X", "what do you think about Y?"), or the PICO frame cannot be filled without guessing.

Ask these 5 questions in a single AskUserQuestion (multiSelect: false, one question per entry):

1. **Data type**: What kind of data is this quantum approach operating on? (tabular / graph / molecular / time-series / unstructured / other)
2. **Regime intent**: Are we asking what's NISQ-feasible now, or what the theoretical direction looks like long-term? (NISQ-feasible now / long-term theoretical / both)
3. **Baseline bar**: What would "it works" mean — better than what? (beat XGBoost/TabPFN / beat GNN / beat SOAP/GAP / beat existing quantum method / no baseline defined yet)
4. **Dequantization concern**: Is the proposed advantage based on data structure access (high dequantization risk) or geometry/Hamiltonian structure (lower risk)? (data-structure / geometry-Hamiltonian / unclear)
5. **Hardware scope**: Must this work on neutral-atom specifically, or is this a hardware-agnostic survey? (neutral-atom only / hardware-agnostic / both)

Use answers to auto-fill the PICO frame. Skip the manual PICO prompting. Proceed to 0.2 FINER.

---

**0.1 PICO framing:**
- P (Problem): What QML problem / domain / data type?
- I (Intervention): What quantum approach is being evaluated?
- C (Comparator): What classical or alternative quantum approach?
- O (Outcome): What metric or capability?

**0.2 FINER quality check:**
- F (Feasible): Can this be answered with available papers?
- I (Interesting): Does the answer matter for team direction?
- N (Novel): Check `triage_log.jsonl` — has this been systematically covered already?
- E (Ethical): No concerns.
- R (Relevant): Directly actionable for QML startup decisions?

Revise the question if any FINER dimension fails.

**0.3 Sub-question decomposition** — for each sub-question define:
- `search_terms[]` — 3-5 keywords including QML facets
- `date_range` — default "2019–2025"
- `min_sources` — default 3
- `domain_tags[]`

**0.4 Write scope to `WORKSPACE/00_scope.md`:**

```markdown
# Research Scope: <parent question>

## PICO Frame
- P: | I: | C: | O:

## Sub-Questions
| ID | Sub-question | Search terms | Date range | Min sources |
|----|---|---|---|---|
| Q1 | ... | ... | ... | 3 |

## Inclusion Criteria
## Exclusion Criteria
## Domain: QML/quantum: yes | no
## Fast mode: yes | no
```

**0.5 GATE — confirm scope with user:**

> Research scope drafted: "<parent question>" — N sub-questions. Confirm to launch?

- A) Looks good — launch (recommended)
- B) Adjust the scope

If B: revise and ask again. If `--scope-only`: stop here.

---

## Phase 1 — Literature Sweep

**Goal:** Screened bibliography for each sub-question cluster.

**Agent:** `agents/literature-scout.md`

Group sub-questions sharing ≥ 2 search terms into clusters (aim 2-3 clusters total).
Run all cluster agents **in parallel** (single message, multiple Agent calls).

For each cluster:

```
Read: .claude/skills/qml-deep-research/agents/literature-scout.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="QML literature sweep: <cluster topic>",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Search QML and quantum computing literature for the following sub-questions.

Sub-questions: <Q_ids and text from 00_scope.md>
Search terms per question: <from 00_scope.md>
Date range: <from scope>
Minimum sources per sub-question: <from scope>
Prioritize: arXiv quant-ph + cs.LG, Semantic Scholar, PRX Quantum, NeurIPS/ICML/ICLR

Return the candidate source table, coverage gaps, and contradictions
using the output format in your Role section above.

Output file: <WORKSPACE>/01_literature_<cluster_slug>.md
Return the file path and a one-paragraph summary.
"""
)
```

Wait for all cluster agents to complete. Retry once if an agent fails to produce its output file; if it fails again, ask user whether to abort or proceed without that cluster.

**Coverage gap handling:** re-run literature-scout with broader terms for any sub-question with < min_sources. Do this at most once per gap; flag remaining gaps in `00_scope.md`.

Merge all cluster output files into `01_literature_merged.md` (mechanical concatenation + deduplication — you can do this yourself).

---

## Lit-Review Mode Gate

**If `--lit-review` flag is set: stop here after Phase 1. Do not run Phases 2-6.**

Produce an annotated bibliography from `01_literature_merged.md`. For each included source write exactly:

```markdown
### [Author YYYY] — <Title>
**arXiv/DOI:** <id>  **Venue:** <venue> (Tier T?)
**Five-criteria tags:** Dequant: LOW/MEDIUM/HIGH | Regime: NISQ/FT/analog | Baseline: STRONG/WEAK/ABSENT
**Key claim:** <one sentence — what the paper claims, in its own terms>
**Why in scope:** <one sentence — which sub-question this addresses>
**Caveat:** <one sentence — main limitation or assumption>
```

Output file: `WORKSPACE/lit_review_<slug>.md`

Report to user:
```
LIT REVIEW COMPLETE

Topic: <parent question>
Workspace: <WORKSPACE>
Sources included: N  |  Excluded: N
Output: lit_review_<slug>.md

Top 3 by relevance:
1. [cite] — <why>
2. [cite] — <why>
3. [cite] — <why>

Dequant risk breakdown: N HIGH / N MEDIUM / N LOW
STATUS: DONE
```

Append one line to vault `recent.md`:
```
[<YYYY-MM-DD>] [SOURCE: session] Lit review completed: <topic>. N sources. Output: <path>
```

---

## Phase 2 — QML Domain Classification

**Skip if scope domain = "no" OR `--fast` flag is set. Go directly to Phase 3.**

**Goal:** Apply the five QML criteria to every candidate source before synthesis.

**Agent:** `agents/quantum-domain-analyst.md`

```
Read: .claude/skills/qml-deep-research/agents/quantum-domain-analyst.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Five-criteria QML classification of literature",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Classify every source in the merged literature file using the five QML criteria
and domain classification format defined in your Role section above.

Input files:
- Merged literature: <WORKSPACE>/01_literature_merged.md
- Research scope: <WORKSPACE>/00_scope.md

Apply all five criteria to each source and produce the full classification output
including the Strong Directions and Deprioritized Directions summaries.

Output file: <WORKSPACE>/02_domain_classification.md
Return the file path and a count of STRONG vs DEPRIORITIZED directions.
"""
)
```

**GATE:** Read `02_domain_classification.md`. Add a `⚠️ HIGH DEQUANTIZATION RISK` comment in `01_literature_merged.md` for every source flagged HIGH. Do not proceed to Phase 3 until classification is written.

---

## Phase 3 — Synthesis

**Goal:** Structured draft report grounded in screened, classified literature. Every claim must be inline-cited.

**Agent:** `agents/research-scientist.md`

**MANDATORY: do NOT write the synthesis yourself.**

```
Read: .claude/skills/qml-deep-research/agents/research-scientist.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="QML synthesis: draft report from classified literature",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Synthesize the screened QML literature into a structured draft report.
Follow the draft report structure in your Role section above exactly.

Input files:
- Scope: <WORKSPACE>/00_scope.md
- Merged literature: <WORKSPACE>/01_literature_merged.md
- Domain classification (if present): <WORKSPACE>/02_domain_classification.md

Write one section per sub-question. Label every claim with its status
(speculative | plausible | observed | supported | strong | published).
State regime (NISQ / FT-required / hardware-agnostic) for every quantum approach.
Flag coverage gaps explicitly. Do NOT include claims not in the literature file.

Output file: <WORKSPACE>/03_draft_report.md
Return the file path and a 3-sentence summary of main findings.
"""
)
```

**GATE:** Verify `03_draft_report.md` exists and has a References section. If any section lacks citations, return to research-scientist with specific revision instructions.

---

## Phase 4 — Challenge

**Goal:** Adversarial review of the draft. Finds QML-specific failure modes.

**Agent:** `agents/devils-advocate-scientist.md`

**MANDATORY: different agent invocation from Phase 3.**

```
Read: .claude/skills/qml-deep-research/agents/devils-advocate-scientist.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Adversarial QML challenge of draft report",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Stress-test the QML research draft using all seven attack vectors in your Role section:
dequantization, weak-baseline, regime-conflation, barren-plateau, hidden-assumption,
statistical-rigor, missing-contradiction.

Input files:
- Draft: <WORKSPACE>/03_draft_report.md
- Literature: <WORKSPACE>/01_literature_merged.md
- Domain classification (if present): <WORKSPACE>/02_domain_classification.md

For each section, identify BLOCKING and NON-BLOCKING issues.
Quote the exact claim challenged; name the attack type; suggest the fix.

Output file: <WORKSPACE>/04_challenges.md
Return the file path and counts: BLOCKING N, NON-BLOCKING N.
"""
)
```

**GATE:** If blocking issues exist, return `03_draft_report.md` to research-scientist with the blocking issues as explicit revision instructions. Re-run Phase 3 then Phase 4 on the revised draft. Allow at most **2 total revision cycles**. If blocking issues persist after cycle 2, flag to user.

---

## Phase 5 — Evidence Audit

**Goal:** Verify every claim in the (revised) draft is correctly supported by its cited source.

**Agent:** `agents/evidence-auditor.md`

```
Read: .claude/skills/qml-deep-research/agents/evidence-auditor.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Source-to-claim audit of QML draft",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Audit every material claim in the QML research draft against its cited source.
Apply the five QML-specific blocking rules and claim status ladder enforcement
from your Role section.

Input files:
- Draft: <WORKSPACE>/03_draft_report.md
- Literature: <WORKSPACE>/01_literature_merged.md
- Challenge log: <WORKSPACE>/04_challenges.md

Produce the full Evidence Ledger table and Audit Summary.

Output file: <WORKSPACE>/05_evidence_ledger.md
Return the file path and audit summary (total claims, alignment breakdown, verdict).
"""
)
```

**GATE:**
- If UNSUPPORTED claims exist: remove or re-cite them in `03_draft_report.md` yourself (mechanical deletion/rewording, not synthesis)
- If overall quality = LOW: return to Phase 3 with the ledger as input; re-run Phases 4-5. Same 2-cycle cap applies.
- Do NOT proceed to Phase 6 until UNSUPPORTED = 0.

---

## Phase 6 — Final Report

**Goal:** Polished report from audited evidence.

**Agent:** `agents/synthesis-writer.md`

**MANDATORY: do NOT author the final report prose yourself.**

```
Read: .claude/skills/qml-deep-research/agents/synthesis-writer.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Final QML research report from audited evidence",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Write the final QML research report following the QML Report Template in your Role section.

Input files (standard mode):
- Scope: <WORKSPACE>/00_scope.md
- Draft: <WORKSPACE>/03_draft_report.md
- Evidence ledger: <WORKSPACE>/05_evidence_ledger.md
- Challenge log: <WORKSPACE>/04_challenges.md

Use only claims rated ALIGNED or MODERATE/STRONG in the evidence ledger.
Soften any OVERSTATED claims as flagged.
Include the Dequantization Risk Table and Hardware Feasibility Summary.
Executive summary: 5-8 bullets, startup-strategy focus.

Output file: <WORKSPACE>/06_final_report.md
Return the file path.
"""
)
```

---

## Completion

1. Confirm `06_final_report.md` exists and is non-empty.

2. Append to vault `recent.md`:
```
[<YYYY-MM-DD>] [SOURCE: session] Deep research completed: <parent question>.
Key findings: <3 bullets from executive summary>.
Report: <WORKSPACE>/06_final_report.md
```

3. Report to user:
```
RESEARCH COMPLETE

Topic: <parent question>
Workspace: <WORKSPACE>

Files:
  00_scope.md              — scope + sub-questions
  01_literature_merged.md  — screened bibliography (N sources)
  02_domain_classification.md — five-criteria QML classification
  03_draft_report.md       — synthesis draft
  04_challenges.md         — adversarial challenges (N blocking resolved)
  05_evidence_ledger.md    — source-to-claim audit (N claims, N% aligned)
  06_final_report.md       — final report

Top findings:
  1. <from executive summary>
  2. <from executive summary>
  3. <from executive summary>

Dequantization risk: N HIGH / N MEDIUM / N LOW
Strong directions: <list>

STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
```

---

## Fast Mode

If the user says "fast research", "quick research", or passes `--fast`:
- Run: Phase 0 → Phase 1 → Phase 3 → Phase 6
- Skip Phases 2, 4, 5
- Phase 6 inputs: only `00_scope.md` and `03_draft_report.md`
- Note in completion: "Fast mode: domain classification, adversarial challenge, and evidence audit skipped. First-pass draft."

---

## Fact-Check Mode (`--fact-check`)

Use when: a specific claim needs verification (from a paper abstract, VC deck, team memo, or collaborator) without running full research.

**Pipeline: Phase 0 (claim framing only) → Phase 1 (targeted) → Phase 5 (audit) → output**

**Step FC-1: Frame the claim**

Identify:
- The exact verbatim claim to verify
- What type of claim: QML advantage | benchmark result | hardware feasibility | theoretical result | commercial claim
- The source (if any): citation, URL, or "unsourced"

Write `WORKSPACE/00_scope.md` with a single sub-question: "Is this claim supported by evidence?"

**Step FC-2: Targeted literature sweep**

Spawn `literature-scout` with a narrow search:
- Search terms: key technical terms from the claim + dequantization + classical baseline + the specific method
- Min sources: 3 papers that directly address the claim (pro or con)
- Date range: last 4 years unless the claim is foundational

```
Read: .claude/skills/qml-deep-research/agents/literature-scout.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Targeted literature sweep for claim verification",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Targeted search for evidence supporting or contradicting this specific claim:

**Claim:** "<verbatim claim>"
**Source:** <source if known>

Search for: papers that directly test, prove, disprove, or qualify this claim.
Also search for: dequantization risks for the specific method; stronger classical baselines.
Minimum 3 sources. Return the candidate source table and any direct contradictions found.

Output file: <WORKSPACE>/01_literature_merged.md
"""
)
```

**Step FC-3: Evidence audit of the claim**

Spawn `evidence-auditor` with a single-claim focus:

```
Read: .claude/skills/qml-deep-research/agents/evidence-auditor.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Claim verification audit",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Verify this specific claim against the literature found:

**Claim to verify:** "<verbatim claim>"

Apply the five QML-specific blocking rules. Return a single verdict:
- SUPPORTED — evidence directly backs the claim as stated
- OVERSTATED — evidence supports a weaker version; provide required rewording
- UNSUPPORTED — no valid evidence found
- CONTRADICTED — evidence directly refutes the claim

Input: <WORKSPACE>/01_literature_merged.md
Output file: <WORKSPACE>/05_evidence_ledger.md
"""
)
```

**Report to user:**
```
FACT-CHECK COMPLETE

Claim: "<verbatim claim>"
Verdict: SUPPORTED | OVERSTATED | UNSUPPORTED | CONTRADICTED
Evidence strength: STRONG | MODERATE | WEAK

[If OVERSTATED]: Suggested rewording: "..."
[If CONTRADICTED]: Contradicting evidence: [cite]

Supporting sources: N
Output: <WORKSPACE>/05_evidence_ledger.md
STATUS: DONE
```

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Main session writes synthesis | No generator/reviewer separation | Delegate to research-scientist agent |
| Use `subagent_type` by name | Couples skill to global agent directory | Always read from `./agents/` and inject inline |
| Skip devil's advocate because draft looks good | QML failure modes are non-obvious | Always run Phase 4 in standard mode |
| Abstract-only synthesis | Methods section often contradicts abstract | Require full-text fetch in literature-scout |
| Merge Phases 3+6 | Skips audit; overstated claims enter report | Always run evidence-auditor between synthesis and final write |
| Agent returns summary, not file | Next phase has no grounded input | Require explicit file path in every agent prompt |
| Vague input → skip Socratic → PICO guesses | Scope based on wrong assumptions; wasted research | Detect vague inputs; run `--socratic` clarification first |
| Use full deep research for a single claim | 6 phases of overhead for a yes/no verdict | Use `--fact-check` for single-claim verification |
| Use full deep research when only a reading list is needed | Synthesis without a real question to answer | Use `--lit-review` for bibliography-only tasks |
