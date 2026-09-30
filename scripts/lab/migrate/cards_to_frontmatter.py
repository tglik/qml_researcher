"""C11 step 4-5: fold Experiment Cards into VERDICT.md frontmatter and rewrite links.

For each `cards/experiments/<slug>.md`:
  * prepend entity frontmatter to the verdict it points at (`canonical_source`, remapped from
    `qml_experiments/experiments/...` to `experiments/...`), with
    `aliases: [cards/experiments/<slug>]` so any link we miss still resolves in Quartz;
  * append the card-only sections (Why It Matters, Caveats, sibling/related links) as a
    `## Graph links` section.
Then rewrite every `[[cards/experiments/<slug>...]]` and
`[[sources/reports/experiments/<slug>_<date>...]]` link across the vault to the verdict path,
and (with --delete) remove the cards and the mirrored source reports.

Legacy verdict values (CLOSED_NO, PROVISIONAL, ...) are kept as-is; mapping onto the D10
vocabulary happens during ledger seeding (C02), where N1-N5 are re-read.

    python cards_to_frontmatter.py --root ~/repos/qml_artifacts [--delete] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[\[(cards/experiments/([a-z0-9-]+)|sources/reports/experiments/([a-z0-9-]+)_\d{4}-\d{2}-\d{2})(\|[^\]]*)?\]\]")
KEEP = ["title", "program", "experiment_number", "topics", "verdict", "claim_status", "evaluated"]


def parse_fm(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        raise ValueError("no frontmatter")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.split(" #")[0].strip()
    return fm, text[m.end():]


def section(body: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |^---\s*$|\Z)", body, re.S | re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    root = a.root
    cards = sorted((root / "cards/experiments").glob("*.md"))

    slug_to_verdict: dict[str, str] = {}
    plans = []
    for card in cards:
        fm, body = parse_fm(card.read_text())
        slug = fm["id"]
        canon = fm["canonical_source"].removeprefix("qml_experiments/")
        verdict = root / canon
        if not verdict.exists():
            raise FileNotFoundError(f"{slug}: {verdict}")
        slug_to_verdict[slug] = canon.removesuffix(".md")
        plans.append((card, fm, body, verdict))

    def rewrite(text: str) -> str:
        def sub(m: re.Match, in_table: bool) -> str:
            slug = m.group(2) or m.group(3)
            target = slug_to_verdict.get(slug)
            if target is None:
                return m.group(0)
            label = m.group(4) or f"|{slug}"
            if in_table and not label.startswith("\\|"):
                label = "\\" + label  # a bare | would split the markdown table cell
            return f"[[{target}{label}]]"
        return "\n".join(LINK_RE.sub(lambda m: sub(m, line.lstrip().startswith("|")), line)
                         for line in text.split("\n"))

    for card, fm, body, verdict in plans:
        slug = fm["id"]
        vtext = verdict.read_text()
        if vtext.startswith("---\n"):
            print(f"skip (already has frontmatter): {verdict.relative_to(root)}")
            continue
        thread = verdict.parent.parent.name
        lines = ["---", f"id: {slug}", "type: experiment", f"aliases: [cards/experiments/{slug}]"]
        for k in KEEP:
            if k in fm:
                lines.append(f"{k}: {fm[k]}")
        lines += [f"thread: {thread}", "audit: legacy-human", "ledger: []", "---", ""]
        why, cav = section(body, "Why It Matters"), section(body, "Caveats")
        links = [l for l in section(body, "Links").splitlines()
                 if l.strip() and not l.lstrip("- ").startswith("Canonical source")]
        tail = ["", "---", "", "## Graph links", "",
                "*Carried over from the retired Experiment Card during the move into qml_artifacts (2026-09-30).*", ""]
        if why:
            tail += ["### Why it matters", "", why, ""]
        if cav:
            tail += ["### Caveats", "", cav, ""]
        if links:
            tail += ["### Related", "", *links, ""]
        new = "\n".join(lines) + vtext.rstrip("\n") + "\n" + rewrite("\n".join(tail))
        if not a.dry_run:
            verdict.write_text(new)
        print(f"frontmatter: {verdict.relative_to(root)}")

    # Rewrite links everywhere else (skip cards/mirrors about to be deleted, and .git).
    doomed = {p.resolve() for p in cards} | {p.resolve() for p in (root / "sources/reports/experiments").glob("*.md")}
    changed = 0
    for md in root.rglob("*.md"):
        if ".git" in md.parts or md.resolve() in doomed:
            continue
        t = md.read_text()
        n = rewrite(t)
        if n != t:
            changed += 1
            print(f"links: {md.relative_to(root)} ({len(LINK_RE.findall(t))} rewritten)")
            if not a.dry_run:
                md.write_text(n)
    print(f"files with rewritten links: {changed}")

    if a.delete and not a.dry_run:
        for p in doomed:
            p.unlink()
        print(f"deleted {len(doomed)} cards + mirrored reports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
