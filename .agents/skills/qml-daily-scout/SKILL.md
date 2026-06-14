---
name: qml-daily-scout
version: 1.1.0
description: |
  Agent-agnostic daily QML research scouting workflow. Scans recent papers,
  technical posts, and publication/news sources for high-signal QML items,
  filters them with skeptical QML criteria, and emits a concise decision-useful
  briefing for a configured audience.

  Use when running a recurring or ad-hoc QML research scout for new papers,
  publications, technical blog posts, or news from the last 24-72 hours.

  Designed for sparse output: most daily runs should emit zero items.
  Only truly exceptional papers — those that alter research priors, expose
  a new advantage signal, or demand the team's immediate attention — pass.
triggers:
  - daily qml scout
  - qml research scout
  - new qml papers
  - recent qml publications
  - qml news scan
  - quantum machine learning watch
  - daily research briefing
input:
  - Time window, default 24 hours
  - Audience or organization context
  - Topic priorities
  - Source list
  - Selection threshold and max item count
  - Delivery/output constraints, supplied by the caller or platform wrapper
output:
  - Concise scout briefing with selected items or a no-high-signal result
  - For every selected item: title, authors/institute, source/link, date, summary, top claims, why it matters, relevance score, novelty score, skepticism/evidence gate, and paper-review recommendation
allowed-tools:
  - WebSearch
  - WebFetch
---

# /qml-daily-scout

Daily or ad-hoc QML research scouting. Recent technical signals in → concise, skeptical, decision-useful briefing out.

This skill is intentionally **agent-agnostic**. It defines the research/scouting method, screening criteria, and briefing schema. Platform-specific delivery details — Slack channel, cron schedule, message routing, model choice, or attachment behavior — must be supplied by the caller/job configuration, not hardcoded here.

---

## Setup

Read `config/workspace.json` → CONFIG.
```
ANALYTICS_PATH   = CONFIG.analytics_folder + "/events.jsonl"
SEEN_PAPERS_PATH = CONFIG.analytics_folder + "/scout_seen.jsonl"
RUN_ID = "sc-{YYYYMMDD-HHMMSS}"
```

