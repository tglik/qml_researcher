---
name: qml-deep-research
version: 1.2.0
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
  - Optional --fast: skip phases 2 and 4-5 (Phase 0A → 0B → 1 → 3 → 6)
  - Optional --scope-only: stop after Phase 0B and wait for user review
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
  - Bash
---

# /qml-deep-research

Multi-agent QML literature research. Question in → grounded report out.

---

## Hermes artifact I/O policy

When running under Hermes, prefer Hermes file tools (`read_file`, `write_file`,
`patch`, `search_files`) for all workspace artifact reads/writes. Do **not** use
`execute_code` merely to create directories, write markdown/json artifacts, merge
phase files, or inspect local workspace files; Slack/gateway `execute_code`
approval is intentionally one-shot and will re-prompt even after “Always Allow”.
Reserve `execute_code` for cases that genuinely need Python control flow over
many tool calls or nontrivial data processing.

---

## User-visible progress protocol

Long-running deep research must not go silent after the interactive scoping gates. After **every phase or revision cycle** completes, send a concise progress update before starting the next phase.

**Hermes/Slack:** use the current conversation as the destination. If a direct `send_message` target for the active Slack DM/thread is available, send the update there immediately; otherwise emit the update as the next assistant message before making the next blocking tool call. Do not send these updates to the Slack home channel unless the research was launched there.

**Format — keep it short:**

```text
Progress: <phase name> completed.
- <1–3 concrete facts: sources found, blockers count, audit verdict, artifact written>
Next: <next phase in one sentence>.
```

**Required checkpoints:**
- After Setup / workspace creation
- After Phase 0A research brief
- After Phase 0B scope confirmation
- After Phase 1 literature sweep / merge
- After Phase 2 domain classification, or explicit skip in fast/non-QML mode
- After each Phase 3 synthesis draft or revision
- After each Phase 4 adversarial review, including `BLOCKING N / NON-BLOCKING N`
- After each blocker-resolution cycle, including `resolved N / remaining N`
- After Phase 5 evidence audit, including `UNSUPPORTED N` and `Proceed YES|NO`
- After Phase 6 final report and Word export

Progress messages are operational status, not research conclusions. Do not dump the report body in progress updates.

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

**Config** — read once at start of Setup:
```
Read: config/workspace.json → CONFIG

OUTPUT_ROOT = resolve(CONFIG.output_root)
  # Relative path → absolute from repo root. Absolute path → used as-is.
  # Examples:
  #   "output"                              → {repo_root}/output
  #   "C:/Users/tmgli/Google Drive/QML"    → used directly
```

**Workspace directory** — all phase outputs go here:
```
WORKSPACE = {OUTPUT_ROOT}/sources/reports/deep-research/{slug}_{YYYY-MM-DD}/
```

