#!/usr/bin/env python3
"""SessionStart / SubagentStart hook: make the plugin work outside a clone of qml_researcher.

Skills and agents name repo files by relative path (`criteria/lab_method.md`,
`python -m lab.tools.gates`, `config/workspace.json`). In a clone those resolve against the
project root. Installed as a plugin, the files live under ${CLAUDE_PLUGIN_ROOT} instead, so this
hook:

  * SessionStart: appends to $CLAUDE_ENV_FILE so every Bash command (main session and subagents)
    gets QML_ROOT, PYTHONPATH (so `python -m lab.tools.*` imports from the plugin) and, when the
    user set the plugin option, LAB_OUTPUT_ROOT (read by lab.tools.common.output_root);
  * both events: tells the model where the files are and which output_root to use, because
    Read/Glob paths are not resolved by the shell.

In a clone (plugin root == project dir) it does nothing. Stdlib only; never blocks.
"""
from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path

DIRS = "criteria/, config/, lab/, artifacts/, scripts/, hooks/, .agents/"


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        event = {}
    name = event.get("hook_event_name", "SessionStart")
    root = os.environ.get("CLAUDE_PLUGIN_ROOT") or str(Path(__file__).resolve().parents[1])
    project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
    out = os.environ.get("CLAUDE_PLUGIN_OPTION_OUTPUT_ROOT", "").strip()
    try:
        in_clone = Path(root).resolve() == Path(project).resolve()
    except OSError:
        in_clone = False
    if in_clone and not out:
        return 0

    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if name == "SessionStart" and env_file:
        q = shlex.quote
        lines = [f"export QML_ROOT={q(root)}"]
        if not in_clone:
            lines.append(f'export PYTHONPATH={q(root)}"${{PYTHONPATH:+:$PYTHONPATH}}"')
        if out:
            lines.append(f"export LAB_OUTPUT_ROOT={q(str(Path(out).expanduser()))}")
        with open(env_file, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    parts = []
    if not in_clone:
        parts.append(
            f"qml-researcher plugin: its files are under {root}. When a qml-researcher skill or agent "
            f"names a path under {DIRS} by relative path, read it under {root} (for example "
            f"{root}/criteria/lab_method.md), not under the current project. `python -m lab.tools.<tool>` "
            f"works from any directory (PYTHONPATH is set). Before judging any QML claim or direction, read "
            f"{root}/criteria/qml_domain.md (the team's five QML criteria and priorities; the repo's "
            f"CLAUDE.md is not loaded for plugins). Never write into {root}: it is replaced on plugin update.")
    if out:
        parts.append(f"qml-researcher output_root is {out} (plugin option; it overrides "
                     f"config/workspace.json). All skill outputs and lab programs go there.")
    elif not in_clone:
        parts.append("qml-researcher output_root is not configured. Before running a skill that writes "
                     "outputs, ask the user to set the plugin option output_root (in /config or /plugin) "
                     "to their qml_artifacts clone; do not use the path in config/workspace.json, which "
                     "belongs to one machine.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": " ".join(parts)}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a context hook must never break a session
        print(f"qml_env hook: {e}", file=sys.stderr)
        sys.exit(0)
