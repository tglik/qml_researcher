---
name: qml-deep-research
version: 1.3.0
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
    - 00_brief.md
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

> **Infrastructure:** Read `.agents/shared/protocol.md` once during Setup. It provides the
> Agent Spawn Convention, Hermes I/O policy, platform compatibility table, progress update
> format, Word export instructions, session memory format, and completion message format.

---

## Hermes Platform Notes

These replace default Claude Code behavior **only when running under Hermes**:

- **Mode Detection (AskUserQuestion):** Use the `clarify` tool instead. Do not batch with later questions.
- **Q1–Q5 free-form questions:** Ask exactly one question per assistant turn and stop; wait for the Slack reply before asking the next. Do not batch.
- **Scope confirmation gate (Phase 0B):** Use `clarify` for the confirm/adjust choice.
- **Question reframing:** Use `clarify` when there are exactly two options; otherwise ask in prose and wait.
- **In-phase technical clarifiers (Q3):** Ask technical clarifiers one at a time in prose, waiting for each reply.

In all cases: do not write `00_brief.md`, `00_scope.md`, spawn subagents, or start literature
search until Phase 0A has been completed with user answers (or the escape hatch below is satisfied).

---

## Iron Rules

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

**Config** — read once at start:
```
Read: config/workspace.json → CONFIG
OUTPUT_ROOT = resolve(CONFIG.output_root)
  # Relative → absolute from repo root.  Absolute → used as-is.
```

**Workspace:**
```
WORKSPACE = {OUTPUT_ROOT}/sources/reports/deep-research/{slug}_{YYYY-MM-DD}/
```
`slug` = parent question → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json` and update after each phase:
`current_phase`, `fast_mode`, `blocking_issues_count`, `blocking_issues_resolved_count`,
`evidence_audit_verdict`, `proceed_recommendation` (YES|NO|CONDITIONAL), `revision_cycle`
(max 2), `last_progress_message`, `final_docx_path`.

**Agents directory:**
```
AGENTS_DIR = .agents/skills/qml-deep-research/agents/
```

**Domain criteria** — read once, inject into every agent that needs it:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

**Read shared/protocol.md** — load Agent Spawn Convention, progress format, and completion format
into context now. Apply them throughout all phases below.

---

## Phase 0A — Research Brief

**Goal:** Establish WHY this research matters before deciding WHAT to research. Surfaces the
decision gate, existing priors, confirmation bias risk, and explicit scope boundaries.

**Runs in the main session — no agent delegation.**

**Escape hatch:** If the user's question already includes ALL of (a) a named decision it will
inform, (b) a stated hypothesis or prior, (c) a falsification criterion, and (d) explicit scope
boundaries — skip 0A and proceed to Phase 0B.

---

### Mode Detection

Ask:

> Before we scope the research — what's the intent?

Options:
- **Validation** — stress-testing a direction we're already leaning toward
- **Discovery** — understanding a space we haven't explored yet
- **Decision Brief** — defensible summary for investors, collaborators, or the team
- **Claim Verification** — checking a specific claim (recommend `--fact-check` and stop 0A)

Mode shapes posture:
- **Validation** → adversarial by default; sub-questions tilt toward disconfirmation
- **Discovery** → balanced sweep; no prior to protect
- **Decision Brief** → executive framing; startup implications front-and-center

---

### The Five Research Forcing Questions

Ask these **one at a time**. Push on each until the answer is specific and actionable.

**Anti-sycophancy rules:**
- "We want to understand the space" is not a decision gate — push for the specific action this enables
- "We think it probably works" is not a falsification criterion — push for thresholds or failure modes
- A question that can't be falsified is a belief, not a research question
- Never accept the stated question without probing whether it's the question that needs answering

**STOP after each question. Wait for the response before asking the next.**

#### Q1: Decision Gate
**Ask:** "What decision will this research inform? What changes in your work if the answer is strongly positive vs. strongly negative?"

**Push until:** A specific named decision — an experiment to run, a direction to pursue or drop, a claim to make or retract, a partnership or pivot to evaluate.

**Red flags:** "We want to understand X better" → push: "Understand it in order to *do* what?"

#### Q2: Existing Belief
**Ask:** "Before we search: what do you already believe about this? What's your working hypothesis — and how confident are you?"

**Push until:** A stated hypothesis (even "I have no strong prior") AND a confidence level.

**Confirmation bias gate:** If confidence ≥ "fairly confident" AND mode = Validation → record `confirmation_bias_risk: HIGH` in the brief. Phase 0B must include at least one sub-question designed to find the strongest counterevidence.

#### Q3: The Real Question
**Ask:** "Make the question as specific as possible. What data type? What regime — NISQ-feasible now or long-term theoretical? What would a paper that directly answers this look like?"

**Push until:** Specific enough that you could imagine a concrete paper title that answers it.

**If still vague**, ask these technical clarifiers (one at a time):
1. **Data type:** tabular / graph / molecular / time-series / unstructured / other
2. **Regime:** NISQ-feasible now / long-term theoretical / both
3. **Baseline bar:** beat XGBoost/TabPFN / beat GNN / beat SOAP/GAP / beat existing quantum / not yet defined
4. **Dequantization prior:** do you expect classical approximations to be competitive? yes / no / unclear
5. **Hardware scope:** neutral-atom only / hardware-agnostic / both

Present the sharpened version and confirm before continuing.

#### Q4: Falsification Criterion
**Ask:** "What result would cause you to abandon or significantly revise this direction? Name specific thresholds, failure modes, or conditions."

**Push until:** At least one concrete criterion. Offer 2-3 QML-specific candidates if they draw a blank (e.g., "classical kernel matches performance within 5%", "barren plateau confirmed at your circuit depth").

#### Q5: Explicit Out-of-Scope
**Ask:** "What adjacent questions should this research explicitly NOT answer?"

**Push until:** At least 1-2 named out-of-scope areas. Offer candidates if they draw a blank.

---

### Question Reframing

After Q3, if the refined question is materially different from what the user stated, present it:

> "Based on what you've described, I think the actual research question is: [reframed]. Is that right?"

Use AskUserQuestion: A) Yes, that's it  B) Adjust the framing

If B: revise and confirm again.

---

### Write Research Brief

Write `{WORKSPACE}/00_brief.md`:

```markdown
# Research Brief

