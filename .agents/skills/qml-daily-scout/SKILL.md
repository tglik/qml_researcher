---
name: qml-daily-scout
version: 1.0.0
description: |
  Agent-agnostic daily QML research scouting workflow. Scans recent papers,
  technical posts, and publication/news sources for high-signal QML items,
  filters them with skeptical QML criteria, and emits a concise decision-useful
  briefing for a configured audience.

  Use when running a recurring or ad-hoc QML research scout for new papers,
  publications, technical blog posts, or news from the last 24-72 hours.
triggers:
  - daily qml scout
  - qml research scout
  - new qml papers
  - recent qml publications
  - qml news scan
  - quantum machine learning watch
  - daily research briefing
input:
  - Time window, default 48 hours
  - Audience or organization context
  - Topic priorities
  - Source list
  - Selection threshold and max item count
  - Delivery/output constraints, supplied by the caller or platform wrapper
output:
  - Concise scout briefing with selected items or a no-high-signal result
  - For every selected item: title, authors/institute, source/link, date, summary, top claims, why it matters, relevance score, novelty score, and skepticism/evidence gate
allowed-tools:
  - WebSearch
  - WebFetch
---

# /qml-daily-scout

Daily or ad-hoc QML research scouting. Recent technical signals in → concise, skeptical, decision-useful briefing out.

This skill is intentionally **agent-agnostic**. It defines the research/scouting method, screening criteria, and briefing schema. Platform-specific delivery details — Slack channel, cron schedule, message routing, model choice, or attachment behavior — must be supplied by the caller/job configuration, not hardcoded here.

---

## Role

You are a QML research scout. Your job is not to summarize everything new. Your job is to find technically interesting signals that could alter research priorities, experiment design, IP thinking, or technical positioning.

You must be skeptical by default. Prefer one technically material paper over ten hype posts. Skip items that are merely adjacent to QML unless they have clear QML transfer value.

---

## Inputs the caller must configure

If a caller does not provide a value, use the defaults below.

| Field | Default | Notes |
|---|---:|---|
| Time window | last 48 hours | Use source publication/submission date where possible. |
| Max selected items | 7 | Fewer is better when signal is weak. |
| Relevance threshold | 4/5 | Item must matter to QML research, not just quantum/AI generally. |
| Novelty threshold | 3/5 | Item should contain new technical content or materially new positioning. |
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
7. **Hardware-aware QML** — near-term constraints, noise/fidelity/resource accounting, especially neutral-atom relevance when applicable.
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
- `quantum reservoir`, `neutral atom`, `Rydberg`, `graph kernel`, `molecular`, `Hamiltonian learning`
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

---

## Scoring rubric

Score each surviving candidate on **relevance** and **novelty**, both 1-5.

### Relevance score

| Score | Meaning |
|---:|---|
| 5 | Directly impacts core QML architecture/advantage/encoding/trainability/kernel/hardware-aware research. |
| 4 | Strong QML transfer value; likely worth a researcher reading soon. |
| 3 | Adjacent but possibly useful; include only if unusually novel. |
| 2 | Mostly adjacent quantum/AI content; normally skip. |
| 1 | Not QML-relevant; skip. |

### Novelty score

| Score | Meaning |
|---:|---|
| 5 | New method, theory, benchmark, dataset, architecture, or strong evidence that changes priors. |
| 4 | Meaningful technical extension or unusually useful synthesis/benchmark. |
| 3 | Incremental but nontrivial. |
| 2 | Mostly repackaging or weak novelty. |
| 1 | No clear new technical content. |

Default selection rule: include only `relevance >= 4` and `novelty >= 3`, unless the caller sets a different threshold.

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
Summary: <2-5 concise technical lines>
Top claims: <1-3 claims>
Why it matters: <specific audience-relevant implication>
Scores: relevance <1-5>/5; novelty <1-5>/5
Skepticism/evidence gate: <one precise sentence>
```

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

---

## Evidence and citation requirements

- Every selected item must have a direct source link.
- Dates must come from the source page when possible; otherwise mark as `date not available` and do not overclaim recency.
- If the item is outside the requested time window but still included due to late indexing or high relevance, explicitly say so.
- Do not invent affiliations, claims, or scores. If authors/institute are not visible, write `not available`.
- Treat company blog claims as weaker evidence than papers unless they include technical details, code, benchmarks, or linked papers.

---

## Common pitfalls

1. **Dumping every QML-adjacent arXiv result.** The scout is a filter. Weak relevance or weak novelty should be skipped.
2. **Overweighting press releases.** A vendor announcement without technical detail is usually not selected.
3. **Missing dequantization risk.** Any kernel/feature-map/advantage claim needs a classical approximation/baseline evidence gate.
4. **Confusing quantum optimization with QML.** Optimization papers are included only when they transfer to QML architecture discovery, training, or representation learning.
5. **Ignoring hardware realism.** Near-term QML claims need resource/fidelity/noise sanity checks.
6. **Writing long literature reviews.** This is a daily briefing. Keep it compact.

---

## Verification checklist

Before finalizing:

- [ ] Sources checked include at least arXiv plus one other source class when available.
- [ ] All selected items have direct links.
- [ ] Dates are within the configured window or clearly labeled otherwise.
- [ ] Each selected item has relevance and novelty scores.
- [ ] Each selected item has a specific skepticism/evidence gate.
- [ ] Generic quantum/AI/business-only items were skipped.
- [ ] Final output is concise enough for a daily briefing.
- [ ] No platform-specific delivery/channel details are embedded in the skill itself.
