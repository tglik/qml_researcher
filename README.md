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
/qml-deep-research "does neutral-atom reservoir computing beat classical reservoir on time-series?"
```

Claude reads the skill, runs the 7-phase workflow (scope → literature → domain classification → synthesis → devil's advocate → evidence audit → final report), writes the output artifact to `artifacts/`, and commits it.

**Design principle: thin harness, fat skills.** The orchestrator is a single ReAct loop. All the intelligence is in the skill definitions.

---

## Two-repo layout

The lab runs across two repos with deliberately different roles:

| Repo | Contents | Configured as | Written by |
|------|----------|---------------|------------|
| **`qml_researcher`** (this repo) | Skills, agents, criteria, schemas, lab tools — the system | — | hand-authored, versioned like normal code |
| **`qml_artifacts`** | Everything the system produces: paper cards, hypothesis cards, indexes, sources — **and every self-run experiment** under `experiments/<thread>/<NN_name>/` (README, `VERDICT.md`, `src/`, `results/`, `figures/`, `data/`) | `output_root` in `config/workspace.json` | research skills write Layer 1 sources; `/extract-artifacts` promotes them to cards; the team (and the lab skills) write experiments |

Each experiment's `VERDICT.md` frontmatter is its entity in the knowledge graph
(`artifacts/lab/experiment_entity_schema.md`) — there are no separate experiment cards.
Quartz publishes the markdown and figures but not code or data. Data files over 5 MB are
gitignored and re-created by each experiment's `data/fetch.py` (hashes in `data/manifest.json`).
`/qml-experiments` reads experiments directly for live context and can rerun an experiment's
reproduce command or make a scoped code edit — always confirmed first; it never writes a verdict.

The third repo, `qml_experiments`, was retired on 2026-09-30 and its contents copied into
`qml_artifacts/experiments/` (see `docs/lab/components/C11_repo_consolidation.md`).

---

## Skill catalog

Every skill below exists in `.agents/skills/`. Earlier versions of this README listed planned
skills (`/qml-skeptic`, `/journal-club`, `/claim-audit`, …) that were never built; they were
removed so that no agent follows an instruction to a skill that is not there.

### Research and paper tools

| Skill | What it does | Output |
|-------|-------------|--------|
| `/qml-deep-research` | 7-phase literature-to-report: scope → search → domain classification → synthesis → devil's advocate → evidence audit → final report | `research/<topic>_<date>/` |
| `/qml-paper-review` | Deep critical review of one QML paper: claim extraction, five-criteria screen, consensus search, verdict | review folder + card |
| `/fetch-arxiv` | Fetch any arXiv paper by id, URL or title | source text |
| `/extract-artifacts` | Promote a Layer 1 source (review, research run) into cards in the `qml_artifacts` vault | cards, indexes |
| `/qml-daily-scout` | Scan new arXiv papers against the active directions; triage cards | `triage/`, `triage_log.jsonl` |
| `/synthesize-hypotheses` | Cross-paper claim clusters scored into hypothesis candidates | hypothesis cards |
| `/qml-primitive-transfer` | Map a quantum primitive onto ML workloads and rate business value | opportunity report |
| `/test-skills` | LLM-graded score cards per skill against committed baselines (see also `evals/`) | `tests/reports/` |

### QML Lab — from candidate direction to audited verdict
*The experiment half of the researcher. Design: [`docs/lab/`](docs/lab/01_high_level_plan.md) ·
implementation and review guide: [`lab/README.md`](lab/README.md). Every skill and role is split
into `ESSENCE.md` (how it thinks — for scientific review) and a protocol (how it runs).*

| Skill | What it does |
|-------|-------------|
| `/qml-lab` | **Entry point.** `new` a program from an algorithm or a use case · `status` (what is waiting, for whom; the backlog of actionable hypotheses) · `next` (runs the next allowed step) · `sign` a checkpoint · `escalate` · `amend` · `stats` / `step-down` (the autonomy ladder) |
| `/qml-intake` | Algorithm path (Adi's Stage 0 analysis) or use-case path → `HYPOTHESIS.md` with numbered falsifiable hypotheses; one question per turn until 5/5 |
| `/qml-screen` | Prior-work lookup, then paper screen G0–G3 + seven rules + five QML criteria → PASS / PASS-NARROWED / KILLED-ON-PAPER / ASK-HUMAN; engages the exclusion ledger by mechanism |
| `/qml-prereg` | Pre-registration (phases P1–P5, arms incl. the classical twin, locked thresholds, gray zones, both verdict sentences) → freeze into `PREREG.lock.json` |
| `/qml-review-panel` | Six adversarial personas, pass 1 on the proposal, pass 2 on raw results before any verdict |
| `/qml-run` | One frozen phase: provenance for every number, gates computed from the lock, guard + lock checks |
| `/qml-verdict` · `/qml-audit` | Verdict against frozen gates; independent fresh-context audit (lock diff, recomputation, reproduction, N1–N5) |
| `/qml-variants` · `/qml-promote` | Variant mining + pivot (paper/IP) · promotion PR: ledger entry, verdict entity, hypothesis status, criteria proposals |
| `/qml-build-on` | Source A of the candidate backlog: up to 5 publishable next steps on a paper, hypothesis card or verdict |
| `/qml-open-problems` | Source B: testable claims from open questions and card limitations |
| `/qml-ingest` | Common ingest gate of the candidate backlog: novelty vs arXiv, triage screen G0–G3, the seven-question advantage-potential profile ([criteria](criteria/advantage_potential.md)), value (rung × p), bet sheets; picks from two lanes, steps and bets ([C14](docs/lab/components/C14_lanes.md)); every idea source writes candidates with `lab.tools.backlog add` ([C13](docs/lab/components/C13_candidate_backlog.md)) |

Human checkpoints (`config/lab_autonomy.json`): people sign the **spec and the frozen scorer** at
CP2, and the verdict (CP4) and promotion (CP5). CP3 (phase gate) passes on the verifier when the
lock holds a frozen scorer and every gate was computed (`lab.tools.autonomy cp3-check`). CP1 is
signed in a weekly batch (`lab.tools.autonomy sign-batch`). Deterministic tools:
`python -m lab.tools.<lock|scorer|state|autonomy|gates|guard|provenance|splits|ledger|backlog|validate|check_sizes>`
(stdlib only; tests: `python -m unittest discover -s tests/lab`).

### Harness rules that are enforced, not requested

- **Frozen scorer.** The implementer never writes the code that grades its method: `scorer/` is
  written before CP2, hashed into the lock and run by `lab.tools.gates` in its own process.
- **PreToolUse guard hook** (`hooks/lab_guard.py`, wired in `.claude/settings.json` and the plugin's
  `hooks/hooks.json`): blocks edits to frozen or tool-written files and reads of
  `scorer/heldout/` during a run; asks a person before any post-freeze edit to the spec.
- **Registered subagents** (`.claude/agents/`, generated by `scripts/gen_agents.py` from
  `lab/roles/` and each skill's `agents/`): each role runs with its own model, tools and turn limit.
- **Workflows** (`workflows/`, Claude Code dynamic workflows): `/qml-researcher:review-panel` runs
  the six personas in parallel and computes the panel verdict in code, so no agent can soften a
  BLOCKING issue; `/qml-researcher:rank-ideas` ranks candidates by a pairwise tournament (each
  pair judged in both orders, Bradley-Terry fit by `lab.tools.tournament`, replayable against
  known outcomes with `tournament replay`).
- **Plugin evals** (`evals/`, `claude plugin eval . --trust-plugin`): skill routing, intake
  behaviour and the guard hook, each against a no-plugin baseline. See `evals/README.md`.

### Experiments bridge
*Closed/legacy experiments in the vault — see [Two-repo layout](#two-repo-layout) below. Live lab programs go through `/qml-lab`.*

| Skill | What it does |
|-------|-------------|
| `/qml-experiments` | Reads `{output_root}/experiments/` directly: status table across every experiment (question, verdict, results freshness, git state, entity frontmatter), full detail for one experiment, run-status diagnosis (is a rerun needed?), rerun an experiment's own reproduce command (always confirmed first), or make a scoped code edit inside one experiment's folder |

---

## Agent roles

The generator and the reviewer are never the same agent. Agent sources live with their owner:
lab roles in `lab/roles/<role>/` (ESSENCE + PROTOCOL), panel personas in
`lab/roles/review-panel/personas/`, research agents in `.agents/skills/<skill>/agents/`.
`python scripts/gen_agents.py` renders all of them into `.claude/agents/` with model routing
(judgment roles inherit the session's frontier model; extraction and formatting run on Haiku;
search and graders on Sonnet). Edit the sources, never the generated files.

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

All outputs go to `output/` by default (configurable in `config/workspace.json`). Triage cards land in `output/triage/`, research workspaces in `output/research/<topic>_<date>/`. Set `output_root` to a Google Drive or OneDrive path to sync automatically.

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

### As a Claude Code plugin

```
/plugin marketplace add tglik/qml_researcher
/plugin install qml-researcher@qml-researcher-local
```

The plugin carries the skills, the 37 registered agents, the guard hook and the workflows, and it
works from any project, without a clone. On enable, Claude Code asks for **QML artifacts folder**
(`output_root`): point it at your local qml_artifacts clone. A SessionStart/SubagentStart hook
(`hooks/qml_env.py`) then tells skills and agents where the plugin's `criteria/`, `lab/` and
`artifacts/` files are, puts `lab.tools` on `PYTHONPATH` for Bash, and sets `LAB_OUTPUT_ROOT`.
Update with `/plugin update qml-researcher`. You need read access to this GitHub repo. The clone
below is still the way to *edit* the plugin; Codex and Hermes keep using the installer path
(they do not read Claude Code plugins, so the hook, registered agents and workflows don't apply
there; the frozen scorer and lock checks are Python and hold everywhere).

### macOS / Linux (Claude Code + Codex + Hermes + Gemini)

1. Clone the repo:
   ```bash
   git clone https://github.com/tglik/qml_researcher /path/to/qml_researcher
   cd /path/to/qml_researcher
   ```

2. The `.agents/skills/` directory (canonical) and `.claude/skills/` symlinks are committed — no setup needed after clone.

   Verify:
   ```bash
   ls -la .claude/skills/        # should show symlinks → ../../.agents/skills/ (no plain-text entries)
   cat .claude/skills/fetch-arxiv/SKILL.md  # should show actual SKILL.md content
   ```

   - **Codex, Hermes, Gemini** read `.agents/skills/` directly — no setup needed.
   - **Claude Code** reads `.claude/skills/` via the committed symlinks — no setup needed.

3. Configure paths (first time only) in `config/workspace.json`:
   ```bash
   # output_root: default is output/ (repo-local, gitignored)
   #   To sync to the qml_artifacts vault: "output_root": "/path/to/qml_artifacts"
   # Experiments live in the vault under {output_root}/experiments/ — no separate path to set.
   ```

4. Run your first skill:
   ```
   # Claude Code: /fetch-arxiv 2401.12345
   # Codex:       codex "/fetch-arxiv 2401.12345"
   # Hermes:      hermes "/fetch-arxiv 2401.12345"
   ```

### Windows

Symlinks require Developer Mode or WSL:
1. Enable Developer Mode (Settings → System → For developers → Developer mode)
2. `git config --global core.symlinks true`
3. Re-clone the repo (an existing clone has text files instead of symlinks)
4. Verify in WSL/Git Bash: `test -L .claude/skills/fetch-arxiv && echo OK`

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `codex skills list` shows empty | Wrong cwd, or `.agents/skills/` not readable | Verify `cwd = repo root`; check `ls -la .agents/skills/` shows actual directories |
| Claude Code can't find skills | `.claude/skills/` symlinks broken | Run `test -L .claude/skills/fetch-arxiv && echo OK`; if text file, see Windows steps |
| Windows: `.claude/skills/fetch-arxiv` is a text file | Symlinks checked out as text (Developer Mode off or `core.symlinks false`) | Enable Developer Mode, `git config core.symlinks true`, delete and re-clone |
| `AskUserQuestion` prompt not showing (Codex/Hermes) | AskUserQuestion is CC-only; skill falls back to prose | Normal — answer in chat when the skill asks a question in prose |
| `File not found: criteria/qml_domain.md` | CLI invoked from wrong directory | Always invoke from repo root, not from inside `.agents/skills/` |

---

## Roadmap: SageLab agent runtime

The local Claude install is v0. The longer-term target is SageLab — a hosted agent runtime that runs the QML researcher as a persistent agent accessible to the whole team.

**SageLab v0 will have two surfaces:**

1. **Research Wiki** — git-backed viewer/editor for all artifacts, research runs, agent definitions, and skill cards. Partners can read, search, and edit. Edits to skills/agents require a validation pass before activation.

2. **Research Chat Runner** — a web interface for running workflows. Partners select a workflow (`/qml-deep-research`, `/qml-paper-review`, `/qml-lab`), see structured progress events (not raw terminal output), provide approvals at human-input gates, and receive artifact links on completion.

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
