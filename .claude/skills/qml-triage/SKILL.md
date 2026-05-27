---
name: qml-triage
version: 2.0.0
description: |
  Fast first-pass filter for any QML-relevant source. Accepts arXiv papers,
  local PDFs, web URLs, blog posts, company announcements, whitepapers, and
  plain paper titles. Fetches and extracts content, applies the five QML domain
  criteria (with N/A where not applicable), and returns a SKIP / TRIAGE / PASS
  verdict with per-criterion rationale in ~30–60 seconds.
  Use before committing to a full read on any source — not just academic papers.
  Auto-invoke when user shares any URL, file path, arXiv ID, or asks "is this
  worth reading?", "should we look at this?", or "triage this."
input:
  - arXiv ID (2401.12345), arXiv URL, or arxiv: prefix
  - Local file path or file:// URL pointing to a PDF
  - Any http/https URL (blog, company site, news article, whitepaper)
  - Plain title string or keyword — triggers arXiv title search via /fetch-arxiv
  - Optional: --mode quick (dequantization + baseline only) | --mode full (default)
output:
  - Inline verdict: SKIP / TRIAGE / PASS with why_interesting + why_verdict summary
  - Per-criterion rationale
  - TRIAGE checklist (if verdict is TRIAGE): 3-5 targeted questions for 30-min spot-read
  - Individual Markdown file written to {vault}/artifacts/triage/{YYYY-MM-DD}_{slug}.md
  - JSONL index entry appended to {vault}/artifacts/triage_log.jsonl
---

# /qml-triage

Fast QML signal filter. Any source, five criteria, one verdict.

---

## ⚠️ IRON RULES — Read Before Starting

```
❌ Do NOT evaluate from the title or headline alone — fetch and read the content.
❌ Do NOT produce a PASS verdict without checking all 5 applicable criteria.
❌ Do NOT fabricate content — only use text actually fetched from the source.
❌ Do NOT skip the triage log write even if the verdict is SKIP.
❌ Do NOT apply these criteria to non-QML sources — domain check first.
```

---

## Phase 0: Input Detection, Fetch, and Domain Check

**Goal:** Identify the input type, fetch the content using the appropriate method,
and confirm the source is in scope (QML / quantum ML / quantum computing or adjacent areas).

### 0.1 Detect input type

Inspect the raw input and classify it:

| Input pattern | Type | Fetch method |
|--------------|------|-------------|
| Matches `\d{4}\.\d{4,5}(v\d+)?` (with or without `arxiv:` prefix) | arXiv ID | → Step 0-A |
| URL contains `arxiv.org`, `ar5iv.org`, or `ar5iv.labs.arxiv.org` | arXiv URL | → Step 0-A |
| Starts with `file://` or is an absolute path ending in `.pdf` | Local PDF | → Step 0-B |
| Starts with `http://` or `https://` (not arXiv/ar5iv) | Web URL | → Step 0-C |
| Plain text, no URL scheme, no ID pattern | Title / keyword | → Step 0-A (search mode) |

If none of the above match after careful inspection, stop:
```
Error: Cannot determine input type for "{input}".
Provide: arXiv ID, arXiv URL, file:// path to PDF, http/https URL, or a plain title to search.
```

---

### Step 0-A: arXiv Fetch (ID, URL, or Title Search)

**Helper:** This step follows the `/fetch-arxiv` skill procedure.
Read `.claude/skills/fetch-arxiv/SKILL.md` and execute it for this input.
The helper returns: `title`, `abstract`, `intro_text`, `arxiv_id`, `venue`, `venue_tier`, `partial_fetch`.

Set `source_type = "academic_paper"` and `fetch_mode = "arxiv"`.
Set `source_url = "https://arxiv.org/abs/{arxiv_id}"`.

---

### Step 0-B: Local PDF Read

**Input:** `file:///path/to/paper.pdf` or an absolute filesystem path ending in `.pdf`.

Extract the absolute path (strip `file://` prefix if present).

Use the `Read` tool:
```
Read {absolute_path} pages="1-4"
```

