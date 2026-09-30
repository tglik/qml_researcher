"""Validate lab files: JSON against artifacts/lab/schemas, markdown artifacts against their templates.

    python -m lab.tools.validate state       <thread>/STATE.json
    python -m lab.tools.validate lock        <thread>/PREREG.lock.json
    python -m lab.tools.validate provenance  <thread>/<phase>/provenance.json
    python -m lab.tools.validate entity      <thread>/VERDICT.md        # experiment entity frontmatter
    python -m lab.tools.validate artifact    <thread>/SCREEN.md         # required sections present
    python -m lab.tools.validate thread      <thread>                   # everything that exists
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .common import (LEGACY_VERDICTS, SCHEMAS, TEMPLATES, VERDICTS, LabError, main_wrapper,
                     parse_list, read_frontmatter, read_json, resolve_thread)

_TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float),
          "boolean": bool, "null": type(None)}


def check_schema(value, schema: dict, path: str = "$") -> list[str]:
    """A small JSON-schema subset: type, enum, required, properties, additionalProperties, items."""
    errs: list[str] = []
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: {value!r} not in {schema['enum']}"]
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        ok = any(isinstance(value, _TYPES[t]) and not (t in ("integer", "number") and isinstance(value, bool))
                 for t in types)
        if not ok:
            return [f"{path}: expected {types}, got {type(value).__name__}"]
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        for k, v in value.items():
            if k in props:
                errs += check_schema(v, props[k], f"{path}.{k}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errs += check_schema(v, schema["additionalProperties"], f"{path}.{k}")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += check_schema(v, schema["items"], f"{path}[{i}]")
    return errs


def validate_json(path: Path, schema_name: str) -> list[str]:
    schema = read_json(SCHEMAS / f"{schema_name}.schema.json")
    return check_schema(read_json(path), schema)


ENTITY_REQUIRED = ("id", "type", "title", "program", "experiment_number", "topics", "verdict",
                   "claim_status", "evaluated", "thread", "audit", "ledger")


def validate_entity(path: Path) -> list[str]:
    fm, _ = read_frontmatter(path)
    if not fm:
        return [f"{path}: no frontmatter"]
    errs = [f"{path}: missing '{k}'" for k in ENTITY_REQUIRED if k not in fm]
    if fm.get("type") and fm["type"] != "experiment":
        errs.append(f"{path}: type must be 'experiment'")
    v = fm.get("verdict")
    if v and v not in VERDICTS + LEGACY_VERDICTS:
        errs.append(f"{path}: verdict {v!r} not in {VERDICTS} (or legacy {LEGACY_VERDICTS})")
    if fm.get("audit") and fm["audit"] not in ("pending", "CONFIRMED", "OVERTURNED", "INSUFFICIENT", "legacy-human"):
        errs.append(f"{path}: audit {fm['audit']!r} invalid")
    if fm.get("claim_status") and fm["claim_status"] not in ("speculative", "plausible", "observed", "refuted"):
        errs.append(f"{path}: claim_status {fm['claim_status']!r} exceeds the single-experiment ceiling 'observed'")
    if "topics" in fm and not parse_list(fm["topics"]):
        errs.append(f"{path}: topics is empty")
    return errs


HEADING_RE = re.compile(r"^(#{2,3}) (.+?)\s*$", re.M)


def required_headings(template: Path) -> list[str]:
    """Level-2 headings of a template, placeholders stripped to a stable prefix."""
    out = []
    for level, title in HEADING_RE.findall(template.read_text()):
        if level != "##":
            continue
        stable = re.split(r"[{(—]", title)[0].strip()
        if stable:
            out.append(stable)
    return out


def validate_artifact(path: Path) -> list[str]:
    template = TEMPLATES / path.name
    if path.parent.name == "results" and path.name == "gates.md":
        template = TEMPLATES / "gates.md"
    if not template.exists():
        return []
    text = path.read_text()
    have = [re.split(r"[{(—]", t)[0].strip() for lvl, t in HEADING_RE.findall(text) if lvl == "##"]
    return [f"{path.name}: missing section '## {h}'" for h in required_headings(template)
            if not any(x.startswith(h) for x in have)]


def validate_thread(thread: Path) -> list[str]:
    errs: list[str] = []
    if (thread / "STATE.json").exists():
        errs += validate_json(thread / "STATE.json", "state")
    if (thread / "PREREG.lock.json").exists():
        errs += validate_json(thread / "PREREG.lock.json", "lock")
    for prov in thread.glob("P*/provenance.json"):
        errs += validate_json(prov, "provenance")
    for name in ("HYPOTHESIS.md", "ALGORITHM_ANALYSIS.md", "SCREEN.md", "PROPOSAL.md",
                 "VERDICT.md", "AUDIT.md", "VARIANTS.md"):
        if (thread / name).exists():
            errs += validate_artifact(thread / name)
    for rep in thread.glob("P*/PHASE_REPORT.md"):
        errs += validate_artifact(rep)
    if (thread / "VERDICT.md").exists():
        errs += validate_entity(thread / "VERDICT.md")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["state", "lock", "provenance", "entity", "artifact", "thread"])
    ap.add_argument("path")
    a = ap.parse_args()
    p = resolve_thread(a.path) if a.kind == "thread" else Path(a.path)
    if a.kind in ("state", "lock", "provenance"):
        errs = validate_json(p, a.kind)
    elif a.kind == "entity":
        errs = validate_entity(p)
    elif a.kind == "artifact":
        errs = validate_artifact(p)
    else:
        errs = validate_thread(p)
    if errs:
        raise LabError(f"{len(errs)} problem(s):\n  " + "\n  ".join(errs))
    print("valid")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
