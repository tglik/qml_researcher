#!/usr/bin/env python3
"""Generate registered Claude Code subagents from the role sources, and list them in plugin.json.

Why: skills used to paste a role file into `Agent(subagent_type="claude", prompt=…)`. That works in
every runtime, but Claude Code then ignores the role's `model`, `tools` and `maxTurns`: every role
ran on the session model with every tool. Registered subagents carry those fields, so model
routing and tool limits take effect. The sources stay where they are and stay the only thing
people edit; this script renders them.

Sources → output (`.claude/agents/<name>.md`):
    lab/roles/<role>/ESSENCE.md + PROTOCOL.md              → <role>
    lab/roles/review-panel/personas/<p>.md (+ panel files) → panel-<p>
    .agents/skills/<skill>/agents/<a>.md                   → <a>   (name kept; frontmatter normalised)

    python scripts/gen_agents.py           # write
    python scripts/gen_agents.py --check   # exit 1 if any generated file is stale (used by tests)

Hermes and Codex keep the paste convention (.agents/shared/protocol.md); they read the sources.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".claude" / "agents"
PLUGIN = REPO / ".claude-plugin" / "plugin.json"
ROLES = REPO / "lab" / "roles"
SKILLS = REPO / ".agents" / "skills"

ALL_TOOLS = "Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch"
NO_WEB = "Read, Write, Edit, Glob, Grep, Bash"

# Model routing (token-cost review, Nov 2026): judgment stays on the session's frontier model
# (`inherit`); mechanical, schema-shaped work goes to Haiku; middle work to Sonnet. Aliases, never
# pinned ids, so a model release does not leave stale pins behind.
LAB_ROLE_CONFIG = {
    "lab-director":                  {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 60},
    "scoping-interviewer":           {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 40},
    "algorithm-analyst":             {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 60},
    "screen-analyst":                {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 60},
    "experiment-designer":           {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 80},
    "classical-competitor-champion": {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 120},
    "implementer":                   {"model": "inherit", "tools": NO_WEB, "maxTurns": 150},
    "verdict-writer":                {"model": "inherit", "tools": NO_WEB, "maxTurns": 40},
    "verdict-auditor":               {"model": "inherit", "tools": NO_WEB, "maxTurns": 80},
    "variant-generator":             {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 60},
    "lab-archivist":                 {"model": "haiku", "tools": NO_WEB, "maxTurns": 40},
    "explainer":                     {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 80},
    "explanation-checker":           {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 80},
    "review-panel":                  None,     # rendered per persona below
}
PANEL_CONFIG = {"model": "inherit", "tools": "Read, Write, Glob, Grep, WebSearch, WebFetch", "maxTurns": 40}
SKILL_AGENT_MODEL = {
    # mechanical extraction / formatting → haiku
    "card-writer": "haiku", "entity-extractor": "haiku", "index-updater": "haiku",
    "source-classifier": "haiku", "claim-extractor": "haiku",
    # search and graders → sonnet
    "literature-scout": "sonnet", "research-scientist": "sonnet",
    "skill-evaluator": "sonnet", "regression-checker": "sonnet",
}
LAB_METHOD_LINE = ("Before you start, Read `criteria/lab_method.md` (the shared lab rules every role "
                   "follows). Repo paths (criteria/, lab/, artifacts/, config/) are relative to the qml-researcher "
                   "root: the repository root in a clone, or the plugin folder your context names when "
                   "installed as a plugin.")


def _front(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, text[m.end():]


def _first_sentence(text: str, fallback: str) -> str:
    body = re.sub(r"^#.*$", "", text, flags=re.M)
    for para in re.split(r"\n\s*\n", body):
        para = " ".join(para.split())
        if para and not para.startswith(("|", "```", "-", "*Read", "**Read")):
            para = re.sub(r"^(Job|Purpose|Role)[.:]\s*", "", para.replace("**", "").replace("*", ""))
            s = re.split(r"(?<=[.!?])\s", para)[0]
            return s[:300]
    return fallback


def _render(name: str, description: str, model: str, tools: str, max_turns: int, body: str, sources: list[str]) -> str:
    desc = description.replace('"', "'")
    head = (f"---\nname: {name}\ndescription: \"{desc}\"\nmodel: {model}\ntools: {tools}\n"
            f"maxTurns: {max_turns}\n---\n\n")
    note = ("<!-- GENERATED by scripts/gen_agents.py from " + ", ".join(sources)
            + ". Edit those files and re-run the script; do not edit this file. -->\n\n")
    return head + note + body.strip() + "\n"


def build() -> dict[str, str]:
    files: dict[str, str] = {}
    for role_dir in sorted(p for p in ROLES.iterdir() if p.is_dir()):
        role = role_dir.name
        if role == "review-panel":
            continue
        cfg = LAB_ROLE_CONFIG.get(role) or {"model": "inherit", "tools": ALL_TOOLS, "maxTurns": 60}
        essence = (role_dir / "ESSENCE.md").read_text(encoding="utf-8")
        protocol = (role_dir / "PROTOCOL.md").read_text(encoding="utf-8")
        desc = f"QML Lab role {role}: " + _first_sentence(essence, f"the {role} role of the QML Lab.")
        body = f"{LAB_METHOD_LINE}\n\n{essence.strip()}\n\n---\n\n{protocol.strip()}"
        src = [f"lab/roles/{role}/ESSENCE.md", f"lab/roles/{role}/PROTOCOL.md"]
        files[role] = _render(role, desc, cfg["model"], cfg["tools"], cfg["maxTurns"], body, src)
    panel = ROLES / "review-panel"
    p_ess = (panel / "ESSENCE.md").read_text(encoding="utf-8")
    p_proto = (panel / "PROTOCOL.md").read_text(encoding="utf-8")
    for persona in sorted((panel / "personas").glob("*.md")):
        text = persona.read_text(encoding="utf-8")
        name = f"panel-{persona.stem}"
        desc = f"QML Lab review-panel persona {persona.stem}: " + _first_sentence(text, "one adversarial reviewer.")
        body = f"{LAB_METHOD_LINE}\n\n{text.strip()}\n\n---\n\n{p_ess.strip()}\n\n---\n\n{p_proto.strip()}"
        src = [f"lab/roles/review-panel/personas/{persona.name}", "lab/roles/review-panel/ESSENCE.md",
               "lab/roles/review-panel/PROTOCOL.md"]
        files[name] = _render(name, desc, PANEL_CONFIG["model"], PANEL_CONFIG["tools"], PANEL_CONFIG["maxTurns"], body, src)
    for agent in sorted(SKILLS.glob("*/agents/*.md")):
        meta, body = _front(agent.read_text(encoding="utf-8"))
        name = meta.get("name") or agent.stem
        if name in files:
            raise SystemExit(f"agent name collision: {name} ({agent})")
        model = SKILL_AGENT_MODEL.get(name, meta.get("model", "inherit"))
        if model.startswith("claude-"):
            model = "sonnet"
        if model == "opus":
            model = "inherit"
        tools = meta.get("tools") or ALL_TOOLS
        turns = int(meta.get("maxTurns", 40))
        desc = meta.get("description") or meta.get("role") or _first_sentence(body, name)
        src = [agent.relative_to(REPO).as_posix()]
        files[name] = _render(name, desc, model, tools, turns, body, src)
    return files


def plugin_manifest(names: list[str]) -> str:
    data = json.loads(PLUGIN.read_text(encoding="utf-8"))
    data["agents"] = [f"./.claude/agents/{n}.md" for n in names]
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    check = "--check" in sys.argv
    files = build()
    stale = []
    for name, text in files.items():
        path = OUT / f"{name}.md"
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(path.relative_to(REPO).as_posix())
            if not check:
                OUT.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    extra = [p for p in OUT.glob("*.md") if p.stem not in files] if OUT.exists() else []
    for p in extra:
        stale.append(p.relative_to(REPO).as_posix() + " (orphan)")
        if not check:
            p.unlink()
    manifest = plugin_manifest(sorted(files))
    if PLUGIN.read_text(encoding="utf-8") != manifest:
        stale.append(".claude-plugin/plugin.json (agents list)")
        if not check:
            PLUGIN.write_text(manifest, encoding="utf-8")
    if check and stale:
        print("stale generated agents — run python scripts/gen_agents.py:\n  " + "\n  ".join(stale))
        return 1
    print(f"{len(files)} agents {'checked' if check else 'written'}" + (f"; updated {len(stale)}" if stale and not check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
