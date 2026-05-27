# Triage Log Schema

Version: 1.1 | Written by: `/qml-triage`
Location: `{vault_path}/artifacts/triage_log.jsonl`

One JSON line per paper evaluated. Append-only. Never delete entries.

---

## JSONL Entry Format

```json
{
  "arxiv_id": "2401.12345",
  "title": "Full paper title as fetched",
  "verdict": "SKIP",
  "why_interesting": "Uses Rydberg Hamiltonian evolution as a quantum kernel; hardware-native feature map with no classical analog in the blockade radius regime.",
  "why_verdict": "SKIP — classical baseline FAIL (CRITICAL): compared only to default SVM; no TabPFN or tuned XGBoost tested on their tabular benchmark.",
  "date": "2026-05-27T13:45:00Z",
  "fetch_mode": "ar5iv",
  "partial_fetch": false,
  "venue": "NeurIPS 2025",
  "venue_tier": "T1",
  "mode": "full",
  "criteria": [
    {
      "name": "dequantization_risk",
      "verdict": "FAIL",
      "severity": "CRITICAL",
      "note": "Claims quantum speedup for kernel SVM without any Nystrom/RFF comparison."
    },
    {
      "name": "geometric_difference",
      "verdict": "PASS",
      "severity": null,
      "note": "Uses Rydberg Hamiltonian evolution; geometry differs from RBF."
    },
    {
      "name": "trainability",
      "verdict": "PASS",
      "severity": null,
      "note": "Fixed-parameter reservoir circuit; no training, no barren plateau risk."
    },
    {
      "name": "hardware_fit",
      "verdict": "WARN",
      "severity": "MAJOR",
      "note": "Results on IBM superconducting only; no neutral-atom analysis."
    },
    {
      "name": "classical_baseline",
      "verdict": "FAIL",
      "severity": "CRITICAL",
      "note": "Compared to default SVM; no TabPFN or tuned XGBoost."
    }
  ],
  "triage_checklist": [],
  "evaluator": "qml-triage/1.0.0",
  "elapsed_seconds": 24
}
```

---

## Field Definitions

| Field | Type | Values | Required |
|-------|------|--------|----------|
| arxiv_id | string \| null | YYMM.NNNNN format; null for non-arXiv sources | Yes |
| title | string | As fetched from source | Yes |
| source_type | string | academic_paper \| pdf_local \| blog_post \| news_article \| company_announcement \| technical_report \| other | Yes |
| source_url | string | Canonical URL or file:// path | Yes |
| verdict | string | SKIP \| TRIAGE \| PASS \| OUT_OF_SCOPE \| DEPRIORITIZED_DIRECTION | Yes |
| why_interesting | string | 1–2 sentences on what is novel or promising — written for ALL verdicts including SKIP. Must cite fetched text. | Yes |
| why_verdict | string | 1–2 sentences naming the dominant criterion outcome. Format: "{VERDICT} — {criterion} {FAIL/WARN/PASS} ({severity}): {specific reason}". Must cite fetched text. | Yes |
| date | string | ISO 8601 UTC | Yes |
| fetch_mode | string | arxiv \| local_pdf \| web | Yes |
| partial_fetch | boolean | true if content was incomplete (abstract-only, paywall, pages 1–4 of PDF) | Yes |
| venue | string | Venue name, "arXiv preprint", "company blog", etc. | Yes |
| venue_tier | string | T1 \| T2 \| T3 \| T4 \| T5 \| unknown | Yes |
| mode | string | full \| quick | Yes |
| criteria[].name | string | dequantization_risk \| geometric_difference \| trainability \| hardware_fit \| classical_baseline | Yes |
| criteria[].verdict | string | FAIL \| WARN \| PASS \| N/A | Yes |
| criteria[].severity | string \| null | CRITICAL \| MAJOR \| MINOR \| null (if PASS or N/A) | Yes |
| criteria[].note | string | One sentence citing source text; for N/A include one-sentence justification | Yes |
| triage_checklist | array of string | Questions for spot-read (only if verdict=TRIAGE) | Yes |
| evaluator | string | skill_name/version | Yes |
| elapsed_seconds | integer | Wall clock seconds for evaluation | Yes |

---

## Querying the Log

Count SKIPs vs PASSes:
```bash
cat artifacts/triage_log.jsonl | python -c "
import sys, json
from collections import Counter
c = Counter(json.loads(l)['verdict'] for l in sys.stdin)
print(c)
"
```

Find all papers with a specific criterion FAIL:
```bash
cat artifacts/triage_log.jsonl | python -c "
import sys, json
for l in sys.stdin:
    p = json.loads(l)
    for c in p.get('criteria', []):
        if c['name'] == 'classical_baseline' and c['verdict'] == 'FAIL':
            print(p['arxiv_id'], p['title'][:60])
"
```

List all PASS papers (ready for /qml-evaluate):
```bash
cat artifacts/triage_log.jsonl | python -c "
import sys, json
for l in sys.stdin:
    p = json.loads(l)
    if p['verdict'] == 'PASS':
        print(p['arxiv_id'], p['date'][:10], p['title'][:60])
"
```

---

## Validation Test Protocol

Run this after building `/qml-triage` to confirm criteria are correctly codified.

**Step 1:** Identify the last 5 papers the team evaluated manually (before this tool existed).

**Step 2:** For each paper, record:
- The team's manual verdict (SKIP / READ / PASS)
- The specific criterion that triggered rejection (if SKIP)

**Step 3:** Run `/qml-triage {arxiv_id}` on each paper.

**Step 4:** Compare:
- Did the tool reach the same verdict?
- If the tool said PASS and the team said SKIP — which criterion did the tool miss? Update `criteria/qml_domain.md`.
- If the tool said SKIP and the team said PASS — was the team right? Add an exception/nuance to the relevant criterion.

**Success threshold:** ≥ 3/5 verdicts match AND ≥ 1 paper that was eventually rejected by the team gets SKIP from the tool (validating triage saves time).

Record results here:

| arXiv ID | Team verdict | Tool verdict | Match? | Notes |
|----------|-------------|-------------|--------|-------|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |
