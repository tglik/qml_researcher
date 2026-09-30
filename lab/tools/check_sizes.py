"""Refuse to commit experiment files over the size limit (D12 data policy).

    python -m lab.tools.check_sizes [--root ~/repos/qml_artifacts] [--limit-mb 5]

Checks every file git would commit under experiments/ (tracked, staged, and untracked-not-ignored).
A file over the limit must instead be listed in its experiment's data/manifest.json with
"tracked": false and re-created by data/fetch.py. Suitable as a pre-commit hook in qml_artifacts.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .common import LabError, git, main_wrapper, output_root


def oversized(root: Path, limit: int) -> list[tuple[str, int]]:
    files = set(git(root, "ls-files", "--", "experiments").splitlines())
    files |= set(git(root, "ls-files", "--others", "--exclude-standard", "--", "experiments").splitlines())
    out = []
    for f in sorted(files):
        p = root / f
        if p.is_file() and p.stat().st_size > limit:
            out.append((f, p.stat().st_size))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--limit-mb", type=float, default=5.0)
    a = ap.parse_args()
    root = a.root or output_root()
    big = oversized(root, int(a.limit_mb * 1_000_000))
    if big:
        raise LabError("files over the size limit would be committed — gitignore them and add a fetch rule:\n  "
                       + "\n  ".join(f"{f} ({s / 1e6:.1f} MB)" for f, s in big))
    print("sizes OK")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
