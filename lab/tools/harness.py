"""Run one tool-free, schema-constrained prompt through a headless agent harness.

Harnesses: Claude Code (`claude -p`) and Codex (`codex exec`). Each call runs in a fresh empty
temporary directory, without user settings, MCP servers, plugins or session persistence, and
returns the harness's own event stream so isolation can be verified after the fact:

- Claude Code: `--tools ""` removes every built-in tool. The only tool left is the internal
  StructuredOutput tool used for `--json-schema`; anything else in the init event or in a
  tool_use block is a violation.
- Codex: there is no switch that removes the shell tool. The read-only sandbox still permits
  reads, so isolation is detection, not prevention: any item other than an agent message,
  reasoning or harness error is reported as a violation.

Binary lookup: $CLAUDE_BIN / $CODEX_BIN, then PATH, then the VS Code extension / Codex app
install locations.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HARNESSES = ("claude-code", "codex")
_ENV = {"claude-code": "CLAUDE_BIN", "codex": "CODEX_BIN"}
_NAME = {"claude-code": "claude", "codex": "codex"}
_FALLBACKS = {
    "claude-code": [".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude.exe",
                    ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude",
                    ".local/bin/claude"],
    "codex": [".codex/.sandbox-bin/codex.exe", ".codex/.sandbox-bin/codex"],
}
CLAUDE_ALLOWED_TOOLS = ["StructuredOutput"]
CODEX_ALLOWED_ITEMS = {"agent_message", "reasoning", "error"}


class HarnessError(ValueError):
    pass


def find_binary(harness: str) -> Path:
    if harness not in HARNESSES:
        raise HarnessError(f"unknown harness: {harness}")
    if os.environ.get(_ENV[harness]):
        path = Path(os.environ[_ENV[harness]])
    elif shutil.which(_NAME[harness]):
        path = Path(shutil.which(_NAME[harness]))
    else:
        found = [p for pattern in _FALLBACKS[harness] for p in Path.home().glob(pattern)]
        if not found:
            raise HarnessError(f"{_NAME[harness]} not found; set {_ENV[harness]} to its executable")
        path = max(found, key=lambda p: p.stat().st_mtime)
    if not path.is_file():
        raise HarnessError(f"{_ENV[harness]} does not point to a file: {path}")
    return path


def version(binary: Path) -> str:
    proc = subprocess.run([str(binary), "--version"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)
    return proc.stdout.strip() or proc.stderr.strip()


def _events(stdout: str) -> list[dict]:
    events = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def parse_claude(events: list[dict]) -> dict:
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    violations = []
    if init is None:
        violations.append("no_init_event")
    else:
        if init.get("tools") != CLAUDE_ALLOWED_TOOLS:
            violations.append("tools_exposed:" + ",".join(init.get("tools") or []))
        if init.get("mcp_servers"):
            violations.append("mcp_servers_exposed")
    for event in events:
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []):
            if block.get("type") == "tool_use" and block.get("name") not in CLAUDE_ALLOWED_TOOLS:
                violations.append("tool_use:" + str(block.get("name")))
    completed = bool(result) and result.get("subtype") == "success" and not result.get("is_error")
    answer = None
    if completed:
        structured = result.get("structured_output")
        answer = json.dumps(structured, ensure_ascii=False) if structured is not None else result.get("result")
    return {
        "completed": completed, "answer_text": answer, "violations": violations,
        "resolved_model": (init or {}).get("model"),
        "usage": {k: (result or {}).get(k) for k in ("usage", "modelUsage", "total_cost_usd", "num_turns")},
        "error": None if completed else str((result or {}).get("result") or (result or {}).get("subtype") or "no result event"),
        "warnings": [],
    }


def parse_codex(events: list[dict], last_message: str | None) -> dict:
    violations, warnings, messages = [], [], []
    usage, failure = None, None
    for event in events:
        kind = event.get("type")
        if kind in ("item.started", "item.updated", "item.completed"):
            item = event.get("item", {})
            item_type = item.get("type")
            if item_type not in CODEX_ALLOWED_ITEMS:
                violations.append("tool_use:" + str(item_type))
            elif item_type == "error" and kind == "item.completed":
                warnings.append(str(item.get("message")))
            elif item_type == "agent_message" and kind == "item.completed":
                messages.append(item.get("text"))
        elif kind == "turn.completed":
            usage = event.get("usage")
        elif kind == "turn.failed":
            failure = str(event.get("error", {}).get("message"))
        elif kind == "error" and failure is None:
            failure = str(event.get("message"))
    completed = usage is not None and failure is None
    answer = last_message if last_message else (messages[-1] if messages else None)
    return {
        "completed": completed, "answer_text": answer if completed else None,
        "violations": sorted(set(violations)), "resolved_model": None,
        "usage": {"usage": usage}, "error": None if completed else (failure or "no turn.completed event"),
        "warnings": warnings,
    }


def run(harness: str, prompt: str, schema: dict, model: str, effort: str | None = None,
        timeout: int = 600) -> dict:
    """One fresh session, prompt on stdin, nothing persisted. Raises HarnessError on transport failure."""
    binary = find_binary(harness)
    with tempfile.TemporaryDirectory(prefix="eval-harness-") as temporary:
        work, io = Path(temporary) / "work", Path(temporary) / "io"
        work.mkdir()
        io.mkdir()
        if harness == "claude-code":
            argv = [str(binary), "-p", "--model", model, "--tools", "", "--strict-mcp-config",
                    "--setting-sources", "", "--no-session-persistence",
                    "--output-format", "stream-json", "--verbose", "--json-schema", json.dumps(schema)]
            if effort:
                argv += ["--effort", effort]
        else:
            (io / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
            argv = [str(binary), "exec", "-m", model, "--ignore-user-config", "--ignore-rules",
                    "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-C", str(work),
                    "--json", "--output-schema", str(io / "schema.json"),
                    "-o", str(io / "last_message.txt")]
            if effort:
                argv += ["-c", f'model_reasoning_effort="{effort}"']
            argv.append("-")
        try:
            proc = subprocess.run(argv, input=prompt, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise HarnessError(f"{harness} timed out after {timeout}s; no retry was attempted") from None
        events = _events(proc.stdout)
        if harness == "claude-code":
            parsed = parse_claude(events)
        else:
            last = io / "last_message.txt"
            parsed = parse_codex(events, last.read_text(encoding="utf-8") if last.exists() else None)
    if proc.returncode != 0 and parsed["completed"]:
        parsed.update(completed=False, answer_text=None, error=f"exit code {proc.returncode}")
    parsed.update(harness=harness, binary=str(binary), returncode=proc.returncode,
                  argv=[a if a != json.dumps(schema) else "<answer-schema>" for a in argv],
                  stdout=proc.stdout, stderr=proc.stderr)
    return parsed
