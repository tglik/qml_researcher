---
name: qml-paper-review
version: 1.1.0
description: |
  Deep critical review of a QML paper. Reads the full paper, extracts every
  claim with type and evidence labels, assesses genuine novelty vs. prior art,
  judges reproducibility and soundness with explicit red flags, applies the five
  QML domain criteria, researches consensus and contradicting evidence across the
  field, and issues a single crisp verdict with a falsification condition.

  Use when: a paper is referenced in a meeting, a collaborator cites a result,
  a paper supposedly supports a team direction, or before citing any result in a
  pitch, strategy doc, or grant proposal.

  Use `--fast` for first-pass filtering (replaces the retired /qml-triage skill).
  Full mode: claims extracted, novelty assessed, quality judged, consensus researched.

triggers:
  - review this paper
  - evaluate this paper
  - is this paper credible
  - deep review
  - paper review
  - what do you think of this paper
  - is this result real
  - does this paper hold up
  - critical review
  - is this bullshit
  - fact check this paper
  - should we trust this result

input:
  - arXiv ID (2401.12345), arXiv URL, local PDF path, or http/https URL (required)
  - Optional --fast: skip Phase 3 (consensus research); verdict from paper alone
  - Optional --claim "<text>": focus the review on one specific claim

output:
  - Review workspace: {output_root}/reviews/{slug}_{YYYY-MM-DD}/
    - 00_paper_content.md       — fetched full paper text
    - 01_claim_registry.md      — claims grouped by category (TOP/SUPPORT/GENERAL/MOTIVATIONAL), each with crisp claim + quote
    - 02_analysis.md            — innovation + quality + QML domain criteria
    - 03_consensus_evidence.md  — supporting and conflicting papers (skipped in --fast)
    - 04_final_review.md        — verdict + crisp report

allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Bash
---

# /qml-paper-review

Any QML paper → claims extracted → novelty and quality judged → consensus researched → crisp verdict with falsification condition.

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

Long-running paper reviews must not go silent after the paper is fetched. After **every phase** completes, send a concise progress update before starting the next phase.

**Hermes/Slack:** use the current conversation as the destination. If a direct `send_message` target for the active Slack DM/thread is available, send the update there immediately; otherwise emit the update as the next assistant message before making the next blocking tool call. Do not send these updates to the Slack home channel unless the review was launched there.

**Format — keep it short:**

```text
Progress: <phase name> completed.
- <1–3 concrete facts: title/arXiv, claim counts, QML criteria summary, consensus count, verdict>
Next: <next phase in one sentence>.
```

**Required checkpoints:**
- After Setup / workspace creation
- After Phase 0 paper fetch and QML relevance gate, including `partial_fetch yes|no` and `QML transfer value HIGH|MEDIUM|LOW`
- After early-stop mismatch notice, if the paper is likely wrong/non-QML
- After Phase 1 claim extraction, including claim counts and vague/misattributed flags
- After Phase 2 analysis, including quality verdict and `PASS/WARN/FAIL` counts for the five QML criteria
- After Phase 3 consensus research, or explicit skip in fast mode, including supporting/contradicting counts and evidence weight
- After Phase 4 final review and Word export, including final verdict

Progress messages are operational status, not the final review. Do not dump the review body in progress updates.

---

## Agent Spawn Compatibility

When running in **Claude Code**: use the `Agent` tool with `subagent_type="claude"`.
When running in **Codex CLI**: use `codex exec "<prompt>" -s read-only`.
When running in **Hermes**: use Hermes parallel task spawning.
When running in **Gemini CLI**: use Gemini's agent mode.

The task prompts below are agent-agnostic — inject them into whichever spawn mechanism your CLI supports.

---

## ⚠️ IRON RULES — Read Before Starting

```
❌ Do NOT summarize the paper — this is a critical review, not an abstract rewrite
❌ Do NOT give a CREDIBLE or LANDMARK verdict without passing all 5 QML criteria
❌ Do NOT fabricate evidence — every claim note must cite fetched paper text
❌ Do NOT use vague hedges ("interesting," "shows promise," "could work") — take a position
❌ Do NOT skip the falsification condition — every verdict must state what would change it
❌ Do NOT let the review-synthesizer run until consensus-researcher completes (in standard mode)
❌ Do NOT produce a review from abstract only — fetch full paper content first
❌ Do NOT continue a full review when the fetched paper is clearly non-QML / LOW transfer value — stop early and flag the likely wrong input unless the user explicitly asks to continue
```

