"""Write <phase>/results/gates.md from locked thresholds and measured values — numbers only.

Programs frozen with a scorer (lab.tools.scorer): this tool runs the frozen scorer in a separate
process, writes <phase>/results/measured.json itself (stamped with the scorer's hash) and records
each number in provenance. Nobody hand-writes measured.json; the implementer only produces raw/.

Legacy programs (lock without a scorer) — the implementer writes <phase>/results/measured.json:

    {"P1.G4.threshold": {"value": 0.031, "ci": [0.02, 0.04], "provenance_id": "P1.G4.gap"},
     "P1.G5.adequacy":  {"value": 0.19, "provenance_id": "P1.G5.mae", "pass": false}}

For each lock item of kind threshold/gate/baseline whose id starts with the phase (or that is
listed in measured.json): if the lock item has `op` and `value`, pass/fail is computed here;
otherwise measured.json must give an explicit "pass" (recorded as manual). No measurement ⇒ BLOCKED.

    python -m lab.tools.gates <thread> P1
"""
from __future__ import annotations

import argparse
import json
import operator
from pathlib import Path

from . import scorer as scorer_mod
from .common import PHASE_DIRS, LabError, main_wrapper, read_json, resolve_thread, sha256_text, write_json
from .lock import _expected, expected_scorer, verify as lock_verify

OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt, "==": operator.eq}


def evaluate(thread: Path, phase: str) -> list[dict]:
    lock_path = thread / "PREREG.lock.json"
    if not lock_path.exists():
        raise LabError("no PREREG.lock.json — gates are evaluated only against a frozen lock")
    lock = read_json(lock_path)
    items = _expected(lock)
    measured_path = thread / PHASE_DIRS[phase] / "results" / "measured.json"
    if expected_scorer(lock) is not None:
        measured = _score(thread, phase, set(items), measured_path)
    else:
        measured = read_json(measured_path) if measured_path.exists() else {}
    measured = {k: v for k, v in measured.items() if not k.startswith("_")}
    unknown = set(measured) - set(items)
    if unknown:
        raise LabError(f"measured.json has ids not in the lock: {sorted(unknown)} — gates cannot be invented after freeze")
    rows = []
    for gid, it in sorted(items.items()):
        if it["kind"] not in ("threshold", "gate", "baseline"):
            continue
        if not (gid.startswith(phase + ".") or gid in measured):
            continue
        m = measured.get(gid)
        row = {"id": gid, "threshold": f"{it.get('op', '')} {it.get('value', '')}".strip() or it["text"][:60],
               "measured": "—", "result": "BLOCKED", "provenance": "—", "how": ""}
        if m is not None:
            ci = f" [{m['ci'][0]}, {m['ci'][1]}]" if m.get("ci") else ""
            row.update(measured=f"{m['value']}{ci}", provenance=m.get("provenance_id", "—"))
            if "op" in it and "value" in it and isinstance(m.get("value"), (int, float)):
                ok = OPS[it["op"]](float(m["value"]), float(it["value"]))
                row.update(result="PASS" if ok else "FAIL", how="computed")
            elif "pass" in m:
                row.update(result="PASS" if m["pass"] else "FAIL", how="manual")
            else:
                raise LabError(f"{gid}: lock has no op/value, so measured.json must give an explicit 'pass'")
        rows.append(row)
    return rows


def _score(thread: Path, phase: str, lock_ids: set[str], measured_path: Path) -> dict:
    """Verify the lock (scorer included), run the frozen scorer, write measured.json, record provenance."""
    from . import provenance
    lock_verify(thread)
    res = scorer_mod.run(thread, phase, allowed_ids=lock_ids)
    measured = dict(res["values"])
    prov_path = thread / PHASE_DIRS[phase] / "provenance.json"
    existing = read_json(prov_path) if prov_path.exists() else []
    to_record = []
    for gid, m in sorted(measured.items()):
        value = m.get("value", m.get("pass"))
        base = f"scorer:{gid}"
        same = [e for e in existing if e["number_id"].split("#")[0] == base]
        if same and same[-1]["value"] == value and same[-1].get("file_sha256"):
            m["provenance_id"] = same[-1]["number_id"]
            continue
        m["provenance_id"] = base if not same else f"{base}#{len(same) + 1}"
        to_record.append((m["provenance_id"], value, m.get("ci")))
    # Provenance points at an immutable snapshot named by its content; measured.json is the working copy.
    payload = {"_scorer": res["stamp"], **measured}
    snap = measured_path.parent / "scored" / f"{sha256_text(json.dumps(payload, sort_keys=True))[:16]}.json"
    snap.parent.mkdir(parents=True, exist_ok=True)
    if not snap.exists():
        write_json(snap, payload)
    write_json(measured_path, payload)
    rel = snap.relative_to(thread).as_posix()
    for pid, value, ci in to_record:
        provenance.record(thread, phase, id=pid, value=value, file=rel, ci=ci, python=res["stamp"]["python"],
                          command=f"python -m lab.tools.gates <thread> {phase} (frozen scorer "
                                  f"{res['stamp']['root_sha256'][:12]})")
    return measured


def write(thread: Path, phase: str) -> Path:
    rows = evaluate(thread, phase)
    out = thread / PHASE_DIRS[phase] / "results" / "gates.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Gates — {phase}", "",
             "Numbers and pass/fail only. No interpretation — that is /qml-verdict's job. Written by "
             "`python -m lab.tools.gates`, never by hand.", "",
             "| Gate (lock id) | Measured | Threshold | Pass/fail | Provenance id |", "|---|---|---|---|---|"]
    for r in rows:
        tag = " (manual)" if r["how"] == "manual" else ""
        lines.append(f"| {r['id']} | {r['measured']} | {r['threshold']} | {r['result']}{tag} | {r['provenance']} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thread"); ap.add_argument("phase", choices=list(PHASE_DIRS))
    a = ap.parse_args()
    out = write(resolve_thread(a.thread), a.phase)
    print(out.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    main_wrapper(main)
