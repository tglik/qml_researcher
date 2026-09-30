"""C11 step 3: write data/manifest.json for every experiment and gitignore files > 5 MB.

For each `experiments/<thread>/<NN_name>/data/` directory, records every file with its
sha256 and size. Files larger than the limit are marked `tracked: false` and appended to
`experiments/.gitignore`; they must be re-creatable by that experiment's `data/fetch.py`
(which `fetch.py --verify` checks against this manifest).

    python split_data.py --root ~/repos/qml_artifacts [--limit-mb 5]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--limit-mb", type=float, default=5.0)
    a = ap.parse_args()
    limit = int(a.limit_mb * 1_000_000)
    exp_root = a.root / "experiments"

    ignored: list[str] = []
    for data_dir in sorted(exp_root.glob("*/*/data")):
        mpath = data_dir / "manifest.json"
        # keep hand-added fields (source, fetch, ...) from a previous run
        prior = {e["path"]: e for e in json.loads(mpath.read_text())} if mpath.exists() else {}
        entries = []
        for f in sorted(p for p in data_dir.rglob("*") if p.is_file()):
            if f.name in {"manifest.json", "fetch.py"}:
                continue
            size = f.stat().st_size
            tracked = size <= limit
            rel = f.relative_to(data_dir).as_posix()
            entry = {**prior.get(rel, {}), "path": rel, "sha256": sha256(f), "bytes": size, "tracked": tracked}
            entries.append(entry)
            if not tracked:
                ignored.append(f.relative_to(exp_root).as_posix())
        mpath.write_text(json.dumps(entries, indent=2) + "\n")
        untracked = sum(not e["tracked"] for e in entries)
        print(f"{data_dir.relative_to(exp_root)}: {len(entries)} files, {untracked} untracked")

    gi = exp_root / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    marker = "# data > limit — re-created by data/fetch.py (see data/manifest.json)"
    if marker not in lines:
        lines += ["", marker]
    lines += [p for p in ignored if p not in lines]
    gi.write_text("\n".join(lines).lstrip("\n") + "\n")
    print(f"gitignored: {len(ignored)}")
    for p in ignored:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
