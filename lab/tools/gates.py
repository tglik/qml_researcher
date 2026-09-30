"""Write <phase>/results/gates.md from locked thresholds and measured values — numbers only.

The implementer writes <phase>/results/measured.json:

    {"P1.G4.threshold": {"value": 0.031, "ci": [0.02, 0.04], "provenance_id": "P1.G4.gap"},
     "P1.G5.adequacy":  {"value": 0.19, "provenance_id": "P1.G5.mae", "pass": false}}

For each lock item of kind threshold/gate/baseline whose id starts with the phase (or that is
listed in measured.json): if the lock item has `op` and `value`, pass/fail is computed here;
otherwise measured.json must give an explicit "pass" (recorded as manual). No measurement ⇒ BLOCKED.

    python -m lab.tools.gates <thread> P1
"""
from __future__ import annotations

import argparse
import operator
from pathlib import Path

from .common import PHASE_DIRS, LabError, main_wrapper, read_json, resolve_thread
from .lock import _expected

OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt, "==": operator.eq}


def evaluate(thread: Path, phase: str) -> list[dict]:
    lock_path = thread / "PREREG.lock.json"
    if not lock_path.exists():
        raise LabError("no PREREG.lock.json — gates are evaluated only against a frozen lock")
    items = _expected(read_json(lock_path))
    measured_path = thread / PHASE_DIRS[phase] / "results" / "measured.json"
    measured = read_json(measured_path) if measured_path.exists() else {}
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
    out.write_text("\n".join(lines) + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thread"); ap.add_argument("phase", choices=list(PHASE_DIRS))
    a = ap.parse_args()
    out = write(resolve_thread(a.thread), a.phase)
    print(out.read_text())
    return 0


if __name__ == "__main__":
    main_wrapper(main)
