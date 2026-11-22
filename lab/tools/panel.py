"""Multi-model scoring panel for backlog candidates: blind per-criterion scores from several model
families, a robust aggregate, and the disagreement statistics that say how much the panel is worth.

Why: one model family proposed, screened and scored every candidate, so its blind spots are the
lab's blind spots. A panel only helps if its judges' errors are not the same errors. Recent work
finds frontier judges from different providers still share most errors (arXiv:2609.22512: error
correlation 0.56, n_eff 1.4 for three providers; "Nine Judges, Two Effective Votes", NeurIPS 2026:
n_eff about 2 for nine judges from seven families). So this tool measures agreement and n_eff on
every run instead of assuming independence, keeps disagreement as a signal (contested candidates,
minority picks) instead of averaging it away, and never shows a judge another judge's answer.

The panel does not rank. It writes per-judge, per-criterion scores and their medians; the backlog's
scoring method consumes the medians. The rubric (lab/rubrics/*.json) names the criteria; the panel
(lab/panels/*.json) names the seats.

    python -m lab.tools.panel prompt   <candidate-id> [--panel P] [--rubric R] [--seat S]
        # print the exact prompt a seat sees (nothing is run)
    python -m lab.tools.panel run      [--panel P] [--rubric R] [--only c-…,c-…] [--extra file.jsonl]
                                      [--seats a,b] [--workers 6] [--limit N] [--out DIR]
        # score every candidate (backlog candidates.jsonl plus --extra) with every available seat;
        # appends to <out>/judgments.jsonl, skips (candidate, seat, prompt) triples already done
    python -m lab.tools.panel report   [--rubric R] [--out DIR] [--json] [--export RUN_ID]
        # reads every <out>/judgments*.jsonl (one per machine: the cloud has Claude, the Mac has Codex);
        # medians, spreads, contested candidates, minority picks, judge agreement and n_eff,
        # comparison with the single-judge gate scores, where tagged bets land, twin (wording) deltas;
        # --export writes scores.jsonl (one record per candidate × criterion) and run.json (n_eff)

Seat harnesses: claude-code and codex (lab.tools.harness, tool-free and fresh per call), and
openai-compat (any OpenAI-compatible /chat/completions endpoint: Gemini, OpenRouter, a local
Ollama server). A seat whose binary, key or server is missing is skipped and reported as skipped.
Default --out: {OUTPUT_ROOT}/indexes/backlog/panel/<rubric>/.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import math
import os
import re
import statistics
import sys
import urllib.error
import urllib.request
from pathlib import Path

from . import harness as agent_harness
from .common import LabError, REPO, main_wrapper, now, output_root

RUBRICS = REPO / "lab" / "rubrics"
PANELS = REPO / "lab" / "panels"
ROLES = ("judge", "advocate", "attacker")
CONTESTED_SPREAD = 0.4      # (max - min) / scale range among judge seats, on a headline criterion
HEADLINE = ("plausibility", "upside")   # spread here marks a candidate contested
PROMPT_VERSION = "panel-prompt-v1"

LAB_CONTEXT = (
    "The lab is a three-person quantum machine learning startup. Its goal is a chain of small, "
    "publishable steps toward a quantum algorithm it owns, eventually with an advantage on real "
    "data or hardware. Refuting or reproducing other people's work can be publishable but is not "
    "a step toward the lab's own algorithm. The lab simulates on classical hardware now and has a "
    "neutral-atom hardware partnership.")

ROLE_TEXT = {
    "judge": "Score as an independent referee. You see no other review and no earlier score.",
    "advocate": ("First build the strongest honest case that this candidate matters and could "
                 "work: the best mechanism, the regime where it would hold, the result it would "
                 "unlock. Do not invent evidence. Then score as that case justifies."),
    "attacker": ("First find the strongest reason this candidate fails or is matched classically: "
                 "dequantization, classical simulability, a tuned baseline, shot or readout cost, "
                 "prior work. Do not invent evidence. Then score as that reason justifies."),
}

RULES = (
    "Rules: score the claim as written. Do not raise a score because a study is cheap or easy, and "
    "do not lower one only because it is ambitious; plausibility and upside are separate questions. "
    "Use the full scale. If you do not know the literature well enough, say so in the objection "
    "rather than guessing a confident number.")


# --- config ------------------------------------------------------------------------------------
def _named(base: Path, name: str) -> Path:
    p = Path(name)
    if p.suffix == ".json" and p.exists():
        return p
    p = base / f"{name}.json"
    if not p.exists():
        raise LabError(f"not found: {p}")
    return p


def load_rubric(name: str = "backlog_lanes") -> dict:
    r = json.loads(_named(RUBRICS, name).read_text(encoding="utf-8"))
    ids = [c["id"] for c in r.get("criteria", [])]
    if not ids or len(set(ids)) != len(ids):
        raise LabError(f"rubric {name}: criteria missing or duplicated")
    for c in r["criteria"]:
        if not (c["min"] < c["max"]) or not c.get("question"):
            raise LabError(f"rubric {name}: bad criterion {c['id']}")
        if c.get("log") and c["min"] <= 0:
            raise LabError(f"rubric {name}: log criterion {c['id']} needs min > 0")
    for k in r.get("composite") or []:
        if k.removesuffix("+0.5") not in ids:
            raise LabError(f"rubric {name}: composite names unknown criterion {k}")
    return r


def load_panel(name: str = "default") -> dict:
    p = json.loads(_named(PANELS, name).read_text(encoding="utf-8"))
    ids = [s["id"] for s in p.get("seats", [])]
    if not ids or len(set(ids)) != len(ids):
        raise LabError(f"panel {name}: seats missing or duplicated")
    for s in p["seats"]:
        if s.get("role", "judge") not in ROLES:
            raise LabError(f"panel {name}: seat {s['id']} has unknown role {s.get('role')}")
        if s["harness"] not in (*agent_harness.HARNESSES, "openai-compat"):
            raise LabError(f"panel {name}: seat {s['id']} has unknown harness {s['harness']}")
        s.setdefault("role", "judge")
    if not any(s["role"] == "judge" for s in p["seats"]):
        raise LabError(f"panel {name}: needs at least one judge seat")
    return p


def answer_schema(rubric: dict) -> dict:
    crit = {c["id"]: {"type": "integer" if c.get("integer") else "number"} for c in rubric["criteria"]}
    return {"type": "object", "additionalProperties": False,
            "required": ["scores", "strongest_case", "strongest_objection"],
            "properties": {
                "scores": {"type": "object", "additionalProperties": False,
                           "required": sorted(crit), "properties": crit},
                "strongest_case": {"type": "string"},
                "strongest_objection": {"type": "string"}}}


# --- candidates ----------------------------------------------------------------------------------
def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def backlog_root(root: Path | None) -> Path:
    return root if root else output_root() / "indexes" / "backlog"


def load_items(root: Path, extra: Path | None = None) -> tuple[list[dict], dict]:
    cands = read_jsonl(root / "candidates.jsonl")
    if extra:
        cands += read_jsonl(extra)
    ids = [c["id"] for c in cands]
    if len(set(ids)) != len(ids):
        raise LabError("duplicate candidate ids (an --extra row reuses a backlog id?)")
    dpath = root / "directions.json"
    dirs = {d["id"]: d for d in json.loads(dpath.read_text(encoding="utf-8"))} if dpath.exists() else {}
    return cands, dirs


def prompt_for(c: dict, direction: dict | None, rubric: dict, role: str) -> str:
    """What a seat sees: the lab, the direction, the candidate's own words, the rubric. Never the
    gate's scores, notes or explainer page, never another seat's answer, never who proposed it."""
    lines = [LAB_CONTEXT, "", ROLE_TEXT[role], RULES, ""]
    if direction:
        lines += [f"Research direction: {direction.get('title', direction['id'])}",
                  f"Direction thesis: {direction.get('thesis', '')}"]
        if direction.get("target_algorithm"):
            lines.append(f"Algorithm the lab wants to own in this direction: {direction['target_algorithm']}")
        lines.append("")
    lines += [f"Candidate: {c['title']}", f"Claim: {c['claim']}"]
    if c.get("base"):
        lines.append(f"Builds on: {c['base']}")
    lines += ["", "Score every criterion on its own scale:"]
    for k in rubric["criteria"]:
        lines.append(f"- {k['id']} ({k['min']} to {k['max']}): {k['question']}")
    lines += ["", "Also give strongest_case and strongest_objection, two sentences each, specific to "
              "this claim. Answer with JSON only, matching the schema."]
    return "\n".join(lines)


def prompt_hash(text: str) -> str:
    return hashlib.sha256((PROMPT_VERSION + "\n" + text).encode("utf-8")).hexdigest()[:12]


# --- seats ---------------------------------------------------------------------------------------
def seat_available(seat: dict) -> str | None:
    """None if the seat can run here, else the reason it is skipped."""
    h = seat["harness"]
    if h in agent_harness.HARNESSES:
        try:
            agent_harness.find_binary(h)
        except agent_harness.HarnessError as e:
            return str(e)
        return None
    key_env = seat.get("key_env")
    if key_env and not os.environ.get(key_env):
        return f"{key_env} not set"
    if not key_env:   # keyless local server: check it answers
        try:
            urllib.request.urlopen(seat["base_url"].rstrip("/") + "/models", timeout=3)
        except Exception as e:   # noqa: BLE001 - any failure means the seat is not here
            return f"{seat['base_url']} not reachable ({type(e).__name__})"
    return None


def call_openai_compat(seat: dict, prompt: str, schema: dict, timeout: int = 600) -> dict:
    body = {"model": seat["model"], "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "panel_answer", "strict": True, "schema": schema}}}
    if seat.get("temperature") is not None:
        body["temperature"] = seat["temperature"]
    headers = {"Content-Type": "application/json"}
    if seat.get("key_env"):
        headers["Authorization"] = "Bearer " + os.environ[seat["key_env"]]
    req = urllib.request.Request(seat["base_url"].rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"completed": False, "answer_text": None, "error": f"HTTP {e.code}: {e.read()[:300]!r}"}
    except Exception as e:   # noqa: BLE001
        return {"completed": False, "answer_text": None, "error": f"{type(e).__name__}: {e}"}
    msg = (data.get("choices") or [{}])[0].get("message", {}).get("content")
    return {"completed": bool(msg), "answer_text": msg, "error": None if msg else "empty answer",
            "resolved_model": data.get("model"), "usage": {"usage": data.get("usage")}, "violations": []}


def call_seat(seat: dict, prompt: str, schema: dict) -> dict:
    if seat["harness"] == "openai-compat":
        return call_openai_compat(seat, prompt, schema)
    try:
        return agent_harness.run(seat["harness"], prompt, schema, seat["model"], seat.get("effort"))
    except agent_harness.HarnessError as e:
        return {"completed": False, "answer_text": None, "error": str(e)}


def parse_answer(text: str | None, rubric: dict) -> tuple[dict | None, str | None]:
    if not text:
        return None, "no answer"
    m = re.search(r"\{.*\}", text, re.S)
    try:
        a = json.loads(m.group(0) if m else text)
    except json.JSONDecodeError as e:
        return None, f"not JSON: {e}"
    scores = a.get("scores") or {}
    for k in rubric["criteria"]:
        v = scores.get(k["id"])
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return None, f"{k['id']} missing or not a number"
        if not (k["min"] <= v <= k["max"]):
            return None, f"{k['id']}={v} outside [{k['min']}, {k['max']}]"
        if k.get("integer") and v != int(v):
            return None, f"{k['id']}={v} must be a whole number"
    return {"scores": {k["id"]: float(scores[k["id"]]) for k in rubric["criteria"]},
            "strongest_case": str(a.get("strongest_case", "")),
            "strongest_objection": str(a.get("strongest_objection", ""))}, None


# --- run -----------------------------------------------------------------------------------------
def run(panel: dict, rubric: dict, cands: list[dict], dirs: dict, out: Path, workers: int = 6,
        seats_filter: set[str] | None = None, caller=call_seat, log=print) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    jpath = out / "judgments.jsonl"
    done = {(j["candidate"], j["seat"], j["prompt_hash"]) for j in read_jsonl(jpath) if j.get("ok")}
    seats, skipped = [], {}
    for s in panel["seats"]:
        if seats_filter and s["id"] not in seats_filter:
            continue
        why = seat_available(s) if caller is call_seat else None
        if why:
            skipped[s["id"]] = why
        else:
            seats.append(s)
    if not seats:
        raise LabError(f"no seat can run here; skipped: {skipped}")
    if not seats_filter and not any(s["role"] == "judge" for s in seats):
        raise LabError(f"no judge seat can run here; skipped: {skipped}")
    schema = answer_schema(rubric)
    tasks = []
    for c in cands:
        for s in seats:
            text = prompt_for(c, dirs.get(c.get("direction")), rubric, s["role"])
            h = prompt_hash(text)
            if (c["id"], s["id"], h) not in done:
                tasks.append((c, s, text, h))
    log(f"panel {panel['name']} · rubric {rubric['name']} · {len(seats)} seats "
        f"({', '.join(s['id'] for s in seats)}) · {len(tasks)} calls to make"
        + (f" · skipped: {skipped}" if skipped else ""))

    def one(t):
        c, s, text, h = t
        res = caller(s, text, schema)
        ans, err = parse_answer(res.get("answer_text"), rubric) if res.get("completed") else (None, res.get("error"))
        return {"candidate": c["id"], "seat": s["id"], "family": s["family"], "role": s["role"],
                "model": s["model"], "resolved_model": res.get("resolved_model"), "harness": s["harness"],
                "rubric": rubric["name"], "prompt_hash": h, "at": now(), "ok": ans is not None,
                "error": err, "violations": res.get("violations") or [],
                "cost_usd": (res.get("usage") or {}).get("total_cost_usd"), **(ans or {})}

    ok = failed = 0
    cost = 0.0
    with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as pool, jpath.open("a", encoding="utf-8") as f:
        for row in pool.map(one, tasks):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            ok += row["ok"]
            failed += not row["ok"]
            cost += row.get("cost_usd") or 0.0
            if not row["ok"]:
                log(f"  failed {row['candidate']} × {row['seat']}: {row['error']}")
    log(f"recorded {ok} answers, {failed} failures, reported cost ${cost:.2f} → {jpath}")
    return {"ok": ok, "failed": failed, "skipped": skipped, "cost_usd": round(cost, 4)}


# --- statistics ----------------------------------------------------------------------------------
def ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def n_eff(k: int, rho: float | None) -> float | None:
    """Effective number of independent judges for k judges with mean pairwise correlation rho."""
    if rho is None or k < 1:
        return None
    rho = max(rho, 0.0)
    return round(k / (1 + (k - 1) * rho), 2)


COMPOSITE = ["rung", "plausibility"]   # set from the rubric by report(); used only to compare orderings


def composite(s: dict, terms: list[str] | None = None) -> float:
    """Product of the rubric's composite terms ("x+0.5" adds a half). Default rung × plausibility:
    the part of the gate's rank_score (rung × p × (0.5 + novelty)) that every rubric has, so panel
    and gate orderings compare like for like. Not a rank: the lane logic in backlog.py ranks."""
    out = 1.0
    for t in terms or COMPOSITE:
        k, half = (t[:-4], 0.5) if t.endswith("+0.5") else (t, 0.0)
        out *= s.get(k, 0.5 if half else 1.0) + half
    return out


def gate_scores(c: dict) -> dict | None:
    g = c.get("gate") or {}
    val, nov = g.get("value"), g.get("novelty")
    if not val or not nov:
        return None
    return {"rung": val.get("rung", 1), "plausibility": val.get("p", 0.1), "novelty": nov.get("score", 0.5)}


def spread_of(k: dict, vals: list[float]) -> float:
    """(max - min) over the scale range; on a log scale for criteria like days of work."""
    if k.get("log"):
        return round((math.log(max(vals)) - math.log(min(vals))) / (math.log(k["max"]) - math.log(k["min"])), 3)
    return round((max(vals) - min(vals)) / (k["max"] - k["min"]), 3)


def cap_champions(rubric: dict, latest: dict) -> list[dict]:
    """A judge may champion at most `champion_cap` candidates per run. Scored blind, a judge cannot
    see its other answers, so the cap is applied afterwards: its champions are kept in order of its
    own upside × plausibility and the rest set to 0. Returns what was capped."""
    cap = rubric.get("champion_cap")
    if not cap or "champion" not in {k["id"] for k in rubric["criteria"]}:
        return []
    capped = []
    for seat in sorted({s for _, s in latest}):
        mine = [r for (c, s), r in latest.items() if s == seat and r["scores"].get("champion") == 1]
        mine.sort(key=lambda r: (-(r["scores"].get("upside", 1) * r["scores"].get("plausibility", 0)), r["candidate"]))
        for r in mine[cap:]:
            r["scores"] = {**r["scores"], "champion": 0.0}
            capped.append({"seat": seat, "candidate": r["candidate"]})
    return capped


def read_tags(root: Path) -> dict[str, str]:
    """bet: field of each candidate explainer page (advantage-bet, kill-test, mechanism-probe, …)."""
    tags = {}
    for p in sorted((root / "explainers" / "candidates").glob("*.md")):
        m = re.search(r"^bet:\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
        if m:
            tags[p.stem] = m.group(1)
    return tags


def report(rubric: dict, rows: list[dict], cands: list[dict], tags: dict[str, str]) -> dict:
    global COMPOSITE
    COMPOSITE = rubric.get("composite") or ["rung", "plausibility"]
    crit = [k["id"] for k in rubric["criteria"]]
    kdef = {k["id"]: k for k in rubric["criteria"]}
    rows = [r for r in rows if r.get("ok") and r.get("rubric") == rubric["name"]]
    latest: dict[tuple[str, str], dict] = {}
    for r in rows:   # the last answer per (candidate, seat) wins: a rerun replaces an old prompt
        latest[(r["candidate"], r["seat"])] = r
    by_c: dict[str, list[dict]] = {}
    for r in latest.values():
        by_c.setdefault(r["candidate"], []).append(r)
    capped = cap_champions(rubric, latest)
    seats = sorted({r["seat"] for r in latest.values() if r["role"] == "judge"})
    meta = {c["id"]: c for c in cands}

    per = {}
    for cid, rs in sorted(by_c.items()):
        judges = [r for r in rs if r["role"] == "judge"]
        if not judges:
            continue
        med = {k: statistics.median(r["scores"][k] for r in judges) for k in crit}
        spread = {k: spread_of(kdef[k], [r["scores"][k] for r in judges]) for k in crit}
        cross = [r for r in judges if r["family"] != "anthropic"]   # candidates so far are Claude-written
        entry = {"n_judges": len(judges), "median": med, "spread": spread,
                 "composite": round(composite(med), 4),
                 "contested": [k for k in HEADLINE if k in spread and len(judges) > 1 and spread[k] >= CONTESTED_SPREAD]
                 + (["champion"] if any(r["scores"].get("champion") == 1 for r in judges) else []),
                 "by_seat": {r["seat"]: r["scores"] for r in rs},
                 "objections": {r["seat"]: r["strongest_objection"] for r in rs},
                 "cases": {r["seat"]: r["strongest_case"] for r in rs}}
        if cross and len(cross) < len(judges):
            entry["composite_cross_family"] = round(composite(
                {k: statistics.median(r["scores"][k] for r in cross) for k in crit}), 4)
        for role in ("advocate", "attacker"):
            r = next((x for x in rs if x["role"] == role), None)
            if r:
                entry[role] = round(composite(r["scores"]), 4)
        per[cid] = entry

    # judge agreement per criterion and on the composite: mean pairwise Spearman → n_eff
    agree = {}
    for k in crit + ["composite"]:
        pairs = []
        for i, a in enumerate(seats):
            for b in seats[i + 1:]:
                common = [c for c in per if a in per[c]["by_seat"] and b in per[c]["by_seat"]]
                if len(common) < 5:
                    continue
                f = (lambda s: composite(s)) if k == "composite" else (lambda s, k=k: s[k])
                rho = spearman([f(per[c]["by_seat"][a]) for c in common], [f(per[c]["by_seat"][b]) for c in common])
                if rho is not None:
                    pairs.append({"a": a, "b": b, "rho": round(rho, 3), "n": len(common)})
        mean = statistics.fmean(p["rho"] for p in pairs) if pairs else None
        agree[k] = {"pairs": pairs, "mean_rho": None if mean is None else round(mean, 3),
                    "n_eff": n_eff(len(seats), mean)}

    # minority picks: a judge puts a candidate in its own top quartile while the panel has it in the
    # bottom half. These are the contrarian bets the median would bury.
    minority = []
    ids = list(per)
    if len(ids) >= 8:
        panel_rank = {c: i for i, c in enumerate(sorted(ids, key=lambda c: -per[c]["composite"]))}
        for s in seats:
            own = [c for c in ids if s in per[c]["by_seat"]]
            top = sorted(own, key=lambda c: -composite(per[c]["by_seat"][s]))[:max(1, len(own) // 4)]
            for c in top:
                if panel_rank[c] >= len(ids) / 2:
                    minority.append({"candidate": c, "seat": s, "panel_rank": panel_rank[c] + 1,
                                     "seat_composite": round(composite(per[c]["by_seat"][s]), 3)})

    # comparison with today's single-judge gate scores
    common = [c for c in per if c in meta and gate_scores(meta[c])]
    vs_gate = None
    if len(common) >= 5:
        g = [composite(gate_scores(meta[c])) for c in common]
        p = [per[c]["composite"] for c in common]
        top_g = set(sorted(common, key=lambda c: -composite(gate_scores(meta[c])))[:10])
        top_p = set(sorted(common, key=lambda c: -per[c]["composite"])[:10])
        vs_gate = {"n": len(common), "spearman": round(spearman(g, p), 3),
                   "top10_overlap": len(top_g & top_p),
                   "per_seat_spearman": {s: round(spearman(
                       [composite(gate_scores(meta[c])) for c in common if s in per[c]["by_seat"]],
                       [composite(per[c]["by_seat"][s]) for c in common if s in per[c]["by_seat"]]) or 0, 3)
                       for s in seats}}

    # where tagged bets land, under the gate and under the panel
    def pct_rank(order, c):
        return round(100 * (order.index(c) + 1) / len(order))
    bets = {}
    if tags:
        p_order = sorted(per, key=lambda c: -per[c]["composite"])
        g_order = sorted(common, key=lambda c: -composite(gate_scores(meta[c])))
        for tag in sorted(set(tags.values())):
            mem = [c for c in per if tags.get(c) == tag]
            if not mem:
                continue
            bets[tag] = {"n": len(mem),
                         "panel_mean_percentile": round(statistics.fmean(pct_rank(p_order, c) for c in mem)),
                         "gate_mean_percentile": round(statistics.fmean(pct_rank(g_order, c) for c in mem if c in g_order))
                         if any(c in g_order for c in mem) else None,
                         "median_upside": statistics.median(per[c]["median"].get("upside", 0) for c in mem),
                         "median_plausibility": statistics.median(per[c]["median"]["plausibility"] for c in mem)}

    # twins: the same claim reworded (fixtures with twin_of); a robust panel scores them alike
    twins = []
    for c in cands:
        t = c.get("twin_of")
        if t and c["id"] in per and t in per:
            twins.append({"candidate": c["id"], "twin_of": t, "wording": c.get("wording", ""),
                          "delta_composite": round(per[c["id"]]["composite"] - per[t]["composite"], 4),
                          "delta_by_seat": {s: round(composite(per[c["id"]]["by_seat"][s]) - composite(per[t]["by_seat"][s]), 4)
                                            for s in per[c["id"]]["by_seat"] if s in per[t]["by_seat"]}})
    controls = [{"candidate": c["id"], "expect": c["expect"], "composite": per[c["id"]]["composite"],
                 "percentile": pct_rank(sorted(per, key=lambda x: -per[x]["composite"]), c["id"])}
                for c in cands if c.get("expect") and c["id"] in per]

    return {"rubric": rubric["name"], "judge_seats": seats, "n_candidates": len(per), "champions_capped": capped,
            "agreement": agree, "contested": sorted(c for c in per if per[c]["contested"]),
            "minority_picks": minority, "vs_gate": vs_gate, "bets": bets, "twins": twins,
            "controls": controls, "candidates": per}


def print_report(rep: dict) -> None:
    print(f"rubric {rep['rubric']} · {rep['n_candidates']} candidates · judges: {', '.join(rep['judge_seats'])}")
    print("\nAgreement between judges (mean pairwise Spearman → effective number of independent judges)")
    for k, a in rep["agreement"].items():
        print(f"  {k:<14} rho {a['mean_rho'] if a['mean_rho'] is not None else '-':>6}   n_eff {a['n_eff'] or '-'}")
    if rep["vs_gate"]:
        v = rep["vs_gate"]
        print(f"\nPanel vs today's single-judge gate: Spearman {v['spearman']} on {v['n']}, top-10 overlap {v['top10_overlap']}/10")
        for s, r in v["per_seat_spearman"].items():
            print(f"  {s:<16} vs gate {r}")
    if rep["bets"]:
        print("\nWhere each kind of bet lands (mean percentile, 1 = top)")
        for t, b in rep["bets"].items():
            print(f"  {t:<18} n {b['n']:>2}  panel {b['panel_mean_percentile']:>3}  gate {b['gate_mean_percentile'] or '-':>3}"
                  f"  median upside {b['median_upside']}  median p {b['median_plausibility']}")
    print(f"\nContested ({len(rep['contested'])}): " + ", ".join(rep["contested"]))
    print(f"Minority picks ({len(rep['minority_picks'])}):")
    for m in rep["minority_picks"]:
        print(f"  {m['candidate']} — {m['seat']} puts it in its top quarter; panel rank {m['panel_rank']}")
    if rep["twins"]:
        print("\nWording twins (same claim, different words; 0 = robust)")
        for t in rep["twins"]:
            print(f"  {t['candidate']} vs {t['twin_of']} ({t['wording']}): Δ {t['delta_composite']:+.3f}  {t['delta_by_seat']}")
    if rep["controls"]:
        print("\nControls (expected position)")
        for c in rep["controls"]:
            print(f"  {c['candidate']} expect {c['expect']}: percentile {c['percentile']}  composite {c['composite']}")


def export(rep: dict, out: Path, run_id: str) -> Path:
    """The consumer format of `python -m lab.tools.backlog panel PATH`: one record per (candidate,
    criterion) with median, spread, contested and every judge's score; plus run.json with n_eff."""
    rows = []
    for cid, e in rep["candidates"].items():
        for k, med in e["median"].items():
            rows.append({"id": cid, "criterion": k, "median": med, "spread": e["spread"][k],
                         "contested": k in e["contested"],
                         "scores": {s: v[k] for s, v in e["by_seat"].items() if s in rep["judge_seats"]},
                         "bounds": {s: v[k] for s, v in e["by_seat"].items() if s not in rep["judge_seats"]},
                         "n_eff": rep["agreement"].get(k, {}).get("n_eff"), "run": run_id})
    path = out / "scores.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (out / "run.json").write_text(json.dumps({
        "run": run_id, "rubric": rep["rubric"], "judge_seats": rep["judge_seats"],
        "n_candidates": rep["n_candidates"],
        "n_eff": {k: a["n_eff"] for k, a in rep["agreement"].items()},
        "mean_rho": {k: a["mean_rho"] for k, a in rep["agreement"].items()},
        "contested": rep["contested"], "minority_picks": rep["minority_picks"],
        "champions_capped": rep["champions_capped"], "vs_gate": rep["vs_gate"], "bets": rep["bets"],
        "twins": rep["twins"], "controls": rep["controls"]}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# --- CLI -----------------------------------------------------------------------------------------
