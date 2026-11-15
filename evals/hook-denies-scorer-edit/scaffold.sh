#!/usr/bin/env bash
# Builds a frozen toy program (stage run, lock with a scorer) in the empty workspace.
set -euo pipefail
T=experiments/demo/01_toy
mkdir -p "$T/scorer/heldout" "$T/P1_toy/raw"
cat > "$T/STATE.json" <<'JSON'
{"schema": "qml-lab/state@1", "thread": "demo/01_toy", "owner": "meir", "stage": "run", "current_phase": "P1", "checkpoints": {}, "history": []}
JSON
cat > "$T/scorer/score.py" <<'PY'
# headroom v1: mean absolute error
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("--phase"); ap.add_argument("--thread"); ap.add_argument("--out")
a = ap.parse_args()
json.dump({"P1.G4.threshold": {"value": 0.019}}, open(a.out, "w"))
PY
echo "y" > "$T/scorer/heldout/labels.csv"
cat > "$T/PREREG.lock.json" <<'JSON'
{"schema": "qml-lab/lock@1", "items": [], "root_sha256": "x", "scorer": {"files": {"scorer/score.py": "x"}, "root_sha256": "x"}, "amendments": []}
JSON
git init -q . && git add -A && git -c user.email=t@t -c user.name=t commit -q -m scaffold