From the first 4 pages, extract:
- Title (usually the largest text on page 1, or a bold/centred heading)
- Abstract or executive summary
- Key claims and any stated contributions
- Author names and affiliation (for credibility assessment)

If `Read` fails (file not found, tool unavailable):
```
Error: Could not read {path}. Check the path exists and is accessible.
Workaround: Upload the paper to arXiv and triage via the arXiv ID instead.
```
Stop.

Set `source_type = "pdf_local"`, `fetch_mode = "local_pdf"`, `partial_fetch = true` (pages 1–4 only).
Set `source_url = "file://{absolute_path}"`.

---

### Step 0-C: Web Fetch (Blog, News, Company Site, Whitepaper)

**Input:** Any `http://` or `https://` URL that is not an arXiv/ar5iv domain.

Use `WebFetch {url}` with this extraction prompt:

> Extract: (1) the page title or headline, (2) the main thesis or claim — what does this source assert about quantum computing, QML, or ML?, (3) any technical description of an approach, method, or product, (4) any comparison to classical methods or stated advantage, (5) author name or organization, (6) any quantitative results (accuracy, speedup, qubit counts, benchmark scores).

If the URL redirects to a login or paywall, note `partial_fetch = true` and work with whatever text was returned.

After fetching, classify `source_type` from the content:

| source_type | Indicators |
|-------------|-----------|
| `blog_post` | Personal blog, company engineering blog, editorial voice |
| `news_article` | Tech/science journalism (TechCrunch, Nature News, MIT News, Wired) |
| `company_announcement` | Product launch, press release, investor update, company website |
| `technical_report` | Whitepaper, non-arXiv preprint, conference proceedings PDF fetched via URL |
| `academic_paper` | Journal paper fetched directly (e.g., Nature, IEEE, ACM via DOI) |
| `other` | Forum post, podcast transcript, social media, anything else |

Set `fetch_mode = "web"`.
Set `source_url = {url}`.

---

### 0.2 Content adequacy check

After fetching, verify you have enough to evaluate:
- Minimum required: title/headline + at least one substantive paragraph describing an approach or claim
- If the fetched content is only a title and date (e.g., a paywalled abstract), mark `partial_fetch = true` and note the limitation in the verdict output

---

### 0.3 Domain check

Read the extracted content. If the source is clearly NOT about quantum computing, quantum machine learning, or QML-adjacent areas (see "Expanded Scope" in `criteria/qml_domain.md`):

```
OUT_OF_SCOPE: This source does not appear to be about QML or quantum computing.
Title/Headline: {title}
Source type: {source_type}
If you believe this is an error, run: /qml-triage {input} --force
```
Stop. Do not write a triage log entry.

**Permissive check for non-academic sources:** A blog or company announcement that
discusses quantum computing for data, optimization, or ML-adjacent tasks IS in scope.
If uncertain, proceed to Phase 1 and let the criteria decide.

### Gate: Phase 0 → Phase 1
- Input type detected ✓
- Content fetched: title + substantive body text ✓
- `source_type`, `source_url`, `fetch_mode`, `partial_fetch` assigned ✓
- Source is QML-relevant ✓

---

## Phase 1: Load Criteria

**Goal:** Load the QML domain criteria into context.

**1.1 Read `criteria/qml_domain.md`** from the repository root.

This file defines all five criteria with:
- Definition
- What failing papers look like
- What passing papers look like
- Red flags and examples

If the file does not exist:
```
Error: criteria/qml_domain.md not found.
This file must exist before /qml-triage can run.
Create it: the team maintains the criteria there.
```
Stop.

**1.2 Note the current "Deprioritized Directions" list** from the criteria file.

If the source's content clearly falls in a deprioritized direction (e.g., ZZ-feature map on UCI dataset, HHL speedup without dequantization refutation, "quantum ML" demo on MNIST):
→ Skip Phase 2 entirely. Issue immediate SKIP with reason: `DEPRIORITIZED_DIRECTION`.

