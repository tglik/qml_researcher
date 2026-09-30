"""Pre-registration lock: freeze, verify, diff, amend.

Every fenced ```lock block in PROPOSAL.md and frozen_definitions.md is one lock item:

    ```lock
    id: P1.G4.threshold
    kind: threshold            # threshold | gate | split | stop_rule | metric | baseline | gray_zone
    text: <canonical text>     # may continue on indented lines
    op: ">="                   # optional — lets lab.tools.gates evaluate mechanically
    value: 0.02                # optional
    ```

`freeze` hashes each item and writes PREREG.lock.json (once). `verify` re-reads the blocks and
fails on any difference not covered by an approved amendment. `diff` prints differences.
`amend` records an approved amendment; it is refused once data exists for the phase it touches.

    python -m lab.tools.lock freeze  <thread> --by <person>
    python -m lab.tools.lock verify  <thread>
    python -m lab.tools.lock diff    <thread>
    python -m lab.tools.lock amend   <thread> --touches ID[,ID] --reason "…" --phase P3 --by <person>
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .common import (LabError, PHASES, PHASE_DIRS, git, main_wrapper, now, read_json,
                     resolve_thread, sha256_text, today, write_json)

SOURCES = ("PROPOSAL.md", "frozen_definitions.md")
BLOCK_RE = re.compile(r"^```lock[ \t]*\n(.*?)^```[ \t]*$", re.S | re.M)
KINDS = {"threshold", "gate", "split", "stop_rule", "metric", "baseline", "gray_zone"}


def parse_blocks(thread: Path) -> dict[str, dict]:
    """Return {id: item} for all lock blocks in the thread's source files."""
    items: dict[str, dict] = {}
    for name in SOURCES:
        path = thread / name
        if not path.exists():
            continue
        text = path.read_text()
        for m in BLOCK_RE.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            item = _parse_block(m.group(1), f"{name}#L{line_no}")
            if item["id"] in items:
                raise LabError(f"duplicate lock id {item['id']} ({item['source']} and {items[item['id']]['source']})")
            items[item["id"]] = item
    return items


def _parse_block(body: str, source: str) -> dict:
    fields: dict[str, str] = {}
    key = None
    for line in body.splitlines():
        if re.match(r"^[a-z_]+:", line):
            key, val = line.split(":", 1)
            fields[key] = val.strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()
    for req in ("id", "kind", "text"):
        if not fields.get(req):
            raise LabError(f"lock block at {source} is missing '{req}'")
    if fields["kind"] not in KINDS:
        raise LabError(f"lock block {fields['id']} has unknown kind '{fields['kind']}' (allowed: {sorted(KINDS)})")
    item = {"id": fields["id"], "kind": fields["kind"], "text": " ".join(fields["text"].split()),
            "source": source}
    for opt in ("op", "value"):
        if opt in fields:
            item[opt] = fields[opt].strip("\"'")
    item["sha256"] = sha256_text(_canonical(item))
    return item


def _canonical(item: dict) -> str:
    return "\n".join(f"{k}={item.get(k, '')}" for k in ("id", "kind", "text", "op", "value"))


def _root(items: list[dict]) -> str:
    return sha256_text("\n".join(sorted(f"{i['id']}:{i['sha256']}" for i in items)))


def freeze(thread: Path, by: str) -> dict:
    lock_path = thread / "PREREG.lock.json"
    if lock_path.exists():
        raise LabError("PREREG.lock.json already exists — the lock is frozen once; use `amend`")
    items = list(parse_blocks(thread).values())
    if not items:
        raise LabError("no ```lock blocks found in PROPOSAL.md / frozen_definitions.md")
    kinds = {i["kind"] for i in items}
    missing = {"threshold", "split", "stop_rule", "baseline"} - kinds
    if missing:
        raise LabError(f"cannot freeze: no lock block of kind {sorted(missing)}")
    lock = {"schema": "qml-lab/lock@1", "locked_at": now(), "locked_by": by,
            "git_commit": git(thread, "rev-parse", "HEAD"), "items": sorted(items, key=lambda i: i["id"]),
            "root_sha256": _root(items), "amendments": []}
    write_json(lock_path, lock)
    return lock


