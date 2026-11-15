"""The frozen scorer: the code that turns a phase's raw outputs into gate numbers.

Why it exists: the implementer writes the method; it must not also write the code that grades the
method. Agents that are told to maximise a metric edit the evaluator in about half of runs
(RewardHackingAgents, arXiv 2603.11337). So the scorer is written before the freeze, signed with
the spec at CP2, hashed into PREREG.lock.json, and run here, in a separate process, by
`lab.tools.gates`. The implementer only produces `<phase>/raw/`.

Layout inside a thread:

    scorer/score.py        entry point (required). Called as
                           python scorer/score.py --phase P1 --thread <thread> --out <json>
                           and writes {"<lock id>": {"value": <number>, "ci": [lo, hi]?, "pass": bool?}}
    scorer/heldout/        test labels and anything else the implementer may not read (optional)
    scorer/*               helpers, fixtures, a README

Every file under scorer/ (heldout included) is hashed into the lock at freeze. Any later change is
a lock mismatch unless an amendment touching `scorer` was approved before the phase had data.

    python -m lab.tools.scorer hash  <thread>            # print the scorer manifest (pre-freeze check)
    python -m lab.tools.scorer run   <thread> <phase>    # dry run: print what the scorer reports
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .common import LabError, PHASE_DIRS, main_wrapper, sha256_file, sha256_text

SCORER_DIR = "scorer"
ENTRY = "score.py"
HELDOUT = "heldout"
SKIP_PARTS = {"__pycache__", ".pytest_cache"}
TIMEOUT_S = int(os.environ.get("LAB_SCORER_TIMEOUT", "3600"))


def manifest(thread: Path) -> dict | None:
    """{"files": {relpath: sha256}, "root_sha256": …} for scorer/, or None if there is no scorer."""
    root = thread / SCORER_DIR
    if not root.is_dir():
        return None
    if not (root / ENTRY).is_file():
        raise LabError(f"{SCORER_DIR}/ exists but has no {ENTRY} — the scorer needs an entry point")
    files = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and not (SKIP_PARTS & set(p.parts)) and p.suffix != ".pyc":
            files[p.relative_to(thread).as_posix()] = sha256_file(p)
    root_sha = sha256_text("\n".join(f"{k}:{v}" for k, v in sorted(files.items())))
    return {"files": files, "root_sha256": root_sha}


def diff(locked: dict | None, thread: Path) -> list[str]:
    """Differences between the locked scorer manifest and the scorer on disk."""
    current = manifest(thread)
    if locked is None:
        return [] if current is None else ["SCORER  scorer/ added after freeze (lock has no scorer)"]
    if current is None:
        return ["SCORER  scorer/ removed after freeze"]
    out = []
    a, b = locked["files"], current["files"]
    for f in sorted(set(a) | set(b)):
        if f not in b:
            out.append(f"SCORER  removed {f}")
        elif f not in a:
            out.append(f"SCORER  added {f}")
        elif a[f] != b[f]:
            out.append(f"SCORER  changed {f}")
    return out


def _python() -> str:
    """Interpreter for the scorer: the experiments venv when present, else this interpreter."""
    explicit = os.environ.get("LAB_SCORER_PYTHON")
    if explicit:
        return explicit
    from .common import experiments_root
    for cand in (experiments_root() / ".venv" / "bin" / "python",
                 experiments_root() / ".venv" / "Scripts" / "python.exe"):
        if cand.exists():
            return str(cand)
    return sys.executable


def run(thread: Path, phase: str, allowed_ids: set[str] | None = None) -> dict:
    """Run scorer/score.py for a phase in a fresh process; return its validated output plus a stamp."""
    if phase not in PHASE_DIRS:
        raise LabError(f"phase must be one of {list(PHASE_DIRS)}")
    man = manifest(thread)
    if man is None:
        raise LabError("this thread has no scorer/ — nothing to run")
    with tempfile.TemporaryDirectory(prefix="lab-scorer-") as tmp:
        out = Path(tmp) / "measured.json"
        argv = [_python(), str(thread / SCORER_DIR / ENTRY), "--phase", phase, "--thread", str(thread),
                "--out", str(out)]
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "SYSTEMROOT", "TMPDIR", "TEMP", "TMP", "LANG")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            proc = subprocess.run(argv, cwd=thread, env=env, capture_output=True, text=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise LabError(f"scorer timed out after {TIMEOUT_S}s") from None
        if proc.returncode != 0:
            raise LabError(f"scorer exited {proc.returncode}:\n{proc.stderr[-2000:]}")
        if not out.exists():
            raise LabError("scorer finished but wrote no --out file")
        try:
            values = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise LabError(f"scorer output is not JSON: {e}") from None
    if not isinstance(values, dict):
        raise LabError("scorer output must be a JSON object keyed by lock id")
    for gid, v in values.items():
        if not isinstance(v, dict) or ("value" not in v and "pass" not in v):
            raise LabError(f"scorer output for {gid} needs 'value' (and optionally 'ci') or 'pass'")
    if allowed_ids is not None:
        unknown = set(values) - allowed_ids
        if unknown:
            raise LabError(f"scorer reported ids not in the lock: {sorted(unknown)}")
    for gid, v in values.items():
        v.setdefault("provenance_id", f"scorer:{gid}")
    stamp = {"by": "lab.tools.scorer", "root_sha256": man["root_sha256"], "phase": phase, "python": argv[0]}
    return {"values": values, "stamp": stamp}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hash"); h.add_argument("thread")
    r = sub.add_parser("run"); r.add_argument("thread"); r.add_argument("phase", choices=list(PHASE_DIRS))
    a = ap.parse_args()
    from .common import resolve_thread
    thread = resolve_thread(a.thread)
    if a.cmd == "hash":
        man = manifest(thread)
        print(json.dumps(man, indent=2) if man else "no scorer/")
    else:
        res = run(thread, a.phase)
        print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    main_wrapper(main)
