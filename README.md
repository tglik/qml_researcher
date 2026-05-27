# qml-researcher

A Claude Code skills plugin that gives the QML startup team an AI research partner — automating the intensive, time-consuming parts of daily research and acting as a second set of eyes for brainstorming, reviewing, and consulting.

**Immediate use:** install locally in Claude Code on each researcher's machine.  
**Future use:** deployed as a SageLab agent runtime to run as a persistent QML researcher agent.

---

## The problem

QML research is demanding in a specific way. Every interesting idea requires:

- A multi-hour literature sweep before it's worth discussing
- Systematic screening against classical baselines (RFF, Nystrom, TabPFN, GNNs) before any advantage claim is credible
- A hardware realism check against NISQ constraints before any experiment is designed
- Careful tracking of claims through evidence — one overclaim in an investor meeting or paper kills credibility

The team (Tsahi, Meir, Adi) runs weekly meetings, journal clubs, investor prep, hardware partner meetings, and live research in parallel. The bottleneck is not ideas — it's the research labor between ideas and defensible conclusions.

This plugin automates the labor and enforces the rigor.

---

## How it works

Skills are `SKILL.md` files — YAML frontmatter + markdown workflow steps. Claude loads them at runtime and executes them with its standard tools. There is no framework, no separate runtime, no new infrastructure to maintain.

```
/deep-research "does neutral-atom reservoir computing beat classical reservoir on time-series?"
```