def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="lab.tools.panel")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("prompt", "run", "report"):
        p = sub.add_parser(name)
        p.add_argument("--rubric", default="backlog_lanes")
        p.add_argument("--root", type=Path, help="backlog folder (default {OUTPUT_ROOT}/indexes/backlog)")
        p.add_argument("--extra", type=Path, help="extra candidates (controls, wording twins), JSONL")
        if name != "report":
            p.add_argument("--panel", default="default")
        if name == "prompt":
            p.add_argument("candidate")
            p.add_argument("--seat")
        else:
            p.add_argument("--out", type=Path)
        if name == "run":
            p.add_argument("--only", default="")
            p.add_argument("--seats", default="")
            p.add_argument("--workers", type=int, default=6)
            p.add_argument("--limit", type=int)
        if name == "report":
            p.add_argument("--json", action="store_true")
            p.add_argument("--export", metavar="RUN_ID", help="also write scores.jsonl + run.json for backlog.py")
            p.add_argument("--seats", default="", help="only these seats (e.g. the production judges)")
    a = ap.parse_args(argv)
    rubric = load_rubric(a.rubric)
    root = backlog_root(a.root)
    cands, dirs = load_items(root, a.extra)
    if a.cmd == "prompt":
        panel = load_panel(a.panel)
        seat = next((s for s in panel["seats"] if s["id"] == a.seat), panel["seats"][0]) if a.seat else panel["seats"][0]
        c = next((c for c in cands if c["id"] == a.candidate), None)
        if not c:
            raise LabError(f"unknown candidate {a.candidate}")
        print(prompt_for(c, dirs.get(c.get("direction")), rubric, seat["role"]))
        return
    out = a.out or root / "panel" / rubric["name"]
    if a.cmd == "run":
        panel = load_panel(a.panel)
        only = {x for x in a.only.split(",") if x}
        todo = [c for c in cands if not only or c["id"] in only]
        if a.limit:
            todo = todo[:a.limit]
        res = run(panel, rubric, todo, dirs, out, a.workers, {x for x in a.seats.split(",") if x} or None)
        if res["failed"]:
            sys.exit(1)
        return
    rows = [r for p in sorted(out.glob("judgments*.jsonl")) for r in read_jsonl(p)]   # one file per machine
    keep = {x for x in a.seats.split(",") if x}
    rows = [r for r in rows if not keep or r["seat"] in keep]
    rep = report(rubric, rows, cands, read_tags(root))
    if a.export:
        print(f"wrote {export(rep, out, a.export)} and run.json", file=sys.stderr)
    if a.json:
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    else:
        print_report(rep)


if __name__ == "__main__":
    main_wrapper(main)
