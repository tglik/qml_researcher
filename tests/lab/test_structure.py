"""Structure tests: the essence/protocol split is enforced, not just intended.

- every lab role has ESSENCE.md and PROTOCOL.md; every panel persona has an essence file
- every lab skill has ESSENCE.md and SKILL.md, and SKILL.md links its ESSENCE
- ESSENCE files contain no mechanics: no file paths, placeholders, tool commands or numbered steps
- every role a SKILL.md spawns exists
- templates exist for every artifact the protocols name
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROLES = REPO / "lab" / "roles"
SKILLS = REPO / ".agents" / "skills"
LAB_SKILLS = ["qml-lab", "qml-intake", "qml-screen", "qml-prereg", "qml-review-panel", "qml-run",
              "qml-verdict", "qml-audit", "qml-variants", "qml-promote"]
PERSONAS = ["methodologist", "dequantization-theorist", "hardware-realist", "baseline-champion", "value-translator",
            "mathematical-critic"]

# Mechanics that must not appear in an ESSENCE file.
MECHANICS = [
    (re.compile(r"\{[A-Z_]+\}"), "placeholder like {THREAD}"),
    (re.compile(r"python -m|lab\.tools"), "tool command"),
    (re.compile(r"\b[\w./-]+\.(md|json|py|yaml)\b"), "file name/path"),
    (re.compile(r"^\s*\d+\.\s", re.M), "numbered step"),
    (re.compile(r"`/qml-[a-z-]+ [a-z<]"), "skill command with arguments"),
]


def essence_violations(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.relative_to(REPO)}: {why}: {m.group(0)!r}"
            for rx, why in MECHANICS for m in rx.finditer(text)]


class StructureTest(unittest.TestCase):
    def test_roles_have_both_files(self):
        roles = [d for d in ROLES.iterdir() if d.is_dir()]
        self.assertGreaterEqual(len(roles), 12)
        for d in roles:
            self.assertTrue((d / "ESSENCE.md").exists(), f"{d.name} missing ESSENCE.md")
            self.assertTrue((d / "PROTOCOL.md").exists(), f"{d.name} missing PROTOCOL.md")
        for p in PERSONAS:
            self.assertTrue((ROLES / "review-panel" / "personas" / f"{p}.md").exists(), p)

    def test_skills_have_both_files_and_link_essence(self):
        for s in LAB_SKILLS:
            self.assertTrue((SKILLS / s / "ESSENCE.md").exists(), f"{s} missing ESSENCE.md")
            skill = (SKILLS / s / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("[ESSENCE.md](ESSENCE.md)", skill, f"{s}/SKILL.md does not link its essence")
            self.assertTrue((REPO / ".claude" / "skills" / s).exists(), f"{s} not linked in .claude/skills")

    def test_essences_contain_no_mechanics(self):
        files = list(ROLES.glob("*/ESSENCE.md")) + list((ROLES / "review-panel" / "personas").glob("*.md")) \
            + [SKILLS / s / "ESSENCE.md" for s in LAB_SKILLS]
        problems = [v for f in files for v in essence_violations(f)]
        self.assertEqual(problems, [], "mechanics found in essence files:\n  " + "\n  ".join(problems))

    def test_spawned_roles_exist(self):
        for s in LAB_SKILLS:
            for role in re.findall(r"lab/roles/([a-z-]+)/", (SKILLS / s / "SKILL.md").read_text(encoding="utf-8")):
                self.assertTrue((ROLES / role).is_dir(), f"{s} references missing role {role}")

    def test_templates_exist_for_named_artifacts(self):
        names = set()
        for f in list(ROLES.glob("*/PROTOCOL.md")) + [SKILLS / s / "SKILL.md" for s in LAB_SKILLS]:
            names |= set(re.findall(r"artifacts/lab/templates/([A-Za-z_]+\.md)", f.read_text(encoding="utf-8")))
        for n in names:
            self.assertTrue((REPO / "artifacts" / "lab" / "templates" / n).exists(), f"template {n} missing")


if __name__ == "__main__":
    unittest.main()


class HarnessWiringTest(unittest.TestCase):
    """The registered agents, plugin manifest and guard hook stay in step with their sources."""

    def test_generated_agents_are_current(self):
        import subprocess, sys
        r = subprocess.run([sys.executable, str(REPO / "scripts" / "gen_agents.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_skill_frontmatter_is_valid_yaml(self):
        # An invalid frontmatter loads the skill with no description, so it never auto-routes
        # (found by the routes-paper-review eval: six skills were invisible to routing).
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml not installed")
        for skill in sorted((REPO / ".agents" / "skills").glob("*/SKILL.md")):
            text = skill.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---", text, re.S)
            self.assertIsNotNone(m, f"{skill}: no frontmatter")
            try:
                meta = yaml.safe_load(m.group(1))
            except yaml.YAMLError as e:
                self.fail(f"{skill.relative_to(REPO)}: invalid YAML frontmatter: {e}")
            self.assertIsInstance(meta.get("description"), str, skill)
            self.assertEqual(meta.get("name"), skill.parent.name, skill)

    def test_every_lab_role_and_persona_is_registered(self):
        agents = {p.stem for p in (REPO / ".claude" / "agents").glob("*.md")}
        for role in (REPO / "lab" / "roles").iterdir():
            if role.is_dir() and role.name != "review-panel":
                self.assertIn(role.name, agents)
        for persona in (REPO / "lab" / "roles" / "review-panel" / "personas").glob("*.md"):
            self.assertIn(f"panel-{persona.stem}", agents)

    def test_no_pinned_model_ids_in_agents(self):
        for p in (REPO / ".claude" / "agents").glob("*.md"):
            m = re.search(r"^model:\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
            self.assertIn(m.group(1), {"inherit", "opus", "sonnet", "haiku"}, p.name)

    def test_guard_hook_is_wired_in_settings_and_plugin(self):
        import json
        for f in (REPO / ".claude" / "settings.json", REPO / "hooks" / "hooks.json"):
            hooks = json.loads(f.read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
            self.assertTrue(any("lab_guard.py" in h["command"] for e in hooks for h in e["hooks"]), f)
