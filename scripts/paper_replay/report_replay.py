"""Aggregate a paper-replay run into tables for the lab analysis and the validation analysis.

    python scripts/paper_replay/report_replay.py            # writes rows.csv, summary.json, summary.md
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
import statistics as st
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts/paper_replay"))
import run_replay as rr  # noqa: E402

STATUS = {"met": 1.0, "partial": 0.5, "missed": 0.0}


def load_rows() -> list[dict]:
    cards = {c["id"]: c for c in rr.load_cards()}
    rows = []
    for card, comp, arm in rr.matrix(list(cards.values())):
        d = rr.run_dir(card["id"], comp, arm)
        run = json.loads((d / "run.json").read_text(encoding="utf-8")) if (d / "run.json").exists() else {}
        grade_f = d / "grade/answer.json"
        g = json.loads(grade_f.read_text(encoding="utf-8")) if grade_f.exists() else None
        cand_f = d / "answer.json"
        cand = json.loads(cand_f.read_text(encoding="utf-8")) if cand_f.exists() else None
        usage = (run.get("usage") or {})
        grun = json.loads((d / "grade/run.json").read_text(encoding="utf-8")) if (d / "grade/run.json").exists() else {}
        row = {"card": card["id"], "domain": card["domain"], "profile": card["profile"], "type": card["type"],
               "component": comp, "arm": arm, "completed": bool(cand), "graded": bool(g),
               "seconds": run.get("seconds"), "cost_usd": (usage.get("total_cost_usd") or 0)
               + ((grun.get("usage") or {}).get("total_cost_usd") or 0),
               "decision": (cand or {}).get("decision", "")[:80]}
        if g and comp == "probe":
            row.update(recall=g["recall"], named_adjudicator=g["named_adjudicator"],
                       direction=g["outcome_direction_correct"], fabrications=len(g["fabrications"]))
        elif g:
            crit = g["criteria"]
            att_no = [c for c in crit if c["attainable_from_input"] == "no"]
            att_yes = [c for c in crit if c["attainable_from_input"] != "no"]
            row.update(
                score=g["score_0_5"], critical=g["critical_failure"], label_match=g["label_match"],
                coverage=round(st.mean(STATUS[c["status"]] for c in crit), 3) if crit else None,
                coverage_attainable=round(st.mean(STATUS[c["status"]] for c in att_yes), 3) if att_yes else None,
                n_criteria=len(crit), n_unattainable=len(att_no),
                unattainable_met=sum(STATUS[c["status"]] for c in att_no),
                must_not=len(g["must_not_violations"]), errors=len(g["errors_or_overclaims"]),
                false_alarms=len(g["false_alarms"]), extras=len(g["extra_valuable_points"]),
                answer_in_input=g["answer_in_input"], key_issues=len(g["key_issues"]),
                rationale=g["rationale"].replace("\n", " ")[:400])
        rows.append(row)
    return rows


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 2) if xs else None


def summarize(rows: list[dict]) -> dict:
    graded = [r for r in rows if r.get("score") is not None]
    by = defaultdict(list)
    for r in graded:
        by[(r["component"], r["arm"])].append(r)
    comp_table = []
    for (comp, arm), rs in sorted(by.items()):
        comp_table.append({
            "component": comp, "arm": arm, "n": len(rs), "score": mean(r["score"] for r in rs),
            "coverage": mean(r["coverage"] for r in rs),
            "coverage_attainable": mean(r["coverage_attainable"] for r in rs),
            "critical_rate": round(sum(r["critical"] for r in rs) / len(rs), 2),
            "must_not": sum(r["must_not"] for r in rs), "errors": sum(r["errors"] for r in rs),
            "false_alarms": sum(r["false_alarms"] for r in rs), "extras": mean(r["extras"] for r in rs),
            "label_match": {k: sum(r["label_match"] == k for r in rs) for k in ("match", "partial", "mismatch")}
            if comp.startswith("verdict") else None,
            "answer_in_input": {k: sum(r["answer_in_input"] == k for r in rs) for k in ("none", "partial", "full")},
            "score_le3": sum(r["score"] <= 3 for r in rs)})
    # domain x component (lab)
    dom = defaultdict(list)
    for r in graded:
        if r["arm"] == "lab":
            dom[(r["domain"], r["component"])].append(r["score"])
    domain_table = {f"{d}|{c}": mean(v) for (d, c), v in sorted(dom.items())}
    # lab vs direct
    pairs = []
    idx = {(r["card"], r["component"], r["arm"]): r for r in graded}
    for (card, comp, arm), r in idx.items():
        if arm == "direct" and (card, comp, "lab") in idx:
            lab = idx[(card, comp, "lab")]
            pairs.append({"card": card, "component": comp, "lab": lab["score"], "direct": r["score"],
                          "delta": lab["score"] - r["score"], "lab_cov": lab["coverage"], "direct_cov": r["coverage"]})
    pair_summary = {}
    for comp in sorted({p["component"] for p in pairs}):
        ps = [p for p in pairs if p["component"] == comp]
        pair_summary[comp] = {"n": len(ps), "lab_mean": mean(p["lab"] for p in ps),
                              "direct_mean": mean(p["direct"] for p in ps), "mean_delta": mean(p["delta"] for p in ps),
                              "lab_better": sum(p["delta"] > 0 for p in ps), "tie": sum(p["delta"] == 0 for p in ps),
                              "direct_better": sum(p["delta"] < 0 for p in ps),
                              "cov_delta": mean((p["lab_cov"] or 0) - (p["direct_cov"] or 0) for p in ps)}
    # probes
    probes = {r["card"]: r for r in rows if r["component"] == "probe" and r.get("recall")}
    # per-paper informativeness
    per_paper = []
    for card in sorted({r["card"] for r in rows}):
        rs = [r for r in graded if r["card"] == card]
        lab = [r for r in rs if r["arm"] == "lab"]
        if not lab:
            continue
        p = probes.get(card, {})
        vh = idx.get((card, "verdict_hist", "lab"))
        deltas = [x["delta"] for x in pairs if x["card"] == card]
        leak = [r["answer_in_input"] for r in lab]
        per_paper.append({
            "card": card, "domain": lab[0]["domain"], "profile": lab[0]["profile"],
            "lab_mean": mean(r["score"] for r in lab), "lab_min": min(r["score"] for r in lab),
            "weak_components": [r["component"] for r in lab if r["score"] <= 3],
            "critical": [r["component"] for r in lab if r["critical"]],
            "probe_recall": p.get("recall"), "probe_named": p.get("named_adjudicator"),
            "verdict_hist_unattainable": (vh or {}).get("n_unattainable"),
            "verdict_hist_unattainable_met": (vh or {}).get("unattainable_met"),
            "leak_full": leak.count("full"), "leak_partial": leak.count("partial"), "n_lab": len(lab),
            "lab_vs_direct": deltas, "key_issues": sum(r["key_issues"] for r in rs),
            "score_spread": round(max(r["score"] for r in lab) - min(r["score"] for r in lab), 1)})
    failures = sorted([r for r in graded if r["score"] <= 3 or r["critical"]],
                      key=lambda r: (r["score"], r["card"]))
    cost = round(sum(r["cost_usd"] or 0 for r in rows), 2)
    nondelivered = sorted(str(p.parent.relative_to(rr.OUT / "runs")).replace("\\", "/")
                          for p in (rr.OUT / "runs").glob("*/*/nondelivered_1"))
    still_nondelivered = [f"{r['card']}/{r['component']}__{r['arm']}" for r in rows
                          if r.get("decision", "").upper().startswith("NOT DELIVERED")]
    return {"n_rows": len(rows), "n_graded": len(graded), "cost_usd": cost,
            "nondelivered_first_attempt": nondelivered, "nondelivered_after_retry": still_nondelivered,
            "components": comp_table, "domain": domain_table, "lab_vs_direct": pair_summary,
            "pairs": pairs, "probe": {k: {"recall": v["recall"], "named": v["named_adjudicator"],
                                          "direction": v["direction"]} for k, v in probes.items()},
            "per_paper": per_paper,
            "failures": [{k: r.get(k) for k in ("card", "component", "arm", "score", "critical", "label_match",
                                               "must_not", "rationale")} for r in failures]}


def main() -> int:
    rows = load_rows()
    out = rr.OUT
    with open(out / "rows.csv", "w", newline="", encoding="utf-8") as f:
        keys = sorted({k for r in rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    s = summarize(rows)
    (out / "summary.json").write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = [f"# Replay summary\n\nrows {s['n_rows']} · graded {s['n_graded']} · cost ${s['cost_usd']}\n",
             "| component | arm | n | score | coverage | cov (attainable) | critical | must-not | errors | false alarms | ≤3 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in s["components"]:
        lines.append(f"| {c['component']} | {c['arm']} | {c['n']} | {c['score']} | {c['coverage']} | "
                     f"{c['coverage_attainable']} | {c['critical_rate']} | {c['must_not']} | {c['errors']} | "
                     f"{c['false_alarms']} | {c['score_le3']} |")
    lines.append("\n## Lab vs direct\n")
    for k, v in s["lab_vs_direct"].items():
        lines.append(f"- {k}: {v}")
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