**Analytics — write start event** (append to ANALYTICS_PATH via `write_file` mode=append):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_start","skill":"qml-daily-scout","version":"1.1.0","mode":"full","input_summary":"QML scout {time_window}"}
```
If ANALYTICS_PATH does not exist yet, create it (empty file) before appending.

**Load seen-paper dedup log** (read SEEN_PAPERS_PATH if it exists):
- Parse each line as JSON. Keep entries where `ts` is within the last 7 days.
- Build a dedup set: a set of `link` values and `arxiv_id` values from these entries.
- Items in the dedup set will be skipped during selection (Step 3 of Search strategy).
- If SEEN_PAPERS_PATH does not exist, treat the dedup set as empty.

---

## Role

You are a QML research scout. Your job is not to summarize everything new. Your job is to find technically interesting signals that could alter research priorities, experiment design, IP thinking, or technical positioning.

You must be skeptical by default. Prefer one technically material paper over ten hype posts. Skip items that are merely adjacent to QML unless they have clear QML transfer value.

---

## Inputs the caller must configure

If a caller does not provide a value, use the defaults below.

| Field | Default | Notes |
|---|---:|---|
| Time window | last 24 hours | Use source publication/submission date where possible. |
| Max selected items | 3 | This is a hard cap, not a target. Zero is expected most days. |
| Relevance threshold | 5/5 | Item must directly impact core QML architecture, advantage, or positioning. |
| Novelty threshold | 4/5 | Item must contain meaningful new technical content or prior-updating evidence. |
| Audience | QML research team | Caller should provide organization-specific context when available. |
| Output format | concise briefing | Caller/platform wrapper may add channel-specific formatting. |

---

## Topic priorities

Prioritize items related to:

1. **Foundational QML architectures** — architectures, circuit families, measurement patterns, reservoirs, MBQC/dynamic-circuit workflows, or dataflow that could become reusable QML primitives.
2. **QML advantage discovery** — representational classes, complexity arguments, geometric separation, quantum-native data, or experiments designed to survive strong classical baselines.
3. **Data encoding and feature geometry** — feature maps, amplitude/basis/angle encodings, graph/molecular encodings, equivariant/geometric encodings, kernel geometry.
4. **Trainability and simulability** — barren plateaus, optimizer behavior, expressibility, tensor-network/stabilizer/matchgate simulability, gradient concentration.
5. **Quantum kernels** — kernel estimation, geometric difference, classical kernel comparisons, dequantization risk, Nyström/RFF checks.
6. **Hybrid QML workflows** — quantum-classical loops, differentiable quantum programming, hybrid inference/training pipelines, compiler/runtime integration.
7. **Hardware-aware QML** — near-term constraints, noise/fidelity/resource accounting across modalities (neutral-atom, superconducting, trapped-ion, photonic). Flag which modality and note relevance to the team's active partnership tracks (neutral-atom/Q-Factor, Israel; other Israel-based quantum stack companies). Also flag noise-correction and error-mitigation results with QML implications.
8. **AI-accelerated quantum algorithm discovery** — LLM/RL/search systems that discover quantum circuits, encodings, Hamiltonians, measurements, or workflows relevant to QML.

---

## Sources to scan

Use the caller's source list if provided. Otherwise scan these classes:

### Primary paper sources

- arXiv recent submissions in `quant-ph`, `cs.LG`, and `cs.AI`
- Semantic Scholar or equivalent paper index/search

### Technical blogs and industrial research sources

- IBM Quantum
- Xanadu / PennyLane
- IonQ
- Quantinuum
- Classiq
- Pasqal
- NVIDIA Quantum
- AWS Braket

### Optional publication sources when accessible

- Nature Quantum Information
- PRX Quantum
- Quantum journal
- other peer-reviewed quantum information / QML venues with new items in the window

Do not rely on a single source. Triangulate at least arXiv plus one paper/search/blog source when available.

---

## Search strategy

### Step 1 — Build targeted queries

Use date-bounded searches and source-specific recent pages. Query terms should include combinations of:

- `quantum machine learning`, `QML`, `quantum kernel`, `quantum neural network`, `variational quantum`, `hybrid quantum-classical`
- `barren plateau`, `trainability`, `expressibility`, `dequantization`, `geometric difference`, `feature map`, `encoding`
- `quantum reservoir`, `neutral atom`, `Rydberg`, `trapped ion`, `superconducting qubit`, `photonic quantum`, `graph kernel`, `molecular`, `Hamiltonian learning`, `quantum error mitigation`, `noise-robust quantum`, `QECC machine learning`
- `AI quantum algorithm discovery`, `LLM quantum circuits`, `automated quantum algorithm`, `quantum circuit synthesis machine learning`

### Step 2 — Collect candidates

For each candidate, capture:

- title
- authors and institutes/affiliations when available
- source and direct link
- date
- abstract or source snippet
- why it entered the candidate pool

Keep candidates broad at this stage. Filtering happens later.

### Step 3 — Remove obvious non-fits

Skip immediately if the item is:

- generic quantum hardware with no QML transfer value
- generic AI/ML with no quantum learning/representation connection
- quantum optimization only, unless it contributes to QML architecture/search/training
- business/funding/product news without technical content
- FTQC-only algorithmic speedup with no plausible near/intermediate-term QML relevance
- a recycled press release with no new paper, method, benchmark, code, or technical claim
- already in the dedup set (link or arxiv_id matches a seen paper from the last 7 days)

---

## Team Value Trigger

Before scoring, apply this mandatory gate. Each candidate must match **at least one** of the following six triggers to proceed. If none apply, skip the item immediately — do not score it.

| Trigger | Passes if… |
|---|---|
| **New algo** | Introduces an algorithm, circuit family, or architecture the team has not seen demonstrated in this form. Not an incremental tweak — a conceptually distinct approach. |
| **Quantum advantage evidence** | Provides new experimental or theoretical evidence of quantum advantage in a learning, classification, regression, or kernel task vs. a strong classical baseline. |
| **Advantage measurement** | Introduces a new method, framework, or complexity argument for measuring or certifying quantum advantage, geometric difference, or classical separability. |
| **Business application** | Demonstrates a concrete business-domain application (finance, drug discovery, logistics, materials, etc.) of a known QML algorithm with credible benchmark results. |
| **Domain survey** | A comprehensive survey or position paper that synthesizes the current state of a QML subfield in a way that would update the team's priors or research roadmap. |
| **High-traction signal** | A paper already generating unusually high early community attention (citations, forks, HN/Twitter discussion, workshop spotlight) that the field is converging on. |

---

## Scoring rubric

Score each candidate that passed the Team Value Trigger on **relevance** and **novelty**, both 1-5.

### Relevance score

| Score | Meaning |
|---:|---|
| 5 | Directly impacts core QML architecture/advantage/encoding/trainability/kernel/hardware-aware research. |
| 4 | Strong QML transfer value; likely worth a researcher reading soon. |
| 3 | Adjacent but possibly useful. |
| 2 | Mostly adjacent quantum/AI content. |
| 1 | Not QML-relevant. |

### Novelty score

| Score | Meaning |
|---:|---|
| 5 | New method, theory, benchmark, dataset, architecture, or strong evidence that changes priors. |
| 4 | Meaningful technical extension or unusually useful synthesis/benchmark. |
| 3 | Incremental but nontrivial. |
| 2 | Mostly repackaging or weak novelty. |
| 1 | No clear new technical content. |

**Selection rule:** include only `relevance >= 5` AND `novelty >= 4`. An item scoring 5/5 relevance + 4/5 novelty is the minimum bar. When in doubt, skip — a false negative is better than a false positive. Zero items selected is a valid, expected outcome on most days.

---

## Skeptical QML filter

For each selected item, include one concise skepticism/evidence gate. Choose the most important one:

- **Baseline risk:** Are classical baselines strong enough? Would TabPFN/XGBoost/GNN/SOAP/GAP/etc. be the right comparison?
- **Dequantization risk:** Could Nyström, Random Fourier Features, tensor networks, stabilizer simulation, or another classical approximation reproduce the result?
- **Trainability risk:** Are barren plateaus, gradient concentration, optimizer instability, or sample inefficiency likely?
- **Hardware realism risk:** Are claimed circuits, shots, qubits, gates, QRAM/oracles, latency, or noise assumptions unrealistic?
- **Data-fit risk:** Is there a real quantum-native data structure, or is this generic tabular/vector data with a quantum wrapper?
- **Evidence weakness:** Is it a single dataset, tiny n, weak ablation, missing code, missing uncertainty, or marketing-only claim?

Do not write vague skepticism like “needs more work.” Name the specific evidence gate.

---

## Output schema

The final briefing must be concise and decision-useful.

Start with:

```text
Daily QML Research Scout — <date>
Scan summary: checked <sources/classes>; <candidate_count> candidates; <selected_count> selected.
```

Then include numbered selected items. For each item:

```text
<N>. <Title>
Authors/institute: <authors/institute or "not available">
Source/date: <source>, <date>
Link: <url>
Team value trigger: <which of the 6 triggers this matched>
Summary: <2-5 concise technical lines>
Top claims: <1-3 claims>
Why it matters: <specific audience-relevant implication>
Scores: relevance <1-5>/5; novelty <1-5>/5
Skepticism/evidence gate: <one precise sentence>
Paper review: <yes/no> — <one sentence explaining why or why not>
```

For `Paper review: yes` examples: the paper claims a new quantum advantage — if the claims hold this changes our roadmap; the paper proposes a business application in [domain] — worth verifying with a full evidence audit before pitching to a customer.

For `Paper review: no` examples: incremental experiment, advantage claim is narrow and conditional on FTQC — not actionable now; survey is broad context but no specific claim worth auditing.

End with:

```text
Scout verdict: <one sentence on what the audience should watch, read, test, or ignore next.>
```

If nothing passes the threshold, output:

```text
Daily QML Research Scout — <date>
Scan summary: checked <sources/classes>; <candidate_count> candidates; 0 selected.
No high-signal QML items found in the last <window>.
Scout verdict: <one sentence explaining whether to keep watching a source/theme or take no action.>
```

**After finalizing selected items**, write each selected item to SEEN_PAPERS_PATH (append, one JSON object per line):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","link":"{url}","arxiv_id":"{arxiv_id or null}","title":"{title}"}
```
This prevents the same paper from appearing in future runs within the 7-day dedup window.