## Research Mode
{Validation | Discovery | Decision Brief}
Confirmation bias risk: {HIGH | LOW | N/A}

## Decision Gate
{what specific decision this research will inform}

## Stated Question
{original question}

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

**Gate:** Refined Question is specific enough for bounded sub-questions | Falsification Criterion named | Mode set.

---

## Phase 0B — Scope Translation

**Goal:** Decompose the refined question into 3-7 bounded sub-questions with explicit search
criteria. Confirm with user before launching literature sweep.

**Runs in the main session — no agent delegation.**

**Input:** `{WORKSPACE}/00_brief.md` — use Refined Question and mode. If `confirmation_bias_risk: HIGH`,
include at least one sub-question designed to find the strongest counterevidence.

### Steps

**0.1 PICO framing:**
- P (Problem): What QML problem / domain / data type?
- I (Intervention): What quantum approach?
- C (Comparator): What classical or alternative quantum approach?
- O (Outcome): What metric or capability?

**0.2 FINER quality check:**
- F (Feasible): Can this be answered with available papers?
- I (Interesting): Does the answer matter for team direction?
- N (Novel): Has this been systematically covered? Check `[[indexes/paper-registry.md]]`.
- E (Ethical): No concerns.
- R (Relevant): Directly actionable for QML startup decisions?

Revise the question if any FINER dimension fails.

**0.3 Sub-question decomposition** — for each sub-question define:
- `search_terms[]` — 3-5 keywords including QML facets
- `date_range` — default "2019–2025"
- `min_sources` — default 3
- `domain_tags[]`

**0.4 Write `{WORKSPACE}/00_scope.md`:**

