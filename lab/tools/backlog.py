"""Candidate backlog: directions → candidates → programs, behind one ingest gate.

Files (under {output_root}/indexes/backlog/):
    directions.json     list of direction objects (the lab's bets)
    candidates.jsonl    one candidate per line (ideas from sources A–E)

Every source writes candidates with `add`; nothing else writes the files. The ingest gate
(`/qml-ingest`) records its checks with `score`. A human picks from `queue` and links the program.

    python -m lab.tools.backlog direction add  --id ID --title T --thesis TEXT --target-rung N
                                               --close-criteria TEXT [--share 0.2] [--cards a,b]
    python -m lab.tools.backlog direction set  ID --status open|paused|closed --reason TEXT
    python -m lab.tools.backlog direction list
    python -m lab.tools.backlog add    --title T --claim TEXT --source A|B|C|D|E --base REF
                                       [--direction ID] [--region R] [--by WHO] [--force]
    python -m lab.tools.backlog score  CID --gate novelty|screen|value|potential ...
    python -m lab.tools.backlog pending                      # candidates the gate has not finished
    python -m lab.tools.backlog queue  [--direction ID] [--top N]
    python -m lab.tools.backlog pick   CID --by WHO
    python -m lab.tools.backlog link   CID --thread PATH
    python -m lab.tools.backlog outcome CID --furthest STAGE [--rung N]
    python -m lab.tools.backlog report                       # yield per source, region, direction
    python -m lab.tools.backlog validate [--explainers]   # --explainers also lints explainer pages
    python -m lab.tools.backlog explain-hash ID            # claim hash an explainer records
    python -m lab.tools.backlog explain-status             # missing / stale / draft / signed explainers
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .common import LabError, main_wrapper, now, output_root, today

SOURCES = {"A": "build-on-base", "B": "open-problem", "C": "combination-grid",
           "D": "programmatic-search", "E": "scout/algorithm/variants"}
REGIONS = ("classical-data", "quantum-native", "other")
DIRECTION_STATUS = ("open", "paused", "closed")
SCREEN = ("pass", "narrowed", "killed")
# Candidate stages, in order. `killed-*` and `duplicate` are terminal unless explored.
STAGES = ("new", "gated", "picked", "program", "closed")
FURTHEST = ("gate", "screen", "prereg", "run", "verdict", "promoted")
RUNGS = {1: "sharp negative / dequantization", 2: "quantum-inspired classical method",
         3: "measured mechanism", 4: "small-scale separation on quantum-native data",
         5: "crossover resource estimate", 6: "advantage on real data and hardware"}
DUP_THRESHOLD = 0.6        # word-set Jaccard on title + claim
EXPLORE_RATE = 0.10        # share of gated candidates shown regardless of score
# Advantage-potential profile (criteria/advantage_potential.md): seven upfront questions, each rated
# 0 (no) · 1 (unclear or partly) · 2 (yes), plus the kind of evidence behind the claimed speedup.
# Recorded and reported, never part of the gate decision or the rank until `report` shows it predicts.
POTENTIAL = ("mechanism", "band", "window", "ensemble", "work", "output", "baseline")
EVIDENCE = ("none", "conjectured", "heuristic", "stage1", "stage2")
POTENTIAL_BANDS = ((0, 4, "low 0-4"), (5, 9, "mid 5-9"), (10, 14, "high 10-14"))
STOP = set("a an the of on in for to and or with by at from is are be does do can vs versus than "
           "that this as its it into over under using via".split())


# --- storage -------------------------------------------------------------------------------
def root() -> Path:
    return output_root() / "indexes" / "backlog"


def load_directions() -> list[dict]:
    p = root() / "directions.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def save_directions(ds: list[dict]) -> None:
    root().mkdir(parents=True, exist_ok=True)
    (root() / "directions.json").write_text(json.dumps(ds, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_candidates() -> list[dict]:
    p = root() / "candidates.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_candidates(cs: list[dict]) -> None:
    root().mkdir(parents=True, exist_ok=True)
    (root() / "candidates.jsonl").write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cs), encoding="utf-8")


def get(cs: list[dict], cid: str) -> dict:
    for c in cs:
        if c["id"] == cid:
            return c
    raise LabError(f"no candidate {cid}")


# --- dedupe --------------------------------------------------------------------------------
def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


CLAIM_RE = re.compile(r"\*\*Claim, in one sentence:\*\*\s*(.+)")


def past_programs() -> list[tuple[str, str]]:
    """(thread, text) for every lab program and closed experiment, for dedupe."""
    out = []
    exp = output_root() / "experiments"
    if not exp.exists():
        return out
    for d in sorted(p for p in exp.glob("*/*") if p.is_dir()):
        parts = [d.name.replace("_", " ")]
        for name in ("HYPOTHESIS.md", "README.md", "VERDICT.md"):
            f = d / name
            if f.exists():
                text = f.read_text(encoding="utf-8", errors="replace")
                m = CLAIM_RE.search(text)
                heading = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")), "")
                parts += [m.group(1) if m else "", heading]
                break
        out.append((f"{d.parent.name}/{d.name}", " ".join(parts)))
    return out


def find_duplicate(text: str, cs: list[dict]) -> tuple[str, float] | None:
    t = tokens(text)
    best = None
    for c in cs:
        s = jaccard(t, tokens(c["title"] + " " + c["claim"]))
        if s >= DUP_THRESHOLD and (best is None or s > best[1]):
            best = (c["id"], s)
    for thread, ptext in past_programs():
        s = jaccard(t, tokens(ptext))
        if s >= DUP_THRESHOLD and (best is None or s > best[1]):
            best = (thread, s)
    return best


def explore_flag(cid: str) -> bool:
    """Deterministic ~10% sample: shown in the queue regardless of score, to measure gate false kills."""
    return int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF < EXPLORE_RATE


# --- gate status ---------------------------------------------------------------------------
def gate_state(c: dict) -> str:
    """'pending' until novelty and screen are recorded; then 'killed' or 'passed'."""
    g = c.get("gate", {})
    nov, scr = g.get("novelty"), g.get("screen")
    if (nov and nov.get("prior_exists")) or (scr and scr.get("verdict") == "killed"):
        return "killed"
    return "passed" if nov and scr else "pending"


def potential_total(c: dict) -> int | None:
    pot = (c.get("gate") or {}).get("potential")
    return sum(pot["answers"].values()) if pot else None


def potential_band(c: dict) -> str:
    t = potential_total(c)
    return "not scored" if t is None else next(name for lo, hi, name in POTENTIAL_BANDS if lo <= t <= hi)


def potential_tag(c: dict) -> str:
    pot = (c.get("gate") or {}).get("potential")
    return f"pot {potential_total(c):>2}/14 {pot['evidence_class']:<9}" if pot else "pot  -/14          "


def rank_score(c: dict) -> float:
    g = c.get("gate", {})
    nov = (g.get("novelty") or {}).get("score", 0.5)
    val = g.get("value") or {}
    return round(val.get("rung", 1) * val.get("p", 0.1) * (0.5 + nov), 4)


# --- commands ------------------------------------------------------------------------------
def cmd_direction(a) -> None:
    ds = load_directions()
    if a.dcmd == "add":
        if any(d["id"] == a.id for d in ds):
            raise LabError(f"direction {a.id} exists")
        if a.target_rung not in RUNGS:
            raise LabError("target rung must be 1–6")
        if len(a.close_criteria.split()) < 6:
            raise LabError("close criteria must say what result closes the direction (≥ 6 words)")
        ds.append({"id": a.id, "title": a.title, "thesis": a.thesis, "target_rung": a.target_rung,
                   "close_criteria": a.close_criteria, "share": a.share, "status": "open",
                   "hypothesis_cards": [x for x in (a.cards or "").split(",") if x],
                   "created": today(), "history": [{"at": now(), "status": "open", "reason": "created"}]})
        save_directions(ds)
        print(f"direction {a.id} open")
    elif a.dcmd == "set":
        d = next((x for x in ds if x["id"] == a.id), None)
        if not d:
            raise LabError(f"no direction {a.id}")
        if a.status not in DIRECTION_STATUS:
            raise LabError(f"status must be one of {DIRECTION_STATUS}")
        d["status"] = a.status
        d["history"].append({"at": now(), "status": a.status, "reason": a.reason})
        save_directions(ds)
        print(f"direction {a.id} → {a.status}")
        if a.status == "closed":
            print("closed: propose an exclusion-ledger entry via /qml-promote if the close criteria fired")
    else:
        cs = load_candidates()
        for d in ds:
            n = sum(1 for c in cs if c.get("direction") == d["id"])
            print(f"{d['id']:<32} {d['status']:<7} rung {d['target_rung']}  share {d.get('share') or '-':<5} "
                  f"candidates {n:<3} {d['title']}")


def cmd_add(a) -> None:
    if a.source not in SOURCES:
        raise LabError(f"source must be one of {list(SOURCES)}")
    if a.region and a.region not in REGIONS:
        raise LabError(f"region must be one of {REGIONS}")
    if len(a.claim.split()) < 8:
        raise LabError("claim must be a testable sentence (≥ 8 words): what, against which baseline, at what size")
    cs = load_candidates()
    if a.direction and not any(d["id"] == a.direction for d in load_directions()):
        raise LabError(f"no direction {a.direction} (create it, or omit to leave the candidate unassigned)")
    dup = find_duplicate(a.title + " " + a.claim, cs)
    if dup and not a.force:
        raise LabError(f"duplicate of {dup[0]} (similarity {dup[1]:.2f}); rephrase the step, or --force with a reason")
    n = sum(1 for c in cs if c["id"].startswith(f"c-{today().replace('-', '')}")) + 1
    cid = f"c-{today().replace('-', '')}-{n:03d}"
    c = {"id": cid, "title": a.title, "claim": a.claim, "source": a.source, "base": a.base,
         "direction": a.direction or None, "region": a.region or "other", "by": a.by or "agent",
         "added": now(), "stage": "new", "explore": explore_flag(cid), "gate": {},
         "dedupe": {"closest": dup[0], "similarity": round(dup[1], 2), "forced": True} if dup else None,
         "thread": None, "outcome": None, "history": [{"at": now(), "stage": "new"}]}
    cs.append(c)
    save_candidates(cs)
    print(cid)


def cmd_score(a) -> None:
    cs = load_candidates()
    c = get(cs, a.cid)
    g = c.setdefault("gate", {})
    if a.gate == "novelty":
        if a.score is None or not 0 <= a.score <= 1:
            raise LabError("novelty needs --score in [0, 1]")
        if a.prior_exists and not a.evidence:
            raise LabError("--prior-exists needs --evidence (the arXiv id of the prior work)")
        g["novelty"] = {"score": a.score, "prior_exists": a.prior_exists,
                        "evidence": a.evidence or [], "note": a.note or "", "at": now()}
    elif a.gate == "screen":
        if a.verdict not in SCREEN:
            raise LabError(f"screen needs --verdict {SCREEN}")
        if a.verdict == "killed" and not a.note:
            raise LabError("a screen kill needs --note naming the mechanism and the deciding gate")
        g["screen"] = {"verdict": a.verdict, "gates": a.gates or "", "note": a.note or "", "at": now()}
    elif a.gate == "value":
        if a.rung not in RUNGS or a.p is None or not 0 <= a.p <= 1:
            raise LabError("value needs --rung 1–6 and --p in [0, 1]")
        g["value"] = {"rung": a.rung, "p": a.p, "note": a.note or "", "at": now()}
    elif a.gate == "potential":
        try:
            vals = [int(x) for x in (a.answers or "").split(",")]
        except ValueError:
            vals = []
        if len(vals) != len(POTENTIAL) or any(v not in (0, 1, 2) for v in vals):
            raise LabError(f"potential needs --answers with {len(POTENTIAL)} values, each 0, 1 or 2, "
                           f"in the order {','.join(POTENTIAL)}")
        if a.evidence_class not in EVIDENCE:
            raise LabError(f"potential needs --evidence-class {EVIDENCE}")
        if not a.note:
            raise LabError("potential needs --note naming the mechanism and the weakest answer")
        g["potential"] = {"answers": dict(zip(POTENTIAL, vals)), "evidence_class": a.evidence_class,
                          "note": a.note, "at": now()}
    else:
        raise LabError("gate must be novelty | screen | value | potential")
    if c["stage"] == "new" and gate_state(c) != "pending":
        c["stage"] = "gated"
        c["history"].append({"at": now(), "stage": "gated", "gate": gate_state(c)})
    save_candidates(cs)
    print(f"{c['id']}: {a.gate} recorded; gate {gate_state(c)}")


def cmd_pending(_a) -> None:
    for c in load_candidates():
        if c["stage"] == "new":
            missing = [k for k in ("novelty", "screen", "value", "potential") if k not in c.get("gate", {})]
            print(f"{c['id']}  src {c['source']}  missing {','.join(missing)}  {c['title']}")


def cmd_queue(a) -> None:
    cs = [c for c in load_candidates() if c["stage"] == "gated"
          and (not a.direction or c.get("direction") == a.direction)]
    passed = sorted((c for c in cs if gate_state(c) == "passed"), key=rank_score, reverse=True)
    print(f"Ranked ({len(passed)} passed the gate):")
    for c in passed[: a.top]:
        print(f"  {rank_score(c):>6}  {potential_tag(c)}  {c['id']}  "
              f"[{c['source']}/{c.get('direction') or 'unassigned'}]  {c['title']}")
    explore = [c for c in cs if c.get("explore") and c not in passed[: a.top]]
    print(f"Explore sample ({len(explore)}; shown regardless of score, incl. gate kills):")
    for c in explore:
        print(f"  {gate_state(c):>6}  {c['id']}  [{c['source']}/{c.get('direction') or 'unassigned'}]  {c['title']}")
    unscored = sum(1 for c in cs if potential_total(c) is None)
    if unscored:
        print(f"No potential profile: {unscored} gated candidates (the rank does not use it; see `report`).")
    unassigned = sum(1 for c in cs if not c.get("direction"))
    if unassigned:
        print(f"Unassigned: {unassigned} gated candidates fit no direction — review for a new direction.")


def move(cs: list[dict], c: dict, stage: str, **extra) -> None:
    c["stage"] = stage
    c["history"].append({"at": now(), "stage": stage, **extra})
    save_candidates(cs)


def cmd_pick(a) -> None:
    cs = load_candidates()
    c = get(cs, a.cid)
    if c["stage"] != "gated":
        raise LabError(f"{c['id']} is {c['stage']}; only gated candidates can be picked")
    if gate_state(c) == "killed" and not c.get("explore"):
        raise LabError(f"{c['id']} was killed by the gate and is not in the explore sample")
    move(cs, c, "picked", by=a.by)
    print(f"{c['id']} picked by {a.by}; open it with /qml-lab new --from-backlog {c['id']}")


def cmd_link(a) -> None:
    cs = load_candidates()
    c = get(cs, a.cid)
    if c["stage"] != "picked":
        raise LabError(f"{c['id']} is {c['stage']}; link a picked candidate")
    c["thread"] = a.thread
    move(cs, c, "program", thread=a.thread)
    print(f"{c['id']} → {a.thread}")


def cmd_outcome(a) -> None:
    if a.furthest not in FURTHEST:
        raise LabError(f"--furthest must be one of {FURTHEST}")
    if a.rung is not None and a.rung not in RUNGS:
        raise LabError("--rung must be 1–6")
    cs = load_candidates()
    c = get(cs, a.cid)
    c["outcome"] = {"furthest": a.furthest, "rung": a.rung, "at": now()}
    move(cs, c, "closed", furthest=a.furthest, rung=a.rung)
    print(f"{c['id']} closed at {a.furthest}" + (f", landed rung {a.rung}" if a.rung else ""))


def tally(cs: list[dict], key) -> dict:
    rows: dict = defaultdict(Counter)
    for c in cs:
        r = rows[key(c)]
        r["added"] += 1
        gs = gate_state(c)
        r["gate_pending"] += gs == "pending"
        r["gate_killed"] += gs == "killed"
        r["gate_passed"] += gs == "passed"
        r["picked"] += c["stage"] in ("picked", "program", "closed")
        r["program"] += c["stage"] in ("program", "closed")
        r["rung"] += bool(c.get("outcome") and c["outcome"].get("rung"))
    return rows


def cmd_report(_a) -> None:
    cs = load_candidates()
    cols = ("added", "gate_pending", "gate_killed", "gate_passed", "picked", "program", "rung")
    for title, key in (("source", lambda c: f"{c['source']} {SOURCES[c['source']]}"),
                       ("region", lambda c: c.get("region", "other")),
                       ("direction", lambda c: c.get("direction") or "unassigned"),
                       ("potential, split by target rung (calibration: does a higher band reach further?)",
                        lambda c: f"{potential_band(c)} · rung "
                        + ("1-2" if ((c.get("gate") or {}).get("value") or {}).get("rung", 1) <= 2 else "3-6")),
                       ("evidence class", lambda c: ((c.get("gate") or {}).get("potential") or {})
                        .get("evidence_class", "not scored"))):
        print(f"\nBy {title}")
        print(f"  {'':<30}" + "".join(f"{h:>13}" for h in cols))
        for k, r in sorted(tally(cs, key).items()):
            print(f"  {k:<30}" + "".join(f"{r[h]:>13}" for h in cols))
    ex = [c for c in cs if c.get("explore") and gate_state(c) == "killed" and c.get("outcome")]
    if ex:
        good = sum(1 for c in ex if c["outcome"].get("rung"))
        print(f"\nGate false-kill check: {good} of {len(ex)} explored gate kills landed a rung")


def validate() -> list[str]:
    errs = []
    ds = load_directions()
    dids = {d["id"] for d in ds}
    for d in ds:
        if d.get("status") not in DIRECTION_STATUS:
            errs.append(f"direction {d.get('id')}: bad status")
        if d.get("target_rung") not in RUNGS:
            errs.append(f"direction {d.get('id')}: bad target_rung")
    seen = set()
    for c in load_candidates():
        cid = c.get("id")
        if cid in seen:
            errs.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c.get("source") not in SOURCES:
            errs.append(f"{cid}: bad source")
        if c.get("stage") not in STAGES:
            errs.append(f"{cid}: bad stage")
        if c.get("direction") and c["direction"] not in dids:
            errs.append(f"{cid}: unknown direction {c['direction']}")
        pot = (c.get("gate") or {}).get("potential")
        if pot and (set(pot.get("answers", {})) != set(POTENTIAL)
                    or any(v not in (0, 1, 2) for v in pot["answers"].values())
                    or pot.get("evidence_class") not in EVIDENCE):
            errs.append(f"{cid}: bad potential profile")
        if c.get("stage") == "program" and not c.get("thread"):
            errs.append(f"{cid}: stage program without a thread")
    return errs


# --- explainers (C13 phase 4) --------------------------------------------------------------
# One markdown page per direction and candidate under indexes/backlog/explainers/. Written by the
# explainer role, signed by the explanation-checker. The renderer in qml_artifacts lays them out;
# keep its claim_hash and bet rules in step with these.
BETS = {1: "kill-test", 2: "quantum-inspired", 3: "mechanism-probe", 4: "advantage-bet",
        5: "resource-estimate", 6: "advantage-bet"}
BET_NAMES = set(BETS.values()) | {"unscreened", "mixed"}
QUANTUM_CASE = ("none", "weak", "plausible", "strong")
CHECK_STATUS = ("draft", "signed")
CONFIDENCE = ("speculative", "plausible", "observed")
CAND_HEADINGS = ["In plain words", "Background", "The real motivation", "Why quantum, honestly",
                 "Why it might fail", "What we learn either way", "Cost and feasibility", "Sources"]
DIR_HEADINGS = ["In plain words", "Background", "The real motivation", "Why quantum, honestly",
                "The case against", "If it works", "Why now", "What closes it", "Sources"]
WORDS = {"candidate": (450, 1100), "direction": (800, 1700)}
# "exponential speedup" stays allowed: kill tests must name the speedup they try to dequantize.
ADVANTAGE_WORDS = re.compile(r"\b(outperform\w*|beats? classical|superior|revolutionary)\b", re.I)
HYPE_WORDS = re.compile(r"\b(breakthrough|unprecedented|game[- ]chang\w*)\b", re.I)
ARXIV_RE = re.compile(r"arXiv:\s?(\d{4}\.\d{4,5})")


def explainer_dir() -> Path:
    return root() / "explainers"


def expected_bet(c: dict) -> str:
    rung = ((c.get("gate") or {}).get("value") or {}).get("rung")
    return BETS.get(rung, "unscreened")


def claim_hash(entity: dict, kind: str) -> str:
    """Hash of what an explainer explains; a change makes the page stale."""
    if kind == "direction":
        parts = [entity.get(k) or "" for k in ("title", "thesis", "close_criteria", "status")]
    else:
        g = entity.get("gate") or {}
        parts = [entity.get("title") or "", entity.get("claim") or ""] + \
                [(g.get(k) or {}).get("note") or "" for k in ("screen", "value", "potential")]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def parse_explainer(text: str) -> tuple[dict, str]:
    """Flat front matter (`key: value`, lists as `[a, b]`) and the body."""
    if not text.startswith("---\n"):
        raise LabError("no front matter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise LabError("unterminated front matter")
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        k, sep, v = line.partition(":")
        if not sep:
            raise LabError(f"bad front matter line {line!r}")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        meta[k.strip()] = v
    return meta, text[end + 5:]


def explainer_path(kind: str, eid: str) -> Path:
    return explainer_dir() / ("directions" if kind == "direction" else "candidates") / f"{eid}.md"


def lint_explainer(path: Path, entity: dict, kind: str) -> list[str]:
    name = f"{kind} {entity['id']}"
    try:
        meta, body = parse_explainer(path.read_text(encoding="utf-8"))
    except LabError as e:
        return [f"{name}: explainer {e}"]
    errs = []
    if meta.get("id") != entity["id"] or meta.get("kind") != kind:
        errs.append(f"{name}: explainer id/kind mismatch")
    bet, qc = meta.get("bet"), meta.get("quantum_case")
    if bet not in BET_NAMES:
        errs.append(f"{name}: bad bet {bet!r}")
    if qc not in QUANTUM_CASE:
        errs.append(f"{name}: bad quantum_case {qc!r}")
    if meta.get("check_status") not in CHECK_STATUS:
        errs.append(f"{name}: bad check_status")
    if meta.get("check_status") == "signed" and meta.get("checked_by") in (None, "", meta.get("written_by")):
        errs.append(f"{name}: signed without a separate checker")
    if meta.get("confidence") not in CONFIDENCE:
        errs.append(f"{name}: bad confidence")
    tag = meta.get("tagline") or ""
    if not tag or len(tag) > 140:
        errs.append(f"{name}: tagline missing or over 140 characters")
    if kind == "candidate":
        want = expected_bet(entity)
        if bet != want:
            errs.append(f"{name}: bet {bet} but value rung says {want}")
        pot = ((entity.get("gate") or {}).get("potential") or {}).get("answers") or {}
        if bet in ("kill-test", "quantum-inspired") and qc in ("plausible", "strong"):
            errs.append(f"{name}: quantum_case {qc} on a {bet}")
        if qc == "strong" and not (bet in ("advantage-bet", "resource-estimate")
                                   and pot.get("mechanism") == 2 and pot.get("window") == 2):
            errs.append(f"{name}: quantum_case strong needs an advantage bet with mechanism=2 and window=2")
        if qc == "plausible" and pot and pot.get("mechanism", 0) < 1:
            errs.append(f"{name}: quantum_case plausible with mechanism=0")
    heads = re.findall(r"^## (.+?)\s*$", body, re.M)
    want_heads = DIR_HEADINGS if kind == "direction" else CAND_HEADINGS
    if heads != want_heads:
        errs.append(f"{name}: headings {heads} != {want_heads}")
    n = len(re.findall(r"\b\w[\w'-]*\b", body))
    lo, hi = WORDS[kind]
    if not lo <= n <= hi:
        errs.append(f"{name}: {n} words, want {lo}-{hi}")
    if qc not in ("plausible", "strong") and ADVANTAGE_WORDS.search(body):
        errs.append(f"{name}: advantage wording {ADVANTAGE_WORDS.search(body).group(0)!r} with quantum_case {qc}")
    if HYPE_WORDS.search(body):
        errs.append(f"{name}: hype word {HYPE_WORDS.search(body).group(0)!r}")
    srcs = {s.replace("arXiv:", "").strip() for s in meta.get("sources") or [] if isinstance(s, str)}
    missing = sorted(set(ARXIV_RE.findall(body)) - srcs)
    if missing:
        errs.append(f"{name}: arXiv ids cited but not in sources: {missing}")
    return errs


def explainer_state(entity: dict, kind: str) -> str:
    p = explainer_path(kind, entity["id"])
    if not p.exists():
        return "missing"
    try:
        meta, _ = parse_explainer(p.read_text(encoding="utf-8"))
    except LabError:
        return "broken"
    if meta.get("claim_hash") != claim_hash(entity, kind):
        return "stale"
    return meta.get("check_status") or "draft"


def validate_explainers() -> list[str]:
    errs = []
    for kind, ents in (("direction", load_directions()), ("candidate", load_candidates())):
        for e in ents:
            p = explainer_path(kind, e["id"])
            if p.exists():
                errs += lint_explainer(p, e, kind)
    known = {("directions", d["id"]) for d in load_directions()} | {("candidates", c["id"]) for c in load_candidates()}
    for p in sorted(explainer_dir().glob("*/*.md")) if explainer_dir().exists() else []:
        if (p.parent.name, p.stem) not in known:
            errs.append(f"orphan explainer {p.parent.name}/{p.name}")
    return errs


def cmd_explain_hash(a) -> None:
    ds = {d["id"]: d for d in load_directions()}
    if a.id in ds:
        print(claim_hash(ds[a.id], "direction"))
    else:
        print(claim_hash(get(load_candidates(), a.id), "candidate"))


def cmd_explain_status(a) -> None:
    rows = [("direction", d) for d in load_directions()] + [("candidate", c) for c in load_candidates()]
    tally = Counter()
    for kind, e in rows:
        st = explainer_state(e, kind)
        tally[st] += 1
        if st != "signed":
            print(f"{st:<8} {kind:<9} {e['id']}  {e.get('title', '')}")
    print("\n" + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("direction"); dsub = d.add_subparsers(dest="dcmd", required=True)
    da = dsub.add_parser("add")
    for f in ("--id", "--title", "--thesis", "--close-criteria"):
        da.add_argument(f, required=True)
    da.add_argument("--target-rung", type=int, required=True)
    da.add_argument("--share", type=float); da.add_argument("--cards")
    ds = dsub.add_parser("set"); ds.add_argument("id"); ds.add_argument("--status", required=True)
    ds.add_argument("--reason", required=True)
    dsub.add_parser("list")
    ad = sub.add_parser("add")
    for f in ("--title", "--claim", "--source", "--base"):
        ad.add_argument(f, required=True)
    for f in ("--direction", "--region", "--by"):
        ad.add_argument(f)
    ad.add_argument("--force", action="store_true")
    sc = sub.add_parser("score"); sc.add_argument("cid"); sc.add_argument("--gate", required=True)
    sc.add_argument("--score", type=float); sc.add_argument("--prior-exists", action="store_true")
    sc.add_argument("--evidence", nargs="*"); sc.add_argument("--verdict"); sc.add_argument("--gates")
    sc.add_argument("--rung", type=int); sc.add_argument("--p", type=float); sc.add_argument("--note")
    sc.add_argument("--answers"); sc.add_argument("--evidence-class")
    sub.add_parser("pending")
    q = sub.add_parser("queue"); q.add_argument("--direction"); q.add_argument("--top", type=int, default=10)
    p = sub.add_parser("pick"); p.add_argument("cid"); p.add_argument("--by", required=True)
    l = sub.add_parser("link"); l.add_argument("cid"); l.add_argument("--thread", required=True)
    o = sub.add_parser("outcome"); o.add_argument("cid"); o.add_argument("--furthest", required=True)
    o.add_argument("--rung", type=int)
    sub.add_parser("report"); v = sub.add_parser("validate"); v.add_argument("--explainers", action="store_true")
    eh = sub.add_parser("explain-hash"); eh.add_argument("id"); sub.add_parser("explain-status")
    a = ap.parse_args()
    if a.cmd == "validate":
        errs = validate() + (validate_explainers() if a.explainers else [])
        if errs:
            raise LabError(f"{len(errs)} backlog problem(s):\n  " + "\n  ".join(errs))
        print(f"backlog OK — {len(load_directions())} directions, {len(load_candidates())} candidates")
        return 0
    {"direction": cmd_direction, "add": cmd_add, "score": cmd_score, "pending": cmd_pending,
     "queue": cmd_queue, "pick": cmd_pick, "link": cmd_link, "outcome": cmd_outcome,
     "report": cmd_report, "explain-hash": cmd_explain_hash, "explain-status": cmd_explain_status}[a.cmd](a)
    return 0


if __name__ == "__main__":
    main_wrapper(main)
