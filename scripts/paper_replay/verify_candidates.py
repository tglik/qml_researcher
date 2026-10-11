"""Verify paper-replay candidates against arXiv, OpenAlex and Semantic Scholar.

For every original/adjudicator pair: resolve IDs and titles, fetch field-normalized citation impact,
check that the adjudicator cites the original (with citing passages), and flag author overlap.
Optionally mine each original's citing papers for challenge language to nominate new adjudicators.

Outputs are evaluator-only (they contain outcomes). Nothing here labels a claim: tiers and
outcomes stay curator hypotheses until a human reads the citing passages.

    python scripts/paper_replay/verify_candidates.py [--mine] [--only qml-01,ml-02]
Set S2_API_KEY to avoid Semantic Scholar's shared rate limit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts/paper_replay"
UA = "qml-researcher-paper-replay/0.1"
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
CHALLENGE = re.compile(
    r"(fail(s|ed)? to (reproduce|replicate)|could not (reproduce|replicate)|did not reproduce|"
    r"classically simulab|classical(ly)? simulat|dequantiz|spoof|contrary to|contradict|"
    r"retract|overestimat|not (robust|significant)|disappear|vanish|outperform(s|ed)? .{0,40}(proposed|original)|"
    r"(simple|tuned|well-tuned|strong) baseline|reality check|revisit)", re.I)


def get(url: str, s2: bool = False) -> bytes:
    headers = {"User-Agent": UA}
    if s2 and os.environ.get("S2_API_KEY"):
        headers["x-api-key"] = os.environ["S2_API_KEY"]
    delay = 2.0
    for attempt in range(7):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                data = r.read()
            time.sleep(1.1 if s2 else 0.2)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(url) from None
            if e.code in (429, 500, 502, 503, 504) and attempt < 6:
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < 6:
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise
    raise RuntimeError(url)


def jget(url: str, s2: bool = False):
    return json.loads(get(url, s2))


def person(name: str) -> str:
    """First initial + surname; surname alone conflates common names (Chen, Li, Zhang, He)."""
    parts = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower().split()
    if not parts:
        return ""
    return parts[0][0] + "." + re.sub(r"[^a-z]", "", parts[-1])


def arxiv_batch(ids: list[str]) -> dict:
    found = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(chunk), "max_results": len(chunk)})
        root = ET.fromstring(get(url))
        for entry in root.findall("a:entry", ATOM):
            full = entry.findtext("a:id", "", ATOM).rsplit("/abs/", 1)[-1]
            base = re.sub(r"v\d+$", "", full)
            found[base] = {
                "title": " ".join(entry.findtext("a:title", "", ATOM).split()),
                "published": entry.findtext("a:published", "", ATOM)[:10],
                "updated": entry.findtext("a:updated", "", ATOM)[:10],
                "latest_version": full[len(base):] or "v1",
                "authors": [a.findtext("a:name", "", ATOM) for a in entry.findall("a:author", ATOM)],
                "journal_doi": entry.findtext("arxiv:doi", None, ATOM),
            }
        time.sleep(3)  # arXiv API etiquette
    return found


def openalex(paper: dict) -> dict | None:
    dois = [d for d in (paper.get("doi"), paper.get("journal_doi"),
                        f"10.48550/arXiv.{paper['arxiv']}" if paper.get("arxiv") else None) if d]
    select = "id,doi,title,publication_date,cited_by_count,fwci,citation_normalized_percentile,authorships,referenced_works"
    for doi in dois:
        try:
            return jget(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?select={select}")
        except LookupError:
            continue
    return None


def s2_id(paper: dict) -> str:
    return f"arXiv:{paper['arxiv']}" if paper.get("arxiv") else f"DOI:{paper['doi']}"


def resolve(paper: dict, arxiv_meta: dict) -> dict:
    out = dict(paper)
    if paper.get("arxiv"):
        meta = arxiv_meta.get(paper["arxiv"])
        out["resolved"] = meta is not None
        if meta:
            out.update(meta)
    oa = openalex(out)
    if oa:
        pct = (oa.get("citation_normalized_percentile") or {}).get("value")
        out.update(openalex_id=oa["id"], cited_by_count=oa.get("cited_by_count"), fwci=oa.get("fwci"),
                   citation_percentile=pct, referenced_works=oa.get("referenced_works") or [])
        if not paper.get("arxiv"):
            out.update(resolved=True, title=oa.get("title"), published=oa.get("publication_date"),
                       authors=[a["author"]["display_name"] for a in oa.get("authorships", [])])
    elif not paper.get("arxiv"):
        out["resolved"] = False
    return out


def match(ids: dict, paper: dict) -> bool:
    ids = {k.lower(): str(v).lower() for k, v in (ids or {}).items()}
    if paper.get("arxiv") and ids.get("arxiv") == paper["arxiv"].lower():
        return True
    return any(d and ids.get("doi") == d.lower() for d in (paper.get("doi"), paper.get("journal_doi")))


def cites(adjudicator: dict, original: dict) -> dict:
    """Does the adjudicator reference the original? Semantic Scholar first (with passages), OpenAlex fallback."""
    try:
        data = jget(f"https://api.semanticscholar.org/graph/v1/paper/{s2_id(adjudicator)}/references?"
                    "fields=externalIds,title,contexts,intents,isInfluential&limit=1000", s2=True)
        for row in data.get("data") or []:
            cited = row.get("citedPaper") or {}
            if match(cited.get("externalIds"), original):
                return {"cites_original": True, "source": "semantic_scholar",
                        "intents": row.get("intents"), "is_influential": row.get("isInfluential"),
                        "contexts": (row.get("contexts") or [])[:4]}
    except (LookupError, urllib.error.HTTPError, RuntimeError) as e:
        s2_error = str(e)
    else:
        s2_error = None
    # Reference lists in both services are incomplete; absence in both is "not found", not "does not cite".
    oa_hit = bool(original.get("openalex_id")) and original["openalex_id"] in adjudicator.get("referenced_works", [])
    return {"cites_original": True if oa_hit else None,
            "source": "openalex" if oa_hit else "none", "s2_error": s2_error, "contexts": []}


def mine(original: dict, pages: int) -> list[dict]:
    hits, offset = [], 0
    for _ in range(pages):
        try:
            data = jget(f"https://api.semanticscholar.org/graph/v1/paper/{s2_id(original)}/citations?"
                        f"fields=title,year,externalIds,contexts,intents&limit=500&offset={offset}", s2=True)
        except (LookupError, urllib.error.HTTPError, RuntimeError):
            break
        for row in data.get("data") or []:
            snippets = [c for c in row.get("contexts") or [] if CHALLENGE.search(c)]
            if snippets:
                paper = row.get("citingPaper") or {}
                hits.append({"title": paper.get("title"), "year": paper.get("year"),
                             "arxiv": (paper.get("externalIds") or {}).get("ArXiv"),
                             "doi": (paper.get("externalIds") or {}).get("DOI"),
                             "intents": row.get("intents"), "snippets": snippets[:2]})
        if data.get("next") is None:
            break
        offset = data["next"]
    return hits


def verify(seed: dict, only: set[str] | None, mine_pages: int) -> list[dict]:
    rows = [c for c in seed["candidates"] if not only or c["id"] in only]
    arxiv_ids = sorted({p["arxiv"] for c in rows for p in [c["original"], *c["adjudicators"]] if p.get("arxiv")})
    arxiv_meta = arxiv_batch(arxiv_ids)
    results = []
    for c in rows:
        print("verifying", c["id"], flush=True)
        original = resolve(c["original"], arxiv_meta)
        issues = [] if original.get("resolved") else ["original_unresolved"]
        adjudicators = []
        for a in c["adjudicators"]:
            adj = resolve(a, arxiv_meta)
            if not adj.get("resolved"):
                issues.append(f"adjudicator_unresolved:{a.get('arxiv') or a.get('doi')}")
                adjudicators.append(adj)
                continue
            adj.update(cites(adj, original))
            overlap = sorted({person(n) for n in original.get("authors", [])} &
                             {person(n) for n in adj.get("authors", [])} - {""})
            adj["author_overlap"] = overlap
            if adj["cites_original"] is None:
                issues.append(f"citation_not_found:{a.get('arxiv') or a.get('doi')}")
            if overlap:
                issues.append(f"author_overlap:{a.get('arxiv') or a.get('doi')}:{','.join(overlap)}")
            adj.pop("referenced_works", None)
            adjudicators.append(adj)
        if not c["adjudicators"]:
            issues.append("no_adjudicator")
        original.pop("referenced_works", None)
        row = {**c, "original": original, "adjudicators": adjudicators, "issues": issues}
        if mine_pages:
            row["nominated_challengers"] = mine(original, mine_pages)
        results.append(row)
    return results


def fmt_pct(v):
    return "—" if v is None else f"{100 * v:.1f}"


def markdown(results: list[dict], generated: str) -> str:
    lines = [f"# Paper-replay candidates (verified {generated})", "",
             "Evaluator-only: contains proposed outcomes. Outcomes and tiers are curator hypotheses until a",
             "human reads the citing passages in `candidates_verified.json`. Citation impact is a selection",
             "tiebreaker only, never a correctness signal (design doc §4).", "",
             "| ID | Domain | Original | Pub. | Cites | FWCI | Pctl | Adjudicators (cites original? / author overlap) | Proposed outcome | Tier guess | Issues |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        o = r["original"]
        adj = "; ".join(
            f"{a.get('arxiv') or a.get('doi')} ({'yes' if a.get('cites_original') else 'not found'}"
            f"{', overlap' if a.get('author_overlap') else ''})" for a in r["adjudicators"]) or "—"
        fwci = "—" if o.get("fwci") is None else f"{o['fwci']:.0f}"
        lines.append(f"| {r['id']} | {r['domain']} | {o.get('title') or o['label']} | {o.get('published', '—')} | "
                     f"{o.get('cited_by_count', '—')} | {fwci} | {fmt_pct(o.get('citation_percentile'))} | {adj} | "
                     f"{r['proposed_outcome']} | {r['tier_guess']} | {', '.join(r['issues']) or '—'} |")
    outcomes, tiers, domains = {}, {}, {}
    for r in results:
        outcomes[r["proposed_outcome"]] = outcomes.get(r["proposed_outcome"], 0) + 1
        tiers[r["tier_guess"]] = tiers.get(r["tier_guess"], 0) + 1
        domains[r["domain"]] = domains.get(r["domain"], 0) + 1
    lines += ["", "**Mix.** " + "; ".join(f"{k}: {v}" for k, v in sorted(domains.items())) +
              " | outcomes " + ", ".join(f"{k} {v}" for k, v in sorted(outcomes.items())) +
              " | tier guesses " + ", ".join(f"{k} {v}" for k, v in sorted(tiers.items()))]
    lines += ["", "## Curation notes", ""]
    lines += [f"- **{r['id']}**: {r['notes']}" for r in results]
    mined = [r for r in results if r.get("nominated_challengers")]
    if mined:
        lines += ["", "## Nominated challengers from citation mining", "",
                  "Regex hits on citing passages. Leads only; most are false positives until read."]
        for r in mined:
            lines += ["", f"### {r['id']}: {r['original'].get('title')}", ""]
            for h in r["nominated_challengers"][:8]:
                ident = h.get("arxiv") or h.get("doi") or "no id"
                lines.append(f"- {h.get('title')} ({h.get('year')}, {ident}): \"{h['snippets'][0][:220]}\"")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=Path, default=OUT / "candidate_seed.json")
    ap.add_argument("--only", help="comma-separated candidate ids")
    ap.add_argument("--mine", type=int, default=0, metavar="PAGES",
                    help="mine up to PAGES x 500 citing papers per original for challenge language")
    ap.add_argument("--render", action="store_true", help="re-render the report from cached results and the seed")
    args = ap.parse_args()
    seed = json.loads(args.seed.read_text(encoding="utf-8"))
    generated = dt.date.today().isoformat()
    if args.render:
        # Refresh curator fields from the seed without re-querying any API.
        previous = json.loads((OUT / "candidates_verified.json").read_text(encoding="utf-8"))
        curated = {c["id"]: c for c in seed["candidates"]}
        results = [{**r, **{k: curated[r["id"]][k] for k in ("claim", "notes", "proposed_outcome", "tier_guess")}}
                   for r in previous["candidates"] if r["id"] in curated]
        (OUT / f"candidates_{previous['generated']}.md").write_text(markdown(results, previous["generated"]), encoding="utf-8")
        print(f"rendered {len(results)} candidates from cached verification")
        return 0
    only = set(args.only.split(",")) if args.only else None
    results = verify(seed, only, args.mine)
    cached = OUT / "candidates_verified.json"
    if only and cached.exists():
        # Merge a partial run into the cached full result, keeping seed order.
        fresh = {r["id"]: r for r in results}
        kept = {r["id"]: r for r in json.loads(cached.read_text(encoding="utf-8"))["candidates"]}
        results = [fresh.get(c["id"]) or kept[c["id"]] for c in seed["candidates"] if c["id"] in fresh or c["id"] in kept]
    payload = {"generated": generated, "seed_version": seed["version"], "evaluator_only": True, "candidates": results}
    (OUT / "candidates_verified.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / f"candidates_{generated}.md").write_text(markdown(results, generated), encoding="utf-8")
    bad = [r["id"] for r in results if r["issues"]]
    print(f"{len(results)} candidates; {len(bad)} with issues: {', '.join(bad) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