This applies to all source types — a blog post promoting a ZZ-feature map demo is as deprioritized as the paper it describes.

### Gate: Phase 1 → Phase 2
- `criteria/qml_domain.md` loaded ✓
- Deprioritized direction check complete ✓

---

## Phase 2: Apply Five Criteria

**Goal:** Evaluate the fetched content against each of the five QML criteria. Produce a per-criterion verdict.

Apply each criterion independently. For each, output:
```
Criterion: {name}
Verdict: FAIL | WARN | PASS | N/A
Severity: CRITICAL | MAJOR | MINOR  (only if FAIL or WARN; omit for PASS and N/A)
Note: {one specific sentence citing text from the source — quote or close paraphrase}
```

Work through criteria in this order (most disqualifying first):

### Adapting to source type

The five criteria were designed for academic papers but apply to all source types.
Use these adaptations:

**Academic paper (arXiv, PDF, journal):** Apply all criteria to abstract + intro + methods.
Cite section numbers where visible.

**Blog post / news article:** Apply criteria to the claims made in the body text.
The author may not state technical details explicitly — infer from what IS stated and mark
gaps as WARN rather than FAIL when details are simply absent (not contradicted).
Note: `[source: blog/news — technical details may be omitted]` when a criterion is hard to
assess due to format.

**Company announcement / press release:** Apply extra skepticism. Commercial sources routinely
omit classical baselines and hardware caveats. Missing technical detail on criteria 3, 4, 5
should default to WARN (not PASS). An unsubstantiated speedup claim → FAIL (CRITICAL) on
dequantization unless a clear proof or citation is present.

**Technical report / whitepaper:** Treat as academic paper but with lower venue tier (T5 by default).

---

### Criterion 1: Dequantization Risk
- Check: Does the source claim speedup, advantage, or superiority for a quantum kernel, quantum linear algebra, or sampling task?
- For academic sources: Is there a hardness argument against Nystrom/RFF approximation? Or empirical evidence that RFF fails?
- For non-academic sources: Does the source cite or reference a rigorous proof of advantage? Vague "quantum is better" claims with no citation → WARN (MAJOR).
- Apply the SKIP/TRIAGE/PASS decision table from `criteria/qml_domain.md`.
- Severity if FAIL: **CRITICAL**

### Criterion 2: Geometric Difference
- Check: Is a quantum feature map or quantum kernel described?
- If yes and it is a single-layer Pauli encoding (Z-map, ZZ-map): FAIL (CRITICAL)
- If described informally (e.g., "our quantum model captures correlations classical models miss"): WARN — requires verification
- If not a kernel/feature map approach (VQC, optimization, hardware): mark N/A with justification
- Severity if FAIL: **CRITICAL**

### Criterion 3: Trainability / Simulability Trilemma
- Check: Is a parameterized/trainable quantum circuit (PQC/VQC) described or implied?
- If yes: Does the source address barren plateaus? Classical simulability?
- For non-academic sources: If a VQC is described without any training analysis, mark WARN (MAJOR) — absence of information, not confirmed failure.
- If the method is fixed-parameter (reservoir computing, Hamiltonian kernel, analog evolution): mark N/A — no training, no barren plateau risk.
- System size: n ≤ 8 qubit experiments only with no scaling analysis → FAIL (CRITICAL)
- Severity if FAIL: **CRITICAL**

### Criterion 4: Hardware Fit — NISQ / Neutral Atom
- Check: Does the method require QRAM, fault-tolerant error correction, or depth O(polylog N)?
- Check: Are results only on superconducting hardware with no neutral-atom analysis?
- For non-academic sources: If hardware is not specified, mark WARN (MAJOR) — not enough information.
- Severity if FAIL: **MAJOR** (hardware fit alone rarely SKIPs a strong result, but flags it)

### Criterion 5: Strong Classical Baseline
- Check: What classical methods are the quantum approach compared against?
- For academic sources: apply task-specific required baseline list from `criteria/qml_domain.md`.
- For non-academic sources: Is any classical comparison stated? If none stated → WARN (MAJOR).
  If classical comparison is stated but the classical method is clearly weak (untuned MLP, etc.) → FAIL (CRITICAL).
  If the source makes no performance claim at all (purely descriptive) → N/A with note.