---

## Evidence and citation requirements

- Every selected item must have a direct source link.
- Dates must come from the source page when possible; otherwise mark as `date not available` and do not overclaim recency.
- If the item is outside the requested time window but still included due to late indexing or high relevance, explicitly say so.
- Do not invent affiliations, claims, or scores. If authors/institute are not visible, write `not available`.
- Treat company blog claims as weaker evidence than papers unless they include technical details, code, benchmarks, or linked papers.

---

## Common pitfalls

1. **Inflated scores.** Every paper is not 4/5 relevance. Scores must be calibrated: incremental extensions are 3 or below, and only papers that genuinely move the needle reach 5/5 relevance. When in doubt, score down and skip.
2. **Bypassing the Team Value Trigger.** All 6 trigger categories are specific. "Interesting QML paper" is not a trigger. If you cannot name which trigger it matches and why, the item fails.
3. **Dumping every QML-adjacent arXiv result.** The scout is a filter. Most days should produce zero items. Quantity is a bug, not a feature.
4. **Overweighting press releases.** A vendor announcement without technical detail is not selected.
5. **Missing dequantization risk.** Any kernel/feature-map/advantage claim needs a classical approximation/baseline evidence gate.
6. **Confusing quantum optimization with QML.** Optimization papers are included only when they transfer to QML architecture discovery, training, or representation learning.
7. **Ignoring hardware realism.** Near-term QML claims need resource/fidelity/noise sanity checks.
8. **Writing long literature reviews.** This is a daily briefing. Keep it compact.
9. **Skipping dedup.** Always load SEEN_PAPERS_PATH before filtering. Sending the same paper twice breaks team trust in the briefing.

