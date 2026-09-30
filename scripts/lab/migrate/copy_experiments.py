"""C11 step 2: copy qml_experiments' tracked files into qml_artifacts/experiments/.

Plain copy (no history) of `git ls-files` at a pinned commit, with one layout
normalization: the stray top-level `experiments/NN_name/` folders (data that belongs
to a thread experiment) are merged into `experiments/<thread>/NN_name/`.

Prints an accounting table and exits non-zero if any tracked file is unaccounted for.

    python copy_experiments.py --src ~/repos/qml_experiments --dst ~/repos/qml_artifacts [--dry-run]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Repo-root files that move to experiments/ (they describe the experiments tree).
ROOT_FILES = {"README.md": "README.md", "requirements.txt": "requirements.txt"}
# Repo-root files that stay behind in the archived repo.
LEFT_BEHIND = {".gitignore", "scripts/make_docx.py"}


def thread_index(src: Path) -> dict[str, str]:
    """Map experiment folder name -> thread, from experiments/<thread>/<NN_name>/."""
    out: dict[str, str] = {}
    for d in (src / "experiments").glob("*/*"):
        if d.is_dir() and d.name[:2].isdigit() and not d.parent.name[:2].isdigit():
            out[d.name] = d.parent.name
    return out


def target_for(rel: str, threads: dict[str, str]) -> str | None:
    parts = rel.split("/")
    if rel in LEFT_BEHIND:
        return None
    if rel in ROOT_FILES:
        return "experiments/" + ROOT_FILES[rel]
    if parts[0] != "experiments":
        raise ValueError(f"unexpected tracked path outside experiments/: {rel}")
    if parts[1][:2].isdigit():  # stray top-level experiments/NN_name/...
        thread = threads.get(parts[1])
        if thread is None:
            raise ValueError(f"stray folder with no thread match: {rel}")
        return "/".join(["experiments", thread, *parts[1:]])
    return rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--dst", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    sha = subprocess.check_output(["git", "-C", a.src, "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", a.src, "status", "--porcelain"], text=True)
    if dirty.strip():
        print("source tree is dirty; commit or stash first", file=sys.stderr)
        return 2
    files = subprocess.check_output(["git", "-C", a.src, "ls-files"], text=True).splitlines()
    threads = thread_index(a.src)

    copied, left, relocated = 0, [], []
    seen_targets: dict[str, str] = {}
    for rel in files:
        tgt = target_for(rel, threads)
        if tgt is None:
            left.append(rel)
            continue
        if tgt in seen_targets:
            raise ValueError(f"collision: {rel} and {seen_targets[tgt]} -> {tgt}")
        seen_targets[tgt] = rel
        if tgt != rel:
            relocated.append((rel, tgt))
        if not a.dry_run:
            dst = a.dst / tgt
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(a.src / rel, dst)
        copied += 1

    print(f"source sha: {sha}")
    print(f"tracked: {len(files)}  copied: {copied}  left behind: {len(left)}")
    for r in left:
        print(f"  left: {r}")
    print(f"relocated: {len(relocated)}")
    for r, t in relocated:
        print(f"  {r} -> {t}")
    if copied + len(left) != len(files):
        print("ACCOUNTING MISMATCH", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
