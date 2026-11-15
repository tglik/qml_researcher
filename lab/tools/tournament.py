"""Pairwise tournament for ranking ideas (candidates) — the scoring half; judges are LLM agents.

Why: absolute value scores (the 0-10 "value score" of the ingest gate) drift with the judge and
favour cheap studies. Pairwise "which of these two would you run first?" judgments are more stable,
and a Bradley-Terry fit turns them into a ranking with uncertainty (as in Google's co-scientist
Elo tournament). Each pair is judged in both orders; a judge that flips with the order counts as a
tie, which removes position bias instead of averaging it in.

Files (JSONL, one object per line):
    candidates:  {"id": "...", "title": "...", "summary": "..."}            (extra keys kept)
    judgments:   {"a": id, "b": id, "winner": "a"|"b"|"tie", "judge": "...", "order": "ab"|"ba",
                  "reason": "..."}   # appended by `record`, never edited

    python -m lab.tools.tournament pairs  <candidates> <judgments> [--max 10]
        # next pairs to judge: Swiss pairing on the current fit, never a pair already judged
        # in that order, deterministic (ties broken by id). Prints JSON [{"a","b","order"}].
    python -m lab.tools.tournament record <judgments> --a X --b Y --winner a|b|tie --judge J --order ab|ba [--reason "…"]
    python -m lab.tools.tournament ingest <judgments> <rows.json> --judge J
        # append a JSON array of {a, b, winner, order, reason} (how the rank-ideas workflow records
        # a round: the rows go through a file, never through shell arguments)
    python -m lab.tools.tournament rank   <candidates> <judgments> [--json]
        # Bradley-Terry (MM algorithm, weak prior of one tie against a virtual average idea),
        # rating on an Elo-like scale, wins/losses/ties, number of comparisons.
    python -m lab.tools.tournament replay <candidates> <judgments> <truth.json> [--k 5]
        # how well the ranking agrees with known outcomes: truth.json {"<id>": <number>}, higher =
        # better (e.g. 1 = experiment reached a publishable/positive result, 0 = killed). Reports
        # Kendall tau-b and precision@k (share of the top k whose outcome is among the k best and
        # above the worst outcome). Use on the closed experiments before trusting the ranker.

No randomness and no network; the same files give the same output.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .common import LabError, main_wrapper

PRIOR = 1.0          # pseudo-comparisons (one tie) against a virtual idea of strength 1
SCALE = 400 / math.log(10)   # Elo-like display scale: +400 = 10x odds


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise LabError(f"{path}:{n}: not JSON ({e})")
    return out


def load(cands_path: Path, judg_path: Path) -> tuple[list[str], list[dict]]:
    cands = read_jsonl(cands_path)
    ids = [c["id"] for c in cands]
    if len(set(ids)) != len(ids):
        raise LabError("duplicate candidate ids")
    known = set(ids)
    judgments = read_jsonl(judg_path)
    for j in judgments:
        if j["a"] not in known or j["b"] not in known:
            raise LabError(f"judgment on unknown candidate: {j['a']} vs {j['b']}")
        if j["winner"] not in ("a", "b", "tie"):
            raise LabError(f"bad winner {j['winner']!r}")
    return ids, judgments


def outcomes(judgments: list[dict]) -> list[tuple[str, str, float]]:
    """(x, y, score of x) per judged pair, after folding both orders together.

    A pair judged in both orders with opposite winners is a tie: the judge followed position, not
    content. Otherwise every judgment counts once."""
    by_pair: dict[tuple[str, str], list[float]] = {}
    for j in judgments:
        x, y = sorted((j["a"], j["b"]))
        s = 0.5 if j["winner"] == "tie" else (1.0 if (j["a"] if j["winner"] == "a" else j["b"]) == x else 0.0)
        by_pair.setdefault((x, y), []).append(s)
    out = []
    for (x, y), scores in sorted(by_pair.items()):
        if len(scores) >= 2 and max(scores) == 1.0 and min(scores) == 0.0 and len(scores) % 2 == 0 \
                and scores.count(1.0) == scores.count(0.0):
            scores = [0.5] * len(scores)
        out.extend((x, y, s) for s in scores)
    return out


def fit(ids: list[str], judgments: list[dict], iters: int = 500) -> dict[str, dict]:
    """Bradley-Terry strengths by Hunter's MM algorithm with a weak prior; returns per-id stats."""
    res = outcomes(judgments)
    w = {i: 1.0 for i in ids}
    wins = {i: PRIOR / 2 for i in ids}   # half a win against the virtual idea
    games: dict[str, list[str]] = {i: [] for i in ids}
    for x, y, s in res:
        wins[x] += s
        wins[y] += 1 - s
        games[x].append(y)
        games[y].append(x)
    for _ in range(iters):
        new = {}
        for i in ids:
            denom = PRIOR / (w[i] + 1.0) + sum(1.0 / (w[i] + w[o]) for o in games[i])
            new[i] = wins[i] / denom
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new))  # fix the scale
        new = {i: v / g for i, v in new.items()}
        if max(abs(new[i] - w[i]) for i in ids) < 1e-10:
            w = new
            break
        w = new
    stats = {}
    for i in ids:
        info = PRIOR * w[i] / (w[i] + 1.0) ** 2 + sum(w[i] * w[o] / (w[i] + w[o]) ** 2 for o in games[i])
        se = 1.0 / math.sqrt(info) if info > 0 else float("inf")
        rec = [s for x, y, s in res if x == i] + [1 - s for x, y, s in res if y == i]
        stats[i] = {"rating": round(1500 + SCALE * math.log(w[i]), 1), "se": round(SCALE * se, 1),
                    "n": len(rec), "w": rec.count(1.0), "l": rec.count(0.0), "t": rec.count(0.5)}
    return stats


