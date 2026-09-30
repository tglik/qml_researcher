"""Checkpoint sign-off and the autonomy ladder (D4/D5).

    python -m lab.tools.autonomy sign <thread> CP2 --by adi --decision approve|reject
                                      --outcome unchanged|minor|material --minutes 25 [--note "…"]
    python -m lab.tools.autonomy auto <thread> CP1 --decision approve [--note "…"]
                                      # AGENT / HUMAN_SPOTCHECK modes only: the agent records the decision
    python -m lab.tools.autonomy spotcheck <thread> CP1 --by adi --outcome unchanged|minor|material --minutes 5
                                      # a person's later review of an auto-decided checkpoint
    python -m lab.tools.autonomy stats          # per-checkpoint streaks + step-down eligibility
    python -m lab.tools.autonomy eval <eval-id> pass|fail   # record an eval result for the current lab_version
    python -m lab.tools.autonomy step-down CP1 --by tsahi   # only step_down_approvers
    python -m lab.tools.autonomy restore   CP1 --reason "…" # automatic on a material finding; manual here

`outcome` records how much the human changed the agent's artifact before approving:
unchanged | minor (wording, small fixes) | material (a decision, number, scope or gate changed).
Every sign-off appends one row to {output_root}/indexes/autonomy-log.md.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from .common import (CHECKPOINTS, CONFIG, MODES, OUTCOMES, LabError, main_wrapper, now,
                     output_root, read_json, resolve_thread, today, write_json)
from . import state as st_mod

LOG_HEADER = ("# Autonomy log\n\nOne row per human checkpoint decision (QML Lab, D5). Append-only; "
              "written by `python -m lab.tools.autonomy sign`.\n\n"
              "| Date | Program | Checkpoint | Mode | Author | Signer | Decision | Outcome | Minutes | Note |\n"
              "|---|---|---|---|---|---|---|---|---|---|\n")
STATS_MARK = "\n## Stats\n"


def log_path() -> Path:
    return output_root() / "indexes" / "autonomy-log.md"


def config() -> dict:
    return read_json(CONFIG / "lab_autonomy.json")


def _append_row(row: list[str]) -> None:
    p = log_path()
    text = p.read_text() if p.exists() else LOG_HEADER
    body, _, _ = text.partition(STATS_MARK)
    body = body.rstrip("\n") + "\n| " + " | ".join(c.replace("|", "\\|") for c in row) + " |\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)


def read_rows() -> list[dict]:
    p = log_path()
    if not p.exists():
        return []
    rows = []
    body = p.read_text().partition(STATS_MARK)[0]
    for line in body.splitlines():
        if not line.startswith("| 20"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
        keys = ["date", "program", "checkpoint", "mode", "author", "signer", "decision", "outcome", "minutes", "note"]
        rows.append(dict(zip(keys, cells)))
    return rows


def sign(thread: Path, cp: str, by: str, decision: str, outcome: str, minutes: float, note: str) -> dict:
    cfg = config()
    if by not in cfg["people"]:
        raise LabError(f"{by!r} is not a lab signer ({cfg['people']})")
    if outcome not in OUTCOMES:
        raise LabError(f"--outcome must be one of {OUTCOMES}")
    st = st_mod.load(thread)
    key = cp if cp != "CP3" else f"CP3:{st.get('current_phase')}"
    c = st["checkpoints"].get(key)
    if not c or c["status"] != "open":
        raise LabError(f"{key} is not open for {st['thread']}")
    author = c.get("author", "")
    if author == by or author == f"person:{by}":
        raise LabError(f"signer = author ({by}); another person must sign {key}")
    c.update({"status": "approved" if decision == "approve" else "rejected", "signer": by,
              "outcome": outcome, "decision": decision, "minutes": minutes, "closed_at": now()})
    st["history"].append({"at": now(), "event": f"{key} {c['status']} by {by} ({outcome})"})
    st_mod.save(thread, st, f"sign:{by}")
    _append_row([today(), st["thread"], key, c["mode"], author, by, decision, outcome,
                 f"{minutes:g}", note or ""])
    with (thread / "decision_log.md").open("a") as f:
        f.write(f"| {today()} | {key} | {decision} ({outcome}) | {note or ''} | {by} |\n")
    if outcome == "material" and cfg["checkpoints"][cp]["mode"] != "HUMAN_APPROVE":
        restore(cp, f"material finding at {st['thread']} {key}")
    return c


def _human(rows: list[dict], cp: str) -> list[dict]:
    """Rows where a person judged the agent's work (sign-offs and spot-checks), for one checkpoint."""
    return [r for r in rows if r["checkpoint"].split(":")[0] == cp and r["outcome"] in OUTCOMES]


