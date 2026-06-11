#!/usr/bin/env python3
"""Install Hermes-compatible qml_researcher skills into the labs profile.

Source of truth:
  <repo>/.agents/skills/<skill>/SKILL.md
  <repo>/.agents/skills/<skill>/agents/*.md
  <repo>/.agents/skills/<skill>/openai.yaml  # optional CLI metadata stub
  <repo>/criteria, <repo>/artifacts, <repo>/config

Destination:
  /Users/tsahi/.hermes/profiles/labs/skills/qml-researcher/<skill>/

The repo's canonical skill location is .agents/skills. .claude/skills is only a
Claude Code discovery bridge made of symlinks. This installer therefore reads
from .agents/skills, generates Hermes-valid SKILL.md wrappers/copies, converts
subagent role prompts into references/agents/*.md, copies optional openai.yaml
metadata into references/openai.yaml, and symlinks shared criteria/artifacts/config
back to the repo so edits there update immediately.

Re-run this script after editing .agents/skills or agent prompts.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / ".agents" / "skills"
DEST_ROOT = Path("/Users/tsahi/.hermes/profiles/labs/skills/qml-researcher")

TOOL_MAP = {
    "Agent": "Hermes delegate_task tool. Inject the converted role prompt from references/agents/<agent>.md into the child context.",
    "Read": "Hermes read_file tool.",
    "Write": "Hermes write_file tool.",
    "Edit": "Hermes patch tool.",
    "Glob": "Hermes search_files(target='files') tool.",
    "Grep": "Hermes search_files(target='content') tool.",
    "WebSearch": "Hermes web/search toolset or browser when dynamic interaction is required.",
    "WebFetch": "Hermes web extraction/browser tools; fetch full text and cite exact retrieved text.",
    "AskUserQuestion": "Hermes clarify tool for multiple-choice/confirmation gates; for free-form scoping questions ask one question in prose and stop the turn until the user replies. Do not proceed past explicit gates without a user answer.",
    "Bash": "Hermes terminal tool.",
}

SKILL_DESCRIPTIONS = {
    "fetch-arxiv": "Use when fetching an arXiv paper by ID, URL, or title for QML workflows or general research; returns structured metadata, abstract, intro text, venue tier, and partial-fetch status.",
    "qml-paper-review": "Use when critically reviewing a QML paper for credibility, novelty, evidence quality, dequantization risk, baselines, hardware fit, and a falsifiable verdict.",
    "qml-deep-research": "Use when doing systematic QML literature research or fact-checking: scope the question, sweep sources, apply QML criteria, challenge claims, audit evidence, and write a final report.",
    "qml-daily-scout": "Use when running a recurring or ad-hoc QML research scout for new papers, technical posts, publications, or news; filters recent items for QML relevance, novelty, and evidence risk.",
}

RELATED = {
    "fetch-arxiv": ["qml-paper-review", "qml-deep-research", "qml-daily-scout", "arxiv"],
    "qml-paper-review": ["fetch-arxiv", "qml-deep-research", "qml-daily-scout"],
    "qml-deep-research": ["fetch-arxiv", "qml-paper-review", "qml-daily-scout"],
    "qml-daily-scout": ["fetch-arxiv", "qml-paper-review", "qml-deep-research", "arxiv"],
}


def split_fm(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def scalar_from_fm(fm: str, key: str, default: str = "") -> str:
    """Conservative frontmatter scalar parser.

    Some source skills intentionally contain Claude/OpenAI metadata that is not
    strict YAML for Hermes (for example unquoted colons in list entries). Avoid
    feeding the whole source frontmatter to yaml.safe_load; parse only the fields
    needed to generate fresh Hermes frontmatter.
    """
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"^{re.escape(key)}\s*:", line):
            val = line.split(":", 1)[1].strip()
            if val in ("|", ">"):
                block: list[str] = []
                for nxt in lines[i + 1 :]:
                    if nxt and not nxt.startswith(" ") and re.match(r"^[A-Za-z0-9_-]+\s*:", nxt):
                        break
                    block.append(nxt.strip())
                return "\n".join(x for x in block if x).strip()
            return val.strip("\"'")
    return default


def list_from_fm(fm: str, key: str) -> list[str]:
    lines = fm.splitlines()
    out: list[str] = []
    in_key = False
    for line in lines:
        if re.match(rf"^{re.escape(key)}\s*:", line):
            in_key = True
            continue
        if in_key:
            if line.startswith("  - "):
                out.append(line[4:].strip().strip("\"'"))
            elif line and not line.startswith(" "):
                break
    return out


def parse_tools(fm: str) -> list[str]:
    allowed = list_from_fm(fm, "allowed-tools")
    if allowed:
        return allowed
    tools = scalar_from_fm(fm, "tools")
    if tools:
        return [t.strip() for t in tools.strip('"').split(",") if t.strip()]
    return []


def q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def canonicalize_body_paths(body: str) -> str:
    """Make generated Hermes copy point at the canonical .agents tree.

    The repository keeps .claude/skills symlinks for Claude Code compatibility,
    but .agents/skills is now source of truth. Generated Hermes skills should not
    teach future agents that .claude is canonical.
    """
    return body.replace(".claude/skills", ".agents/skills")


def converted_skill(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    fm, body = split_fm(text)
    body = canonicalize_body_paths(body)
    name = scalar_from_fm(fm, "name", skill_dir.name)
    version = scalar_from_fm(fm, "version", "1.0.0")
    desc = SKILL_DESCRIPTIONS.get(name) or scalar_from_fm(fm, "description")[:900]
    triggers = list_from_fm(fm, "triggers")
    allowed = parse_tools(fm)
    agent_dir = skill_dir / "agents"
    agent_names = sorted(p.stem for p in agent_dir.glob("*.md")) if agent_dir.exists() else []
    has_openai_yaml = (skill_dir / "openai.yaml").exists()

    tags = ["qml", "research", "hermes-converted", "agent-neutral-source"]
    if "paper" in name:
        tags.append("paper-review")
    if "deep" in name:
        tags.append("literature-review")
    if "scout" in name:
        tags.extend(["daily-briefing", "research-scout"])
    if "arxiv" in name:
        tags.append("arxiv")

    header = [
        "---",
        f"name: {name}",
        f"description: {q(desc)}",
        f"version: {version}",
        "author: QML Researcher repo; converted for Hermes Agent labs profile",
        "license: MIT",
        "platforms: [macos, linux, windows]",
        "metadata:",
        "  hermes:",
        "    tags: [" + ", ".join(tags) + "]",
        "    related_skills: [" + ", ".join(RELATED.get(name, [])) + "]",
        f"    source_repo: {q(str(REPO))}",
        f"    source_skill: {q(str(skill_dir.relative_to(REPO)))}",
        "    source_layout: agent-neutral-.agents",
        "    converted_from: agent-neutral-skill",
    ]
    if triggers:
        header += ["    source_triggers:"] + [f"      - {q(t)}" for t in triggers]
    if allowed:
        header += ["    source_allowed_tools:"] + [f"      - {q(t)}" for t in allowed]
    if agent_names:
        header += ["    converted_agents:"] + [f"      - {a}" for a in agent_names]
    if has_openai_yaml:
        header += ["    source_openai_yaml: references/openai.yaml"]
    header.append("---")

    notes = [
        f"# {name}\n",
        "## Hermes Conversion Contract\n",
        f"This Hermes skill is generated from `{skill_dir.relative_to(REPO)}/SKILL.md` in the qml_researcher repo. Treat `.agents/skills/` as the canonical source of truth; `.claude/skills/` is only a symlink bridge for Claude Code.\n",
        f"Canonical repo root:\n\n`{REPO}`\n",
        "Before executing the workflow, read these linked references when relevant:\n",
        "- `references/shared/protocol.md` — agent spawn convention, Hermes I/O policy, progress update format, Word export instructions, session memory format, and completion message format. Read once during Setup before spawning any agents.\n",
        "- `references/criteria/qml_domain.md` — authoritative QML criteria; do not rely on stale inline copies.\n",
        "- `references/config/workspace.json` — output root configuration.\n",
        "- `references/artifacts/` — schemas for paper cards, triage logs, evidence records, and other outputs.\n",
    ]
    if agent_names:
        notes.append("- `references/agents/*.md` — converted Hermes subagent role prompts for this skill.\n")
    if has_openai_yaml:
        notes.append("- `references/openai.yaml` — optional OpenAI/Codex CLI metadata from the source skill. It is preserved for auditability; Hermes does not consume it directly.\n")
    notes.append("\nHermes tool mapping for the source skill metadata:\n")
    for tool in allowed:
        notes.append(f"- `{tool}` → {TOOL_MAP.get(tool, 'Use the closest Hermes tool; if none exists, state the limitation explicitly.')}\n")
    if agent_names:
        notes.append("\nSubagent conversion rule: spawn these roles with `delegate_task`; paste the relevant `references/agents/<name>.md` content into the child context. The agent that generates a claim must not be the agent that verifies it.\n")
        notes.append("\nConverted subagents:\n")
        for agent in agent_names:
            notes.append(f"- `{agent}` → `references/agents/{agent}.md`\n")
    notes.extend([
        f"\nOutput path rule: resolve `output_root` from `references/config/workspace.json`; relative paths are relative to `{REPO}`.\n",
        "\n## Original Source Skill Metadata\n\n```yaml\n" + fm.strip() + "\n```\n",
        "\n## Original Workflow Body, with Hermes Notes Above Taking Precedence\n",
    ])
    return "\n".join(header) + "\n\n" + "".join(notes) + "\n" + body.lstrip()


def converted_agent(agent_path: Path) -> str:
    text = agent_path.read_text(encoding="utf-8")
    fm, body = split_fm(text)
    body = canonicalize_body_paths(body)
    name = scalar_from_fm(fm, "name", agent_path.stem)
    desc = scalar_from_fm(fm, "description", "")
    tools = parse_tools(fm)
    model = scalar_from_fm(fm, "model", "")
    max_turns = scalar_from_fm(fm, "maxTurns", "")

    lines = [
        f"# Hermes Subagent Role: {name}",
        "",
        "## Converted Source Agent Metadata",
        "",
        "```yaml",
        fm.strip(),
        "```",
        "",
        "## Hermes Execution Contract",
        "",
        f"- Role description: {desc}",
        "- Invoke via Hermes `delegate_task`, not Claude Code `Agent`.",
        "- Provide this whole role file plus the phase input, source files, workspace paths, and QML criteria in the child context.",
        "- Leaf subagents cannot ask the user questions; the parent must resolve ambiguity first.",
        "- Return a verifiable artifact path or structured report. The parent must read back/check artifacts before trusting side effects.",
        "- Do not expand scope beyond the phase contract.",
        "- Preserve the QML epistemic ladder: speculative → plausible → observed → supported → strong → published / refuted.",
        "- Never strengthen a claim beyond the evidence provided.",
        "",
    ]
    if tools:
        lines.append("Hermes tool mapping:")
        for tool in tools:
            lines.append(f"- `{tool}` → {TOOL_MAP.get(tool, 'closest Hermes equivalent')}")
        lines.append("")
    if model:
        lines.append(f"Original model hint: `{model}`. In Hermes, use the current model unless the orchestrator explicitly chooses a stronger model for this delegate_task.")
    if max_turns:
        lines.append(f"Original maxTurns hint: `{max_turns}`. In Hermes, keep the child task bounded and require a concise final summary.")
    lines += ["", "## Original Agent Prompt", "", body.lstrip()]
    return "\n".join(lines)


def install() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing source skills directory: {SRC}")
    if DEST_ROOT.exists() or DEST_ROOT.is_symlink():
        if DEST_ROOT.is_symlink() or DEST_ROOT.is_file():
            DEST_ROOT.unlink()
        else:
            shutil.rmtree(DEST_ROOT)
    DEST_ROOT.mkdir(parents=True)

    installed = 0
    for skill_dir in sorted(p for p in SRC.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        out = DEST_ROOT / skill_dir.name
        (out / "references").mkdir(parents=True)
        (out / "SKILL.md").write_text(converted_skill(skill_dir), encoding="utf-8")

        if (skill_dir / "agents").exists():
            (out / "references" / "agents").mkdir()
            for agent in sorted((skill_dir / "agents").glob("*.md")):
                (out / "references" / "agents" / agent.name).write_text(converted_agent(agent), encoding="utf-8")

        if (skill_dir / "openai.yaml").exists():
            shutil.copy2(skill_dir / "openai.yaml", out / "references" / "openai.yaml")

        for subdir in ["criteria", "artifacts", "config"]:
            target = REPO / subdir
            link = out / "references" / subdir
            if target.exists():
                os.symlink(target, link, target_is_directory=True)

        # shared infrastructure lives under .agents/shared, not repo root
        shared_target = REPO / ".agents" / "shared"
        if shared_target.exists():
            os.symlink(shared_target, out / "references" / "shared", target_is_directory=True)
        installed += 1

    print(f"Installed {installed} Hermes qml_researcher skills from {SRC} into {DEST_ROOT}")


if __name__ == "__main__":
    install()