def ranking(ids, judgments) -> list[tuple[str, dict]]:
    st = fit(ids, judgments)
    return sorted(st.items(), key=lambda kv: (-kv[1]["rating"], kv[0]))


def next_pairs(ids, judgments, max_pairs: int = 10) -> list[dict]:
    """Swiss pairing: walk the current ranking, pair each idea with the nearest-rated one it has not
    met in that order yet. Both orders of a pair are emitted together so position bias folds out."""
    done = {(j["a"], j["b"]) for j in judgments}
    order = [i for i, _ in ranking(ids, judgments)]
    used: set[str] = set()
    out: list[dict] = []
    for pos, x in enumerate(order):
        if x in used:
            continue
        for y in order[pos + 1:]:
            if y in used:
                continue
            todo = [p for p in ((x, y), (y, x)) if p not in done]
            if todo:
                used.update((x, y))
                out.extend({"a": a, "b": b, "order": "ab" if a == x else "ba"} for a, b in todo)
                break
        if len(out) >= max_pairs:
            break
    return out[:max_pairs]


def kendall_tau_b(xs: list[float], ys: list[float]) -> float:
    conc = disc = tx = ty = 0
    n = len(xs)
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = xs[i] - xs[j], ys[i] - ys[j]
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tx += 1
            elif dy == 0:
                ty += 1
            elif dx * dy > 0:
                conc += 1
            else:
                disc += 1
    denom = math.sqrt((conc + disc + tx) * (conc + disc + ty))
    return (conc - disc) / denom if denom else 0.0


def replay(ids, judgments, truth: dict[str, float], k: int) -> dict:
    ranked = [i for i, _ in ranking(ids, judgments) if i in truth]
    if len(ranked) < 3:
        raise LabError("need at least 3 candidates with a known outcome")
    st = fit(ids, judgments)
    tau = kendall_tau_b([st[i]["rating"] for i in ranked], [truth[i] for i in ranked])
    best = sorted(truth.values(), reverse=True)
    cutoff = best[min(k, len(best)) - 1]
    top = ranked[:k]
    prec = sum(1 for i in top if truth[i] >= cutoff and truth[i] > min(best)) / len(top)
    return {"n": len(ranked), "kendall_tau_b": round(tau, 3), "k": k, "precision_at_k": round(prec, 3),
            "top_k": top}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="lab.tools.tournament")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs"); p.add_argument("candidates"); p.add_argument("judgments"); p.add_argument("--max", type=int, default=10)
    r = sub.add_parser("record"); r.add_argument("judgments")
    for f in ("--a", "--b", "--judge"):
        r.add_argument(f, required=True)
    r.add_argument("--winner", required=True, choices=["a", "b", "tie"])
    r.add_argument("--order", required=True, choices=["ab", "ba"]); r.add_argument("--reason", default="")
    g = sub.add_parser("ingest"); g.add_argument("judgments"); g.add_argument("rows"); g.add_argument("--judge", required=True)
    k = sub.add_parser("rank"); k.add_argument("candidates"); k.add_argument("judgments"); k.add_argument("--json", action="store_true")
    y = sub.add_parser("replay"); y.add_argument("candidates"); y.add_argument("judgments"); y.add_argument("truth")
    y.add_argument("--k", type=int, default=5)
    a = ap.parse_args(argv)

    if a.cmd == "record":
        if a.a == a.b:
            raise LabError("a and b must differ")
        row = {"a": a.a, "b": a.b, "winner": a.winner, "judge": a.judge, "order": a.order, "reason": a.reason}
        with Path(a.judgments).open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"recorded {a.a} vs {a.b}: {a.winner}")
        return
    if a.cmd == "ingest":
        rows = json.loads(Path(a.rows).read_text(encoding="utf-8"))
        with Path(a.judgments).open("a", encoding="utf-8") as f:
            for x in rows:
                if x.get("winner") not in ("a", "b", "tie") or x.get("order") not in ("ab", "ba") or x["a"] == x["b"]:
                    raise LabError(f"bad row {x}")
                row = {"a": x["a"], "b": x["b"], "winner": x["winner"], "judge": a.judge,
                       "order": x["order"], "reason": x.get("reason", "")}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"ingested {len(rows)} judgments")
        return
    ids, judgments = load(Path(a.candidates), Path(a.judgments))
    if a.cmd == "pairs":
        print(json.dumps(next_pairs(ids, judgments, a.max), indent=1))
    elif a.cmd == "rank":
        rows = ranking(ids, judgments)
        if a.json:
            print(json.dumps([{"id": i, **s} for i, s in rows], indent=1))
            return
        print(f"| # | Candidate | Rating | ± | W-L-T | n |\n|---|---|---|---|---|---|")
        for n, (i, s) in enumerate(rows, 1):
            print(f"| {n} | {i} | {s['rating']} | {s['se']} | {s['w']}-{s['l']}-{s['t']} | {s['n']} |")
    elif a.cmd == "replay":
        truth = json.loads(Path(a.truth).read_text(encoding="utf-8"))
        print(json.dumps(replay(ids, judgments, truth, a.k), indent=1))


if __name__ == "__main__":
    main_wrapper(main)