---

## Setup

**Config** — read once at start of Setup:
```
Read: config/workspace.json → CONFIG
OUTPUT_ROOT = resolve(CONFIG.output_root)
```

**Workspace directory:**
```
WORKSPACE = {OUTPUT_ROOT}/reviews/{slug}_{YYYY-MM-DD}/
```

Where `slug` = paper title → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json` with: `current_phase`, `fast_mode`, `target_claim` (if --claim flag used), `paper_id`, `paper_title`, `partial_fetch`, `qml_transfer_value`, `claim_counts`, `quality_verdict`, `qml_criteria_summary`, `consensus_summary`, `final_verdict`, `last_progress_message`, and `final_docx_path` when available.

**Agent definitions directory:**
```
AGENTS_DIR = .claude/skills/qml-paper-review/agents/
```

**Domain criteria** — read once during Setup, inject into every agent:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

**Prior review check** — before fetching, check whether this paper has been reviewed before:
```
Grep: {OUTPUT_ROOT}/reviews/ for the paper ID or slug (session_memory.md files)
```
If a prior review exists, note the verdict (WEAK/MARGINAL/CREDIBLE/LANDMARK) in the workspace state. A prior WEAK verdict is a red flag — state it explicitly in Phase 2 output.

---

## Agent Spawn Convention

All agent definitions live in `agents/` alongside this SKILL.md.
Always `subagent_type="claude"`, inject the agent definition into the prompt.

```
[Orchestrator]
Read: .claude/skills/qml-paper-review/agents/<agent-name>.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="<short description>",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

