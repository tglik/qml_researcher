---
name: qml-deep-research
version: 1.0.0
description: |
  Multi-agent deep research workflow for QML topics. Decomposes a question into
  scoped sub-questions, runs parallel literature sweeps, applies the five QML criteria
  to classify every source, synthesizes evidence into a grounded draft, adversarially
  challenges it, audits every claim against its source, and writes a final report with
  a dequantization risk table and startup implications.

  Use when asked to "research X", "what does the field say about X", "literature review",
  "investigate QML topic", or any question requiring systematic evidence (not just triage).
  
  Input can be any QML question: "does quantum reservoir computing beat classical on graphs?",
  "what NISQ-feasible advantage exists for molecular simulations?", "neutral-atom kernel
  methods — state of the field", etc.

triggers:
  - deep research
  - research this topic
  - literature review on
  - what does the field say
  - investigate qml
  - qml research
  - what do we know about

input:
  - Research question or topic (required)
  - Optional --fast: skip phases 2 and 4-5 (Phase 0 → 1 → 3 → 6)
  - Optional --scope-only: stop after Phase 0 and wait for user review

output:
  - Research workspace: {vault}/research/{slug}_{YYYY-MM-DD}/
    - 00_scope.md          — decomposed sub-questions, inclusion criteria
    - 01_literature_merged.md — screened bibliography (N sources)
    - 02_domain_classification.md — five-criteria classification per source [QML topics]
    - 03_draft_report.md   — synthesis with inline citations
    - 04_challenges.md     — adversarial challenge log (N blocking resolved)
    - 05_evidence_ledger.md — claim-to-source audit
    - 06_final_report.md   — final report with dequantization risk table

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
❌ Do NOT synthesize research content yourself — delegate to research-scientist agent
❌ Do NOT write the final report prose yourself — delegate to synthesis-writer agent
❌ Do NOT skip Phase 4 (devil's advocate) in standard mode even if draft looks clean
❌ Do NOT merge adjacent phases to save time
❌ Do NOT let synthesis-writer run until evidence-auditor clears the draft
❌ Do NOT treat "abstract-only synthesis" as a valid research output
```

---

## Setup

**Determine workspace directory.** All phase outputs go here:
```
WORKSPACE = C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup\research\{slug}_{YYYY-MM-DD}\
```

Where `slug` = parent question → lowercase → hyphens → 40-char max (e.g. `neutral-atom-graph-kernels`).

Create the workspace directory. Write `state.json` to WORKSPACE and update after each phase with: `current_phase`, `fast_mode`, `coverage_retry_per_subq`, `blocking_issues_count`, `revision_cycle` (max 2), `phase3_input_hash`.

---

## Phase 0 — Scope

**Goal:** Decompose the research question into 3-7 bounded sub-questions with explicit criteria. Confirm with user before launching literature sweep.

**This phase runs in the main session (no agent delegation).**

### Steps

**0.1 PICO framing** (for QML questions):
- P (Problem): What QML problem / domain / data type?
- I (Intervention): What quantum approach is being evaluated?
- C (Comparator): What classical or alternative quantum approach?
- O (Outcome): What metric or capability?

**0.2 FINER quality check** — score the research question before proceeding:
- F (Feasible): Can this be answered with available papers?
- I (Interesting): Does the answer matter for team direction?
- N (Novel): Has this been systematically answered before? Check `triage_log.jsonl` for prior coverage.
- E (Ethical): No concerns.
- R (Relevant): Directly actionable for QML startup decisions?

If any FINER dimension fails, revise the question before proceeding.

**0.3 Sub-question decomposition** — for each sub-question define:
- `search_terms[]` — 3-5 keywords (include QML facets: method terms, hardware terms, risk terms)
- `date_range` — default "2019–2025"; extend if foundational
- `min_sources` — default 3
- `domain_tags[]` — e.g. ["QML", "NISQ", "kernel methods", "neutral-atom"]

**0.4 Write scope to `00_scope.md`:**

```markdown
# Research Scope: <parent question>

## PICO Frame
- P: <problem>
- I: <intervention>
- C: <comparator>
- O: <outcome>

## Sub-Questions
| ID | Sub-question | Search terms | Date range | Min sources |
|----|-------------|--------------|------------|-------------|
| Q1 | ...         | ...          | ...        | 3           |

## Inclusion Criteria
- Peer-reviewed or arXiv preprints from 2019-2025
- QML or quantum computing methods directly (adjacent sources only if < 30% of total)
- Results on quantum hardware or credible simulation

## Exclusion Criteria
- Pure classical ML with no quantum component
- Vendor blog posts without technical backing (may cite as context only)
- Papers retracted or superseded by contradicting follow-up

## Domain: QML/quantum: yes | no
## Fast mode: yes | no
```

**0.5 GATE — confirm scope with user:**

AskUserQuestion:
> Research scope drafted for: "<parent question>" — N sub-questions. Confirm to launch literature sweep?

Options:
- A) Looks good — launch (recommended)
- B) Adjust the scope — describe changes

If B: revise `00_scope.md` and ask again.

If `--scope-only` flag: stop here and report the scope. Do not proceed to Phase 1.

---

## Phase 1 — Literature Sweep

**Goal:** Gather a screened bibliography for each sub-question cluster.

**MANDATORY: use Agent tool. Do NOT search yourself.**

Group sub-questions that share ≥ 2 search terms or the same domain tags into a single cluster. Aim for 2-3 clusters; if all sub-questions are materially distinct, create one cluster per sub-question.

For each cluster, call:

```
Agent(
  subagent_type="literature-scout",
  description="QML literature sweep for <cluster topic>",
  prompt="""
Search QML and quantum computing literature for the following sub-questions.
Return a screened bibliography following the output format in your role definition.

Sub-questions:
<Q_ids and text from 00_scope.md>

Search terms per question: <from 00_scope.md>
Date range: <from scope>
Minimum sources per sub-question: <from scope>
Prioritize: arXiv quant-ph and cs.LG, Semantic Scholar, PRX Quantum, NeurIPS/ICML/ICLR

For each source return:
- arXiv ID or DOI (exact — do not invent)
- title, authors, year, venue, tier (T1-T5), citation count if available
- relevance score (1-5) and which sub-questions it addresses
- abstract excerpt (2-3 sentences from actual abstract)
- key QML assumptions: hardware platform, qubit count, classical baseline used

Also return:
- coverage_gaps: sub-questions with < min_sources
- contradictions: papers that directly contradict each other on the same claim

Output file: <WORKSPACE>/01_literature_<cluster_slug>.md
Return the file path and a one-paragraph summary.
"""
)
```

Run all cluster agents **in parallel** (single message, multiple Agent calls).

Wait for all to complete. If any agent fails to produce its output file, retry once. If it fails again, ask user whether to abort or proceed without that cluster.

**Coverage gap handling:**
- If any `coverage_gaps` exist, re-run the literature-scout for that sub-question with broader terms. Do this at most once per gap.
- If gaps remain, flag them in `00_scope.md` as known gaps.
- Do NOT proceed until all gaps are filled or explicitly flagged.

Merge all cluster files into `01_literature_merged.md` yourself (you can do this — it is mechanical concatenation + deduplication, not synthesis).

---

## Phase 2 — QML Domain Classification

**Skip this phase if scope domain = "no" OR `--fast` flag is set. Go directly to Phase 3.**

**Goal:** Apply the five QML criteria to every candidate source before synthesis.

Call:

```
Agent(
  subagent_type="quantum-domain-analyst",
  description="Five-criteria QML classification of literature",
  prompt="""
Classify every source in the merged literature file using the five QML criteria
and domain classification fields defined in your role definition.

Input: <WORKSPACE>/01_literature_merged.md
Research scope: <WORKSPACE>/00_scope.md

Apply all five criteria to each source:
1. Dequantization Risk (LOW / MEDIUM / HIGH)
2. Geometric Difference (DISTINCT / UNCLEAR / REDUNDANT)
3. Trainability (PASS / WARN / FAIL)
4. Hardware Fit — neutral-atom NISQ (PASS / CONDITIONAL / FAIL)
5. Classical Baseline (STRONG / WEAK / ABSENT)

Output the full domain classification table plus Strong/Deprioritized summaries.
Output file: <WORKSPACE>/02_domain_classification.md
Return the file path and a count of STRONG vs DEPRIORITIZED directions.
"""
)
```

**GATE:** Read `02_domain_classification.md`. Add a warning comment to `01_literature_merged.md` for any source with Dequantization Risk = HIGH. Do NOT proceed to Phase 3 until classification is written.

---

## Phase 3 — Synthesis

**Goal:** Write a structured draft report grounded in screened, classified literature. Every claim must be inline-cited. No unsourced claims.

**MANDATORY: use Agent tool. Do NOT write the synthesis yourself.**

```
Agent(
  subagent_type="research-scientist",
  description="QML synthesis: draft report from classified literature",
  prompt="""
Synthesize the screened, classified QML literature into a structured draft report.
Follow the draft report structure in your role definition exactly.

Input files:
- Scope: <WORKSPACE>/00_scope.md
- Merged literature: <WORKSPACE>/01_literature_merged.md
- Domain classification: <WORKSPACE>/02_domain_classification.md [if present]

Instructions:
- Write one section per sub-question from the scope file
- Every factual claim must have an inline citation: [Author YYYY] or [arXiv:YYMM.NNNNN]
- Label every claim with its status: (speculative | plausible | observed | supported | strong | published)
- For every quantum approach: state regime (NISQ / FT-required / hardware-agnostic)
- If evidence is mixed, say so — do not smooth over disagreement
- Flag explicitly when a sub-question has insufficient sources (coverage gap)
- Do NOT include claims not in the literature file

Output file: <WORKSPACE>/03_draft_report.md
Return the file path and a 3-sentence summary of main findings.
"""
)
```

**GATE:** Verify `03_draft_report.md` exists and has a References section. If any section lacks citations, return to research-scientist with specific instructions to add citations before proceeding.

---

## Phase 4 — Challenge

**Goal:** Adversarial review of the draft. Finds QML-specific failure modes.

**MANDATORY: use Agent tool. Must be a different agent from Phase 3.**

```
Agent(
  subagent_type="devils-advocate-scientist",
  description="Adversarial QML challenge of draft research report",
  prompt="""
Stress-test the QML research draft using all seven QML attack vectors in your role definition:
dequantization, weak baseline, regime conflation, barren plateau, hidden assumptions,
statistical rigor, and missing contradicting literature.

Input files:
- Draft: <WORKSPACE>/03_draft_report.md
- Literature: <WORKSPACE>/01_literature_merged.md
- Domain classification (if present): <WORKSPACE>/02_domain_classification.md

For each section, look for BLOCKING and NON-BLOCKING issues.
Be specific: quote the exact claim challenged, name the attack type, suggest the fix.

Output file: <WORKSPACE>/04_challenges.md
Return the file path and counts: BLOCKING N, NON-BLOCKING N.
"""
)
```

**GATE:** Read `04_challenges.md`. If blocking issues exist:
- Return `03_draft_report.md` to research-scientist with the blocking issues as explicit revision instructions
- Re-run Phase 3, then Phase 4 on the revised draft
- Allow at most **2 total revision cycles**. If blocking issues persist after cycle 2, flag to user via AskUserQuestion

---

## Phase 5 — Evidence Audit

**Goal:** Verify every claim in the (revised) draft is correctly supported by its cited source.

**MANDATORY: use Agent tool.**

```
Agent(
  subagent_type="evidence-auditor",
  description="Source-to-claim alignment audit of QML draft",
  prompt="""
Audit every material claim in the QML research draft against its cited source.
Apply the five QML-specific blocking rules and claim status ladder enforcement
from your role definition.

Input files:
- Draft: <WORKSPACE>/03_draft_report.md
- Literature: <WORKSPACE>/01_literature_merged.md
- Challenge log: <WORKSPACE>/04_challenges.md

For each claim: verdict (ALIGNED | OVERSTATED | UNDERSTATED | UNSUPPORTED | MISATTRIBUTED),
evidence strength, and required rewrite if overstated.

Output file: <WORKSPACE>/05_evidence_ledger.md
Return the file path and audit summary.
"""
)
```

**GATE:** Read the audit summary.
- If UNSUPPORTED claims exist: remove or re-cite them directly in `03_draft_report.md` (mechanical deletion/rewording — you can do this yourself)
- If overall quality = LOW: return to Phase 3 with the ledger as revision input; then re-run Phases 4-5. Same 2-cycle cap applies across all revisions.
- Do NOT proceed to Phase 6 until UNSUPPORTED claims = 0

---

## Phase 6 — Final Report

**Goal:** Produce the polished report from the audited evidence.

**MANDATORY: use Agent tool for the final report. Do NOT author the final report prose yourself.**

```
Agent(
  subagent_type="synthesis-writer",
  description="Final QML research report from audited evidence",
  prompt="""
Write the final QML research report following the QML Report Template in your role definition.

Input files (standard mode):
- Scope: <WORKSPACE>/00_scope.md
- Draft: <WORKSPACE>/03_draft_report.md
- Evidence ledger: <WORKSPACE>/05_evidence_ledger.md
- Challenge log: <WORKSPACE>/04_challenges.md

Instructions:
- Use only claims rated ALIGNED or MODERATE/STRONG in the evidence ledger
- Soften any OVERSTATED claims as flagged in the ledger
- Include the Dequantization Risk Table if QML topic
- Include the Hardware Feasibility Summary for neutral-atom NISQ
- Include Strong Directions and Deprioritized Directions sections
- Executive summary: 5-8 bullets, startup-strategy focus
- Tone: precise, hedged where evidence is weak, no unsupported superlatives

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
[<YYYY-MM-DD>] [SOURCE: session] Deep research completed: <parent question>. Key findings: <3 bullets from executive summary>. Report: <WORKSPACE>/06_final_report.md
```

3. Report to user:
```
RESEARCH COMPLETE

Topic: <parent question>
Workspace: <WORKSPACE>

Files:
  00_scope.md              — scope + sub-questions
  01_literature_merged.md  — screened bibliography (N sources)
  02_domain_classification.md — five-criteria QML classification [QML only]
  03_draft_report.md       — synthesis draft
  04_challenges.md         — adversarial challenges (N blocking resolved)
  05_evidence_ledger.md    — source-to-claim audit (N claims, N% aligned)
  06_final_report.md       — final report

Top findings:
  1. <from executive summary>
  2. <from executive summary>
  3. <from executive summary>

Dequantization risk: N HIGH / N MEDIUM / N LOW directions
Strong directions for team: <list if any>

STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED
```

---

## Fast Mode

If user says "fast research" or "quick research" or includes `--fast` flag:
- Run: Phase 0 → Phase 1 → Phase 3 → Phase 6
- Skip Phases 2, 4, and 5
- In Phase 6, provide only `00_scope.md` and `03_draft_report.md` as inputs; instruct synthesis-writer to treat the result as a first-pass draft

Note in completion report: "Fast mode: domain classification, adversarial challenge, and evidence audit were skipped. Report is a first-pass draft."

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Main session writes synthesis | Confirmation bias; no generator/reviewer separation | Delegate to research-scientist agent |
| Skip devil's advocate because draft looks good | QML-specific failure modes missed | Always run Phase 4 in standard mode |
| Abstract-only synthesis | Paper methods section often contradicts abstract claims | Require full-text fetch in literature-scout |
| Merge Phases 3+6 to save turns | Skips audit; overstated claims enter final report | Always run evidence-auditor between synthesis and final write |
| Agent returns summary, not file | Next phase has no grounded input | Require explicit file path in every agent prompt |
| Trust dequantization verdict from paper authors | Authors have incentive to claim quantum advantage | Always apply dequantization attack in Phase 4 |
| Treat arXiv preprint as "published" | Venture/business decisions need signal quality | Use venue tier; flag preprints explicitly in claims |