def _expected(lock: dict) -> dict[str, dict]:
    """Items as they should read now: frozen items, overridden by approved amendments in order."""
    cur = {i["id"]: i for i in lock["items"]}
    for a in lock.get("amendments", []):
        for it in a.get("new_items", []):
            cur[it["id"]] = it
    return cur


def diff(thread: Path) -> list[str]:
    lock_path = thread / "PREREG.lock.json"
    if not lock_path.exists():
        raise LabError("no PREREG.lock.json — nothing frozen yet")
    expected = _expected(read_json(lock_path))
    actual = parse_blocks(thread)
    out = []
    for i in sorted(set(expected) | set(actual)):
        if i not in actual:
            out.append(f"REMOVED  {i}  (was: {expected[i]['text'][:100]})")
        elif i not in expected:
            out.append(f"ADDED    {i}  ({actual[i]['source']}: {actual[i]['text'][:100]})")
        elif actual[i]["sha256"] != expected[i]["sha256"]:
            out.append(f"CHANGED  {i}  ({actual[i]['source']})\n  locked: {expected[i]['text']}\n  now:    {actual[i]['text']}")
    return out


def verify(thread: Path) -> None:
    changes = diff(thread)
    if changes:
        raise LabError("lock mismatch — thresholds/splits/stop rules changed without an approved amendment:\n"
                       + "\n".join(changes))


def first_data_time(thread: Path, phase: str) -> str | None:
    prov = thread / PHASE_DIRS[phase] / "provenance.json"
    if not prov.exists():
        return None
    entries = read_json(prov)
    times = [e.get("at") for e in entries if e.get("at")]
    return min(times) if times else None


def amend(thread: Path, touches: list[str], reason: str, phase: str, by: str) -> dict:
    lock_path = thread / "PREREG.lock.json"
    lock = read_json(lock_path)
    if phase not in PHASES:
        raise LabError(f"--phase must be one of {PHASES}")
    started = first_data_time(thread, phase)
    if started:
        raise LabError(f"amendment refused: {phase} already has data (first provenance record {started}). "
                       "Amendments must precede data access for the phase they touch.")
    actual = parse_blocks(thread)
    changed = {c.split()[1] for c in diff(thread)}
    if not changed:
        raise LabError("nothing to amend — the lock blocks match the lock")
    if set(touches) != changed:
        raise LabError(f"--touches {sorted(touches)} does not match the changed ids {sorted(changed)}")
    new_items = [actual[i] for i in touches if i in actual]
    n = len(lock["amendments"]) + 1
    expected = _expected(lock)
    for it in new_items:
        expected[it["id"]] = it
    for i in touches:
        if i not in actual:
            expected.pop(i, None)
    lock["amendments"].append({"n": n, "date": today(), "at": now(), "touches": touches, "reason": reason,
                               "precedes_data_access_for": phase, "approved_by": by,
                               "new_items": new_items, "new_root_sha256": _root(list(expected.values()))})
    write_json(lock_path, lock)
    return lock["amendments"][-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze"); f.add_argument("thread"); f.add_argument("--by", required=True)
    v = sub.add_parser("verify"); v.add_argument("thread")
    d = sub.add_parser("diff"); d.add_argument("thread")
    s = sub.add_parser("show"); s.add_argument("thread")
    m = sub.add_parser("amend"); m.add_argument("thread"); m.add_argument("--touches", required=True)
    m.add_argument("--reason", required=True); m.add_argument("--phase", required=True); m.add_argument("--by", required=True)
    a = ap.parse_args()
    thread = resolve_thread(a.thread)
    if a.cmd == "freeze":
        lock = freeze(thread, a.by)
        print(f"frozen: {len(lock['items'])} items, root {lock['root_sha256'][:12]}")
    elif a.cmd == "verify":
        verify(thread)
        print("lock OK")
    elif a.cmd == "diff":
        changes = diff(thread)
        print("\n".join(changes) if changes else "no differences")
    elif a.cmd == "show":
        for i in parse_blocks(thread).values():
            print(f"{i['id']:<28} {i['kind']:<10} {i['source']:<24} {i['text'][:80]}")
    elif a.cmd == "amend":
        am = amend(thread, [t.strip() for t in a.touches.split(",")], a.reason, a.phase, a.by)
        print(f"amendment {am['n']} recorded; new root {am['new_root_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