Claude reads the skill, runs the 7-phase workflow (scope → literature → domain classification → synthesis → devil's advocate → evidence audit → final report), writes the output artifact to `artifacts/`, and commits it.

**Design principle: thin harness, fat skills.** The orchestrator is a single ReAct loop. All the intelligence is in the skill definitions.

---

## Skill catalog

### Research workflows
*Automate multi-hour tasks that currently require sustained manual effort.*

| Skill | What it does | Output artifact |
|-------|-------------|-----------------|
| `/deep-research` | 7-phase literature-to-report: scope → search → domain classification → synthesis → devil's advocate → evidence audit → final report | `research/<topic>_<date>/` |
| `/project-intake` | Converts a vague idea into a Research Question Card + charter decision (approve / read more / reject) | `research_question_card.md` |
| `/literature-review` | Systematic search across arXiv/Semantic Scholar/OpenAlex, paper cards, citation chain analysis, gap map | `literature_matrix.md`, `paper_cards/` |
| `/experiment-design` | Defines minimal decisive experiment, kill criteria, ablations, QML reproducibility fields | `experiment_passport.md` |
| `/claim-promotion` | Evidence-gated promotion of a claim through statuses: speculative → plausible → observed → supported → strong | `claim_ledger.md` update |
| `/weekly-review` | Per-project status: current question, evidence, strongest counterargument, claim ledger, continue/pivot/kill | `weekly_review_<date>.md` |
| `/portfolio-review` | Monthly: promote, pause, pivot, kill, or convert each active project | `portfolio_review_<date>.md` |
| `/experiment-postmortem` | Structured debrief after a failed or ambiguous experiment | `postmortem_<date>.md` |

### Paper & evidence tools
*Replace hours of manual reading with structured extraction.*

| Skill | What it does | Output artifact |
|-------|-------------|-----------------|
| `/paper-card` | Extracts structured knowledge from a paper: problem, main claim, method, evidence, baselines, assumptions, limitations, follow-up actions, and belief-update questions | `paper_card_<id>.md` |
| `/journal-club` | Multi-role structured analysis: literature scout summarizes, quantum theorist audits assumptions, classical skeptic audits baselines, hardware reviewer audits realism, director decides roadmap impact | `journal_club_<date>.md` |
| `/literature-monitor` | Scans new arXiv/Semantic Scholar papers on a topic, flags by relevance to active research questions | `literature_digest_<date>.md` |
| `/citation-verify` | Verifies every citation in an artifact against primary sources — no fabricated DOIs, PMIDs, or author names | verification report inline |

### QML domain reviewers
*Second set of eyes — specialized critics that run independently from the researcher.*

| Skill | What it does |
|-------|-------------|
| `/qml-skeptic` | Devil's advocate: attacks the quantum advantage claim from every angle — toy baseline, state-prep cost, dequantization, hardware gap, business relevance |
| `/classical-baseline-check` | Identifies the strongest classical alternatives for the task and checks whether the comparison is fair (strong, tuned baselines — not MLPs vs quantum kernels) |
| `/hardware-realism` | Assesses NISQ feasibility on neutral-atom hardware (Q-Factor): qubits, depth, topology, noise, connectivity, shot count, wall-clock cost |
| `/claim-audit` | Screens a QML claim against all 5 criteria: dequantization risk, geometric difference, trainability/simulability trilemma, hardware fit, strong classical baseline |
| `/quantum-assumption-audit` | Identifies hidden assumptions: QRAM, oracle construction, block-encoding cost, state preparation, readout/sample complexity |

### Brainstorming & consulting
*On-demand research partner for thinking through ideas, preparing meetings, and making decisions.*

| Skill | What it does |
|-------|-------------|
| `/research-question` | Sharpens a vague idea into a testable hypothesis: what would support it, what would falsify it, minimal next action |
| `/idea-ranking` | Ranks a set of QML ideas against startup-relevant criteria: near-term feasibility, classical-baseline gap, hardware fit, business defensibility, team fit |
| `/meeting-prep` | Synthesizes open questions, claim ledger status, and recent evidence into meeting-ready talking points |
| `/brainstorm-qml-angles` | Given a classical ML problem, surfaces candidate QML primitives that might apply — with explicit failure-mode flags for each |

### Integrity & reproducibility
*Enforce the same standards as a strong peer-reviewed lab.*

| Skill | What it does |
|-------|-------------|
| `/integrity-check` | Verifies citations, claim-to-evidence alignment, figure/table provenance, and that wording matches claim strength |
| `/reproducibility-audit` | Checks QML reproducibility fields: code commit, seeds, dataset version, backend, circuit family, qubit count, depth, shots, noise model, optimizer, hyperparameters |
| `/negative-result` | Structures a failed experiment as a durable artifact: what failed, hypothesis status, what was learned, what should not be retried |

---

## Agent roles

Skills invoke specialized agents for different parts of the work. Each agent has a defined responsibility and output contract — the generator and the reviewer are never the same agent.

| Agent | Responsibility |
|-------|---------------|
| `research-scientist` | Orchestrates workflow execution, maintains project state |
| `literature-scout` | Searches and screens papers; builds paper cards and literature matrix |
| `evidence-auditor` | Verifies citations from tool results only — never from memory; extracts quote spans |
| `devils-advocate-scientist` | Attacks claims, assumptions, and baselines; forces decisive tests |
| `quantum-domain-analyst` | Audits quantum assumptions; NISQ/FT classification; resource accounting |
| `quantum-experiment-planner` | Designs minimal decisive experiments; defines kill criteria and ablations |
| `synthesis-writer` | Writes only from promoted claims; preserves uncertainty and limitations |

---

## Artifact system

Every workflow produces durable artifacts. Claims, evidence, and decisions accumulate in the lab's memory across sessions.

| Artifact | Purpose |
|----------|---------|
| **Research Question Card** | One per idea: question, hypothesis, support, falsification, minimal next action |
| **Project Charter** | Approved projects: question, hypothesis, novelty claim, classical baselines, quantum primitive, hardware assumptions, success/kill criteria |
| **Paper Card** | One per paper: problem, claim, method, evidence, baselines, assumptions, limitations, belief-update questions |
| **Literature Matrix** | Across papers for a topic: coverage map, contradictions, gaps |
| **Evidence Record** | One per evidence item: source, quote/result, what it supports/contradicts, claim strength |
| **Experiment Passport** | One per experiment: full reproducibility fields (backend, qubits, depth, shots, seeds, noise, optimizer) |
| **Claim Ledger** | Per-project: all claims with status, evidence links, allowed/forbidden wording |
| **Review Panel Report** | Post-review: decision, strengths, weaknesses, required fixes, decisive next test |
| **Final Integrity Report** | Pre-publication: citation verification, figure/data alignment, reproducibility |

Artifacts are saved to `ai-os/01_Projects/QML_Startup/artifacts/` as `<topic>_<YYYY-MM-DD>.md`. Research runs go to `research/<topic>_<date>/`.

### Claim status ladder

Claims move through statuses — promotion requires passing an evidence gate:

```
speculative → plausible → observed → supported → strong → published
                                                         ↘ refuted
```

No writing agent may strengthen a claim's wording beyond its current status.

---

## QML failure modes this plugin is designed to catch

The plugin encodes 17 known failure modes in QML research claims:

- Quantum advantage shown only against weak toy baseline (MLP, SVM, generic kernel)
- Classical baseline not tuned (TabPFN-2.5/XGBoost for tabular; GNN/SOAP for graphs)
- Noise-free simulation treated as hardware-relevant result
- State preparation, QRAM, or oracle cost hidden
- Readout / sample complexity ignored
- Shot count too low or not reported
- Circuit selected post-hoc on test data
- Too few seeds / optimizer stochasticity not reported
- Barren plateau / training failure not reported
- Dequantization-vulnerable claim (RFF/Nystrom matches quantum kernel)
- Geometric difference not checked
- Hardware topology / calibration constraints ignored
- Wall-clock / resource cost against classical not computed
- Expressibility used as proxy for task performance without evidence
- "Neutral atom fit" asserted generically without primitive mapping
- Fault-tolerant result framed as near-term startup wedge without a bridge
- Single-encoding PQC = truncated Fourier model (not a new capability)

---

## Installation

### Local install (Claude Code)

```bash
# Clone into your Claude skills directory
git clone https://github.com/<org>/qml-researcher ~/.claude/skills/qml-researcher

# Or add to an existing Claude Code project
git clone https://github.com/<org>/qml-researcher .claude/skills/qml-researcher
```

Skills are auto-discovered by Claude Code from the `.claude/skills/` directory. No additional setup needed.

### Usage

```
/deep-research <question>
/paper-card <arxiv_id or url>
/qml-skeptic <claim or direction>
/claim-audit <claim>
/meeting-prep
```

---

## Roadmap: SageLab agent runtime

The local Claude install is v0. The longer-term target is SageLab — a hosted agent runtime that runs the QML researcher as a persistent agent accessible to the whole team.

**SageLab v0 will have two surfaces:**

1. **Research Wiki** — git-backed viewer/editor for all artifacts, research runs, agent definitions, and skill cards. Partners can read, search, and edit. Edits to skills/agents require a validation pass before activation.

2. **Research Chat Runner** — a web interface for running workflows. Partners select a workflow (`/deep-research`, `/paper-card`, `/claim-audit`), see structured progress events (not raw terminal output), provide approvals at human-input gates, and receive artifact links on completion.

Human judgment remains central — the agent runs the research labor, humans decide on direction, claim strength, and startup relevance.

---

## Design principles

1. Build the lab around artifacts, not chats.
2. Use roles to separate creation from verification — the generator and reviewer are never the same agent.
3. Make claim promotion explicit and evidence-gated.
4. Force every QML idea through classical baselines and hardware realism before it becomes a talking point.
5. Preserve negative results and failed experiments.
6. Require source/citation verification from tool results, not model memory.
7. Make reproducibility part of the claim, not an appendix.
8. Keep human judgment central for direction, claim strength, and startup relevance.
