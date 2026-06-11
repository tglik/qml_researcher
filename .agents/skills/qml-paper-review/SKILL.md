---
name: qml-paper-review
version: 1.2.0
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
    - 01_claim_registry.md      — claims grouped by category (TOP/SUPPORT/GENERAL/MOTIVATIONAL)
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

> **Infrastructure:** Read `.agents/shared/protocol.md` once during Setup. It provides the
> Agent Spawn Convention, Hermes I/O policy, platform compatibility table, progress update
> format, Word export instructions, session memory format, and completion message format.

---

## Hermes Platform Notes

When running under Hermes, progress updates go to the current DM/thread — not the home channel
unless the review was launched there. Emit each update as the next assistant message before the
next blocking tool call.

---

## Iron Rules

```
❌ Do NOT summarize the paper — this is a critical review, not an abstract rewrite
❌ Do NOT give a CREDIBLE or LANDMARK verdict without passing all 5 QML criteria
❌ Do NOT fabricate evidence — every claim note must cite fetched paper text
❌ Do NOT use vague hedges ("interesting," "shows promise," "could work") — take a position
❌ Do NOT skip the falsification condition — every verdict must state what would change it
❌ Do NOT let the review-synthesizer run until consensus-researcher completes (in standard mode)
❌ Do NOT produce a review from abstract only — fetch full paper content first
❌ Do NOT continue a full review when the fetched paper is clearly non-QML / LOW transfer value
```

---

## Setup

**Config** — read once at start:
```
Read: config/workspace.json → CONFIG
OUTPUT_ROOT = resolve(CONFIG.output_root)
```

**Workspace:**
```
WORKSPACE = {OUTPUT_ROOT}/sources/reports/paper-reviews/{slug}_{YYYY-MM-DD}/
```
`slug` = paper title → lowercase → hyphens → 40-char max.

Create the workspace directory. Write `state.json`:
`current_phase`, `fast_mode`, `target_claim` (if --claim), `paper_id`, `paper_title`,
`partial_fetch`, `qml_transfer_value`, `claim_counts`, `quality_verdict`,
`qml_criteria_summary`, `consensus_summary`, `final_verdict`, `final_docx_path`.

**Agents directory:**
```
AGENTS_DIR = .agents/skills/qml-paper-review/agents/
```

**Domain criteria** — read once, inject into every agent:
```
Read: criteria/qml_domain.md → QML_DOMAIN
```

**Prior review check:** Before fetching, check `{OUTPUT_ROOT}/reviews/` for the paper ID or
slug in `session_memory.md` files. If a prior WEAK verdict exists, state it explicitly in Phase 2 output.

**Read shared/protocol.md** — load Agent Spawn Convention, progress format, and completion format
into context now.

---

## Phase 0 — Fetch Full Paper Content

**Goal:** Retrieve the full paper text — not just the abstract.

**Runs in the main session — no agent delegation.**

### 0.1 Detect input type

| Input pattern | Type | Fetch method |
|--------------|------|-------------|
| `\d{4}\.\d{4,5}(v\d+)?` (bare ID or `arxiv:` prefix) | arXiv ID | → Step 0-A |
| URL contains `arxiv.org` or `ar5iv.org` | arXiv URL | → Step 0-A |
| Absolute path ending `.pdf` or `file://` | Local PDF | → Step 0-B |
| `http://` or `https://` (not arXiv) | Web URL | → Step 0-C |
| Plain text, no URL | Title search | → Step 0-A (search mode) |

### Step 0-A: arXiv Fetch

Execute the `/fetch-arxiv` skill:
```
Read: .agents/skills/fetch-arxiv/SKILL.md → execute
```
Returns: `title`, `abstract`, `intro_text`, `arxiv_id`, `venue`, `venue_tier`, `partial_fetch`.

Also attempt HTML full text from ar5iv:
```
WebFetch: https://ar5iv.org/html/{arxiv_id}
```
Extract additionally: methods section, results (including table numbers), conclusions, related work.
If ar5iv fails, work with abstract + intro (`partial_fetch = true`).

### Step 0-B: Local PDF

```
Read: {absolute_path} pages="1-5"   → abstract + intro + start of methods
Read: {absolute_path} pages="6-15"  → methods + results
```
Extract: title, authors, abstract, methods, experimental setup, results tables, conclusions.

### Step 0-C: Web Fetch

```
WebFetch: {url}
```
Extract: title, thesis/claims, technical description, methods, quantitative results, comparisons to classical methods, authors/organization.