def auto(thread: Path, cp: str, decision: str, note: str) -> dict:
    """Close a checkpoint without a person — allowed only when its current mode permits."""
    st = st_mod.load(thread)
    key = cp if cp != "CP3" else f"CP3:{st.get('current_phase')}"
    c = st["checkpoints"].get(key)
    if not c or c["status"] != "open":
        raise LabError(f"{key} is not open for {st['thread']}")
    if c["mode"] == "HUMAN_APPROVE":
        raise LabError(f"{key} is HUMAN_APPROVE — a person must sign it")
    cfg = config()
    import random
    sampled = c["mode"] == "HUMAN_SPOTCHECK" and random.random() < cfg["spotcheck"]["sample_rate"]
    if c["mode"] == "HUMAN_SPOTCHECK" and cp == "CP4":
        v = (thread / "VERDICT.md").read_text() if (thread / "VERDICT.md").exists() else ""
        sampled = sampled or any(f"verdict: {x}" in v for x in cfg["spotcheck"]["always_review_verdicts"])
    c.update({"status": "approved" if decision == "approve" else "rejected", "signer": "agent",
              "outcome": None, "decision": decision, "minutes": 0, "closed_at": now(),
              "spotcheck": "pending" if sampled else "not-sampled"})
    st["history"].append({"at": now(), "event": f"{key} auto-{decision} ({c['mode']}, spot-check {c['spotcheck']})"})
    st_mod.save(thread, st, "auto")
    _append_row([today(), st["thread"], key, c["mode"], c.get("author", ""), "agent", decision,
                 f"auto ({c['spotcheck']})", "0", note or ""])
    return c


def spotcheck(thread: Path, cp: str, by: str, outcome: str, minutes: float, note: str) -> None:
    cfg = config()
    if by not in cfg["people"]:
        raise LabError(f"{by!r} is not a lab signer")
    st = st_mod.load(thread)
    key = next((k for k, v in st["checkpoints"].items() if k.split(":")[0] == cp and v.get("spotcheck") == "pending"), None)
    if not key:
        raise LabError(f"no pending spot-check for {cp} in {st['thread']}")
    c = st["checkpoints"][key]
    if c.get("author") in (by, f"person:{by}"):
        raise LabError("the author cannot spot-check their own work")
    c["spotcheck"] = f"done:{outcome}"
    st_mod.save(thread, st, f"spotcheck:{by}")
    _append_row([today(), st["thread"], key, c["mode"], c.get("author", ""), by, "spot-check", outcome,
                 f"{minutes:g}", note or ""])
    if outcome == "material":
        restore(cp, f"material spot-check finding at {st['thread']} {key}")


def streak(rows: list[dict], cp: str) -> int:
    n = 0
    for r in reversed(_human(rows, cp)):
        if r["outcome"] == "material":
            break
        n += 1
    return n