- Severity if FAIL: **CRITICAL**

**Mode: quick** — run only Criterion 1 (Dequantization) and Criterion 5 (Baseline). Skip 2, 3, 4.

### Gate: Phase 2 → Phase 3
- All applicable criteria evaluated ✓
- Each criterion has: name, verdict (FAIL/WARN/PASS/N/A), severity (if FAIL/WARN), one-sentence note citing source text ✓

---

## Phase 3: Aggregate Verdict and Output

**Goal:** Compute the final verdict, format output, generate TRIAGE checklist if needed.

### 3.1 Compute verdict

```
If any criterion is FAIL with severity CRITICAL → verdict = SKIP
If any criterion is FAIL with severity MAJOR only → verdict = SKIP (unless exceptional novelty: see below)
If no FAIL, at least one WARN → verdict = TRIAGE
If all PASS → verdict = PASS
```

**Exceptional novelty override (MAJOR only):** If the paper scores PASS on 4 criteria and FAIL (MAJOR) on hardware fit only, but is a T1/T2 venue paper on a strong direction → upgrade to TRIAGE instead of SKIP. Note the override explicitly.

### 3.2 Format output

Print to stdout:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QML TRIAGE VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title:       {title or headline}
Source:      {source_url}
Type:        {academic_paper | pdf_local | blog_post | news_article |
              company_announcement | technical_report | other}
Fetched:     {what was retrieved} via {arxiv | local_pdf | web}
Venue/Auth:  {venue/author/organization if known, else "unknown"}

VERDICT: {SKIP | TRIAGE | PASS}

Why interesting:  {1–2 sentences on what is novel, promising, or worth
                   knowing — written even for SKIP papers. Focus on the
                   strongest claim or technique, not the flaws.}

{If SKIP:}
Why SKIP:         {1–2 sentences naming the specific criterion failure(s)
                   that disqualify this paper. Quote the red flag from the
                   fetched text where possible.}

{If TRIAGE:}
Why TRIAGE:       {1–2 sentences on what is unresolved — the specific
                   concern(s) that prevent a PASS. Name the criterion and
                   the open question, not just "hardware fit unclear."}

{If PASS:}
Why PASS:         {1–2 sentences on why all criteria are satisfied and
                   what makes this paper ready for full evaluation.}

Per-criterion:
  ✗ FAIL  [{severity}]  Dequantization Risk — {note}
  ⚠ WARN  [MAJOR]       Hardware Fit — {note}
  ✓ PASS               Geometric Difference — {note}
  ✓ PASS               Trainability — {note}
  ✗ FAIL  [CRITICAL]   Classical Baseline — {note}

{If SKIP:}
Rejected in: ~{seconds elapsed} seconds. Saved: ~half a day of reading.

{If TRIAGE:}
TRIAGE CHECKLIST — 30-minute spot-read guide:
  □ {question 1 targeting the specific WARN criterion}
  □ {question 2 targeting another ambiguity from the abstract}
  □ {question 3 targeting baseline or hardware gap}
  Resolution: If all □ resolve YES → escalate to /qml-evaluate
              If any □ resolves NO → treat as SKIP

{If PASS:}
Recommended next step: /qml-evaluate {arxiv_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Use these symbols: ✗ for FAIL/SKIP, ⚠ for WARN/TRIAGE, ✓ for PASS.

**Writing rules for the summary fields:**
- `Why interesting` is always written, including for SKIP. A paper can be interesting but still disqualified.
- `Why SKIP/TRIAGE/PASS` names the dominant criterion outcome, not a generic statement. Bad: "hardware concerns exist." Good: "Hardware fit FAIL — superconducting-only; no neutral-atom gate budget analyzed."
- Both fields must be derived from fetched text only. No fabrication.
- For adjacent papers, `Why interesting` should name the QML Transfer Value (HIGH/MEDIUM/LOW) and explain the specific QML implication.

### 3.3 Generate TRIAGE checklist

If verdict is TRIAGE, generate 3-5 targeted questions based on the specific WARN criteria.
Questions must be:
- Answerable from a 30-minute spot-read of the methods section
- Specific to this paper (cite section numbers from the abstract/intro if visible)
- Binary (yes/no resolvable)

Examples:
- "Does Section 3 report RFF/Nystrom approximation comparison results? (Check Table 2 or Figure 3)"
- "Does the gradient norm scaling figure (if present) show polynomial rather than exponential decay with n?"
- "Is the neutral-atom hardware topology explicitly analyzed, or are results on superconducting hardware only?"

### Gate: Phase 3 → Phase 4
- Verdict computed ✓
- Output printed ✓
- TRIAGE checklist generated if verdict = TRIAGE ✓

---

## Phase 4: Write Triage Output

**Goal:** Write a human-readable Markdown file for this evaluation AND append one JSON
line to the machine-readable index. Every evaluation is logged, even SKIPs.

Vault path: `C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup`

---

### 4.1 Compute file slug

- If `arxiv_id` is not null: `slug = arxiv_id` (e.g. `2207.00028`)
- If `arxiv_id` is null: take the title, lowercase, replace spaces/special chars with hyphens,
  truncate to 40 chars, trim trailing hyphens.
  Example: "Opportunities in Full-Stack Design..." → `opportunities-in-full-stack-design`

File path: `{vault_path}/artifacts/triage/{YYYY-MM-DD}_{slug}.md`
where `{YYYY-MM-DD}` comes from the `date` field.

---

### 4.2 Write individual Markdown file

Write the file using this template:

```markdown
# {VERDICT_BADGE} {title}

> {why_interesting}

**Why {VERDICT}:** {why_verdict}

---

## Details

| Field | Value |
|-------|-------|
| arXiv ID | {arxiv_id or `—`} |
| Source | [{source_url}]({source_url}) |
| Type | {source_type} |
| Venue | {venue} · {venue_tier} |
| Fetched | {fetch_mode}{partial_fetch note: " (partial)" if true} |
| Date | {date} |
| Evaluator | {evaluator} · {elapsed_seconds}s |

---

## Criteria

| Criterion | Verdict | Severity | Note |
|-----------|---------|----------|------|
| Dequantization Risk | {verdict} | {severity or `—`} | {note} |
| Geometric Difference | {verdict} | {severity or `—`} | {note} |
| Trainability | {verdict} | {severity or `—`} | {note} |
| Hardware Fit | {verdict} | {severity or `—`} | {note} |
| Classical Baseline | {verdict} | {severity or `—`} | {note} |

{IF verdict == TRIAGE:}
---

## TRIAGE Checklist

Resolve these before committing to a full read. If all resolve YES → `/qml-evaluate`. If any NO → SKIP.

- [ ] {question 1}
- [ ] {question 2}
- [ ] {question 3}
{additional questions if present}
{END IF}

---

*Generated by {evaluator} on {date}*
```

**VERDICT_BADGE** mapping:
- SKIP → `⛔ SKIP —`
- TRIAGE → `⚠️ TRIAGE —`
- PASS → `✅ PASS —`
- OUT_OF_SCOPE → `🔲 OUT_OF_SCOPE —`
- DEPRIORITIZED_DIRECTION → `🚫 DEPRIORITIZED —`

If the file already exists at that path, append a `-2` suffix to the slug before writing
(avoid silent overwrites of earlier evaluations of the same paper).

---

### 4.3 Construct JSONL log entry and append

```json
{
  "arxiv_id": "2401.12345 | null (if not an arXiv source)",
  "title": "...",
  "source_type": "academic_paper | pdf_local | blog_post | news_article | company_announcement | technical_report | other",
  "source_url": "https://arxiv.org/abs/2401.12345 | file:///path/to/paper.pdf | https://...",
  "verdict": "SKIP",
  "why_interesting": "1–2 sentences on the source's most novel or promising aspect. Written for every verdict including SKIP. Must cite fetched text, not general topic knowledge.",
  "why_verdict": "SKIP — classical_baseline FAIL (CRITICAL): compared only to default SVM; no TabPFN or tuned XGBoost tested. Name the specific criterion and quote the evidence.",
  "date": "2026-05-27T13:45:00Z",
  "fetch_mode": "arxiv | local_pdf | web",
  "partial_fetch": false,
  "venue": "arXiv preprint | NeurIPS 2025 | company blog | ...",
  "venue_tier": "T1 | T2 | T3 | T4 | T5 | unknown",
  "mode": "full | quick",
  "md_file": "artifacts/triage/2026-05-27_2401.12345.md",
  "criteria": [
    {"name": "dequantization_risk", "verdict": "FAIL", "severity": "CRITICAL", "note": "..."},
    {"name": "geometric_difference", "verdict": "N/A", "severity": null, "note": "N/A — not a kernel paper; no feature map described."},
    {"name": "trainability", "verdict": "PASS", "severity": null, "note": "..."},
    {"name": "hardware_fit", "verdict": "WARN", "severity": "MAJOR", "note": "..."},
    {"name": "classical_baseline", "verdict": "FAIL", "severity": "CRITICAL", "note": "..."}
  ],
  "triage_checklist": [],
  "evaluator": "qml-triage/2.0.0",
  "elapsed_seconds": 35
}
```

New field: `"md_file"` — relative path from vault root to the individual Markdown file.

**Rules for `why_interesting` and `why_verdict`:**
- Both fields must use fetched text only — no general knowledge about the topic.
- `why_interesting` is written even for SKIP. A source can have a genuinely interesting idea and still be disqualified.
- `why_verdict` must name the specific criterion and severity: `"SKIP — {criterion} FAIL ({severity}): {quote or paraphrase from source}"`.
- `arxiv_id` is `null` for non-arXiv sources — do not fabricate an ID.
- `venue_tier` is `unknown` for blogs and company announcements unless the author's credibility warrants otherwise.

Write to: `{vault_path}/artifacts/triage_log.jsonl`
If the file does not exist, create it (single JSON line, no header). Append mode — never overwrite.

---

### 4.4 Print confirmation

```
📝 Saved: artifacts/triage/{YYYY-MM-DD}_{slug}.md
📋 Logged: artifacts/triage_log.jsonl
```

### Gate: Phase 4 complete
- MD file written ✓
- JSONL entry appended ✓

---

## Failure Modes to Check

These are the most common ways this skill produces wrong results:

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Abstract-only evaluation | Paper passes because intro wasn't fetched | Verify intro section was retrieved; use fallback note if abstract-only |
| Hallucinated paper content | Criteria note cites content not in fetched text | Every note must quote or paraphrase from the fetched text only |
| Criterion not applicable | Applying hardware fit to a theory paper | If criterion clearly doesn't apply to paper type, mark PASS with note "N/A for pure theory paper" |
| Venue tier not checked | Preprint treated as peer-reviewed | Check venue if mentioned in abstract; default to T5 if unknown |
| False PASS on deprioritized direction | ZZ-feature map paper slips through | Check deprioritized list in Phase 1.2 explicitly |
| Triage checklist too vague | Questions not answerable in 30 min | Questions must cite specific section/figure from the abstract |

---

## Output Artifact Reference

**Per-paper Markdown:** `{vault_path}/artifacts/triage/{YYYY-MM-DD}_{slug}.md`
Human-readable. One file per evaluation. See template in Phase 4.2.

**Triage index:** `{vault_path}/artifacts/triage_log.jsonl`
Machine-readable JSONL. One line per evaluation. `md_file` field links to the Markdown file.
Schema: see `artifacts/triage_log_schema.md`

**Next steps:**
- `PASS` or `TRIAGE-resolved` → `/qml-evaluate {arxiv_id}` for full Paper Card
- `SKIP` → no further action; log entry preserves the rationale for future reference