Where `slug` = parent question → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json` and update after each phase with: `current_phase`, `fast_mode`, `coverage_retry_per_subq`, `blocking_issues_count`, `blocking_issues_resolved_count`, `evidence_audit_verdict`, `proceed_recommendation` (`YES|NO|CONDITIONAL`), `revision_cycle` (max 2), `last_progress_message`, and `final_docx_path` when available.

**Agent definitions directory** — all agents for this skill live here:
```
AGENTS_DIR = .claude/skills/qml-deep-research/agents/
```

**Domain criteria** — read once during Setup, before Phase 1. Inject into every agent that needs domain knowledge. This ensures all agents use the team's current criteria, not stale inline copies:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

The `QML_DOMAIN` variable is passed as a labelled section inside every relevant agent prompt (see Agent Spawn Convention and each phase below).

**Working directory:** This skill uses repo-root-relative paths (`criteria/qml_domain.md`, `config/workspace.json`, `AGENTS_DIR`). Always invoke from the repository root, not from inside `.agents/skills/` or any subdirectory.

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

## Agent Spawn Compatibility

When running in **Claude Code**: use the `Agent` tool with `subagent_type="claude"`.
When running in **Codex CLI**: use `codex exec "<prompt>" -s read-only`.
When running in **Hermes**: use Hermes parallel task spawning.
When running in **Gemini CLI**: use Gemini's agent mode.

The task prompts below are agent-agnostic — inject them into whichever spawn mechanism your CLI supports.

---

## Phase 0A — Research Brief

**Goal:** Establish WHY this research matters before deciding WHAT to research. Surfaces the decision gate, existing priors, confirmation bias risk, and explicit scope boundaries. Produces a brief that grounds Phase 0B's mechanical scope translation.

**This phase runs in the main session — no agent delegation.**

**Hermes interactive gate (MANDATORY):** In Hermes, the `clarify` tool is available and is the correct replacement for Claude Code `AskUserQuestion`. Use `clarify` for the Mode Detection multiple-choice question and for the Phase 0B scope-confirmation question. For free-form Q1–Q5, ask exactly one question in the assistant's final response and stop the turn; wait for the user's reply before continuing. Do not write `00_brief.md`, `00_scope.md`, spawn subagents, or start literature search until Phase 0A has either been completed with user answers or the escape hatch below is explicitly satisfied.

**Escape hatch:** If the user provides a question that already includes ALL of (a) a named decision it will inform, (b) a stated hypothesis or prior, (c) a falsification criterion, and (d) explicit scope boundaries — skip 0A entirely and proceed to Phase 0B. A fully-specified brief is its own answer. If any of those four fields is missing, Phase 0A is not complete.

---

### Mode Detection

> **Hermes:** Use the `clarify` tool for this multiple-choice question. Other non-Claude runtimes may ask in prose and wait for the user's typed reply. Do not batch this with later questions.

Ask:

> Before we scope the research — what's the intent?

Options:
- **Validation** — we're already leaning toward a direction and want to stress-test it
- **Discovery** — we want to understand a space we haven't explored yet
- **Decision Brief** — we need a defensible summary to share with investors, collaborators, or the team
- **Claim Verification** — someone made a specific claim and we want to check it

If **Claim Verification**: recommend `--fact-check` and stop Phase 0A. The user has the right concept but the wrong mode.

Mode shapes the research posture:
- **Validation** → adversarial by default; sub-questions tilt toward disconfirmation; classical baselines prominent
- **Discovery** → balanced sweep; no prior hypothesis to protect
- **Decision Brief** → executive framing; startup implications front-and-center; strong classical baselines named explicitly

---

### The Five Research Forcing Questions

> **Hermes:** For Q1–Q5, ask one free-form question per assistant turn and stop; wait for the user's Slack reply before asking the next. Do not batch multiple questions in one message.

Ask these **ONE AT A TIME**. Push on each until the answer is specific and actionable. A vague answer means the research question itself isn't ready to launch.

**Anti-sycophancy rules for this phase:**
- "We want to understand the space" is not a decision gate — push for the specific action this research enables
- "We think it probably works" is not a falsification criterion — push for specific thresholds or failure modes
- A question that can't be falsified is a belief, not a research question
- Never accept the stated question without probing whether it's actually the question that needs answering

**STOP** after each question. Wait for the response before asking the next.

#### Q1: Decision Gate

**Ask:** "What decision will this research inform? What changes in your work if the answer is strongly positive vs. strongly negative?"

**Push until you hear:** A specific named decision — an experiment to run, a direction to pursue or drop, a claim to make or retract, a partnership or pivot to evaluate.

**Red flags:**
- "We want to understand X better" → push: "Understand it in order to *do* what?"
- "We should know about this area" → push: "What would you do differently if you knew?"
- No outcome changes anything → "If neither result changes what you do next, why run this research now?"

#### Q2: Existing Belief

**Ask:** "Before we search: what do you already believe about this? What's your working hypothesis — and how confident are you in it?"

**Push until you hear:** A stated hypothesis (even "I have no strong prior") AND a confidence level.

**Red flags:**
- High confidence + no mention of what would change their mind → confirmation bias risk; name it explicitly: "You're going in with a strong prior. The research should be designed to challenge that, not confirm it. I'll tilt the sub-questions toward disconfirmation."
- "We believe in this direction" → not a hypothesis; push for a specific technical claim

**Confirmation bias gate:** If confidence ≥ "fairly confident" AND mode = Validation → record `confirmation_bias_risk: HIGH` in the brief. Phase 0B must include at least one sub-question designed to find the strongest counterevidence.

#### Q3: The Real Question

**Ask:** "Make the question as specific as possible. What data type? What regime — NISQ-feasible now or long-term theoretical? What would a paper that directly answers this look like?"

**Push until you hear:** A question specific enough that you could imagine a concrete paper title that answers it. "Neutral-atom reservoir computing for molecular graph regression vs. GNN on QM9-scale benchmarks, NISQ-feasible" is specific. "Quantum reservoirs for molecules" is not.

> **Hermes:** Ask any needed technical clarifiers one at a time in prose, waiting for each reply.

**If still vague after the first answer**, ask these technical clarifiers in a single follow-up AskUserQuestion:

1. **Data type**: tabular / graph / molecular / time-series / unstructured / other
2. **Regime**: NISQ-feasible now / long-term theoretical / both
3. **Baseline bar**: beat XGBoost/TabPFN / beat GNN / beat SOAP/GAP / beat existing quantum method / not yet defined
4. **Dequantization prior**: do you expect classical approximations to be competitive? yes / no / unclear
5. **Hardware scope**: neutral-atom only / hardware-agnostic / both

Use the answers to sharpen the question. Present the sharpened version to the user and confirm before continuing.

#### Q4: Falsification Criterion

**Ask:** "What result would cause you to abandon or significantly revise this direction? Name specific thresholds, failure modes, or conditions."

**Push until you hear:** At least one concrete criterion — a performance threshold not met, a dequantization result that holds, a hardware constraint that rules it out, a regime mismatch between the paper and your hardware.

**Red flags:**
- "We'd need overwhelming evidence against it" → push: "What does 'overwhelming' look like specifically?"
- No falsification criterion at all → the question may be a belief, not a research question; name this

**If they draw a blank:** Offer 2-3 QML-specific falsification candidates relevant to their question (e.g., "classical kernel matches performance within 5%", "barren plateau confirmed at your circuit depth", "no neutral-atom implementation demonstrated"). Get agreement on at least one.

#### Q5: Explicit Out-of-Scope

**Ask:** "What adjacent questions should this research explicitly NOT answer? What should stay out of scope?"

**Push until you hear:** At least 1-2 named out-of-scope areas. This prevents Phase 0B from generating sub-questions that drift into adjacent territory.

**If they draw a blank:** Offer candidates based on the question context — "Should we exclude error-correction overhead, training circuit design, or hardware comparison across modalities?" Get explicit confirmation.

---

### Question Reframing

After Q3, if the refined question is materially different from what the user originally stated, present the reframe:

> "Based on what you've described, I think the actual research question is: [reframed question]. Is that right?"

> **Hermes:** Use `clarify` for the reframing confirmation when there are exactly two options; otherwise ask in prose and wait for the reply.

Use AskUserQuestion / clarify: A) Yes, that's it  B) Adjust the framing

If B: revise and confirm again. Do not proceed until the refined question is agreed.

---

### Write Research Brief

Write `WORKSPACE/00_brief.md`:

```markdown
# Research Brief