def stats() -> list[dict]:
    cfg, rows = config(), read_rows()
    need = cfg["retire_rule"]["consecutive_runs"]
    out = []
    for cp in CHECKPOINTS:
        c = cfg["checkpoints"][cp]
        s = streak(rows, cp)
        evals_ok = all(cfg["eval_status"].get(e, {}).get("result") == "pass"
                       and cfg["eval_status"][e].get("lab_version") == cfg["lab_version"] for e in c["evals"])
        at_target = c["mode"] == c["target"]
        runs = _human(rows, cp)
        mins = sorted(float(r["minutes"]) for r in runs if r["minutes"])
        out.append({"cp": cp, "name": c["name"], "mode": c["mode"], "target": c["target"], "runs": len(runs),
                    "streak": s, "needed": need, "evals_ok": evals_ok,
                    "median_minutes": mins[len(mins) // 2] if mins else None,
                    "eligible": (not at_target) and s >= need and evals_ok})
    _write_stats(out)
    return out


def _write_stats(rows: list[dict]) -> None:
    p = log_path()
    body = (p.read_text() if p.exists() else LOG_HEADER).partition(STATS_MARK)[0].rstrip("\n") + "\n"
    lines = [STATS_MARK, f"*Regenerated {now()} by `python -m lab.tools.autonomy stats`.*\n",
             "| Checkpoint | Mode → target | Runs | Streak (need) | Evals | Median min | Step-down eligible |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        flag = " ⚠ rubber-stamp?" if r["median_minutes"] is not None and r["median_minutes"] < 3 else ""
        lines.append(f"| {r['cp']} {r['name']} | {r['mode']} → {r['target']} | {r['runs']} | {r['streak']} ({r['needed']}) | "
                     f"{'pass' if r['evals_ok'] else 'not yet'} | {r['median_minutes']}{flag} | {'YES' if r['eligible'] else 'no'} |")
    p.write_text(body + "\n".join(lines) + "\n")


def _next_mode(mode: str) -> str:
    return MODES[min(MODES.index(mode) + 1, len(MODES) - 1)]


def step_down(cp: str, by: str) -> str:
    cfg = config()
    if by not in cfg["step_down_approvers"]:
        raise LabError(f"only {cfg['step_down_approvers']} may approve a step-down")
    row = next(r for r in stats() if r["cp"] == cp)
    if not row["eligible"]:
        raise LabError(f"{cp} not eligible: streak {row['streak']}/{row['needed']}, evals {'ok' if row['evals_ok'] else 'missing'}, "
                       f"mode {row['mode']} target {row['target']}")
    old = cfg["checkpoints"][cp]["mode"]
    cfg["checkpoints"][cp]["mode"] = _next_mode(old)
    cfg["history"].append({"date": today(), "cp": cp, "from": old, "to": cfg["checkpoints"][cp]["mode"], "by": by,
                           "evidence": f"streak {row['streak']}, evals pass on {cfg['lab_version']}"})
    write_json(CONFIG / "lab_autonomy.json", cfg)
    return cfg["checkpoints"][cp]["mode"]


def restore(cp: str, reason: str) -> str:
    cfg = config()
    old = cfg["checkpoints"][cp]["mode"]
    if old == "HUMAN_APPROVE":
        return old
    cfg["checkpoints"][cp]["mode"] = MODES[MODES.index(old) - 1]
    cfg["history"].append({"date": today(), "cp": cp, "from": old, "to": cfg["checkpoints"][cp]["mode"],
                           "by": "auto-restore", "evidence": reason})
    write_json(CONFIG / "lab_autonomy.json", cfg)
    return cfg["checkpoints"][cp]["mode"]


def record_eval(eval_id: str, result: str) -> None:
    cfg = config()
    cfg["eval_status"][eval_id] = {"result": result, "lab_version": cfg["lab_version"], "at": now()}
    write_json(CONFIG / "lab_autonomy.json", cfg)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sign"); s.add_argument("thread"); s.add_argument("cp", choices=CHECKPOINTS)
    s.add_argument("--by", required=True); s.add_argument("--decision", required=True, choices=["approve", "reject"])
    s.add_argument("--outcome", required=True); s.add_argument("--minutes", type=float, required=True); s.add_argument("--note", default="")
    sub.add_parser("stats")
    au = sub.add_parser("auto"); au.add_argument("thread"); au.add_argument("cp", choices=CHECKPOINTS)
    au.add_argument("--decision", required=True, choices=["approve", "reject"]); au.add_argument("--note", default="")
    sc = sub.add_parser("spotcheck"); sc.add_argument("thread"); sc.add_argument("cp", choices=CHECKPOINTS)
    sc.add_argument("--by", required=True); sc.add_argument("--outcome", required=True, choices=list(OUTCOMES))
    sc.add_argument("--minutes", type=float, required=True); sc.add_argument("--note", default="")
    e = sub.add_parser("eval"); e.add_argument("eval_id"); e.add_argument("result", choices=["pass", "fail"])
    d = sub.add_parser("step-down"); d.add_argument("cp", choices=CHECKPOINTS); d.add_argument("--by", required=True)
    r = sub.add_parser("restore"); r.add_argument("cp", choices=CHECKPOINTS); r.add_argument("--reason", required=True)
    a = ap.parse_args()
    if a.cmd == "sign":
        c = sign(resolve_thread(a.thread), a.cp, a.by, a.decision, a.outcome, a.minutes, a.note)
        print(f"{a.cp} {c['status']} by {a.by} ({a.outcome}); logged to {log_path()}")
    elif a.cmd == "auto":
        c = auto(resolve_thread(a.thread), a.cp, a.decision, a.note)
        print(f"{a.cp} auto-{a.decision} ({c['mode']}); spot-check {c['spotcheck']}")
    elif a.cmd == "spotcheck":
        spotcheck(resolve_thread(a.thread), a.cp, a.by, a.outcome, a.minutes, a.note); print("spot-check logged")
    elif a.cmd == "stats":
        for r in stats():
            print(f"{r['cp']} {r['name']:<10} {r['mode']:<16}→ {r['target']:<16} runs={r['runs']} "
                  f"streak={r['streak']}/{r['needed']} evals={'ok' if r['evals_ok'] else '—'} eligible={'YES' if r['eligible'] else 'no'}")
    elif a.cmd == "eval":
        record_eval(a.eval_id, a.result); print(f"recorded {a.eval_id}={a.result}")
    elif a.cmd == "step-down":
        print(f"{a.cp} now {step_down(a.cp, a.by)}")
    elif a.cmd == "restore":
        print(f"{a.cp} now {restore(a.cp, a.reason)}")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
