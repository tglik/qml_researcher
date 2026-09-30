"""Check that a run phase did not touch files the implementer may not write.

    python -m lab.tools.guard <thread>

Compares the thread against the commit recorded when the current phase started
(STATE history "phase Pk started"), plus uncommitted changes. Protected: the lock, the
proposal, frozen definitions, the operating point, the verdict and the audit. A PROPOSAL.md
change is allowed only if a lock amendment was recorded after the phase started.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import LabError, git, main_wrapper, read_json, resolve_thread
from .lock import verify as lock_verify
from . import state as st_mod

PROTECTED = ("PREREG.lock.json", "PROPOSAL.md", "frozen_definitions.md", "00_operating_point.md",
             "VERDICT.md", "AUDIT.md", "splits.json")


def changed_files(thread: Path, since: str | None) -> set[str]:
    rel = git(thread, "rev-parse", "--show-prefix").rstrip("/")
    names: set[str] = set()
    if since:
        names |= set(git(thread, "diff", "--name-only", since, "--", ".").splitlines())
    names |= {l[3:] for l in git(thread, "status", "--porcelain", "--", ".").splitlines() if l}
    return {n[len(rel) + 1:] if rel and n.startswith(rel + "/") else n for n in names}


def check(thread: Path) -> list[str]:
    st = st_mod.load(thread)
    phase = st.get("current_phase")
    since = None
    started_at = None
    for h in st.get("history", []):
        if h.get("event") == f"phase {phase} started":
            since, started_at = h.get("commit") or None, h.get("at")
    touched = changed_files(thread, since)
    problems = []
    lock = read_json(thread / "PREREG.lock.json") if (thread / "PREREG.lock.json").exists() else {"amendments": []}
    amended_after = any(a.get("at", "") > (started_at or "") for a in lock.get("amendments", []))
    for f in sorted(touched):
        if f in PROTECTED:
            if f in ("PROPOSAL.md", "PREREG.lock.json") and amended_after:
                continue
            problems.append(f"protected file changed during {phase}: {f}")
    try:
        lock_verify(thread)
    except LabError as e:
        problems.append(str(e))
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thread")
    a = ap.parse_args()
    problems = check(resolve_thread(a.thread))
    if problems:
        raise LabError("guard failed:\n  " + "\n  ".join(problems))
    print("guard OK")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