## Research Mode
{Validation | Discovery | Decision Brief}
Confirmation bias risk: {HIGH | LOW | N/A}

## Decision Gate
{what specific decision this research will inform}

## Stated Question
{original question as the user phrased it}

## Refined Question
{sharpened version agreed in Q3}

## Existing Belief / Prior
Hypothesis: {stated hypothesis}
Confidence: {low | moderate | high}

## Falsification Criterion
{specific conditions that would cause a direction change}

## Explicit Out-of-Scope
- {item 1}
- {item 2}

## Notes for Phase 0B
{any confirmation-bias tilts, adversarial sub-question requirements, mode-specific framing}

---

## Links

- Scope: [[00_scope.md]]
- Final report: [[06_final_report.md]]
```

---

### Gate

Before proceeding to Phase 0B, verify:
- Refined Question is specific enough to generate bounded sub-questions
- At least one Falsification Criterion is named
- Mode is set

If any check fails, loop back to the relevant question.

---

## Phase 0B — Scope Translation

**Goal:** Decompose the refined research question from the brief into 3-7 bounded sub-questions with explicit search criteria. Confirm with user before launching literature sweep.

**This phase runs in the main session — no agent delegation.**

**Input:** `WORKSPACE/00_brief.md` — use the Refined Question and mode as the starting point for PICO. If `confirmation_bias_risk: HIGH`, the sub-question set in 0.3 must include at least one question designed to find the strongest counterevidence or the strongest competing classical baseline.

### Steps

**0.1 PICO framing:**
- P (Problem): What QML problem / domain / data type?
- I (Intervention): What quantum approach is being evaluated?
- C (Comparator): What classical or alternative quantum approach?
- O (Outcome): What metric or capability?

**0.2 FINER quality check:**
- F (Feasible): Can this be answered with available papers?
- I (Interesting): Does the answer matter for team direction?
- N (Novel): Check `[[indexes/paper-registry.md]]` — has this been systematically covered already?
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
# Research Scope: <refined question from brief>

## Brief Reference
Mode: {from brief}
Decision gate: {from brief}
Falsification criterion: {from brief}
Confirmation bias risk: {from brief}

## PICO Frame
- P: | I: | C: | O:

## Sub-Questions
| ID | Sub-question | Search terms | Date range | Min sources |
|----|---|---|---|---|
| Q1 | ... | ... | ... | 3 |

## Inclusion Criteria
## Exclusion Criteria
## Explicit Out-of-Scope
{from brief}
## Domain: QML/quantum: yes | no
## Fast mode: yes | no

---

## Links

- Brief: [[00_brief.md]]
- Literature: [[01_literature_merged.md]]
- Draft report: [[03_draft_report.md]]
- Final report: [[06_final_report.md]]
```

