# AGENTS.md — qml-researcher project instructions

This is the Codex CLI / Hermes / Gemini CLI project-level instruction file (equivalent of CLAUDE.md for non-Anthropic agents). For Claude Code, see CLAUDE.md.

**Full QML domain criteria are in `criteria/qml_domain.md` — read it when you need the complete specification.** The key criteria and safety rules are inlined below.

---

## Project overview

**qml-researcher** packages all QML research workflows as SKILL.md files. The team is Tsahi, Meir, Adi — a QML startup working with neutral-atom hardware (Q-Factor, QuEra, Pasqal).

---

## Skill discovery

Skills live in `.agents/skills/` (canonical). Invoke by name:

| Skill | Invocation |
|-------|-----------|
| `/fetch-arxiv` | Fetch any arXiv paper by ID, URL, or title |
| `/qml-deep-research` | Multi-phase literature research for a QML topic |
| `/qml-paper-review` | Deep critical review of a single QML paper |

Always invoke skills from the **repository root** — skills use repo-root-relative paths (`criteria/qml_domain.md`, `config/workspace.json`).

---

## Agent spawn mapping (Codex)

Skills use `Agent(subagent_type="claude", ...)` syntax (Claude Code SDK). In Codex, map this to:
```
codex exec "<prompt>" -s read-only
```
The task prompts in each skill are agent-agnostic — inject them into Codex's spawn mechanism.

---

## Output configuration

Output path is controlled by `config/workspace.json` → `output_root`.
Default: `output/` (repo-local, gitignored).
To sync to cloud storage, set `output_root` to an absolute path.

---

## QML domain criteria (inline — enforced in all research skills)

All skills that evaluate a QML direction or claim screen against these 5 criteria. Full details: `criteria/qml_domain.md`.

### The 5 criteria

1. **Strong Classical Baseline** — comparison must use the best available classical method, tuned appropriately.
   - Tabular: TabPFN-2.5, XGBoost with Optuna. NOT vanilla MLP or untuned SVM.
   - Graph/molecular: GNN (GIN/MPNN), SOAP+GP, GAP. NOT SVM on fingerprints.
   - Time series: LSTM, Transformer (Mamba, PatchTST). NOT ARIMA.

2. **Dequantization Risk** — a quantum kernel or speedup is vulnerable if a classical Nystrom/RFF approximation matches performance. Must prove hardness or show empirical gap.

3. **Quantum-Native Data Fit** (geometric difference) — the quantum kernel must be genuinely different from RBF/polynomial kernels (Huang et al. 2021). Single-layer encodings (ZZ-feature map) = truncated Fourier ≈ classical.

4. **Trainability / Simulability** — barren plateau risk for deep random PQCs; classical simulability for shallow circuits. Fixed-parameter circuits (reservoir, Hamiltonian kernels) sidestep training risk.

5. **Hardware Fit** — NISQ-realistic on neutral-atom hardware (Q-Factor modality):
   - < 50 qubits, < 50 two-qubit gates: PASS
   - 50–300 qubits / 50–500 gates: CONDITIONAL
   - > 300 qubits or QRAM assumed: FAIL

### Quick reference: SKIP / TRIAGE / PASS

| Criterion | SKIP (CRITICAL FAIL) | TRIAGE (WARN) | PASS |
|-----------|---------------------|---------------|------|
| Classical Baseline | Toy baseline only (MLP/default SVM) | Missing one required baseline | All required, tuned |
| Dequantization | Clear RFF/Nystrom vulnerability, no hardness argument | Partially addresses; regime unclear | Explicit hardness or empirical disproof |
| Quantum-Native Data Fit | Single-layer encoding / ZZ-feature map only | Structured encoding, no kernel comparison | Geometric difference computed or argued |
| Trainability | Barren plateau regime; n ≤ 8 qubits only | Shallow circuit, no simulability check | Risks addressed for this architecture |
| Hardware Fit | QRAM assumed; FTQC required without acknowledgment | Cross-platform claimed without analysis | Hardware-specific analysis, platform-realistic |

**Any CRITICAL = SKIP immediately.**

### Current strong directions (read unless criterion fails outright)
- Neutral-atom graph kernels and Rydberg-native ML
- Quantum reservoir computing on neutral-atom hardware
- Hamiltonian kernels (kernel defined by quantum evolution)
- Dynamic circuits with mid-circuit measurement and feedforward
- MBQC-style architectures for learning
- Geometric QML (equivariant circuits on molecular symmetry groups)

### Deprioritized (do not re-suggest without new evidence)
- Generic low-data tabular VQC demos (n < 200 samples, standard UCI datasets)
- Single-encoding PQC claims (ZZ/Z-feature map) — equivalent to truncated Fourier
- Generic HHL linear-algebra speedups without dequantization refutation
- Quantum advantage on MNIST, iris, or breast cancer datasets
- VQE for chemistry without noise analysis and strong classical baseline (CCSD(T), DMRG)

### Claim status ladder

All material claims must carry a status label. Writing agents may not strengthen wording beyond current status:

```
speculative → plausible → observed → supported → strong → published
                                                         ↘ refuted
```