---

## Verification checklist

Before finalizing:

- [ ] Dedup log loaded; no selected item appears in SEEN_PAPERS_PATH within the last 7 days.
- [ ] Every selected item passed the Team Value Trigger; the trigger name is stated in the output.
- [ ] Scores are calibrated: no item scores 5/5 relevance unless it truly alters research priorities.
- [ ] Selected item count is 0–3. If 0, the no-signal output is used.
- [ ] Sources checked include at least arXiv plus one other source class when available.
- [ ] All selected items have direct links.
- [ ] Dates are within the configured window or clearly labeled otherwise.
- [ ] Each selected item has a specific skepticism/evidence gate.
- [ ] Each selected item has a paper-review recommendation with a rationale.
- [ ] Generic quantum/AI/business-only items were skipped.
- [ ] Final output is concise enough for a daily briefing.
- [ ] Selected items appended to SEEN_PAPERS_PATH.
- [ ] No platform-specific delivery/channel details are embedded in the skill itself.

---

## Completion

**Analytics — write end event** (append to ANALYTICS_PATH after sending the briefing):
```json
{"ts":"{ISO_NOW}","run_id":"{RUN_ID}","event":"skill_end","skill":"qml-daily-scout","version":"1.1.0","outcome":"success","duration_s":{elapsed},"items_selected":{count},"output_path":null}
```
An empty-result scout (0 items selected) is still `outcome: "success"` — it is a valid, expected run, not an error.