**0.5 GATE — confirm scope with user:**

Use `clarify` in Hermes before launching any literature sweep:

> Research scope drafted: "<refined question>" — N sub-questions. Confirm to launch?

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

At the end of your output file, add a `## Links` section:
- Scope: [[00_scope.md]]
- Brief: [[00_brief.md]]
- Domain classification (next): [[02_domain_classification.md]]
- Draft report (next): [[03_draft_report.md]]
For each paper included, add a wiki link: [[cards/paper-cards/{arxiv_id}]] (these are pre-extraction stubs that extract-artifacts will resolve).

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

Write session memory file at `{WORKSPACE}/session_memory.md`:

```
---
skill: qml-deep-research
mode: lit-review
slug: {slug}
date: {YYYY-MM-DD}
topic: {parent question}
status: COMPLETE
pushed_to_permanent: false
---

## Summary
- Lit review: {N} sources screened for "{topic}"
- Dequant breakdown: {N_HIGH} HIGH / {N_MEDIUM} MEDIUM / {N_LOW} LOW
- Output: {WORKSPACE}/lit_review_{slug}.md

## Connector Payload
[{YYYY-MM-DD}] [SOURCE: qml-deep-research] Lit review: {topic}. {N} sources. Output: {WORKSPACE}/lit_review_{slug}.md
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

At the end of your output file, add a `## Links` section:
- Literature: [[01_literature_merged.md]]
- Scope: [[00_scope.md]]
- Draft report (next): [[03_draft_report.md]]

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

