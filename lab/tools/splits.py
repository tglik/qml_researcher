"""Hash data splits before any modeling; refuse to silently re-create them.

    python -m lab.tools.splits hash   <thread> --name test --file P3_real/data/test_ids.csv
    python -m lab.tools.splits verify <thread>
    python -m lab.tools.splits show   <thread>

Hashes are stored in <thread>/splits.json. Re-hashing a split name with different contents is
refused — a changed split after modeling started is exactly the leak this exists to prevent.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import LabError, main_wrapper, now, read_json, resolve_thread, sha256_file, write_json


def _load(thread: Path) -> dict:
    p = thread / "splits.json"
    return read_json(p) if p.exists() else {}


def hash_split(thread: Path, name: str, file: str) -> dict:
    target = thread / file
    if not target.exists():
        raise LabError(f"split file {file} does not exist")
    splits = _load(thread)
    digest = sha256_file(target)
    if name in splits and splits[name]["sha256"] != digest:
        raise LabError(f"split '{name}' was already hashed with different contents ({splits[name]['at']}). "
                       "Splits are immutable once created; a changed split needs a lock amendment before data access.")
    splits.setdefault(name, {"file": file, "sha256": digest, "at": now()})
    write_json(thread / "splits.json", splits)
    return splits[name]


def verify(thread: Path) -> list[str]:
    problems = []
    for name, s in _load(thread).items():
        f = thread / s["file"]
        if not f.exists():
            problems.append(f"{name}: {s['file']} missing")
        elif sha256_file(f) != s["sha256"]:
            problems.append(f"{name}: {s['file']} changed since {s['at']}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hash"); h.add_argument("thread"); h.add_argument("--name", required=True); h.add_argument("--file", required=True)
    for c in ("verify", "show"):
        sub.add_parser(c).add_argument("thread")
    a = ap.parse_args()
    thread = resolve_thread(a.thread)
    if a.cmd == "hash":
        s = hash_split(thread, a.name, a.file); print(f"{a.name}: {s['sha256'][:12]}")
    elif a.cmd == "verify":
        problems = verify(thread)
        if problems:
            raise LabError("split problems:\n  " + "\n  ".join(problems))
        print("splits OK")
    else:
        for n, s in _load(thread).items():
            print(f"{n:<16} {s['sha256'][:12]}  {s['file']}  {s['at']}")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