<task-specific instructions>
"""
)
```

---

## Phase 0 — Fetch Full Paper Content

**Goal:** Retrieve the full paper text — not just the abstract.

**This phase runs in the main session — no agent delegation.**

### 0.1 Detect input type

| Input pattern | Type | Fetch method |
|--------------|------|-------------|
| `\d{4}\.\d{4,5}(v\d+)?` (with or without `arxiv:` prefix) | arXiv ID | → Step 0-A |
| URL contains `arxiv.org` or `ar5iv.org` | arXiv URL | → Step 0-A |
| Absolute path ending in `.pdf` or `file://` prefix | Local PDF | → Step 0-B |
| `http://` or `https://` (not arXiv) | Web URL | → Step 0-C |
| Plain text, no URL pattern | Title search | → Step 0-A (search mode) |

### Step 0-A: arXiv Fetch

Execute the `/fetch-arxiv` skill procedure:
```
Read: .claude/skills/fetch-arxiv/SKILL.md → execute
```
This returns: `title`, `abstract`, `intro_text`, `arxiv_id`, `venue`, `venue_tier`, `partial_fetch`.

After the basic fetch, also attempt to retrieve the HTML full text from ar5iv:
```
WebFetch: https://ar5iv.org/html/{arxiv_id}
```
Extract additionally: methods section text, results (including table numbers), conclusions, related work section.

If ar5iv fetch fails, work with abstract + intro (mark `partial_fetch = true` in state.json).

### Step 0-B: Local PDF Read

Read the PDF in pages:
```
Read: {absolute_path} pages="1-5"   → first 5 pages (abstract + intro + start of methods)
Read: {absolute_path} pages="6-15"  → methods + results (adjust range if needed)
```

Extract: title, authors, abstract, methods, experimental setup, results tables, conclusions.

### Step 0-C: Web Fetch

```
WebFetch: {url}
```
Extraction target: title, thesis/claims, technical description, methods, any quantitative results, comparisons to classical methods, authors/organization.

### 0.2 Content adequacy check

Minimum required content to proceed:
- Title + authors
- Abstract or executive summary
- At least partial methods description (not just abstract claims)

If only abstract is available: mark `partial_fetch = true`, proceed but note in every phase output that analysis is limited to abstract-level claims.

If no substantive content at all: stop.
```
Error: Insufficient content fetched from "{input}".
Fetched: {what was retrieved}
Try: provide the arXiv ID or a direct PDF path.
```

### 0.3 QML relevance early-stop gate

Before writing the workspace or spawning any agents, classify whether the fetched paper is actually in-scope for QML review.

**Stop early by default** if the title/abstract/methods contain no substantive QML signal:
- no quantum model, quantum circuit, quantum kernel, quantum data, quantum speedup, quantum hardware, quantum chemistry simulation claim, or direct QML benchmark relevance;
- or the paper is clearly from a non-QML native domain (e.g. classical wireless, statistics, optimization, classical ML) with only generic terms such as "kernel", "feature", "learning", or "optimization";
- or QML Transfer Value is `LOW`.

When this gate fires, do **not** run Phase 1 claim extraction, Phase 2 analysis, Phase 3 consensus research, or Phase 4 synthesis. Report a compact mismatch notice instead:

```
POSSIBLE WRONG PAPER ID — STOPPED EARLY

Paper: {title}
arXiv: {arxiv_id or —}
Native domain: {domain}
QML transfer value: LOW

What it is about: {one short paragraph grounded in the abstract/methods}

Why I stopped: I found no quantum model/kernel/data/hardware/speedup or direct QML benchmark relevance. This is likely not the QML paper you intended.

Next: provide the corrected paper ID, or explicitly ask me to continue with a native-domain review.
```

Only continue past this gate if one of these is true:
- the paper has concrete QML relevance (`MEDIUM` or `HIGH` transfer value);
- the user explicitly requested review of a non-QML paper;
- the user confirms continuation after the early-stop notice.

If continuing on a confirmed non-QML paper, separate native-domain credibility from QML relevance in every downstream artifact. Mark the five QML criteria `N/A` when there is no quantum claim; do not mark them `FAIL` merely because the paper is out-of-domain.

### 0.4 Write paper content to workspace

Write `WORKSPACE/00_paper_content.md`:

```markdown
# Paper Content: {title}

**arXiv ID:** {arxiv_id or —}
**Authors:** {authors}
**Venue:** {venue} · {venue_tier}
**Source URL:** {url}
**Fetch method:** {arxiv | local_pdf | web}
**Partial fetch:** {yes | no}
**Fetch date:** {YYYY-MM-DD}

---

## Abstract
{abstract text}

## Introduction
{intro_text}

## Methods
{methods_text — or "NOT FETCHED (partial)" if unavailable}

## Results
{results_text including any table summaries}

## Conclusions
{conclusions_text}

## Related Work
{related_work_text — key papers the authors acknowledge as prior art}
```

**Gate Phase 0 → Phase 1:**
- QML relevance early-stop gate passed, or user explicitly confirmed continuation ✓
- Paper content written to `00_paper_content.md` ✓
- Fetch adequacy noted (full / partial) ✓

---

## Phase 1 — Claim Extraction

**Goal:** Extract every material claim in the paper with type label and evidence label. No interpretation yet — just extraction.

**Agent:** `agents/claim-extractor.md`

```
Read: .claude/skills/qml-paper-review/agents/claim-extractor.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Extract and label all claims from QML paper",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Extract claims from this QML paper separated into four categories: TOP, SUPPORT, GENERAL, MOTIVATIONAL.
Include a crisp rephrased claim (≤20 words) plus the supporting quote for every entry.
Include the paper's stated main contribution, the gap it claims to fill, and prior art cited.

Fast mode: <yes | no>
  — If yes: extract TOP and MOTIVATIONAL claims only (skip SUPPORT and GENERAL).

Input file: <WORKSPACE>/00_paper_content.md
Output file: <WORKSPACE>/01_claim_registry.md

Return the file path and a count of: total claims, TOP claims, MOTIVATIONAL claims,
SUPPORT claims (0 if fast mode), GENERAL claims (0 if fast mode), VAGUE flags, MISATTRIBUTED flags.
"""
)
```

**Gate Phase 1 → Phase 2:**
- `01_claim_registry.md` exists and is non-empty ✓
- TOP and MOTIVATIONAL claim counts reported ✓
- In full mode: SUPPORT and GENERAL counts reported ✓

---

## Phase 2 — Innovation, Quality & Domain Analysis

**Goal:** Assess genuine novelty vs. prior art. Judge reproducibility and soundness. Apply the five QML criteria to the specific paper.

**Agent:** `agents/paper-analyst.md`

**MANDATORY:** This agent does NOT search the external literature. It works only from the fetched paper content and claim registry.

```
Read: .claude/skills/qml-paper-review/agents/paper-analyst.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Assess novelty, quality, and QML domain criteria for paper",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Assess the innovation, quality, and QML compliance of this paper.
Apply all five QML domain criteria to the specific claims and methods described.

