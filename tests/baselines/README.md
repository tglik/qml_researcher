# tests/baselines/

Committed baseline score files for `/test-skills` regression detection.

---

## What lives here

One JSON file per test case, named `{test_id}.json`. Each file stores the combined score
and per-axis scores from a known-good run of the skill. The regression-checker agent loads
these and computes deltas against the current run.

## File format

```json
{
  "test_id": "qml-paper-review-full-strong-paper",
  "skill": "qml-paper-review",
  "mode": "full",
  "skill_version": "1.2.0",
  "baseline_date": "2026-06-13",
  "run_id": "ts-20260613-120000",
  "scores": {
    "fetch_quality":      { "score": 4, "note": "Full text fetched; partial_fetch=false" },
    "claim_extraction":   { "score": 5, "note": "6 TOP claims, each with supporting quote" },
    "qml_criteria":       { "score": 4, "note": "All 5 criteria; 1 lacks direct paper quote" },
    "verdict_specificity":{ "score": 5, "note": "CREDIBLE verdict; falsification names 5% RFF threshold" },
    "consensus_evidence": { "score": 4, "note": "2 supporting papers; no contradicting found, explicitly noted" },
    "anti_hallucination": { "score": 5, "note": "All arXiv IDs valid format; results consistent" }
  },
  "combined": 4.5
}
```

## How to create a baseline

After a successful skill run:

```
/test-skills --eval {workspace} --case {test_id}
```

Review the scores. If they reflect expected quality:

```
/test-skills --accept-baseline {test_id}
```

This writes `tests/baselines/{test_id}.json`. **Commit it immediately** so regressions can be
detected in future runs.

## When to update a baseline

Update baselines when you intentionally change skill behavior and the scores reflect the
new expected quality:

1. Bump skill version in `SKILL.md`
2. Run `/test-skills` and review the score deltas
3. If the change is intentional (not a regression), run `--accept-baseline`
4. Commit the new baseline alongside the skill change

**Do not accept a baseline to hide a regression.** If the scores dropped because the skill
got worse, fix the skill first.

## Regression thresholds (defaults)

Defined per test case in the YAML, but the defaults are:

| Threshold | Value | Classification |
|---|---|---|
| Combined drop | ≥ 0.5 | REGRESSION |
| Any axis drop | ≥ 1.0 | AXIS_REGRESSION |
| Any axis: was ≥4, now ≤2 | — | CRITICAL_REGRESSION |
| Combined gain | ≥ 0.5 | IMPROVEMENT |

Daily scout uses looser thresholds (combined drop ≥ 0.7) due to live web variability.

## Current baselines

No baselines committed yet. Run each test case once with a known-good skill version and
use `--accept-baseline` to populate this directory.