### 0.2 Content adequacy check

Minimum to proceed: title + authors | abstract or executive summary | partial methods description.

If only abstract available: mark `partial_fetch = true`, proceed but flag in every phase output.

If no substantive content:
```
Error: Insufficient content fetched from "{input}".
Try: provide the arXiv ID or a direct PDF path.
```

### 0.3 QML relevance early-stop gate

**Stop early** if the paper has no substantive QML signal (no quantum model/kernel/circuit/data/
speedup/hardware claim, or clearly non-QML native domain) OR QML Transfer Value = LOW.

Early-stop notice:
```
POSSIBLE WRONG PAPER ID — STOPPED EARLY
Paper: {title}  |  arXiv: {arxiv_id or —}  |  Native domain: {domain}
QML transfer value: LOW
What it is about: {one paragraph}
Why I stopped: {reason}
Next: provide the corrected paper ID, or explicitly ask me to continue.
```

Continue only if: transfer value is MEDIUM or HIGH | user explicitly confirms | user requested
non-QML review. On confirmed non-QML paper: mark five QML criteria N/A (not FAIL) and note
native-domain credibility separately.

### 0.4 Write paper content to workspace

Write `{WORKSPACE}/00_paper_content.md` with: arXiv ID, authors, venue, tier, source URL,
fetch method, partial_fetch flag, fetch date, then sections: Abstract | Introduction | Methods
| Results | Conclusions | Related Work (with `[[cards/paper-cards/{arxiv_id}]]` links for
cited papers).

Add `## Links`: [[01_claim_registry.md]] (next), [[02_analysis.md]] (next), [[04_final_review.md]] (next)

**Gate Phase 0 → Phase 1:**
- QML relevance gate passed (or user confirmed) ✓
- `00_paper_content.md` written ✓
- Fetch adequacy noted (full / partial) ✓

---

## Phase 1 — Claim Extraction

**Goal:** Extract every material claim with type label and evidence label. No interpretation — extraction only.

**Agent:** `claim-extractor`

**Task:**
- Input: `{WORKSPACE}/00_paper_content.md`
- Extract claims in four categories: TOP, SUPPORT, GENERAL, MOTIVATIONAL
- Include crisp rephrased claim (≤20 words) + supporting quote for every entry
- Include paper's stated main contribution, the gap it claims to fill, and prior art cited
- Fast mode: extract TOP and MOTIVATIONAL only (skip SUPPORT and GENERAL)
- Add `## Links`: [[00_paper_content.md]], [[cards/paper-cards/{arxiv_id}]] (post-extraction), [[02_analysis.md]] (next), [[04_final_review.md]] (next)
- Output: `{WORKSPACE}/01_claim_registry.md`
- Return path + counts: total claims, TOP, MOTIVATIONAL, SUPPORT, GENERAL, VAGUE flags, MISATTRIBUTED flags

**Gate Phase 1 → Phase 2:**
- `01_claim_registry.md` exists and is non-empty ✓
- TOP and MOTIVATIONAL counts reported ✓
- Full mode: SUPPORT and GENERAL counts reported ✓

---

## Phase 2 — Innovation, Quality & Domain Analysis

**Goal:** Assess genuine novelty vs. prior art. Judge reproducibility and soundness. Apply five QML criteria.

**Agent:** `paper-analyst` — works **only from fetched paper content and claim registry. Does NOT search external literature.**

**Task:**
- Input: `{WORKSPACE}/00_paper_content.md`, `{WORKSPACE}/01_claim_registry.md`
- Inject: prior triage verdict (from state.json), partial_fetch flag
- Assess innovation, quality, and QML domain compliance
- Apply all five QML criteria to this paper's specific methods and claims (quoting paper text)
- Reference specific claims with section anchors: `[§Claim Category](01_claim_registry.md#category)`
- Add `## Links`: [[00_paper_content.md]], [[01_claim_registry.md]], [[cards/paper-cards/{arxiv_id}]], [[03_consensus_evidence.md]] (next), [[04_final_review.md]] (next)
- Output: `{WORKSPACE}/02_analysis.md`
- Return path, quality verdict, QML criteria summary (PASS / WARN / FAIL counts)

**Gate Phase 2 → Phase 3:**
- `02_analysis.md` exists ✓
- Quality verdict assigned ✓
- All 5 QML criteria evaluated ✓
- If prior triage = SKIP and Phase 2 assessment = CREDIBLE/LANDMARK preliminary: flag to user before proceeding.

---

## Phase 3 — Consensus Research

**Skip if `--fast`. Note in final review: "Fast mode: consensus research skipped."**

**Goal:** Find papers that support or contradict main claims. Score evidence weight.

**Agent:** `consensus-researcher`

**Task:**
- Input: `{WORKSPACE}/01_claim_registry.md`, `{WORKSPACE}/02_analysis.md`
- Focus on 3-5 highest-stakes claims (EMPIRICAL ADVANTAGE or THEORETICAL NOVELTY labels, and any QML criteria concerns from Phase 2)
- For supporting/contradicting papers with arXiv ID: `[[cards/paper-cards/{arxiv_id}]]`
- Reference registry claims with: `[§Category](01_claim_registry.md#category)`
- Add `## Links`: [[01_claim_registry.md]], [[02_analysis.md]], [[cards/paper-cards/{arxiv_id}]], [[04_final_review.md]] (next)
- Output: `{WORKSPACE}/03_consensus_evidence.md`
- Return path + summary: N supporting / N contradicting / evidence weight

**Gate Phase 3 → Phase 4:** `03_consensus_evidence.md` exists ✓ | evidence weight assigned ✓

---

## Phase 4 — Final Review

**Goal:** Write the crisp, position-taking review with verdict and falsification condition.

**Agent:** `review-synthesizer` — **MANDATORY: do NOT write the final review yourself.**

**Task:**
- Input: `00_paper_content.md`, `01_claim_registry.md`, `02_analysis.md`, `03_consensus_evidence.md`
  (if absent — fast mode — write "Consensus research skipped (--fast mode)")
- Issue single crisp verdict with falsification condition
- Reference claims with: `[§Category](01_claim_registry.md#category)`
- Reference QML criteria findings: `[§QML Criteria](02_analysis.md#qml-domain-criteria)`
- For supporting/contradicting papers: `[[cards/paper-cards/{arxiv_id}]]`
- Add `## Workspace` table linking all workspace artifacts
- Output: `{WORKSPACE}/04_final_review.md` and `{WORKSPACE}/04_final_review.docx`
- Return both paths and the verdict (LANDMARK | CREDIBLE | MARGINAL | WEAK | REFUTED | UNSOUND)

**Word export:** See `.agents/shared/protocol.md` → Word Export section.

---

## Completion

1. Confirm `04_final_review.md` and `04_final_review.docx` exist and are non-empty.

2. Write `{WORKSPACE}/session_memory.md` using the format in `shared/protocol.md`.
   Skill-specific fields:
   - `paper_id`, `title`, `verdict`
   - `novelty` (NOVEL | INCREMENTAL | PRIOR-ART | MISATTRIBUTED)
   - `quality` (RIGOROUS | ADEQUATE | WEAK | UNSOUND)
   - `qml_criteria` (N PASS / N WARN / N FAIL)
   - `consensus` (STRONG_SUPPORT | MIXED | CONTRADICTED | INSUFFICIENT | SKIPPED)
   - `falsification` (one sentence)
   - Connector payload: `[{date}] [SOURCE: qml-paper-review] Paper review: "{title}" — Verdict: {verdict}. {one-sentence takeaway}. Word review: [[{WORKSPACE}/04_final_review.docx]]`

3. Report to user using the completion message format in `shared/protocol.md`. Lead with the
   verdict and one-line summary; include what-was-done checklist; attach the Word review.

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
| Summarize instead of review | User wants a verdict, not a summary | Extract claims, judge quality, take a position |
| Vague quality judgment ("interesting") | Nothing to act on | Name the specific flaw or strength with a quote |
| Accept paper's own quality framing | Authors never say their paper is bad | Apply external quality criteria regardless |
| Skip QML criteria because paper looks good | QML failure modes are invisible without the criteria | Always run all 5 criteria |
| No falsification condition | Verdict is unfalsifiable and useless | Every verdict: "This would change if [specific evidence]" |
| Abstract-only review | Methods section often contradicts abstract | Require full text or partial_fetch flag |
| Continue full review on clearly non-QML paper | Wastes effort; hides likely wrong paper ID | Stop after Phase 0 with mismatch notice |
| Issue CREDIBLE with a WARN criterion | Downgrades trust in the verdict | WARN → MARGINAL at best; FAIL → WEAK or worse |
| Write the final review as orchestrator | Removes synthesis/judgment separation | Always delegate to review-synthesizer |
