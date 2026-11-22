# C15 — Multi-model scoring panel

**Date:** 2026-11-22 · **Status:** built and run once on the 77 backlog candidates plus 7 fixtures
(Claude in the cloud, GPT-6.1 Sol through Codex on the Mac) · **Tool:** `lab/tools/panel.py` · **Rubric:** `lab/rubrics/backlog_lanes.json`
(criteria owned by the scoring redesign) · **Panels:** `lab/panels/default.json`, `claude-only.json`

## Why
One model family wrote, screened and scored every candidate. Its blind spots are the lab's blind
spots, and its single-number scores were ranked to two decimals. Tsahi asked to break this without
adding human review: several models score independently.

## What the evidence says before we build
- Judges from different providers still share most errors. Three frontier judges from three
  providers: error correlation 0.56, about 1.4 effective votes; they fail together at 7.7× the
  independence rate (Hossain et al., arXiv:2609.22512). Nine judges from seven families: about two
  effective votes, and the panel never beat its best single judge (Kohli, NeurIPS 2026 workshop,
  "Nine Judges, Two Effective Votes"). Same company or architecture adds error agreement (Kim et
  al., ICML 2025, arXiv:2506.07962).
- In those studies, a different prompt style or family barely decorrelates. Mixing in open-weight
  judges raised n_eff but lowered accuracy (arXiv:2609.22512).
- LLM novelty verdicts flip on over half of identical pairs when the prompt is reworded
  (arXiv:2610.02022). LLM-generated ideas that reviewers rated higher before execution lost
  1–1.9 points (of 10) after execution, while human ideas held (Si, Hashimoto, Yang,
  arXiv:2506.20803).

So a panel is worth what its independence is worth, and that has to be measured, not assumed.

## Design
1. **Blind, independent seats.** Each seat sees the lab's goal, the direction (thesis, target
   algorithm) and the candidate's own title, claim and base. It never sees the gate's notes or
   scores, the explainer, who proposed it, or another seat's answer. It returns one score per rubric
   criterion plus its strongest case and strongest objection. Calls are tool-free and fresh
   (`lab/tools/harness.py`: `claude -p` with no tools, `codex exec` read-only in an empty folder,
   or any OpenAI-compatible endpoint such as Gemini, OpenRouter or a local Ollama).
2. **Rubric-agnostic.** The criteria come from a rubric file. The default is the scoring redesign's
   `backlog_lanes` (no_go, on_path, rung, plausibility, upside, insight, fatal_test_days, champion).
   The panel writes medians and disagreement. It does not rank; `backlog.py` does.
3. **Disagreement is output, not noise.** Per candidate: median, spread (log scale for days),
   *contested* when judges differ by ≥ 40% of the scale on upside or plausibility, or any judge
   champions it. Per run: *minority picks*, where one judge puts a candidate in its own top quarter
   while the panel has it in the bottom half. These are the contrarian bets a median would bury.
   They go to the portfolio step by name.
4. **Measured independence.** Every report gives the mean pairwise Spearman per criterion and
   n_eff = k / (1 + (k − 1)ρ̄). It shows it beside the rank, so nobody reads three agreeing judges
   as three votes.
5. **Built-in checks without human labels.** Three controls the lab already deprioritized (a
   tabular VQC demo, a single-encoding PQC claim, end-to-end HHL on dense data) must land at the
   bottom. Reworded twins of real candidates (hype or modest wording, same claim) measure how far
   wording alone moves a score.
6. **No stance seats in production.** Advocate and attacker seats are supported (as bounds, never in
   the median) but removed from the default panel: both runs below show they are the same judge.

## Results

### Claude-only control (Opus, Sonnet, Haiku judges; Sonnet advocate and attacker)
84 items (77 candidates and 7 fixtures) × 5 seats = 420 answers. Cost $7.83 as reported, about 25
minutes with 8 workers.

| Measure | Result | Reading |
|---|---|---|
| n_eff, plausibility / upside / rung | 1.22 / 1.32 / 1.10 of 3 | three Claude tiers are about one vote |
| n_eff, champion | 3.0 (ρ ≈ 0) | only 5 champions in 252 judge answers, no two on the same candidate |
| Panel vs today's gate ranking (rung × p) | Spearman 0.48, top-10 overlap 5/10 | the same family, scoring blind, reproduces only half of today's top 10: the two-decimal ranks are mostly noise |
| Controls | percentiles 98, 99, 100 | known-bad ideas sink, as they should |
| Hype twin of c-…-008 | composite 1.40 → 0.80 | wording that adds "clear quantum advantage" is punished hard: partly fair (an overclaim), but large |
| Modest twin of c-…-008 ("a tie is likely") | 1.40 → 0.90 | the proposer's own hedging moves the score as much as hype does |
| Advocate / attacker vs neutral Sonnet | plausibility ρ 0.95 / 0.93, mean shift −0.02 / −0.02 | role prompts do not decorrelate; they are the same judge |
| Advantage bets (4) | mean percentile 30 (gate 31) | no lift; median upside 2.5, plausibility 0.28 |

### Cross-family: GPT-6.1 Sol added (Codex on the Mac)
GPT judge 84/84 answers; GPT advocate 64/84 before the ChatGPT usage limit. Codex reports no cost.

Agreement with GPT is barely lower than agreement inside the Claude family:

| Criterion | Opus–Sonnet ρ | Opus–GPT ρ | Sonnet–GPT ρ | n_eff, Opus + GPT |
|---|---|---|---|---|
| plausibility | 0.76 | 0.65 | 0.52 | 1.21 of 2 |
| upside | 0.66 | **0.72** | 0.64 | 1.16 |
| rung | 0.86 | 0.86 | 0.81 | 1.08 |
| on_path | 0.89 | 0.78 | 0.74 | 1.12 |
| no_go | 0.51 | 0.31 | 0.32 | 1.53 |
| insight | 0.61 | 0.49 | 0.44 | 1.34 |

| Measure | Claude ×3 | Opus + GPT |
|---|---|---|
| Mean plausibility / upside over 77 | 0.34–0.45 / 1.8–2.0 | GPT 0.42 / 1.99: the same level |
| Candidates any judge gives upside ≥ 4 | 2 | GPT adds 3; 5 of 77 in all |
| Champions (would spend a week now) | 2 | GPT 1; never the same candidate twice |
| vs today's gate ranking | Spearman 0.48 | 0.42, top-10 overlap 3/10 |
| Advantage bets (4), mean percentile | 30 (gate 31) | **19** |
| GPT advocate vs GPT judge | — | plausibility ρ 0.96, upside ρ 0.96 |
| Control: tabular VQC beats logistic regression | percentile 99 | 79: GPT gives it p 0.4, since logistic regression is a weak baseline |
| Hype twin of c-…-008 | −0.6 | −1.4 (GPT −2.0): both families punish wording |

## What this means (blunt)
1. **A second family is not a second opinion.** GPT agrees with Opus on upside more than Sonnet
   does. It adds some independence only where judges know least: no_go (prior work, ρ 0.31),
   insight and plausibility. Two families give about 1.2 effective votes, not 2, which matches the
   literature. Average n_eff over the panel is the number to show next to any rank.
2. **Role prompts are theatre.** Advocate and attacker of the same model correlate 0.93–0.96 with
   its neutral answer in both families. Removed from the default panel.
3. **The echo chamber is mostly upstream of scoring.** Every judge, in both families, scores the
   backlog as a kill-first list: upside ≈ 2, at most 5 of 77 candidates at upside ≥ 4, 3 champions
   in about 310 judge answers. Re-scoring Claude-written candidates with more models cannot create bets that
   were never written. The biggest lever is cross-family *generation*: run sources A–E with GPT
   (and Gemini once a key exists) and compare the yield of upside ≥ 4 candidates.
4. **Wording moves scores as much as content.** A hype rewording of the same claim cut its score by
   40–77%; the proposer's own hedge ("a tie is likely") cut it by 35–46%. Because the proposer
   writes the claim, the proposer still controls the score. Fix: a fixed claim template at
   `backlog add` (claim, operating point, baseline, number to beat, no adjectives or expected
   outcome), and judge only that.
5. **Blind re-scoring alone changes today's ranking a lot.** A single blind Opus reproduces
   today's ranking at Spearman 0.48. Most of the rank change comes from blinding the judge to the
   gate's notes, not from adding models. Today's two-decimal ranks were mostly noise.
6. **GPT lifted the four advantage bets (percentile 31 → 19)** by giving quantum-native claims
   higher plausibility (c-…-008: GPT 0.65, Claude 0.35). With no outcomes yet, nobody can say
   whether that is less bias or more optimism. Mark it as an open measurement, not a win.
7. **Where knowledge is thin, add evidence, not judges.** no_go is the least agreed criterion. The
   fix is one retrieved evidence pack (arXiv search, the lab's verdicts) given to every judge, so
   they disagree about the claim and not about what they happen to remember.

## Next (in order of value per cost)
1. Cross-family generation: one GPT-run pass of sources A and B per open direction, tagged `--by`;
   panel-score it; compare upside ≥ 4 and champion yield against the Claude-written pool.
2. Claim template at `backlog add`, and re-run the wording twins: target Δ < 15%.
3. Evidence pack in the prompt (novelty search hits, lab verdict summaries), then re-measure no_go
   agreement.
4. A third family with real independence: Gemini needs a `GEMINI_API_KEY`; an open-weight judge
   needs Ollama on the Mac (more independent, less accurate per arXiv:2609.22512).
5. Calibrate on outcomes: as candidates close, `report` against outcomes (rung reached), and drop
   any judge whose scores do not predict them.

## Cost
Claude: 420 answers, $7.83 as reported by `claude -p` (about $0.06 per Opus answer, $0.005 per
Haiku answer). Codex: inside the ChatGPT plan; the GPT advocate hit its usage limit at 64 answers,
so a GPT judge on a full 80-candidate backlog fits in one plan window, two seats do not. Production
(Opus + GPT, judges only) costs about $5 per full backlog run, plus one Codex window.

## Run it
```
python -m lab.tools.panel run --panel default                 # skips seats not installed here
python -m lab.tools.panel run --panel default --extra tests/fixtures/panel/controls.jsonl
python -m lab.tools.panel report --export <run-id> --seats claude-opus,gpt-sol   # scores.jsonl + run.json
python -m lab.tools.panel prompt <candidate-id> --seat gpt-sol # the exact text a seat sees
```
Codex and Gemini seats run where their CLI or key exists, which today means the Mac. The cloud has
only Claude. Each machine writes its own `judgments*.jsonl` under
`{OUTPUT_ROOT}/indexes/backlog/panel/<rubric>/`; `report` reads them all. The 2026-11-22 answers are
in qml_artifacts (`judgments_claude.jsonl`, `judgments_codex.jsonl`, `scores.jsonl`, `run.json`).
