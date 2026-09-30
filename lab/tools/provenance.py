"""Record where every material number came from.

    python -m lab.tools.provenance record <thread> <phase> --id P3.G6.ndcg_q --value 0.412
        --file P3_real/raw/metrics.csv --command "python -m src.eval --arm Q" [--unit NDCG@20]
        [--ci 0.40,0.42] [--selector "arm=Q,split=test"] [--seeds 0,1,2] [--wall 812] [--mem 3.1]
        [--dataset-sha …] [--split-sha …]
    python -m lab.tools.provenance show   <thread> <phase>
    python -m lab.tools.provenance check  <thread>      # every file exists and still hashes the same

Git commit and environment hash are captured automatically. The environment hash is the sha256
of `pip freeze` for the interpreter given by --python (default: experiments/.venv, else current).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .common import (PHASE_DIRS, LabError, experiments_root, git, main_wrapper, now, read_json,
                     resolve_thread, sha256_file, sha256_text, write_json)


def env_hash(python: str | None = None) -> str:
    py = python or str(experiments_root() / ".venv" / "bin" / "python")
    if not Path(py).exists():
        py = sys.executable
    try:
        frozen = subprocess.check_output([py, "-m", "pip", "freeze"], text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        frozen = f"unknown:{py}"
    return sha256_text(frozen)[:16]


def record(thread: Path, phase: str, **kw) -> dict:
    target = thread / kw["file"]
    if not target.exists():
        raise LabError(f"--file {kw['file']} does not exist under {thread}")
    entry = {"number_id": kw["id"], "value": kw["value"], "ci": kw.get("ci"), "unit": kw.get("unit"),
             "file": kw["file"], "file_sha256": sha256_file(target), "row_selector": kw.get("selector"),
             "command": kw["command"], "git_commit": git(thread, "rev-parse", "HEAD") or "uncommitted",
             "env_hash": env_hash(kw.get("python")), "dataset_sha256": kw.get("dataset_sha"),
             "split_sha256": kw.get("split_sha"), "seeds": kw.get("seeds"), "wall_clock_s": kw.get("wall"),
             "peak_mem_gb": kw.get("mem"), "at": now()}
    path = thread / PHASE_DIRS[phase] / "provenance.json"
    entries = read_json(path) if path.exists() else []
    if any(e["number_id"] == entry["number_id"] for e in entries):
        raise LabError(f"number id {entry['number_id']} already recorded in {phase} — ids are unique; use a new id for a rerun")
    entries.append(entry)
    write_json(path, entries)
    return entry


def check(thread: Path) -> list[str]:
    problems = []
    for prov in sorted(thread.glob("P*/provenance.json")):
        for e in read_json(prov):
            f = thread / e["file"]
            if not f.exists():
                problems.append(f"{e['number_id']}: file missing {e['file']}")
            elif e.get("file_sha256") and sha256_file(f) != e["file_sha256"]:
                problems.append(f"{e['number_id']}: {e['file']} changed since the number was recorded")
    return problems


def _num(s: str):
    try:
        return float(s)
    except ValueError:
        return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("thread"); r.add_argument("phase", choices=list(PHASE_DIRS))
    r.add_argument("--id", required=True); r.add_argument("--value", required=True); r.add_argument("--file", required=True)
    r.add_argument("--command", required=True); r.add_argument("--unit"); r.add_argument("--ci"); r.add_argument("--selector")
    r.add_argument("--seeds"); r.add_argument("--wall", type=float); r.add_argument("--mem", type=float)
    r.add_argument("--dataset-sha"); r.add_argument("--split-sha"); r.add_argument("--python")
    s = sub.add_parser("show"); s.add_argument("thread"); s.add_argument("phase", choices=list(PHASE_DIRS))
    c = sub.add_parser("check"); c.add_argument("thread")
    a = ap.parse_args()
    thread = resolve_thread(a.thread)
    if a.cmd == "record":
        e = record(thread, a.phase, id=a.id, value=_num(a.value), file=a.file, command=a.command, unit=a.unit,
                   ci=[float(x) for x in a.ci.split(",")] if a.ci else None, selector=a.selector,
                   seeds=[int(x) for x in a.seeds.split(",")] if a.seeds else None, wall=a.wall, mem=a.mem,
                   dataset_sha=a.dataset_sha, split_sha=a.split_sha, python=a.python)
        print(f"recorded {e['number_id']} = {e['value']}")
    elif a.cmd == "show":
        path = thread / PHASE_DIRS[a.phase] / "provenance.json"
        for e in (read_json(path) if path.exists() else []):
            print(f"{e['number_id']:<32} {e['value']!s:<12} {e['file']}  [{e['git_commit'][:8]}]")
    elif a.cmd == "check":
        problems = check(thread)
        if problems:
            raise LabError("provenance problems:\n  " + "\n  ".join(problems))
        print("provenance OK")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