```markdown
# Research Scope: <refined question>

## Brief Reference
Mode: {from brief}  |  Decision gate: {from brief}
Falsification criterion: {from brief}  |  Confirmation bias risk: {from brief}

## PICO Frame
P: | I: | C: | O:

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

**0.5 Gate — confirm scope with user:**

> Research scope drafted: "<refined question>" — N sub-questions. Confirm to launch?
> A) Looks good — launch (recommended)  B) Adjust the scope

If B: revise and ask again. If `--scope-only`: stop here.

---

## Phase 1 — Literature Sweep

**Goal:** Screened bibliography for each sub-question cluster.

**Agent:** `literature-scout`

Group sub-questions sharing ≥ 2 search terms into clusters (aim 2-3 clusters). Run all cluster
agents **in parallel** (single message, multiple Agent calls).

**Per cluster task:**
- Search terms, sub-questions, date range, min_sources from `00_scope.md`
- Prioritize: arXiv quant-ph + cs.LG, Semantic Scholar, PRX Quantum, NeurIPS/ICML/ICLR
- Return candidate source table, coverage gaps, contradictions
- Add `## Links` section: [[00_scope.md]], [[00_brief.md]], [[02_domain_classification.md]] (next), [[03_draft_report.md]] (next)
- For each included paper: `[[cards/paper-cards/{arxiv_id}]]`
- Output: `{WORKSPACE}/01_literature_{cluster_slug}.md`

**Coverage gaps:** Re-run literature-scout with broader terms for any sub-question with
< min_sources. Max one retry per gap; flag remaining gaps in `00_scope.md`.

**Merge** all cluster files into `01_literature_merged.md` (concatenate + deduplicate).

**Gate:** All cluster output files exist ✓ | `01_literature_merged.md` written ✓

---

## Lit-Review Mode Gate

**If `--lit-review` flag is set: stop here. Do not run Phases 2–6.**

Produce an annotated bibliography from `01_literature_merged.md`. For each source:

```markdown
### [Author YYYY] — <Title>
**arXiv/DOI:** <id>  **Venue:** <venue> (Tier T?)
**Five-criteria tags:** Dequant: LOW/MEDIUM/HIGH | Regime: NISQ/FT/analog | Baseline: STRONG/WEAK/ABSENT
**Key claim:** <one sentence>
**Why in scope:** <one sentence>
**Caveat:** <one sentence>
```

Output: `{WORKSPACE}/lit_review_{slug}.md`. Write `session_memory.md` (see `shared/protocol.md` format). Report to user:

```
LIT REVIEW COMPLETE
Topic: <question>  |  Workspace: <WORKSPACE>
Sources included: N  |  Excluded: N
Dequant risk: N HIGH / N MEDIUM / N LOW
Top 3: [cite] — why; [cite] — why; [cite] — why
STATUS: DONE
```

---

## Phase 2 — QML Domain Classification

**Skip if scope domain = "no" OR `--fast`. Go directly to Phase 3.**

**Goal:** Apply the five QML criteria to every candidate source before synthesis.

**Agent:** `quantum-domain-analyst`

**Task:**
- Classify every source in `01_literature_merged.md` using the five QML criteria
- Produce full classification output including Strong and Deprioritized direction summaries
- Add `## Links`: [[01_literature_merged.md]], [[00_scope.md]], [[03_draft_report.md]] (next)
- Output: `{WORKSPACE}/02_domain_classification.md`

**Gate:** Add `⚠️ HIGH DEQUANTIZATION RISK` comment in `01_literature_merged.md` for every
source flagged HIGH. Do not proceed to Phase 3 until classification is written ✓

---

## Phase 3 — Synthesis

**Goal:** Structured draft report grounded in screened, classified literature. Every claim cited.

**Agent:** `research-scientist` — **MANDATORY: do NOT write the synthesis yourself.**

**Task:**
- Input: `00_scope.md`, `01_literature_merged.md`, `02_domain_classification.md` (if present)
- Write one section per sub-question
- Label every claim: `(speculative | plausible | observed | supported | strong | published)`
- State regime (NISQ / FT-required / hardware-agnostic) for every quantum approach
- Flag coverage gaps explicitly — do NOT include claims not in the literature file
- Inline citations: `[Author YYYY]` tied to a `## References` section
- For cited papers with arXiv ID: `[[cards/paper-cards/{arxiv_id}]]`
- Add `## Links`: [[00_scope.md]], [[01_literature_merged.md]], [[02_domain_classification.md]], [[04_challenges.md]] (next), [[05_evidence_ledger.md]] (next), [[06_final_report.md]] (next)
- Output: `{WORKSPACE}/03_draft_report.md`

