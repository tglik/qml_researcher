import json
import os
from pathlib import Path

def get_output_root() -> Path:
    """Resolve output_root from config/workspace.json relative to repo root."""
    repo_root = Path(__file__).parent.parent  # scripts/ -> repo root
    config_path = repo_root / "config" / "workspace.json"
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    raw = config["output_root"]
    p = Path(raw)
    return p if p.is_absolute() else (repo_root / p).resolve()

entries = [
    {
        "arxiv_id": "2207.00028",
        "title": "Approximate encoding of quantum states using shallow circuits",
        "source_type": "academic_paper",
        "source_url": "file:///C:/Users/tmgli/Downloads/2207.00028v3.pdf",
        "verdict": "TRIAGE",
        "why_interesting": "Adjacent-A HIGH transfer: local cost function avoids barren plateaus with polynomial measurement scaling; intro explicitly cites quantum machine learning as target use case for state preparation.",
        "why_verdict": "TRIAGE - hardware_fit WARN MAJOR: demonstrated on IonQ+IBM only; staircase linear connectivity required; no neutral-atom Rydberg topology analysis.",
        "date": "2026-05-27T15:00:00Z",
        "fetch_mode": "arxiv",
        "partial_fetch": False,
        "venue": "arXiv preprint",
        "venue_tier": "T5",
        "mode": "full",
        "scope": "adjacent_A",
        "criteria": [
            {"name": "dequantization_risk", "verdict": "N/A", "severity": None, "note": "N/A: classical algorithm for circuit design; no quantum speedup claim."},
            {"name": "geometric_difference", "verdict": "N/A", "severity": None, "note": "N/A: not a kernel paper; no feature map or kernel geometry."},
            {"name": "trainability", "verdict": "PASS", "severity": None, "note": "Local cost function validated against barren plateaus; polynomial measurement scaling confirmed under realistic shot noise."},
            {"name": "hardware_fit", "verdict": "WARN", "severity": "MAJOR", "note": "IonQ (trapped-ion) and IBM (superconducting) only; requires staircase linear connectivity; no neutral-atom Rydberg topology analysis."},
            {"name": "classical_baseline", "verdict": "N/A", "severity": None, "note": "N/A: not an ML learning task; comparison is optimal vs suboptimal circuit implementations."}
        ],
        "qml_transfer_value": "HIGH",
        "triage_checklist": [
            "Staircase linear connectivity vs neutral-atom 2D topology: compatible via atom transport? Check circuit diagram connectivity requirements.",
            "At 20-24 qubits, what is total 2-qubit gate count vs neutral-atom 100-1000 gate coherence budget? Check Figure showing depth vs qubit count.",
            "Does local cost function generalize to quantum kernel circuits (overlap-based objectives) beyond state prep? Check Discussion/Conclusions."
        ],
        "evaluator": "qml-triage/2.0.0",
        "elapsed_seconds": 52
    },
    {
        "arxiv_id": "2308.10383",
        "title": "A Variational Qubit-Efficient MaxCut Heuristic Algorithm",
        "source_type": "academic_paper",
        "source_url": "file:///C:/Users/tmgli/Downloads/2308.10383v2.pdf",
        "verdict": "SKIP",
        "why_interesting": "Adjacent-B: log(N)-qubit graph encoding is a creative compression idea; paper is unusually transparent about its limitations - a clean negative result rather than a misleading claim.",
        "why_verdict": "SKIP - dequantization FAIL CRITICAL: authors confirm O(M+LN) classical simulation matching quantum resources, explicitly obscuring any quantum advantage. LOW QML transfer value.",
        "date": "2026-05-27T15:01:00Z",
        "fetch_mode": "arxiv",
        "partial_fetch": False,
        "venue": "arXiv preprint",
        "venue_tier": "T5",
        "mode": "full",
        "scope": "adjacent_B",
        "criteria": [
            {"name": "dequantization_risk", "verdict": "FAIL", "severity": "CRITICAL", "note": "Authors confirm encoding scheme enables efficient classical simulation O(M+LN), obscuring any quantum advantage."},
            {"name": "geometric_difference", "verdict": "N/A", "severity": None, "note": "N/A: no kernel or feature map; VQC used for optimization."},
            {"name": "trainability", "verdict": "FAIL", "severity": "CRITICAL", "note": "Strongly entangling layers (instance-independent ansatz); explicitly classically simulable; 5-qubit real hardware only."},
            {"name": "hardware_fit", "verdict": "FAIL", "severity": "MAJOR", "note": "IBM superconducting only (Jakarta, Perth, Lagos); no neutral-atom analysis; 5-qubit real-device cap."},
            {"name": "classical_baseline", "verdict": "WARN", "severity": "MAJOR", "note": "Goemans-Williamson present; Gurobi/exact solver and tuned simulated annealing absent."}
        ],
        "qml_transfer_value": "LOW",
        "triage_checklist": [],
        "evaluator": "qml-triage/2.0.0",
        "elapsed_seconds": 40
    },
    {
        "arxiv_id": "2604.07639",
        "title": "Exponential quantum advantage in processing massive classical data",
        "source_type": "academic_paper",
        "source_url": "https://arxiv.org/pdf/2604.07639",
        "verdict": "TRIAGE",
        "why_interesting": "Claims information-theoretic exponential advantage for classification and dimension reduction via quantum oracle sketching without QRAM; processes random classical samples sequentially; advantage persists even if BPP=BQP depending only on quantum mechanics. If proof holds for natural distributions, structurally unaffected by dequantization.",
        "why_verdict": "TRIAGE - three WARN MAJOR: hardness proof scope for natural distributions unconfirmed; 60 logical qubits implies FTQC regime with no NISQ path stated; LS-SVM baseline for sentiment analysis where BERT is standard.",
        "date": "2026-05-27T15:02:00Z",
        "fetch_mode": "arxiv",
        "partial_fetch": False,
        "venue": "arXiv preprint",
        "venue_tier": "T5",
        "mode": "full",
        "criteria": [
            {"name": "dequantization_risk", "verdict": "WARN", "severity": "MAJOR", "note": "Advantage claimed independent of BPP=BQP via info-theoretic separation; random classical samples processed sequentially without QRAM; proof scope for natural distributions unconfirmed from abstract."},
            {"name": "geometric_difference", "verdict": "N/A", "severity": None, "note": "N/A: quantum oracle sketching + QSVT; not a kernel or feature map computation."},
            {"name": "trainability", "verdict": "N/A", "severity": None, "note": "N/A: fixed-parameter non-variational; incremental quantum rotations + classical shadow tomography; no training."},
            {"name": "hardware_fit", "verdict": "WARN", "severity": "MAJOR", "note": "Fewer than 60 logical qubits for demos implies fault-tolerant regime; pure theory/simulation; no hardware experiments; no neutral-atom analysis."},
            {"name": "classical_baseline", "verdict": "WARN", "severity": "MAJOR", "note": "Classical streaming baselines appropriate for theoretical claim; sentiment analysis missing BERT/transformer; RNA-seq dimension reduction missing UMAP/scVI."}
        ],
        "triage_checklist": [
            "Hardness proof: information-theoretic sample complexity lower bound (unlimited classical compute) or computational time complexity only? Check Theorem 1 or Section 2.",
            "Hardness for natural distributions or adversarially constructed ones only? Check proof data distribution assumptions.",
            "Oracle sketching: truly sequential random samples, or hidden quantum data structure prep step? Check data loading description in methods.",
            "Sentiment analysis: BERT/transformer comparison present or only classical streaming baselines? Check experiments table."
        ],
        "evaluator": "qml-triage/2.0.0",
        "elapsed_seconds": 65
    },
    {
        "arxiv_id": None,
        "title": "Opportunities in Full-Stack Design of Low-Overhead Fault-Tolerant Quantum Computation",
        "source_type": "academic_paper",
        "source_url": "file:///C:/Users/tmgli/Downloads/2025_Lukin_Full_Stack_Design_Nature_Comp_Science.pdf",
        "verdict": "TRIAGE",
        "why_interesting": "Adjacent-C MEDIUM transfer: T1 review by QuEra researcher Madelyn Cain and Mikhail Lukin on co-designing algorithms+QEC+hardware to reduce fault-tolerant overhead, with explicit focus on adaptable qubit arrangements (neutral-atom reconfigurable arrays) and quantum LDPC codes. Direct relevance to team hardware partner and 2-5 year roadmap.",
        "why_verdict": "TRIAGE - Adjacent-C; all five QML criteria N/A (not an ML paper). Targeted read to extract LDPC overhead implications for QML circuit feasibility and identify QuEra architectural bets.",
        "date": "2026-05-27T15:03:00Z",
        "fetch_mode": "web",
        "partial_fetch": True,
        "venue": "Nature Computational Science, Dec 2025",
        "venue_tier": "T1",
        "mode": "full",
        "scope": "adjacent_C",
        "criteria": [
            {"name": "dequantization_risk", "verdict": "N/A", "severity": None, "note": "N/A: hardware architecture review; no QML method or speedup claim."},
            {"name": "geometric_difference", "verdict": "N/A", "severity": None, "note": "N/A: no quantum kernel or feature map described."},
            {"name": "trainability", "verdict": "N/A", "severity": None, "note": "N/A: QEC code design paper; no parameterized circuit training discussed."},
            {"name": "hardware_fit", "verdict": "N/A", "severity": None, "note": "N/A (subject): paper IS the hardware fit analysis; focuses on neutral-atom reconfigurable arrays and LDPC codes; QuEra co-authored."},
            {"name": "classical_baseline", "verdict": "N/A", "severity": None, "note": "N/A: hardware architecture review; no ML performance claim."}
        ],
        "qml_transfer_value": "MEDIUM",
        "triage_checklist": [
            "What qubit counts and circuit depths does LDPC overhead reduction enable on neutral-atom hardware in 2-5 years vs team QML circuit requirements?",
            "Does paper analyze neutral-atom reconfigurable arrays (tweezer/Rydberg) specifically or generically? Look for reconfigurable/tweezer/Rydberg.",
            "Does paper identify specific algorithm classes where LDPC-reduced overhead enables advantage within a defined timeline?"
        ],
        "evaluator": "qml-triage/2.0.0",
        "elapsed_seconds": 55
    }
]

output_root = get_output_root()
output_root.mkdir(parents=True, exist_ok=True)
(output_root / "triage").mkdir(parents=True, exist_ok=True)
path = output_root / "triage_log.jsonl"
with open(str(path), "a", encoding="utf-8") as f:
    for e in entries:
        f.write(json.dumps(e) + "\n")

with open(str(path), encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total log entries: {len(lines)}")
for l in lines[-4:]:
    p = json.loads(l)
    aid = p.get("arxiv_id") or "no-arxiv"
    print(f"  {aid:<15}  {p['verdict']:<7}  {p['title'][:52]}")