Input files:
- Paper content: <WORKSPACE>/00_paper_content.md
- Claim registry: <WORKSPACE>/01_claim_registry.md

Prior triage verdict (if any): <from state.json>
Partial fetch flag: <from state.json>

Output file: <WORKSPACE>/02_analysis.md
Return the file path, the quality verdict, and the QML criteria summary
(how many PASS / WARN / FAIL).
"""
)
```

**Gate Phase 2 → Phase 3:**
- `02_analysis.md` exists ✓
- Quality verdict assigned ✓
- All 5 QML criteria evaluated ✓
- If prior triage verdict was SKIP and Phase 2 produces a CREDIBLE or LANDMARK preliminary assessment: flag to user before proceeding.

---

## Phase 3 — Consensus Research

**Skip if `--fast` flag is set. Note in final review: "Fast mode: consensus research skipped."**

**Goal:** Find papers that support or contradict the main claims. Score the evidence weight.

**Agent:** `agents/consensus-researcher.md`

```
Read: .claude/skills/qml-paper-review/agents/consensus-researcher.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Research consensus and contradicting evidence for paper claims",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Search QML and quantum computing literature for papers that support or contradict
the main claims extracted from this paper.

Input files:
- Claim registry: <WORKSPACE>/01_claim_registry.md
- Innovation/quality analysis: <WORKSPACE>/02_analysis.md

Focus search on: the 3-5 highest-stakes claims from 01_claim_registry.md — specifically
any claim labeled EMPIRICAL ADVANTAGE or THEORETICAL NOVELTY, and any QML criteria
concern flagged in 02_analysis.md.

Output file: <WORKSPACE>/03_consensus_evidence.md
Return the file path and a summary: N supporting / N contradicting / evidence weight.
"""
)
```

**Gate Phase 3 → Phase 4:**
- `03_consensus_evidence.md` exists ✓
- Evidence weight assigned ✓

---

## Phase 4 — Final Review

**Goal:** Write the crisp, position-taking review with verdict and falsification condition.

**Agent:** `agents/review-synthesizer.md`

**MANDATORY:** Do NOT write the final review yourself. The review-synthesizer takes a position you may not take.

```
Read: .claude/skills/qml-paper-review/agents/review-synthesizer.md → AGENT_DEF

Agent(
  subagent_type="claude",
  description="Write crisp final QML paper review with verdict",
  prompt="""
{AGENT_DEF}

---

## QML Domain Criteria (authoritative — injected from criteria/qml_domain.md)

{QML_DOMAIN}

---

## Task for this invocation

Write the final critical review of this QML paper. Issue a single crisp verdict with
a falsification condition. Apply the review format in your Role section exactly.

Input files:
- Paper content: <WORKSPACE>/00_paper_content.md
- Claim registry: <WORKSPACE>/01_claim_registry.md
- Innovation/quality/domain analysis: <WORKSPACE>/02_analysis.md
- Consensus evidence: <WORKSPACE>/03_consensus_evidence.md
  (if missing — fast mode — write "Consensus research skipped (--fast mode)" in that section)

Fast mode: <yes | no>
Partial fetch: <yes | no>

Output files:
- Markdown: <WORKSPACE>/04_final_review.md
- Word preview copy: <WORKSPACE>/04_final_review.docx

Return both file paths and the verdict (LANDMARK | CREDIBLE | MARGINAL | WEAK | REFUTED | UNSOUND).
"""
)
```

**Word export gate:** Convert `04_final_review.md` to `04_final_review.docx` after the final review is written.
- Preferred: `pandoc <WORKSPACE>/04_final_review.md -o <WORKSPACE>/04_final_review.docx --metadata title="<paper title> review"`
- If `pandoc` is unavailable, use a Python fallback in a temporary venv with `python-docx` (Hermes/macOS example: `uv venv <WORKSPACE>/.docx-venv && <WORKSPACE>/.docx-venv/bin/python -m ensurepip --upgrade && <WORKSPACE>/.docx-venv/bin/python -m pip install python-docx`, then run a small converter script). Preserve headings, bullets, tables where feasible, and citations as plain text.
- Verify the `.docx` exists and is non-empty before completion.

---

## Completion

1. Confirm `04_final_review.md` and `04_final_review.docx` exist and are non-empty.

2. Write session memory at `{WORKSPACE}/session_memory.md`:

```
---
skill: qml-paper-review
paper_id: {arxiv_id or slug}
date: {YYYY-MM-DD}
title: {paper title}
verdict: {LANDMARK | CREDIBLE | MARGINAL | WEAK | REFUTED | UNSOUND}
status: COMPLETE
pushed_to_permanent: false
---

