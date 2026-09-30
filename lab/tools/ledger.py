"""Exclusion ledger ({output_root}/indexes/exclusion-ledger.md): parse, validate, list, slice.

Each entry is a `## <id>` heading followed by a fenced ```yaml block using a restricted subset:
`key: value`, `key: [a, b]`, and folded text `key: >` followed by indented lines.

    python -m lab.tools.ledger validate [--file PATH]
    python -m lab.tools.ledger list     [--status final|provisional] [--topic TOPIC]
    python -m lab.tools.ledger show     <id>
    python -m lab.tools.ledger slice    --before 2026-07-20 --out PATH   # time-sliced copy for replay evals
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .common import LabError, main_wrapper, output_root, parse_list

ENTRY_RE = re.compile(r"^## (\S+)\s*\n+```yaml\n(.*?)^```", re.S | re.M)
REQUIRED = ("id", "status", "created", "verdict_ref", "mechanism", "excludes", "does_not_exclude",
            "evidence", "audit", "review_by", "topics")
LIST_FIELDS = ("evidence", "covered_cases", "topics")


def default_path() -> Path:
    return output_root() / "indexes" / "exclusion-ledger.md"


def parse_yaml(body: str) -> dict:
    out: dict = {}
    key = None
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m and not line.startswith(" "):
            key, val = m.group(1), m.group(2).split("  #")[0].strip()
            if val == ">":
                out[key] = ""
            elif key in LIST_FIELDS or (val.startswith("[") and val.endswith("]")):
                out[key] = parse_list(val)
            else:
                out[key] = val.strip("\"'")
        elif key is not None and line.startswith(" "):
            out[key] = (out.get(key, "") + " " + line.strip()).strip()
    return out


def parse(path: Path | None = None) -> list[dict]:
    path = path or default_path()
    if not path.exists():
        return []
    entries = []
    for m in ENTRY_RE.finditer(path.read_text()):
        e = parse_yaml(m.group(2))
        e["_heading"] = m.group(1)
        entries.append(e)
    return entries


def validate(entries: list[dict]) -> list[str]:
    errs, seen = [], set()
    for e in entries:
        eid = e.get("id", e.get("_heading"))
        for k in REQUIRED:
            if not e.get(k):
                errs.append(f"{eid}: missing or empty '{k}'")
        if e.get("id") != e.get("_heading"):
            errs.append(f"{eid}: heading '{e.get('_heading')}' does not match id")
        if eid in seen:
            errs.append(f"{eid}: duplicate id")
        seen.add(eid)
        if e.get("status") not in ("final", "provisional"):
            errs.append(f"{eid}: status must be final|provisional")
        if e.get("status") == "final" and e.get("audit") not in ("CONFIRMED", "legacy-human"):
            errs.append(f"{eid}: a final entry needs audit CONFIRMED (or legacy-human for pre-lab verdicts)")
        if e.get("status") == "provisional" and not e.get("reopening_condition"):
            errs.append(f"{eid}: a provisional entry needs a reopening_condition")
        if e.get("audit") not in ("CONFIRMED", "INSUFFICIENT", "legacy-human", None):
            errs.append(f"{eid}: audit must be CONFIRMED | INSUFFICIENT | legacy-human")
        excl = (e.get("excludes") or "").lower()
        if len(excl.split()) < 8:
            errs.append(f"{eid}: 'excludes' is too short to be mechanism-scoped (name the construction, the role, the setting)")
    return errs


def slice_before(src: Path, date: str, out: Path) -> int:
    """Write a copy of the ledger containing only entries created before `date` (for replay evals)."""
    text = src.read_text()
    head = text.split("\n## ", 1)[0]
    keep = [m.group(0) for m in ENTRY_RE.finditer(text) if parse_yaml(m.group(2)).get("created", "9999") < date]
    out.write_text(head.rstrip("\n") + "\n\n" + "\n\n".join(keep) + "\n")
    return len(keep)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    l = sub.add_parser("list"); l.add_argument("--status"); l.add_argument("--topic")
    s = sub.add_parser("show"); s.add_argument("id")
    c = sub.add_parser("slice"); c.add_argument("--before", required=True); c.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    path = a.file or default_path()
    entries = parse(path)
    if a.cmd == "validate":
        errs = validate(entries)
        if errs:
            raise LabError(f"{len(errs)} ledger problem(s):\n  " + "\n  ".join(errs))
        print(f"ledger OK — {len(entries)} entries")
    elif a.cmd == "list":
        for e in entries:
            if (a.status and e.get("status") != a.status) or (a.topic and a.topic not in e.get("topics", [])):
                continue
            print(f"{e['id']:<48} {e.get('status', '?'):<12} review_by={e.get('review_by')}")
    elif a.cmd == "show":
        e = next((x for x in entries if x.get("id") == a.id), None)
        if not e:
            raise LabError(f"no ledger entry {a.id}")
        for k, v in e.items():
            if not k.startswith("_"):
                print(f"{k}: {v}")
    elif a.cmd == "slice":
        n = slice_before(path, a.before, a.out)
        print(f"wrote {n} entries created before {a.before} to {a.out}")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
