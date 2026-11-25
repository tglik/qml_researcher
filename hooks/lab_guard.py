#!/usr/bin/env python3
"""PreToolUse hook: enforce the lab's write and read rules before a tool runs, not after.

`lab.tools.guard` checks after a phase that protected files were not touched. That is detection:
a broken run and a person to adjudicate. This hook makes the same rules hold at the moment of the
tool call, for the main session and for every subagent. guard.py stays as the second check.

Rules, for any path inside a program thread (a folder that holds STATE.json):

  Always denied to Edit/Write and to shell writes (only `python -m lab.tools.*` writes these):
      STATE.json · PREREG.lock.json · splits.json · P*/provenance.json · P*/results/gates.md ·
      P*/results/scored/*
  Denied once the lock is frozen:
      scorer/**                    the frozen scorer (amend it through /qml-lab amend)
      P*/results/measured.json     when the lock has a scorer (lab.tools.gates writes it)
  Asks a person once the lock is frozen (a post-freeze edit is an amendment):
      PROPOSAL.md · frozen_definitions.md · 00_operating_point.md · experiments/*.md
  Denied while stage is `run`:
      VERDICT.md · AUDIT.md (writes) · scorer/heldout/** (reads too: held-out labels)

For the study workspace ({output_root}/workspace/, C16), a study is a folder under studies/ that
holds state.json, and the log is workspace/log/:

  Always denied to Edit/Write and shell writes (only `python -m lab.tools.workspace` writes these):
      studies/*/state.json · ledger.jsonl · objections.jsonl · bundle.lock.json · log/*
  Denied once the study is locked, unless the author posted a correction after the last lock or
  amendment and no number is in the ledger yet (then `workspace amend` records the change):
      studies/*/STUDY.md
  Denied once the study is released: every file in the study folder.

Shell commands are checked by the paths they mention; a command that mentions a protected path and
looks like a write (redirect, tee, sed -i, mv, cp, rm, touch, truncate, open(...,'w'), write_text)
is treated as a write. This is a tripwire against casual tampering, not a sandbox.

A person can switch it off for one Claude Code session with LAB_GUARD_OFF=1 in the environment
that launches Claude Code. Agents cannot set that variable for the hook process.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

ALWAYS = {"STATE.json", "PREREG.lock.json", "splits.json"}
AMEND = {"PROPOSAL.md", "frozen_definitions.md", "00_operating_point.md"}
RUN_ONLY = {"VERDICT.md", "AUDIT.md"}
PHASE_RE = re.compile(r"^P\d_[^/]+/")
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
SHELL_WRITE = re.compile(
    r"(?<![<>&0-9])>{1,2}(?!&)|\btee\b|\bsed\s+(-[a-zA-Z]*i|--in-place)|\bmv\b|\bcp\b|\brm\b|\btouch\b|"
    r"\btruncate\b|\bchmod\b|\bln\b|\bdd\b|write_text|write_bytes|open\([^)]*['\"][wax]\+?b?['\"]|"
    r"\bgit\s+(checkout|restore|reset|stash|clean)\b")
LAB_TOOL = re.compile(r"^\s*(cd\s+\S+\s*&&\s*)?(\S*python3?(\.exe)?)\s+-m\s+lab\.tools\.[a-z_]+\b")


def find_thread(path: Path) -> Path | None:
    for parent in [path, *path.parents][:8]:
        if (parent / "STATE.json").is_file():
            return parent
    return None


def thread_info(thread: Path) -> dict:
    info = {"stage": None, "frozen": False, "scorer": False}
    try:
        info["stage"] = json.loads((thread / "STATE.json").read_text(encoding="utf-8")).get("stage")
    except (OSError, json.JSONDecodeError):
        pass
    lock = thread / "PREREG.lock.json"
    if lock.is_file():
        info["frozen"] = True
        try:
            data = json.loads(lock.read_text(encoding="utf-8"))
            current = data.get("scorer")
            for a in data.get("amendments", []):
                if "new_scorer" in a:
                    current = a["new_scorer"]
            info["scorer"] = current is not None
        except (OSError, json.JSONDecodeError):
            pass
    return info


def judge(rel: str, info: dict, write: bool) -> tuple[str, str] | None:
    """Return (decision, reason) for one path relative to its thread, or None to allow."""
    name = rel.split("/")[-1]
    if rel.startswith("scorer/heldout/") and info["stage"] == "run":
        return "deny", ("scorer/heldout/ holds held-out labels; nobody reads it during a run phase. "
                        "The frozen scorer reads it when lab.tools.gates runs.")
    if not write:
        return None
    if rel in ALWAYS or re.match(r"^P\d_[^/]+/provenance\.json$", rel) or re.match(
            r"^P\d_[^/]+/results/(gates\.md|scored/)", rel):
        return "deny", f"{rel} is written only by `python -m lab.tools.*`, never by hand."
    if info["frozen"] and rel.startswith("scorer/"):
        return "deny", ("the scorer is frozen in PREREG.lock.json. A change is an amendment: "
                        "/qml-lab amend, approved by a person who is not the designer, before the phase has data.")
    if info["frozen"] and info["scorer"] and re.match(r"^P\d_[^/]+/results/measured\.json$", rel):
        return "deny", "measured.json is written by lab.tools.gates from the frozen scorer, not by hand."
    if info["frozen"] and (rel in AMEND or re.match(r"^experiments/[^/]+\.md$", rel)):
        return "ask", (f"{rel} is part of the frozen pre-registration. Editing it now is an amendment: approve only "
                       "if a person other than the designer agreed, then record it with /qml-lab amend.")
    if info["stage"] == "run" and rel in RUN_ONLY:
        return "deny", f"{name} cannot be written while a phase is running."
    return None


STUDY_TOOL_FILES = {"state.json", "ledger.jsonl", "objections.jsonl", "bundle.lock.json"}


def find_study(path: Path) -> Path | None:
    for parent in [path, *path.parents][:6]:
        if (parent / "state.json").is_file() and parent.parent.name == "studies" \
                and parent.parent.parent.name == "workspace":
            return parent
    return None


def find_log(path: Path) -> bool:
    return any(p.name == "log" and p.parent.name == "workspace" for p in [path, *path.parents][:3])


def _read_fm(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def judge_study(study: Path, rel: str, write: bool) -> tuple[str, str] | None:
    if not write:
        return None
    try:
        st = json.loads((study / "state.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        st = {}
    status = st.get("status")
    if rel in STUDY_TOOL_FILES:
        return "deny", f"{rel} is written only by `python -m lab.tools.workspace`, never by hand."
    if status == "released":
        return "deny", (f"study {study.name} is released and frozen. Post a correction with "
                        "`lab.tools.workspace post correction`, or start a new study.")
    if status == "locked" and rel == "STUDY.md":
        try:
            lock = json.loads((study / "bundle.lock.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            lock = {}
        last = max([lock.get("locked_at", "")] + [a.get("at", "") for a in lock.get("amendments", [])])
        log = study.parent.parent / "log"
        corrected = any(_read_fm(p).get("at", "") > last
                        for p in log.glob(f"*__{study.name}__correction__*.md")) if log.is_dir() else False
        ledger = study / "ledger.jsonl"
        if ledger.is_file() and ledger.read_text(encoding="utf-8").strip():
            return "deny", "the ledger already holds numbers; a plan change now is a new study, not an amendment."
        if not corrected:
            return "deny", ("STUDY.md is locked. Post a correction first (`lab.tools.workspace post correction`), "
                            "edit, then record it with `lab.tools.workspace amend`.")
    return None


def candidate_paths(tool: str, tin: dict, cwd: Path) -> list[Path]:
    raw: list[str] = []
    if tool in WRITE_TOOLS or tool == "Read":
        raw.append(tin.get("file_path") or tin.get("notebook_path") or "")
    elif tool == "Grep":
        raw.append(tin.get("path") or "")
    elif tool == "Glob":
        base = tin.get("path") or ""
        raw.append(str(Path(base) / (tin.get("pattern") or "")) if base else (tin.get("pattern") or ""))
    elif tool == "Bash":
        cmd = tin.get("command") or ""
        try:
            tokens = shlex.split(cmd, posix=True)
        except ValueError:
            tokens = cmd.split()
        for t in tokens:
            for part in re.split(r"[=:,;|&<>()]", t):
                if "/" in part or part.split("/")[-1] in ALWAYS | AMEND | RUN_ONLY | {"measured.json", "gates.md"}:
                    raw.append(part)
    out = []
    for r in raw:
        r = r.strip().strip("'\"")
        if not r:
            continue
        p = Path(os.path.expanduser(r))
        out.append(p if p.is_absolute() else (cwd / p))
    return out


def decide(event: dict) -> tuple[str, str] | None:
    tool = event.get("tool_name", "")
    tin = event.get("tool_input") or {}
    cwd = Path(event.get("cwd") or os.getcwd())
    if tool not in WRITE_TOOLS | READ_TOOLS | {"Bash"}:
        return None
    if tool == "Bash":
        cmd = tin.get("command") or ""
        if LAB_TOOL.match(cmd) and not re.search(r"[;&|]\s*\S", LAB_TOOL.sub("", cmd, count=1)):
            return None                      # a single lab tool call: the tool enforces its own rules
        write = bool(SHELL_WRITE.search(cmd))
    else:
        write = tool in WRITE_TOOLS
    worst = None
    for path in candidate_paths(tool, tin, cwd):
        try:
            resolved = path.resolve()
        except OSError:
            continue
        base = resolved if resolved.is_dir() else resolved.parent
        if write and find_log(base):
            verdict = ("deny", "the workspace log is append-only and written only by "
                       "`python -m lab.tools.workspace post`.")
            worst = verdict
            break
        study = find_study(base)
        if study is not None:
            try:
                verdict = judge_study(study, resolved.relative_to(study).as_posix(), write)
            except ValueError:
                verdict = None
            if verdict and (worst is None or verdict[0] == "deny"):
                worst = verdict
                if verdict[0] == "deny":
                    break
            continue
        thread = find_thread(base)
        if thread is None:
            continue
        try:
            rel = resolved.relative_to(thread).as_posix()
        except ValueError:
            continue
        verdict = judge(rel, thread_info(thread), write)
        if verdict and (worst is None or verdict[0] == "deny"):
            worst = verdict
            if verdict[0] == "deny":
                break
    return worst


def main() -> int:
    if os.environ.get("LAB_GUARD_OFF") == "1":
        return 0
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    verdict = decide(event)
    if verdict:
        decision, reason = verdict
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                                 "permissionDecision": decision,
                                                 "permissionDecisionReason": f"lab guard: {reason}"}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