## Summary
- Verdict: {verdict}
- Novelty: {NOVEL | INCREMENTAL | PRIOR-ART | MISATTRIBUTED}
- Quality: {RIGOROUS | ADEQUATE | WEAK | UNSOUND}
- QML criteria: {N PASS / N WARN / N FAIL}
- Consensus: {STRONG_SUPPORT | MIXED | CONTRADICTED | INSUFFICIENT | SKIPPED}
- Falsification: {one sentence}

## Artifacts
workspace: {WORKSPACE}
final_review_md: {WORKSPACE}/04_final_review.md
final_review_docx: {WORKSPACE}/04_final_review.docx

## Connector Payload
[{date}] [SOURCE: qml-paper-review] Paper review: "{title}" — Verdict: {verdict}. {one-sentence takeaway}. Word review: {WORKSPACE}/04_final_review.docx
```

3. Report to user with a user-focused completion message. The final Slack/message body must not be a raw artifact dump. Put the decision-relevant verdict first, then a compact checklist of what was done, then attach/link the Word review.

Required final format:

```text
REVIEW COMPLETE — DONE

Paper:    {title}
arXiv:    {arxiv_id or —}
Verdict:  *{LANDMARK | CREDIBLE | MARGINAL | WEAK | REFUTED | UNSOUND}*

Executive summary:
- <3-5 bullets from 04_final_review.md: what the paper claims, whether to trust it, main blocker/strength, startup relevance>

What was done:
- Full paper fetch completed: partial_fetch <yes|no>; QML transfer value <HIGH|MEDIUM|LOW>
- Claim extraction completed: <N_total> claims (<N_top> TOP, <N_motivational> MOTIVATIONAL, <N_support> SUPPORT, <N_general> GENERAL); <N_vague> vague / <N_misattributed> misattributed flags
- Innovation + quality analysis completed: novelty <...>; quality <...>
- QML criteria completed: <N PASS / N WARN / N FAIL>
- Consensus research <completed|skipped>: <N_supporting> supporting / <N_contradicting> contradicting; evidence weight <...>
- Final review written: verdict *<verdict>*
- Final Word review generated: <04_final_review.docx>

One-line verdict: <direct sentence>
Falsification: <what evidence would change the verdict>

Detailed review:
MEDIA:<WORKSPACE>/04_final_review.docx

Markdown copy: <WORKSPACE>/04_final_review.md
Workspace: <WORKSPACE>
STATUS: DONE
```

If Word export fails after a real fallback attempt, do not hide it. Send the same executive summary, mark `Final Word review generated: NO`, attach/link the Markdown review instead, and include the exact blocker command/error in one line.

---

## Fast Mode

If the user passes `--fast` or says "quick review":
- Run: Phase 0 → Phase 1 → Phase 2 → Phase 4 (skip Phase 3)
- Phase 4 inputs: `00`, `01`, `02` only
- Note in completion and final review: "Fast mode: consensus research skipped. Verdict from paper analysis alone; may change with field evidence."

---

## Anti-Pattern Reference

| Anti-pattern | Why it fails | What to do instead |
|---|---|---|
| Summarize instead of review | Misses the point — user wants a verdict, not a summary | Extract claims, judge quality, take a position |
| Vague quality judgment ("interesting") | Gives the team nothing to act on | Name the specific flaw or strength with a quote from the paper |
| Accept paper's own quality framing | Authors never say their paper is bad | Apply external quality criteria regardless of author framing |
| Skip QML criteria because paper looks good | QML failure modes are invisible without the criteria | Always run all 5 criteria |
| No falsification condition | Verdict is unfalsifiable and useless | Every verdict must state: "This would change if [specific evidence]" |
| Abstract-only review | Methods section often contradicts abstract claims | Require full text or partial_fetch flag |
| Continuing full review on a clearly non-QML paper | Wastes effort and hides likely wrong paper IDs | Stop after Phase 0 with a mismatch notice unless the user asks to continue |
| Issue CREDIBLE with a WARN criterion | Downgrades trust in the verdict | WARN → MARGINAL at best; FAIL → WEAK or worse |
| Write the final review as orchestrator | Removes the separation of synthesis and judgment | Always delegate to review-synthesizer |