**Gate:** `03_draft_report.md` exists and has a References section ✓
If any section lacks citations, return to research-scientist with specific revision instructions.

---

## Phase 4 — Challenge

**Goal:** Adversarial review of the draft. Finds QML-specific failure modes.

**Agent:** `devils-advocate-scientist` — **MANDATORY: different invocation from Phase 3.**

**Task:**
- Input: `03_draft_report.md`, `01_literature_merged.md`, `02_domain_classification.md` (if present)
- Stress-test using all seven attack vectors: dequantization, weak-baseline, regime-conflation,
  barren-plateau, hidden-assumption, statistical-rigor, missing-contradiction
- For each section: identify BLOCKING and NON-BLOCKING issues
- Quote the exact claim challenged; name attack type; suggest fix
- Reference specific claims with section anchors: `[§Section Name](03_draft_report.md#section-name)`
- Add `## Links`: [[03_draft_report.md]], [[01_literature_merged.md]], [[02_domain_classification.md]], [[05_evidence_ledger.md]] (next), [[06_final_report.md]] (next)
- Output: `{WORKSPACE}/04_challenges.md` — return path and counts: BLOCKING N, NON-BLOCKING N

**Gate:** If blocking issues exist → return `03_draft_report.md` to research-scientist with the
blocking issues as explicit revision instructions. Re-run Phase 3 then Phase 4 on the revised
draft. Max **2 total revision cycles**. If blocking issues persist after cycle 2, flag to user.

---

## Phase 5 — Evidence Audit

**Goal:** Verify every claim in the (revised) draft is correctly supported by its cited source.

**Agent:** `evidence-auditor`

**Task:**
- Input: `03_draft_report.md`, `01_literature_merged.md`, `04_challenges.md`
- Audit every material claim against its cited source
- Apply the five QML-specific blocking rules and claim status ladder
- In the ledger table, link each claim's source: `[[cards/paper-cards/{arxiv_id}]]`
- Flag specific claims with section anchors: `[§Section Name](03_draft_report.md#section-name)`
- Add `## Links`: [[03_draft_report.md]], [[04_challenges.md]], [[01_literature_merged.md]], [[06_final_report.md]] (next)
- Output: `{WORKSPACE}/05_evidence_ledger.md` — return path and audit summary (total claims, alignment breakdown, verdict)

**Gate:**
- If UNSUPPORTED claims exist: remove or re-cite them in `03_draft_report.md` (mechanical edit)
- If overall quality = LOW: return to Phase 3 with the ledger as input; re-run Phases 4-5 (same 2-cycle cap)
- Do NOT proceed to Phase 6 until UNSUPPORTED = 0 ✓

---

## Phase 6 — Final Report

**Goal:** Polished report from audited evidence.

**Agent:** `synthesis-writer` — **MANDATORY: do NOT author the final report prose yourself.**

**Task (standard mode):**
- Input: `00_scope.md`, `03_draft_report.md`, `05_evidence_ledger.md`, `04_challenges.md`
- Use only claims rated ALIGNED or MODERATE/STRONG in the evidence ledger
- Soften any OVERSTATED claims as flagged
- Include Dequantization Risk Table and Hardware Feasibility Summary
- Executive summary: 5-8 bullets, startup-strategy focus
- Inline citations: `[Author YYYY]` + `## References` section
- For cited papers with arXiv ID: `[[cards/paper-cards/{arxiv_id}]]`
- Add `## Workspace` table linking all workspace artifacts
- Output: `{WORKSPACE}/06_final_report.md` and `{WORKSPACE}/06_final_report.docx`

**Word export:** See `.agents/shared/protocol.md` → Word Export section.

**Gate:** Confirm both `06_final_report.md` and `06_final_report.docx` exist and are non-empty ✓

---

## Completion

1. Confirm `06_final_report.md` and `06_final_report.docx` exist and are non-empty.

2. Write `{WORKSPACE}/session_memory.md` using the format in `shared/protocol.md`.
   Skill-specific fields to include:
   - `sources_count`, `dequant_risk` (N HIGH / N MEDIUM / N LOW)
   - `blockers_found`, `blockers_resolved`, `evidence_audit` (PASSED | PASSED_WITH_CONCERNS | FAILED)
   - `proceed_recommendation` (YES | NO | CONDITIONAL)
   - `strong_directions` (list)
   - Executive summary bullets (3)
   - Connector payload: `[{date}] [SOURCE: qml-deep-research] Deep research: {topic}. {bullet 1}. Proceed: {YES|NO|CONDITIONAL}. Word report: [[{WORKSPACE}/06_final_report.docx]]`

3. Report to user using the completion message format in `shared/protocol.md`. Lead with the
   executive summary and proceed recommendation; include a what-was-done checklist; attach the
   Word report. Mark `DONE_WITH_CONCERNS` if any blockers remain or the audit found concerns.

---

## Fast Mode

If the user says "fast research" or passes `--fast`:
- Run: Phase 0A → Phase 0B → Phase 1 → Phase 3 → Phase 6
- Skip Phases 2, 4, 5
- Phase 6 inputs: `00_scope.md` and `03_draft_report.md` only
- Note in completion: "Fast mode: domain classification, adversarial challenge, and evidence audit skipped. First-pass draft."

---

## Fact-Check Mode (`--fact-check`)

Use when a specific claim needs verification without running full research.

**Pipeline:** Phase 0 (claim framing) → Phase 1 (targeted) → Phase 5 (audit) → output

**FC-1: Frame the claim**

Identify: verbatim claim | claim type (QML advantage / benchmark / hardware / theoretical / commercial) | source.

Write `{WORKSPACE}/00_scope.md` with a single sub-question: "Is this claim supported by evidence?"

**FC-2: Targeted literature sweep**

Agent: `literature-scout`

Task: Search for papers that directly test, prove, disprove, or qualify this specific claim.
Also search for: dequantization risks; stronger classical baselines.
Search terms: key technical terms from the claim + dequantization + classical baseline + specific method.
Min sources: 3 papers directly addressing the claim (pro or con). Date range: last 4 years.
Output: `{WORKSPACE}/01_literature_merged.md`

**FC-3: Evidence audit**

Agent: `evidence-auditor`

Task: Verify the specific claim against the literature. Apply five QML blocking rules.
Return a single verdict: SUPPORTED | OVERSTATED (provide rewording) | UNSUPPORTED | CONTRADICTED.
Input: `{WORKSPACE}/01_literature_merged.md`
Output: `{WORKSPACE}/05_evidence_ledger.md`

**Report to user:**
```
FACT-CHECK COMPLETE
Claim: "<verbatim>"
Verdict: SUPPORTED | OVERSTATED | UNSUPPORTED | CONTRADICTED
Evidence strength: STRONG | MODERATE | WEAK
[If OVERSTATED]: Suggested rewording: "..."
[If CONTRADICTED]: Contradicting evidence: [cite]
Supporting sources: N  |  Output: <WORKSPACE>/05_evidence_ledger.md
STATUS: DONE
```

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Main session writes synthesis | No generator/reviewer separation | Delegate to research-scientist agent |
| Use `subagent_type` by name | Couples skill to global agent directory | Read from `./agents/` and inject inline |
| Skip devil's advocate because draft looks good | QML failure modes are non-obvious | Always run Phase 4 in standard mode |
| Abstract-only synthesis | Methods section often contradicts abstract | Require full-text fetch in literature-scout |
| Merge Phases 3+6 | Skips audit; overstated claims enter report | Always run evidence-auditor between synthesis and final write |
| Agent returns summary, not file | Next phase has no grounded input | Require explicit file path in every agent prompt |
| Vague input → skip Phase 0A | Scope based on wrong assumptions | Always run Phase 0A; use Q3 clarifiers if question is vague |
| High-confidence prior → no adversarial sub-question | Confirmation bias confirmed, not tested | Set `confirmation_bias_risk: HIGH`; require disconfirmation sub-question |
| Use full deep research for a single claim | 6 phases of overhead for a yes/no | Use `--fact-check` |
| Use full deep research when only a reading list is needed | Synthesis without a real question | Use `--lit-review` |
