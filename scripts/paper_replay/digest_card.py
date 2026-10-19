"""Compact digest of one card's runs and grades, for the per-paper review.

    python scripts/paper_replay/digest_card.py qml-03
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts/paper_replay"))
import run_replay as rr  # noqa: E402


def main() -> int:
    cid = sys.argv[1]
    card = next(c for c in rr.load_cards() if c["id"] == cid)
    out = []
    w = out.append
    w(f"# {cid} {card['title']} | {card['domain']} / {card['profile']} / {card['type']}")
    w(f"expected: {card['expected_verdict'][:300]}")
    cost = 0.0
    for c, comp, arm in rr.matrix([card]):
        d = rr.run_dir(cid, comp, arm)
        for f in (d / "run.json", d / "grade/run.json"):
            if f.exists():
                cost += ((json.loads(f.read_text(encoding="utf-8")).get("usage") or {}).get("total_cost_usd") or 0)
        a = d / "answer.json"
        g = d / "grade/answer.json"
        if not a.exists():
            w(f"\n## {comp}/{arm}: NO ANSWER")
            continue
        ans = json.loads(a.read_text(encoding="utf-8"))
        w(f"\n## {comp}/{arm} — decision: {ans['decision'][:160]}")
        if ans.get("claims"):
            w("claims: " + " | ".join(f"{x['label']}: {x['claim'][:90]}" for x in ans["claims"]))
        if (d / "nondelivered_1").exists():
            w("(first attempt non-delivered; this is the rerun)")
        if not g.exists():
            w("NOT GRADED")
            continue
        gr = json.loads(g.read_text(encoding="utf-8"))
        if comp == "probe":
            w(f"probe: recall={gr['recall']} named={gr['named_adjudicator']} direction={gr['outcome_direction_correct']}"
              f" fabrications={gr['fabrications'][:2]}")
            continue
        crit, mn = rr.reference_items(card, comp)
        w(f"score {gr['score_0_5']} | label {gr['label_match']} | critical {gr['critical_failure']} | "
          f"answer_in_input {gr['answer_in_input']}")
        for c_ in gr["criteria"]:
            text = crit[c_["id"] - 1][:110] if 0 < c_["id"] <= len(crit) else "?"
            w(f"  [{c_['status']:7} att={c_['attainable_from_input']:7}] {text}")
        for k in ("must_not_violations", "errors_or_overclaims", "false_alarms", "key_issues"):
            if gr[k]:
                w(f"  {k}: " + " || ".join((x if isinstance(x, str) else f"#{x['id']} {x['quote']}")[:200] for x in gr[k][:3]))
        w(f"  rationale: {gr['rationale'][:350]}")
    w(f"\ncost so far: ${cost:.2f}")
    # machine-readable scores for the cross-paper report
    scores = {"card": cid, "domain": card["domain"], "profile": card["profile"], "type": card["type"],
              "cost_usd": round(cost, 2), "runs": {}}
    for c, comp, arm in rr.matrix([card]):
        g = rr.run_dir(cid, comp, arm) / "grade/answer.json"
        if not g.exists():
            scores["runs"][f"{comp}/{arm}"] = None
            continue
        gr = json.loads(g.read_text(encoding="utf-8"))
        ans_ = json.loads((rr.run_dir(cid, comp, arm) / "answer.json").read_text(encoding="utf-8"))
        if rr.is_nondelivered(ans_):
            scores["runs"][f"{comp}/{arm}"] = {"nondelivered": True}
            continue
        if comp == "probe":
            scores["runs"][f"{comp}/{arm}"] = {"recall": gr["recall"], "named": gr["named_adjudicator"],
                                               "direction": gr["outcome_direction_correct"]}
        else:
            crit = gr["criteria"]
            scores["runs"][f"{comp}/{arm}"] = {
                "score": gr["score_0_5"], "label_match": gr["label_match"], "critical": gr["critical_failure"],
                "answer_in_input": gr["answer_in_input"],
                "met": sum(x["status"] == "met" for x in crit), "partial": sum(x["status"] == "partial" for x in crit),
                "missed": sum(x["status"] == "missed" for x in crit),
                "unattainable": sum(x["attainable_from_input"] == "no" for x in crit),
                "must_not": len(gr["must_not_violations"]), "false_alarms": len(gr["false_alarms"]),
                "key_issues": len(gr["key_issues"])}
    pdir = rr.OUT / "papers"
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / f"{cid}.scores.json").write_text(json.dumps(scores, indent=1), encoding="utf-8")
    sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
