"""Frozen scorer for <thread> — template. Written by the experiment designer before CP2.

Contract (lab/tools/scorer.py):
    python scorer/score.py --phase P1 --thread <thread> --out <json>
reads <thread>/<phase dir>/raw/ and <thread>/scorer/heldout/, writes
    {"<lock id>": {"value": <number>, "ci": [lo, hi]}, ...}
for every numeric gate of that phase, and nothing else. No network, no randomness without a fixed
seed, no imports from the method's src/. Standard library plus the experiments venv only.
After CP2 this file is hashed into PREREG.lock.json; changing it is an amendment.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PHASE_DIRS = {"P1": "P1_toy", "P2": "P2_medium", "P3": "P3_real", "P4": "P4_noise", "P5": "P5_hardware"}


def read_column(path: Path, column: str) -> list[float]:
    with path.open(newline="", encoding="utf-8") as f:
        return [float(row[column]) for row in csv.DictReader(f)]


def mae(pred: list[float], truth: list[float]) -> float:
    if len(pred) != len(truth):
        raise SystemExit(f"length mismatch: {len(pred)} predictions, {len(truth)} labels")
    return sum(abs(p - t) for p, t in zip(pred, truth)) / len(truth)


def score_p1(thread: Path) -> dict:
    """Example: headroom = classical error minus quantum-arm error on the held-out split."""
    raw = thread / PHASE_DIRS["P1"] / "raw"
    truth = read_column(thread / "scorer" / "heldout" / "test_labels.csv", "y")
    classical = mae(read_column(raw / "classical_preds.csv", "y_hat"), truth)
    proposed = mae(read_column(raw / "proposed_preds.csv", "y_hat"), truth)
    return {"P1.G4.threshold": {"value": round(classical - proposed, 6)}}


SCORERS = {"P1": score_p1}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=list(PHASE_DIRS))
    ap.add_argument("--thread", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.phase not in SCORERS:
        raise SystemExit(f"no scorer for {a.phase}")
    Path(a.out).write_text(json.dumps(SCORERS[a.phase](Path(a.thread)), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