Inline citations must use the format `[Author YYYY]` tied to a `## References` section at the end.
For each cited paper with a known arXiv ID, include a wiki link: `[[cards/paper-cards/{arxiv_id}]]`.

At the end of your output file (after References), add a `## Links` section:
- Scope: [[00_scope.md]]
- Literature: [[01_literature_merged.md]]
- Domain classification: [[02_domain_classification.md]]
- Challenges (next): [[04_challenges.md]]
- Evidence ledger (next): [[05_evidence_ledger.md]]
- Final report (next): [[06_final_report.md]]

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
When referencing a specific claim in the draft, use a section anchor: [§Section Name](03_draft_report.md#section-name).

At the end of your output file, add a `## Links` section:
- Draft report: [[03_draft_report.md]]
- Literature: [[01_literature_merged.md]]
- Domain classification: [[02_domain_classification.md]]
- Evidence ledger (next): [[05_evidence_ledger.md]]
- Final report (next): [[06_final_report.md]]

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
In the ledger table, link each claim's source paper: [[cards/paper-cards/{arxiv_id}]].
When flagging a specific claim, cite the section: [§Section Name](03_draft_report.md#section-name).

At the end of your output file, add a `## Links` section:
- Draft report: [[03_draft_report.md]]
- Challenge log: [[04_challenges.md]]
- Literature: [[01_literature_merged.md]]
- Final report (next): [[06_final_report.md]]

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

Inline citations must use `[Author YYYY]` format tied to a `## References` section.
For each cited paper with a known arXiv ID, add a wiki link next to its reference entry: [[cards/paper-cards/{arxiv_id}]].

At the end of your output file (after References), add a `## Workspace` section:

```markdown
## Workspace

| Artifact | File | Role |
|----------|------|------|
| Research Brief | [[00_brief.md]] | Decision gate + priors |
| Research Scope | [[00_scope.md]] | Sub-questions + PICO frame |
| Literature | [[01_literature_merged.md]] | Screened source bibliography |
| Domain Classification | [[02_domain_classification.md]] | Five-criteria QML classification |
| Draft Report | [[03_draft_report.md]] | Pre-audit synthesis |
| Challenge Log | [[04_challenges.md]] | Adversarial issues found |
| Evidence Ledger | [[05_evidence_ledger.md]] | Claim-to-source audit |
| Final Report | [[06_final_report.md]] | This document |
```

Output files:
- Markdown: <WORKSPACE>/06_final_report.md
- Word preview copy: <WORKSPACE>/06_final_report.docx

Return both file paths.
"""
)
```

**Word export gate:** Convert `06_final_report.md` to `06_final_report.docx` after the final report is written.
- Preferred: `pandoc <WORKSPACE>/06_final_report.md -o <WORKSPACE>/06_final_report.docx --metadata title="<topic>"`
- If `pandoc` is unavailable, use a Python fallback in a temporary venv with `python-docx` (Hermes/macOS example: `uv venv <WORKSPACE>/.docx-venv && <WORKSPACE>/.docx-venv/bin/python -m ensurepip --upgrade && <WORKSPACE>/.docx-venv/bin/python -m pip install python-docx`, then run a small converter script). Preserve headings, bullets, tables where feasible, and citations as plain text.
- Verify the `.docx` exists and is non-empty before completion.

---

## Completion

1. Confirm `06_final_report.md` and `06_final_report.docx` exist and are non-empty.

2. Write session memory file at `{WORKSPACE}/session_memory.md`:

```
---
skill: qml-deep-research
mode: {full | fast}
slug: {slug}
date: {YYYY-MM-DD}
topic: {parent question}
status: {COMPLETE | DONE_WITH_CONCERNS}
pushed_to_permanent: false
---

## Summary
- {bullet 1 from executive summary}
- {bullet 2 from executive summary}
- {bullet 3 from executive summary}

## Artifacts

| Artifact | Wiki link |
|----------|-----------|
| Research Brief | [[{WORKSPACE}/00_brief.md]] |
| Research Scope | [[{WORKSPACE}/00_scope.md]] |
| Literature | [[{WORKSPACE}/01_literature_merged.md]] |
| Domain Classification | [[{WORKSPACE}/02_domain_classification.md]] |
| Draft Report | [[{WORKSPACE}/03_draft_report.md]] |
| Challenge Log | [[{WORKSPACE}/04_challenges.md]] |
| Evidence Ledger | [[{WORKSPACE}/05_evidence_ledger.md]] |
| Final Report (MD) | [[{WORKSPACE}/06_final_report.md]] |
| Final Report (DOCX) | [[{WORKSPACE}/06_final_report.docx]] |

sources_count: {N}
dequant_risk: {N_HIGH} HIGH / {N_MEDIUM} MEDIUM / {N_LOW} LOW
blockers_found: {N_BLOCKING}
blockers_resolved: {N_BLOCKING_RESOLVED}
evidence_audit: {PASSED | PASSED_WITH_CONCERNS | FAILED}
proceed_recommendation: {YES | NO | CONDITIONAL}
strong_directions:
  - {direction 1}
  - {direction 2}

## Connector Payload
[{date}] [SOURCE: qml-deep-research] Deep research: {topic}. Executive summary: {bullet 1}. {bullet 2}. Proceed: {YES|NO|CONDITIONAL}. Word report: [[{WORKSPACE}/06_final_report.docx]]
```

3. Report to user with a user-focused completion message. The final Slack/message body must not be a raw artifact dump. Put the decision-relevant summary first, then a compact checklist of what was done, then attach/link the Word report.

Required final format:

```text
RESEARCH COMPLETE — <DONE | DONE_WITH_CONCERNS | BLOCKED>

Topic: <parent question>
Workspace: <WORKSPACE>

Executive summary:
- <5-8 bullets copied or compressed from 06_final_report.md; startup/decision relevance first>

What was done:
- Literature sweep completed: <N sources screened/included; note major coverage gaps if any>
- QML domain classification completed: <N STRONG / N DEPRIORITIZED; dequant risk N HIGH / N MEDIUM / N LOW>
- Draft written: <03_draft_report.md>
- Adversarial review found *<N_BLOCKING> blockers* and <N_NONBLOCKING> non-blockers
- All *<N_BLOCKING_RESOLVED>/<N_BLOCKING> blockers resolved* OR *<N_REMAINING> blockers remain*
- Evidence audit <passed|failed|passed with concerns>: *Proceed <YES|NO|CONDITIONAL>* (<N claims audited; <N_UNSUPPORTED> unsupported)
- Final Word report generated: <06_final_report.docx>

Detailed report:
MEDIA:<WORKSPACE>/06_final_report.docx

Markdown copy: <WORKSPACE>/06_final_report.md
STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
```

If Word export fails after a real fallback attempt, do not hide it. Send the same executive summary, mark `Word report generated: NO`, attach/link the Markdown report instead, and include the exact blocker command/error in one line.

---

## Fast Mode

If the user says "fast research", "quick research", or passes `--fast`:
- Run: Phase 0A → Phase 0B → Phase 1 → Phase 3 → Phase 6
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
| Vague input → skip Phase 0A → PICO guesses | Scope based on wrong assumptions; wasted research | Always run Phase 0A; use Q3 technical clarifiers if question is still vague |
| High-confidence prior → no adversarial sub-question | Confirmation bias confirmed, not tested | Set confirmation_bias_risk: HIGH in brief; require disconfirmation sub-question in 0B |
| Use full deep research for a single claim | 6 phases of overhead for a yes/no verdict | Use `--fact-check` for single-claim verification |
| Use full deep research when only a reading list is needed | Synthesis without a real question to answer | Use `--lit-review` for bibliography-only tasks |
