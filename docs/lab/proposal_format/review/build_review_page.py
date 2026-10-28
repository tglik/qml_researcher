"""Build the exp 18 rewrite review page (an Artifact) from the current drafts.

    python docs/lab/proposal_format/review/build_review_page.py <out.html>

Each item shows a current document and, where one exists, the original it replaces (the frozen
exp 18 HYPOTHESIS.md, the matching section of its PROPOSAL.md, or the legacy template). Reviews
are stored by the page in the `exp18_review` collection, one document per reviewer.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
EXP18 = REPO.parent / "qml_artifacts" / "experiments" / "materials_configuration_space" / "18_config_space_features"
DRAFTS = "docs/lab/proposal_format/exp18"

G_START = "Start here"
G_EXP18 = "Exp 18, rewritten"
G_EXAMPLE = "A second example"
G_TEMPLATES = "The new templates (every program)"

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)


def proposal_section(*phases: str) -> str:
    """The frozen proposal's text for the given phase headings ("P0", "P1", …), in order."""
    text = (EXP18 / "PROPOSAL.md").read_text(encoding="utf-8")
    heads = [m for m in re.finditer(r"^#{2,3} .*$", text, re.M)]
    out = []
    for ph in phases:
        start = next(m for m in heads if m.group(0).startswith(f"### {ph} "))
        nxt = next((m for m in heads if m.start() > start.start()), None)
        out.append(text[start.start(): nxt.start() if nxt else len(text)])
    return "\n".join(out)


def proposal_head() -> str:
    text = (EXP18 / "PROPOSAL.md").read_text(encoding="utf-8")
    end = text.index("\n## 2. Metrics")
    return FM_RE.sub("", text[:end])


def clean(text: str, keep_frontmatter: bool = False) -> str:
    m = FM_RE.match(text)
    if m:
        text = text[m.end():]
        if keep_frontmatter:
            text = "```yaml\n" + m.group(1) + "\n```\n\n" + text
    return COMMENT_RE.sub(lambda c: "\n> **Guidance for the writer:** " + " ".join(c.group(1).split()) + "\n", text)


def read(path: str) -> str:
    return (REPO / path).read_text(encoding="utf-8")


def fenced_header(text: str) -> str:
    """A card file opening with bare `key: value` lines: show those lines as a code block."""
    head, _, rest = text.partition("\n\n")
    return "```yaml\n" + head + "\n```\n\n" + rest


def n_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


PROPOSAL_LINES = n_lines(EXP18 / "PROPOSAL.md")

# (group, id, title, kind, path, focus, before text, before label)
ITEMS = [
    (G_START, "overview", "What changed, and what we would like from you", "Overview",
     "docs/lab/proposal_format/review/overview.md",
     "Read this first. Is the diagnosis right? Is anything else making the lab's documents hard to read?",
     None, None),
    (G_EXP18, "hypothesis", "Hypothesis", "Hypothesis (rewritten)",
     "docs/lab/hypothesis_format/exp18_HYPOTHESIS_v1.md",
     "After reading it, could you explain the claim, the algorithm and why it is built this way to someone "
     "else? Meir: is the chemistry background right? Is the first known risk (the labels are DFT) stated fairly?",
     clean((EXP18 / "HYPOTHESIS.md").read_text(encoding="utf-8")), "the frozen HYPOTHESIS.md (121 lines)"),
    (G_EXP18, "plan", "Plan", "Plan (rewritten from PROPOSAL.md)", f"{DRAFTS}/PLAN.md",
     "Can you get the whole program from this in five minutes? Meir: the four questions under "
     "“Before spending” need your decision: UMA access, cutting E2 to its pilot, running E3 before E2, "
     "and the tuning-cost estimate.",
     proposal_head(), f"the first part of PROPOSAL.md (revision notes and the hypothesis map; {PROPOSAL_LINES:,} lines in total)"),
    (G_EXP18, "E1", "E1: baseline and headroom", "Experiment doc (rewritten)",
     f"{DRAFTS}/experiments/E1_baseline_and_headroom.md",
     "Running now. Do the decision rules match what you expect E1 to decide? Is the status (no UMA "
     "access, tuning cost) right?",
     proposal_section("P1"), "PROPOSAL.md, section P1"),
    (G_EXP18, "E2", "E2: classical hardness", "Experiment doc (rewritten)",
     f"{DRAFTS}/experiments/E2_classical_hardness.md",
     "Are the classical solvers and the wall criterion described correctly? Should E2 be cut to its pilot "
     "(see the plan)?",
     proposal_section("P2"), "PROPOSAL.md, section P2"),
    (G_EXP18, "E3", "E3: feature gain", "Experiment doc (rewritten)",
     f"{DRAFTS}/experiments/E3_feature_gain.md",
     "The core experiment. Are the four pass conditions and the five follow-up checks clear? Does "
     "“Why these thresholds” justify each number?",
     proposal_section("P3"), "PROPOSAL.md, section P3"),
    (G_EXP18, "E4", "E4: precision and noise", "Experiment doc (rewritten)",
     f"{DRAFTS}/experiments/E4_precision_and_noise.md",
     "Is the noise check described correctly? Is it clear why it matters for E3 and E5?",
     proposal_section("P4"), "PROPOSAL.md, section P4"),
    (G_EXP18, "E5", "E5: cost crossover", "Experiment doc (rewritten)",
     f"{DRAFTS}/experiments/E5_cost_crossover.md",
     "Is the cost comparison clear? Are the three hardware scenarios and the classical front right?",
     proposal_section("P0", "P5"), "PROPOSAL.md, sections P0 and P5"),
    (G_EXAMPLE, "qml06", "qml-06 hypothesis (power of data)", "Hypothesis (new format, validation paper)",
     "docs/lab/hypothesis_format/qml-06_HYPOTHESIS_v2.md",
     "A second example, on Huang et al. 2021 (projected quantum kernels). Adi: does the “why” section "
     "explain the method the way you would want from a PhD student? Is anything wrong?",
     fenced_header(read("tests/fixtures/paper_replay/cards_v2/qml-06/input.md")), "the input the lab received (algorithm and task)"),
    (G_TEMPLATES, "tpl.hypothesis", "Hypothesis template", "Template",
     "artifacts/lab/templates/HYPOTHESIS.md",
     "Every new program's hypothesis will follow this. Missing sections? Sections we do not need?",
     clean(read("artifacts/lab/templates/legacy/HYPOTHESIS.md"), True), "the previous template"),
    (G_TEMPLATES, "tpl.plan", "Plan template", "Template",
     "artifacts/lab/templates/PROPOSAL.md",
     "The plan for every new program. Is this the right overview?",
     clean(read("artifacts/lab/templates/legacy/PROPOSAL.md"), True), "the previous proposal template"),
    (G_TEMPLATES, "tpl.experiment", "Experiment template", "Template (new)",
     "artifacts/lab/templates/EXPERIMENT.md",
     "One document per experiment. Is anything an implementer or a reviewer needs missing?",
     None, None),
]


def build(out: Path) -> None:
    items = []
    for group, iid, title, kind, path, focus, before, before_label in ITEMS:
        keep_fm = kind.startswith("Template")
        items.append({"group": group, "id": iid, "title": title, "kind": kind, "path": path,
                      "markdown": clean(read(path), keep_fm), "focus": focus,
                      "before": before, "before_label": before_label})
    data = json.dumps({"items": items}, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "page_template.html").read_text(encoding="utf-8").replace("__DATA__", data)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"{out}: {len(items)} items, {len(html) // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    build(Path(sys.argv[1]))
