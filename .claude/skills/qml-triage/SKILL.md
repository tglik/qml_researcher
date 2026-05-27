---
name: qml-triage
version: 1.0.0
description: |
  Fast first-pass filter for QML papers. Given an arXiv ID or URL, fetches
  the abstract and introduction, applies the five QML domain criteria, and
  returns a SKIP / TRIAGE / PASS verdict with per-criterion rationale in ~30 seconds.
  Use before committing to a full paper read. Saves time on papers that should
  be rejected in minutes rather than hours.
  Auto-invoke when user shares an arXiv URL or asks "is this worth reading?",
  "should we look at this paper?", or "triage this paper."
input:
  - arXiv ID (e.g. 2401.12345) or full arXiv URL
  - Optional: --mode quick (dequantization + baseline only) | --mode full (default, all 5 criteria)
output:
  - Inline verdict: SKIP / TRIAGE / PASS with per-criterion rationale
  - TRIAGE checklist (if verdict is TRIAGE): 3-5 targeted questions for 30-minute spot-read
  - Triage log entry appended to artifacts/triage_log.jsonl
---

# /qml-triage

Fast QML paper filter. Five criteria, one verdict, under 30 seconds.

---

## ⚠️ IRON RULES — Read Before Starting

```
❌ Do NOT evaluate from the title alone. Abstract + intro must be read.
❌ Do NOT produce a PASS verdict without checking all 5 criteria.
❌ Do NOT hallucinate paper content. Only use text fetched from the source.
❌ Do NOT skip the triage log write even if the verdict is SKIP.
❌ Do NOT apply these criteria to non-QML papers — check first.
```

---

## Phase 0: Input Parsing and Domain Check

**Goal:** Extract a clean arXiv ID and confirm the paper is in scope (QML / quantum ML / quantum computing for ML).

### Steps

**0.1 Parse the input.**

Accept any of these formats and extract the arXiv ID:
- `2401.12345` → ID is `2401.12345`
- `2401.12345v2` → ID is `2401.12345` (strip version suffix for fetch)
- `https://arxiv.org/abs/2401.12345` → ID is `2401.12345`
- `https://ar5iv.org/abs/2401.12345` → ID is `2401.12345`
- `arxiv:2401.12345` → ID is `2401.12345`

If input does not match any of these patterns, stop immediately:
```
Error: "{input}" is not a valid arXiv ID or URL.
Expected format: 2401.12345  or  https://arxiv.org/abs/2401.12345
```

**0.2 Fetch abstract and title.**

Primary: `WebFetch https://ar5iv.org/abs/{arxiv_id}`

Extract from the HTML:
- Title (look for `<h1 class="ltx_title"` or `<title>` tag)
- Abstract (look for `<div id="abstract"` or `<blockquote class="abstract"`)
- First section of the introduction (look for `<section id="S1"` or `<h2` containing "Introduction")

If ar5iv returns 404 or the page body is empty (paper not yet indexed, typically < 48h from submission):
→ Fallback: `WebFetch https://export.arxiv.org/abs/{arxiv_id}`
  Extract: title and abstract from the XML response (`<title>`, `<summary>` tags).
  Note: fallback gives abstract only, no introduction. Mark as `PARTIAL_FETCH: true` in log.

If both fail, stop:
```
Error: Could not fetch paper {arxiv_id}. Check the ID is correct and try again.
ar5iv: {status_code}
arXiv API: {status_code}
```

**0.3 Domain check.**

Read the title and abstract. If the paper is clearly NOT about quantum computing, quantum machine learning, or hybrid classical-quantum methods:
```
OUT_OF_SCOPE: This paper does not appear to be about QML or quantum computing.
Title: {title}
If you believe this is an error, run: /qml-triage {arxiv_id} --force
```
Stop. Do not continue. Do not write a triage log entry.

### Gate: Phase 0 → Phase 1
- arXiv ID parsed ✓
- Paper text fetched (abstract + intro, or abstract only if fallback) ✓
- Paper is QML-relevant ✓

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

If the paper's abstract clearly places it in a deprioritized direction (e.g., ZZ-feature map on UCI dataset, HHL speedup without dequantization refutation):
→ Skip Phase 2 entirely. Issue immediate SKIP with reason: `DEPRIORITIZED_DIRECTION`.

### Gate: Phase 1 → Phase 2
- `criteria/qml_domain.md` loaded ✓
- Deprioritized direction check complete ✓

---

## Phase 2: Apply Five Criteria

**Goal:** Evaluate the paper's abstract and introduction against each of the five QML criteria. Produce a per-criterion verdict.

Apply each criterion independently. For each, output:
```
Criterion: {name}
Verdict: FAIL | WARN | PASS
Severity: CRITICAL | MAJOR | MINOR  (only if FAIL or WARN)
Note: {one specific sentence citing evidence from the paper text}
```

Work through the criteria in this order (most disqualifying first):

