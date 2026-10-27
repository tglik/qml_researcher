"""Build the gate-table mock for card v2 qml-06 from the reference rerun.

    python scripts/paper_replay/reference/build_qml06_mocks.py

Reads output/paper-replay/reference/qml-06/results.json and writes
tests/fixtures/paper_replay/cards_v2/qml-06/gate_table.md (numbers only, no interpretation) and
tests/fixtures/paper_replay/cards_v2/qml-06/{raw_results.csv, reference_results.json} (per-seed rows for the
auditor; the numeric key for graders).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REF = REPO / "output/paper-replay/reference/qml-06"
CARD = REPO / "tests/fixtures/paper_replay/cards_v2/qml-06"
SIZES = [2, 4, 6, 8, 10, 12]


def cell(res: dict, key: str, val: str, digits: int = 3) -> str:
    g = res.get(key)
    if not g or val not in g["mean"]:
        return "—"
    return f"{g['mean'][val]:.{digits}f} ± {g['sd'][val]:.{digits}f}"


def gate(res: dict, task: str, rel: bool = False) -> str:
    rows = []
    for emb in ("E2", "E3"):
        r = res.get(f"{emb}|n=12|N=600")
        if not r:
            rows.append(f"{emb}: no data at n = 12")
            continue
        pq, cl = r["mean"][f"{task}.PQ.cv"], r["mean"][f"{task}.best_classical.cv"]
        if rel:
            ratio = pq / cl if cl else float("nan")
            rows.append(f"{emb}: PFK / best classical = {ratio:.3f} (pass if ≤ 0.9): "
                        f"{'PASS' if ratio <= 0.9 else 'FAIL'}")
        else:
            sd = r["sd"][f"{task}.PQ.cv"] + r["sd"][f"{task}.best_classical.cv"]
            ok = (cl - pq) >= 0.02 and (cl - pq) > 2 * sd
            rows.append(f"{emb}: gap = {cl - pq:+.3f}, seed spread {sd:.3f} (pass if gap ≥ 0.02 and > 2× spread): "
                        f"{'PASS' if ok else 'FAIL'}")
    return "; ".join(rows)


def main() -> None:
    res = json.loads((REF / "results.json").read_text(encoding="utf-8"))
    out = ["# Gate table: qml-06", "",
           "Source: `output/paper-replay/reference/qml-06/results.json`, built by "
           "`scripts/paper_replay/reference/qml06_power_of_data.py` (3 seeds; mean ± standard deviation "
           "over seeds). Test errors use 3-fold cross-validation on the training split. Raw per-seed rows: "
           "`raw_results.csv`.", ""]
    for task, name, unit in (("C", "Task C: dress vs shirt", "test classification error"),
                             ("Q", "Task Q: quantum-process labels", "test mean absolute error"),
                             ("engineered", "Task E: engineered labels", "test classification error")):
        out += [f"## {name} ({unit})", "",
                "| Embedding | n | Fidelity kernel | PFK | Best classical |", "|---|---|---|---|---|"]
        for emb in ("E1", "E2", "E3"):
            for n in SIZES:
                k = f"{emb}|n={n}|N=600"
                if k in res:
                    out.append(f"| {emb} | {n} | {cell(res, k, f'{task}.Q.cv')} | {cell(res, k, f'{task}.PQ.cv')} | "
                               f"{cell(res, k, f'{task}.best_classical.cv')} |")
        out.append("")
    out += ["## Diagnostics (label-free)", "",
            "| Embedding | n | qubits | d, fidelity | d, PFK | g(C‖fidelity) | g(C‖PFK) | mean off-diagonal fidelity |",
            "|---|---|---|---|---|---|---|---|"]
    for emb in ("E1", "E2", "E3"):
        for n in SIZES:
            k = f"{emb}|n={n}|N=600"
            if k in res:
                q = n + 1 if emb == "E3" else n
                out.append(f"| {emb} | {n} | {q} | {cell(res, k, 'd_Q', 1)} | {cell(res, k, 'd_PQ', 1)} | "
                           f"{cell(res, k, 'g_CQ', 2)} | {cell(res, k, 'g_CPQ', 2)} | {cell(res, k, 'kq_offdiag_mean')} |")
    out += ["", "## Training-size sweep (n = 10)", "",
            "| Embedding | Task | Training size | PFK | Best classical |", "|---|---|---|---|---|"]
    for emb in ("E2", "E3"):
        for task in ("C", "Q", "engineered"):
            for m in (100, 200, 400, 600):
                k = f"{emb}|n=10|N={m}"
                if k in res:
                    out.append(f"| {emb} | {task} | {m} | {cell(res, k, f'{task}.PQ.cv')} | "
                               f"{cell(res, k, f'{task}.best_classical.cv')} |")
    out += ["", "## Gates (mechanical, locked rules)", "",
            f"- **G-C (H1):** {gate(res, 'C')}",
            f"- **G-Q (H2):** {gate(res, 'Q', rel=True)}",
            f"- **G-E (existence, synthetic):** {gate(res, 'engineered')}", ""]
    (CARD / "gate_table.md").write_text("\n".join(out), encoding="utf-8")

    (CARD / "reference_results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    rows = [json.loads(l) for l in (REF / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    with (CARD / "raw_results.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["emb", "n", "qubits", "seed", "n_train", "task", "arm", "test_error_cv", "test_error_best",
                    "selected_config", "d_Q", "d_PQ", "g_CQ", "g_CPQ"])
        for r in sorted(rows, key=lambda r: (r["emb"], r["n"], r["n_train"], r["seed"])):
            for task, t in r["tasks"].items():
                for arm, v in t.items():
                    if arm == "best_classical":
                        continue
                    w.writerow([r["emb"], r["n"], r["qubits"], r["seed"], r["n_train"], task, arm,
                                f"{v['test_cv']:.4f}", f"{v['test_best']:.4f}", v["cfg"],
                                f"{r['d_Q']:.2f}", f"{r['d_PQ']:.2f}", f"{r['g_CQ']:.3f}", f"{r['g_CPQ']:.3f}"])
    print("wrote gate_table.md, raw_results.csv, reference_results.json in", CARD)


if __name__ == "__main__":
    main()
