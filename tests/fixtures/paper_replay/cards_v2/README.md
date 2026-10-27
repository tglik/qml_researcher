# Paper-replay cards, v2

A v2 card turns one QML paper into a lab program the way the lab will really be used: the
proposer brings an **algorithm and a task**, and the lab analyzes, scopes, designs, builds
baselines, runs and writes the verdict. The paper's results and insights stay in a hidden key. The
lab earns points by reaching them, not by reading them.

Changes from v1 (see the 13-card run, October 2026):
- The input is the algorithm and the task, not a curated summary that states the flaw.
- Components run in isolation: each gets gold upstream outputs (mocks), so a score is about one
  component only.
- The screen and literature retrieval are out of scope for now; the prior-work packet replaces them.
- Numeric items are graded against our own reference rerun of the paper, not against the paper's
  figures.
- Each component has a weighted checklist instead of a 0–5 grade.

## Files per card

| File | Who sees it | Content |
|---|---|---|
| `input.md` | every candidate | Algorithm spec, task, proposer's claim, budget, cutoff |
| `intake_answers.md` | the proposer stub only | What the proposer answers when the interviewer asks; "I don't know" otherwise |
| `mocks.md` | one section per component, as listed in its header | Gold upstream outputs: hypothesis, prior work, screen pass, locked proposal, gate table, verdict to audit |
| `gate_table.md`, `raw_results.csv` | verdict and audit (the auditor also gets the CSV) | Our reference rerun's numbers, no interpretation |
| `key.yaml` | graders only | Rubric items per component |
| `reference_results.json` | graders only | Aggregated reference numbers that numeric items point to |

The reference rerun lives in `scripts/paper_replay/reference/` (one script per card plus a mock
builder); its working files go to `output/paper-replay/reference/<card>/`.

Rule for mocks: **a mock passes on a decision, never on the downstream key.** The screen mock says
PASS and nothing else, so the designer has to bring the lab rules itself.

## Components and their inputs

| Component (role) | Tools | Sees |
|---|---|---|
| analyst (algorithm-analyst) | none | input |
| intake (scoping-interviewer) | none | input, analyst mock; talks to the proposer stub (max 8 turns) |
| designer (experiment-designer) | none | input, hypothesis mock, prior-work mock, screen mock |
| champion (classical-competitor-champion) | none | input, hypothesis mock, proposal mock with classical arms removed |
| implementer | code, no network | locked proposal mock, the dataset files |
| verdict (verdict-writer) | none | locked proposal mock, gate table mock |
| audit (verdict-auditor) | code, no network | locked proposal mock, gate table mock, raw results, verdict-to-audit mock |

Every component also runs as the plain-prompt arm (the same inputs, no lab role or lab method),
so we can see what the lab adds.

## key.yaml format

```yaml
component:
  - id: D1            # unique in the card
    w: 3              # weight 1–3
    type: judge       # judge | numeric | forbid
    critical: true    # optional: missing it caps the component at 0.5
    bonus: true       # optional: counts if met, never against
    text: what the output must contain, in one sentence
    src: where the answer comes from (paper section, or lab rule)
    # numeric only:
    ref: "E3|n=12|N=600:engineered.PQ.cv"   # "<group>:<value>" in reference/results.json;
                                            # "a - b" for a difference of two refs
    tol: 0.04         # absolute tolerance, or tol_rel: 0.15 for relative
```

## Scoring

- Each judge item earns 1 (met), 0.5 (partial) or 0 (missed). The grader must quote the line of
  the output that meets it; no quote means missed.
- Numeric items are checked by code against the reference, within `tol`.
- Score = Σ w·credit / Σ w over non-bonus judge and numeric items, plus bonus credit, minus the
  weight of each forbid item violated (with a quote), clipped to 0–1. A missed critical item caps
  the score at 0.5.
- Grader: Sonnet, given the component's key items and the lab method. Calibration before any
  comparison: grade every output twice and report per-item agreement; one of Tsahi, Meir or Adi
  hand-grades a sample.
- Trials: 3 per component per arm. Report the mean and spread.