### Criterion 1: Dequantization Risk
- Check: Does the paper claim speedup for a quantum kernel, quantum linear algebra, or sampling task?
- If yes: Is there a hardness argument against Nystrom/RFF approximation? Or empirical evidence that RFF fails?
- Apply the SKIP/TRIAGE/PASS decision table from `criteria/qml_domain.md`.
- Severity if FAIL: **CRITICAL**

### Criterion 2: Geometric Difference
- Check: Is the feature map a single-layer Pauli encoding (Z-map, ZZ-map)?
- If yes: These produce kernels equivalent to truncated Fourier series → FAIL (CRITICAL)
- If structured encoding: is there evidence the geometry differs from RBF/polynomial?
- Severity if FAIL: **CRITICAL**

### Criterion 3: Trainability / Simulability Trilemma
- Check: Is this a parameterized quantum circuit (PQC/VQC) paper?
- If yes: Does it address barren plateaus (gradient scaling with n)? Does it address classical simulability?
- Check system size: n ≤ 8 qubit experiments only with no scaling analysis → FAIL (CRITICAL)
- Severity if FAIL: **CRITICAL**

### Criterion 4: Hardware Fit — NISQ / Neutral Atom
- Check: Does the method require QRAM, fault-tolerant error correction, or depth O(polylog N)?
- Check: Are results only on superconducting hardware with no neutral-atom analysis?
- Severity if FAIL: **MAJOR** (hardware fit alone rarely SKIPs a strong result, but flags it)

### Criterion 5: Strong Classical Baseline
- Check: What classical baselines are used? Are they competitive?
- For tabular data: is TabPFN or XGBoost present?
- For graphs/molecules: is GNN/SOAP/GAP present?
- Missing required baseline → FAIL (CRITICAL)
- Using untuned/toy baseline only → FAIL (CRITICAL)
- Severity if FAIL: **CRITICAL**

**Mode: quick** — run only Criterion 1 (Dequantization) and Criterion 5 (Baseline). Skip 2, 3, 4.

### Gate: Phase 2 → Phase 3
- All applicable criteria evaluated ✓
- Each criterion has: name, verdict, severity (if FAIL/WARN), one-sentence note ✓

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
Paper:   {title}
arXiv:   {arxiv_id}
Fetched: {abstract | abstract+intro} via {ar5iv | arXiv API}
Venue:   {venue if known, else "unknown — arXiv preprint"}

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

## Phase 4: Write Triage Log

**Goal:** Append one JSON line to the triage log. Every evaluation is logged, even SKIPs.

**4.1 Construct log entry:**

```json
{
  "arxiv_id": "2401.12345",
  "title": "...",
  "verdict": "SKIP",
  "why_interesting": "1–2 sentences on the paper's most novel or promising aspect. Written for every verdict including SKIP. Must cite fetched text, not general topic knowledge.",
  "why_verdict": "SKIP — classical_baseline FAIL (CRITICAL): compared only to default SVM; no TabPFN or tuned XGBoost tested. Name the specific criterion and quote the evidence.",
  "date": "2026-05-27T13:45:00Z",
  "fetch_mode": "ar5iv | arxiv_api",
  "partial_fetch": false,
  "venue": "arXiv preprint | NeurIPS 2025 | ...",
  "criteria": [
    {"name": "dequantization_risk", "verdict": "FAIL", "severity": "CRITICAL", "note": "..."},
    {"name": "geometric_difference", "verdict": "PASS", "severity": null, "note": "..."},
    {"name": "trainability", "verdict": "PASS", "severity": null, "note": "..."},
    {"name": "hardware_fit", "verdict": "WARN", "severity": "MAJOR", "note": "..."},
    {"name": "classical_baseline", "verdict": "FAIL", "severity": "CRITICAL", "note": "..."}
  ],
  "triage_checklist": [],
  "evaluator": "qml-triage/1.0.0",
  "elapsed_seconds": 28
}
```

**Rules for `why_interesting` and `why_verdict`:**
- Both fields must use fetched text only — no general knowledge about the paper topic.
- `why_interesting` is written even for SKIP. A paper can have a genuinely interesting idea and still be disqualified.
- `why_verdict` must name the specific criterion and severity: `"SKIP — {criterion} FAIL ({severity}): {quote or paraphrase from paper}"`. For TRIAGE, name the criteria at WARN and the specific open question. For PASS, name what passed and why the evidence was sufficient.

**4.2 Append to log file.**

Write to: `{vault_path}/artifacts/triage_log.jsonl`
where `vault_path` is `C:\Users\tmgli\Documents\Source\ai-os\01_Projects\QML_Startup`

If the file does not exist, create it (single JSON line, no header).
Append mode — never overwrite the file.

**4.3 Print log confirmation:**

```
📝 Logged to artifacts/triage_log.jsonl
```

### Gate: Phase 4 complete
- Log entry written ✓

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

**Triage log:** `artifacts/triage_log.jsonl`
Schema: see `artifacts/triage_log_schema.md`

**Next steps:**
- `PASS` or `TRIAGE-resolved` → `/qml-evaluate {arxiv_id}` for full Paper Card
- `SKIP` → no further action; log entry preserves the rationale for future reference
