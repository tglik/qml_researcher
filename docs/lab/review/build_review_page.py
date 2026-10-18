"""Build the lab essence review page (an Artifact) from the current essence files.

    python docs/lab/review/build_review_page.py <out.html>

Reads the files listed in ITEMS, the round-1 responses in round1_responses.json, and fills
page_template.html. Round-2 reviews are stored by the page in the `reviews2` collection; round-1
reviews stay read-only in `reviews`. For a later round, bump ROUND and the collection names.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ROUND = 2

G_START = "Start here"
G_ROLES = "The four judgment-heavy roles"
G_PANEL = "Algorithm analysis & review panel"
G_OTHER = "The other lab roles"
G_SKILL = "Skills (what each lab command is for)"

# (group, id, title, kind, path, focus for this round, round-1 id if renamed)
ITEMS = [
    (G_START, "criteria.lab_method", "Lab method (shared rules)", "Shared criteria — loaded by every role",
     "criteria/lab_method.md",
     "Rewritten from your round-1 comments. Check: is the Rule 1 checklist complete and correctly stated? "
     "Is the sign-free paragraph right? Do Rules 4 and 7 say what you meant? Are the advantage-type and "
     "N1–N5 tables the right bar?", None),
    (G_START, "lab.style", "How these files are written", "Writing rules for every role and skill file",
     "lab/STYLE.md",
     "New. The writing rules every file below now follows. Anything here that would make the files "
     "worse for a researcher to read?", None),
    (G_ROLES, "role.screen-analyst", "Screen analyst", "Role", "lab/roles/screen-analyst/ESSENCE.md",
     "Built from Adi's rewrite. Is the order of questions right (loading and readout, then bottleneck, "
     "then competitor)? Is there a kill it would get wrong?", None),
    (G_ROLES, "role.classical-competitor-champion", "Classical competitor champion", "Role (renamed)",
     "lab/roles/classical-competitor-champion/ESSENCE.md",
     "Renamed from the classical-twin champion. Does it now look for the use case's state of the art "
     "first, and use the whole Rule 1 checklist?", "role.classical-twin-champion"),
    (G_ROLES, "role.experiment-designer", "Experiment designer", "Role",
     "lab/roles/experiment-designer/ESSENCE.md",
     "Now starts from P0 and budgets both sides. Would these principles produce a design you would "
     "freeze?", None),
    (G_ROLES, "role.verdict-auditor", "Verdict auditor", "Role", "lab/roles/verdict-auditor/ESSENCE.md",
     "Is over-killing the right fear? Would it have caught a missing size-matched control and an "
     "inadequate baseline?", None),
    (G_PANEL, "role.algorithm-analyst", "Algorithm analyst (Adi's Stage 0)", "Role",
     "lab/roles/algorithm-analyst/ESSENCE.md",
     "Adi — is anything from your Stage 0 protocol lost or distorted? Is its relation to the screen "
     "analyst now clear?", None),
    (G_PANEL, "role.review-panel", "Review panel (shared stance)", "Role", "lab/roles/review-panel/ESSENCE.md",
     "Six reviewers now. Is the blocking rule right?", None),
    (G_PANEL, "persona.methodologist", "Panel · methodologist", "Panel persona",
     "lab/roles/review-panel/personas/methodologist.md", "Are these the right reference standards?", None),
    (G_PANEL, "persona.dequantization-theorist", "Panel · dequantization theorist", "Panel persona",
     "lab/roles/review-panel/personas/dequantization-theorist.md", "Does the sign-free check say the right thing?", None),
    (G_PANEL, "persona.hardware-realist", "Panel · hardware realist", "Panel persona",
     "lab/roles/review-panel/personas/hardware-realist.md",
     "Are the modality capabilities right? Is the six-month staleness rule right?", None),
    (G_PANEL, "persona.baseline-champion", "Panel · baseline champion", "Panel persona",
     "lab/roles/review-panel/personas/baseline-champion.md", "Not reviewed in round 1. Anything missing?", None),
    (G_PANEL, "persona.value-translator", "Panel · value translator", "Panel persona",
     "lab/roles/review-panel/personas/value-translator.md",
     "Meir — does it use the value metrics the way you intended?", None),
    (G_PANEL, "persona.mathematical-critic", "Panel · mathematical critic", "Panel persona (new)",
     "lab/roles/review-panel/personas/mathematical-critic.md",
     "New, from Meir's AI Peer Reviewer role. Is the scope right, and does it overlap the others too much?", None),
    (G_PANEL, "criteria.hardware_roadmaps", "Hardware roadmaps (reference)", "Reference data — sourced, dated",
     "criteria/hardware_roadmaps.md",
     "New, filled from web sources on 2026-10-18. Wrong numbers, missing vendors, or capabilities you "
     "know better (Q-Factor especially)?", None),
    (G_OTHER, "role.scoping-interviewer", "Scoping interviewer", "Role", "lab/roles/scoping-interviewer/ESSENCE.md",
     "Not reviewed in round 1. Are the five pieces of a hypothesis the right ones?", None),
    (G_OTHER, "role.implementer", "Implementer", "Role", "lab/roles/implementer/ESSENCE.md",
     "Not reviewed in round 1. Meir — you may fill this slot; does it match how you would work?", None),
    (G_OTHER, "role.verdict-writer", "Verdict writer", "Role", "lab/roles/verdict-writer/ESSENCE.md",
     "Not reviewed in round 1. Is the wording discipline right?", None),
    (G_OTHER, "role.lab-director", "Lab director", "Role", "lab/roles/lab-director/ESSENCE.md",
     "Not reviewed in round 1. Are the escalation triggers the right ones?", None),
    (G_OTHER, "role.variant-generator", "Variant generator", "Role", "lab/roles/variant-generator/ESSENCE.md",
     "Adi — your Creative alternatives finder spec, applied here. Is it what you meant?", None),
    (G_OTHER, "role.lab-archivist", "Lab archivist", "Role", "lab/roles/lab-archivist/ESSENCE.md",
     "Meir — your research memory role is the new lookup mode. Is it what you meant?", None),
]
SKILLS = [
    ("qml-lab", "entry point"), ("qml-intake", "turn an idea into a hypothesis"),
    ("qml-screen", "kill on paper"), ("qml-prereg", "pre-registration"),
    ("qml-review-panel", "adversarial review"), ("qml-run", "run one phase"),
    ("qml-verdict", "write the verdict"), ("qml-audit", "audit the verdict"),
    ("qml-variants", "variants after a verdict"), ("qml-promote", "record and learn"),
]
for name, what in SKILLS:
    ITEMS.append((G_SKILL, f"skill.{name}", f"/{name}", f"Skill — {what}", f".agents/skills/{name}/ESSENCE.md",
                  "Not reviewed in round 1. Are these the right judgment calls for this step?", None))


def build(out: Path) -> None:
    responses = json.loads((HERE / "round1_responses.json").read_text(encoding="utf-8"))
    items = []
    for group, iid, title, kind, path, focus, r1_id in ITEMS:
        items.append({"group": group, "id": iid, "title": title, "kind": kind, "path": path,
                      "markdown": (REPO / path).read_text(encoding="utf-8"), "focus": focus,
                      "r1_id": r1_id or iid, "r1_response": responses.get(iid, "")})
    missing = set(responses) - {i["id"] for i in items}
    if missing:
        raise SystemExit(f"responses for unknown items: {sorted(missing)}")
    data = json.dumps({"round": ROUND, "items": items}, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "page_template.html").read_text(encoding="utf-8").replace("__DATA__", data)
    out.write_text(html, encoding="utf-8")
    print(f"{out}: {len(items)} items, {len(html) // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    build(Path(sys.argv[1]))
