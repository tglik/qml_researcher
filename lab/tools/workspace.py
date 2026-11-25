"""Shared study workspace: small studies, announced and critiqued before they run (C16).

A *study* is the lab's smallest unit: one falsifiable claim, run in hours, by one author agent,
with no human checkpoint before release. It borrows the four mechanisms that made the
Agent alphaXiv cohort (arXiv-style "A Society of AI Scientists", Nov 2026) rigorous:
announce and get one peer critique before running; bind every reported number to a file;
run major objections as scripts, not text; audit the code against the title before release.

Files (under {output_root}/workspace/):
    lab.json                     the lab: agenda (ordered backlog candidate ids), budget per study
    log/<stamp>__<sid>__<kind>__<agent>.md      one file per post, append-only (no merge conflicts)
    studies/<sid>/STUDY.md       claim, prediction, disproof, plan  (frozen at lock)
    studies/<sid>/code/ outputs/ objections/    the study's own files
    studies/<sid>/state.json     written only by this tool
    studies/<sid>/ledger.jsonl   every reported number → file + sha256 + command (this tool only)
    studies/<sid>/objections.jsonl   each executable objection and whether it flipped the result
    studies/<sid>/AUDIT.md       clean-context audit by another agent; frontmatter `verdict: PASS|FAIL`
    studies/<sid>/bundle.lock.json   plan hash at lock; whole-bundle hashes at release

    python -m lab.tools.workspace next                         # first agenda candidate not yet studied
    python -m lab.tools.workspace new    --from CID --by AGENT [--title T]
    python -m lab.tools.workspace post   KIND --study SID --by AGENT (--body TEXT | --body-file F)
                                          [--changed yes|no]   # on a response: did the critique change the design
    python -m lab.tools.workspace read   [--study SID] [--kind K] [--last N]
    python -m lab.tools.workspace lock   SID --by AGENT
    python -m lab.tools.workspace amend  SID --by AGENT --reason TEXT      # needs a posted correction
    python -m lab.tools.workspace ledger SID --id ID --value V --file outputs/x.json --command "…"
    python -m lab.tools.workspace objection SID --script objections/x.py --by AGENT --flips yes|no
                                          --note TEXT
    python -m lab.tools.workspace release SID --by AGENT [--cost-usd X] [--outcome supported|refuted|null|mixed]
    python -m lab.tools.workspace status [SID]
    python -m lab.tools.workspace report                       # debrief metrics for the lab

Kinds of post: announce · critique · response · correction · result · note.
Rules this tool enforces:
  - lock needs an announce by the author, ≥1 critique by a different agent, and an author response
    that says whether the design changed;
  - after lock, STUDY.md changes only through `amend`, which needs a correction post first;
  - release needs: plan hash unchanged, ≥1 ledger entry with every file present and unchanged,
    every objection script present, AUDIT.md with `verdict: PASS` by an agent who is neither the
    author nor (if possible) the critic, and the auditor named in its frontmatter;
  - after release, nothing in the study folder changes (the lab guard hook also blocks it).
Agent names are self-reported strings; the tool checks they differ, it cannot check who wrote what.
Scores and rankings are never copied into a study: `new` takes only the candidate's title, claim,
base and, for a bet, its cheapest fatal test (herding: Agent alphaXiv saw 88% of trials crowd the
leader when scores were visible, 30% when hidden).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
from pathlib import Path

from .common import (LabError, main_wrapper, output_root, read_frontmatter, read_json,
                     sha256_file, write_json)

KINDS = ("announce", "critique", "response", "correction", "result", "note")
STATUSES = ("draft", "locked", "released")
OUTCOMES = ("supported", "refuted", "null", "mixed")
FROZEN_AT_LOCK = ("STUDY.md",)
TOOL_FILES = ("state.json", "ledger.jsonl", "objections.jsonl", "bundle.lock.json")
SID_RE = re.compile(r"^s-\d{8}-\d{3}$")
AGENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

STUDY_TEMPLATE = """---
study: {sid}
from: {cid}
author: {by}
direction: {direction}
---
# {title}

## Claim
{claim}

## Why this study (from the backlog)
Source candidate `{cid}`; base: {base}.
{fatal}
## Prediction
<The number you expect, at a named operating point, before any run.>

## Disproof
<The result that would make you say the claim is false. Written now, not after the run.>

## Plan
<Steps, in the cheapest-fatal order. Name the classical baseline and how it is tuned.>

## Budget
<Hours and dollars you will spend at most (lab.json caps them).>
"""


def now() -> str:
    """UTC time to the microsecond: posts, locks and amendments are ordered by it."""
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds")


# --- paths -------------------------------------------------------------------------------------
def ws() -> Path:
    return output_root() / "workspace"


def study_dir(sid: str) -> Path:
    if not SID_RE.match(sid):
        raise LabError(f"bad study id {sid!r} (expected s-YYYYMMDD-NNN)")
    d = ws() / "studies" / sid
    if not (d / "state.json").exists():
        raise LabError(f"no study {sid} under {ws() / 'studies'}")
    return d


def lab_config() -> dict:
    p = ws() / "lab.json"
    if not p.exists():
        raise LabError(f"no lab config at {p}; create it with an agenda (see docs/lab/components/C16)")
    return read_json(p)


def state(sid: str) -> dict:
    return read_json(study_dir(sid) / "state.json")


def save_state(sid: str, st: dict) -> None:
    write_json(study_dir(sid) / "state.json", st)


def all_states() -> list[dict]:
    root = ws() / "studies"
    return [read_json(p) for p in sorted(root.glob("s-*/state.json"))] if root.exists() else []


def check_agent(name: str) -> str:
    if not AGENT_RE.match(name or ""):
        raise LabError(f"bad agent name {name!r}: letters, digits, . _ - only")
    return name


# --- log ---------------------------------------------------------------------------------------
def posts(sid: str | None = None, kind: str | None = None) -> list[dict]:
    root = ws() / "log"
    out = []
    for p in sorted(root.glob("*.md")) if root.exists() else []:
        fm, body = read_frontmatter(p)
        if (sid and fm.get("study") != sid) or (kind and fm.get("kind") != kind):
            continue
        out.append({**fm, "body": body.strip(), "file": p.name})
    return out


def write_post(kind: str, sid: str, by: str, body: str, extra: dict | None = None) -> Path:
    if kind not in KINDS:
        raise LabError(f"kind must be one of {KINDS}")
    if not body.strip():
        raise LabError("a post needs a body")
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = ws() / "log" / f"{stamp}__{sid}__{kind}__{by}.md"
    fm = {"kind": kind, "study": sid, "by": by, "at": now(), **(extra or {})}
    head = "\n".join(f"{k}: {v}" for k, v in fm.items())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{head}\n---\n{body.strip()}\n", encoding="utf-8")
    return path


# --- hashing -----------------------------------------------------------------------------------
def plan_hash(d: Path) -> dict:
    return {n: sha256_file(d / n) for n in FROZEN_AT_LOCK if (d / n).exists()}


def bundle_hashes(d: Path) -> dict:
    return {p.relative_to(d).as_posix(): sha256_file(p) for p in sorted(d.rglob("*"))
            if p.is_file() and p.name != "bundle.lock.json"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] \
        if path.exists() else []


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# --- commands ----------------------------------------------------------------------------------
def load_candidate(cid: str) -> dict:
    path = output_root() / "indexes" / "backlog" / "candidates.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
        c = json.loads(line)
        if c["id"] == cid:
            return c
    raise LabError(f"candidate {cid} not in {path}")


def fatal_test(cid: str) -> str:
    p = output_root() / "indexes" / "backlog" / "bet_sheets" / f"{cid}.json"
    if not p.exists():
        return ""
    sheet = read_json(p)
    return (f"This is a bet. Study its cheapest fatal test first ({sheet.get('fatal_test_days', '?')} days "
            f"budgeted): {sheet.get('fatal_test', '')}\n") if sheet.get("fatal_test") else ""


def cmd_next() -> str | None:
    studied = {s["from"] for s in all_states()}
    for cid in lab_config().get("agenda", []):
        if cid not in studied:
            return cid
    return None


def new_sid() -> str:
    day = _dt.date.today().strftime("%Y%m%d")
    root = ws() / "studies"
    n = len(list(root.glob(f"s-{day}-*"))) + 1 if root.exists() else 1
    return f"s-{day}-{n:03d}"


def cmd_new(cid: str, by: str, title: str | None) -> str:
    check_agent(by)
    if cid not in lab_config().get("agenda", []):
        raise LabError(f"{cid} is not on the lab agenda in lab.json; a person adds it there first")
    if any(s["from"] == cid and s["status"] != "released" for s in all_states()):
        raise LabError(f"{cid} already has a study in progress")
    c = load_candidate(cid)
    sid = new_sid()
    d = ws() / "studies" / sid
    for sub in ("code", "outputs", "objections"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "STUDY.md").write_text(STUDY_TEMPLATE.format(
        sid=sid, cid=cid, by=by, direction=c.get("direction") or "unassigned",
        title=title or c["title"], claim=c["claim"], base=c.get("base") or "none",
        fatal=fatal_test(cid)), encoding="utf-8")
    write_json(d / "state.json", {"sid": sid, "from": cid, "author": by, "status": "draft",
                                  "created": now(), "events": [["new", by, now()]]})
    return sid


def cmd_post(kind: str, sid: str, by: str, body: str, changed: str | None) -> Path:
    check_agent(by)
    st = state(sid)
    extra = {}
    if kind == "announce":
        if by != st["author"]:
            raise LabError("only the study's author announces it")
        if st["status"] != "draft":
            raise LabError("announce before lock")
    if kind == "critique":
        if by == st["author"]:
            raise LabError("a critique must come from a different agent than the author")
        if not posts(sid, "announce"):
            raise LabError("critique an announced study (no announce post yet)")
    if kind == "response":
        if by != st["author"]:
            raise LabError("only the author responds to critiques")
        if changed not in ("yes", "no"):
            raise LabError("a response needs --changed yes|no: did the critique change the design?")
        extra["changed"] = changed
    if kind == "correction" and by != st["author"]:
        raise LabError("a correction is the author's own retraction or revision of a claim")
    if st["status"] == "released" and kind not in ("note", "correction"):
        raise LabError(f"{sid} is released; only notes and corrections can follow")
    return write_post(kind, sid, by, body, extra)


def cmd_lock(sid: str, by: str) -> dict:
    st = state(sid)
    d = study_dir(sid)
    if st["status"] != "draft":
        raise LabError(f"{sid} is {st['status']}, not draft")
    if by != st["author"]:
        raise LabError("the author locks the plan")
    if not posts(sid, "announce"):
        raise LabError("lock needs an announce post first")
    critics = {p["by"] for p in posts(sid, "critique") if p["by"] != st["author"]}
    if not critics:
        raise LabError("lock needs at least one critique from a different agent")
    if not posts(sid, "response"):
        raise LabError("lock needs an author response to the critique (--changed yes|no)")
    text = (d / "STUDY.md").read_text(encoding="utf-8")
    for heading in ("## Prediction", "## Disproof", "## Plan"):
        section = text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in text else ""
        if not section.strip() or section.strip().startswith("<"):
            raise LabError(f"STUDY.md {heading[3:]} is still the template; write it before locking")
    write_json(d / "bundle.lock.json", {"locked_at": now(), "locked_by": by, "plan": plan_hash(d),
                                        "critics": sorted(critics), "amendments": []})
    st.update(status="locked", locked=now(), critics=sorted(critics))
    st["events"].append(["lock", by, now()])
    save_state(sid, st)
    return st


def cmd_amend(sid: str, by: str, reason: str) -> None:
    st = state(sid)
    d = study_dir(sid)
    if st["status"] != "locked":
        raise LabError("amend applies to a locked study")
    if by != st["author"]:
        raise LabError("only the author amends")
    lock = read_json(d / "bundle.lock.json")
    last = max([lock["locked_at"]] + [a["at"] for a in lock["amendments"]])
    if not [p for p in posts(sid, "correction") if p.get("at", "") > last]:
        raise LabError("post a correction explaining the change before amending the plan")
    if ledger_rows(d):
        raise LabError("numbers are already in the ledger; a plan change now is a new study, not an amendment")
    lock["amendments"].append({"at": now(), "by": by, "reason": reason, "plan": plan_hash(d)})
    write_json(d / "bundle.lock.json", lock)
    st["events"].append(["amend", by, now()])
    save_state(sid, st)


def current_plan(lock: dict) -> dict:
    return lock["amendments"][-1]["plan"] if lock.get("amendments") else lock["plan"]


def ledger_rows(d: Path) -> list[dict]:
    return read_jsonl(d / "ledger.jsonl")


def cmd_ledger(sid: str, nid: str, value: str, file: str, command: str) -> dict:
    st = state(sid)
    d = study_dir(sid)
    if st["status"] != "locked":
        raise LabError("record numbers after lock and before release")
    target = (d / file).resolve()
    if d.resolve() not in target.parents or not target.exists():
        raise LabError(f"--file must be an existing file inside the study folder: {file}")
    if any(r["id"] == nid for r in ledger_rows(d)):
        raise LabError(f"ledger id {nid} already used; ids are unique")
    try:
        val: object = float(value)
    except ValueError:
        val = value
    row = {"id": nid, "value": val, "file": target.relative_to(d.resolve()).as_posix(),
           "sha256": sha256_file(target), "command": command, "at": now()}
    append_jsonl(d / "ledger.jsonl", row)
    return row


def cmd_objection(sid: str, script: str, by: str, flips: str, note: str) -> dict:
    st = state(sid)
    d = study_dir(sid)
    check_agent(by)
    if st["status"] != "locked":
        raise LabError("objections are run on a locked study before release")
    if by == st["author"]:
        raise LabError("an objection comes from someone other than the author")
    if flips not in ("yes", "no"):
        raise LabError("--flips yes|no: did running the script overturn the headline result?")
    path = d / script
    if not script.startswith("objections/") or not path.is_file():
        raise LabError("--script must be an existing file under objections/ — an objection is code that runs")
    row = {"script": script, "sha256": sha256_file(path), "by": by, "flips": flips == "yes",
           "note": note, "at": now()}
    append_jsonl(d / "objections.jsonl", row)
    return row


def cmd_release(sid: str, by: str, cost: float | None, outcome: str | None) -> dict:
    st = state(sid)
    d = study_dir(sid)
    if st["status"] != "locked":
        raise LabError(f"{sid} is {st['status']}; release a locked study")
    if by != st["author"]:
        raise LabError("the author releases")
    lock = read_json(d / "bundle.lock.json")
    if plan_hash(d) != current_plan(lock):
        raise LabError("STUDY.md changed since lock without an amendment")
    rows = ledger_rows(d)
    if not rows:
        raise LabError("release needs at least one ledger entry: every reported number bound to a file")
    bad = [r["id"] for r in rows if not (d / r["file"]).exists() or sha256_file(d / r["file"]) != r["sha256"]]
    if bad:
        raise LabError(f"ledger files missing or changed: {', '.join(bad)}")
    obj = read_jsonl(d / "objections.jsonl")
    gone = [o["script"] for o in obj if not (d / o["script"]).exists()]
    if gone:
        raise LabError(f"objection scripts missing: {', '.join(gone)}")
    if not (d / "AUDIT.md").exists():
        raise LabError("release needs AUDIT.md from a clean-context auditor")
    fm, _ = read_frontmatter(d / "AUDIT.md")
    auditor = fm.get("auditor", "")
    if not auditor or auditor == st["author"]:
        raise LabError("AUDIT.md frontmatter must name an `auditor:` who is not the author")
    if fm.get("verdict") != "PASS":
        raise LabError(f"AUDIT.md verdict is {fm.get('verdict')!r}; release needs PASS "
                       "(a FAIL is fixed in a new study, or posted as a correction)")
    if outcome and outcome not in OUTCOMES:
        raise LabError(f"--outcome must be one of {OUTCOMES}")
    write_json(d / "bundle.lock.json", {**lock, "released_at": now(), "released_by": by,
                                        "bundle": bundle_hashes(d)})
    st.update(status="released", released=now(), auditor=auditor, cost_usd=cost, outcome=outcome)
    st["events"].append(["release", by, now()])
    save_state(sid, st)
    return st


def hours(a: str | None, b: str | None) -> float | None:
    if not a or not b:
        return None
    t = lambda s: _dt.datetime.fromisoformat(s)
    return round((t(b) - t(a)).total_seconds() / 3600, 2)


def cmd_report() -> dict:
    sts = all_states()
    rows = []
    for s in sts:
        sid = s["sid"]
        d = ws() / "studies" / sid
        resp = posts(sid, "response")
        obj = read_jsonl(d / "objections.jsonl")
        ann = posts(sid, "announce")
        rows.append({"sid": sid, "from": s["from"], "status": s["status"], "outcome": s.get("outcome"),
                     "critiques": len(posts(sid, "critique")),
                     "design_changed": any(p.get("changed") == "yes" for p in resp),
                     "corrections": len(posts(sid, "correction")),
                     "objections": len(obj), "objections_flipped": sum(o["flips"] for o in obj),
                     "ledger": len(ledger_rows(d)),
                     "hours_announce_to_release": hours(ann[0]["at"] if ann else None, s.get("released")),
                     "cost_usd": s.get("cost_usd")})
    rel = [r for r in rows if r["status"] == "released"]
    summary = {"studies": len(rows), "released": len(rel),
               "design_changed_by_critique": sum(r["design_changed"] for r in rows),
               "corrections": sum(r["corrections"] for r in rows),
               "objections": sum(r["objections"] for r in rows),
               "objections_flipped": sum(r["objections_flipped"] for r in rows),
               "outcomes": {o: sum(r["outcome"] == o for r in rel) for o in OUTCOMES},
               "cost_usd": round(sum(r["cost_usd"] or 0 for r in rel), 2)}
    return {"summary": summary, "studies": rows}


# --- CLI ---------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("next")
    n = sub.add_parser("new"); n.add_argument("--from", dest="cid", required=True)
    n.add_argument("--by", required=True); n.add_argument("--title")
    p = sub.add_parser("post"); p.add_argument("kind", choices=KINDS); p.add_argument("--study", required=True)
    p.add_argument("--by", required=True); p.add_argument("--body"); p.add_argument("--body-file")
    p.add_argument("--changed", choices=("yes", "no"))
    r = sub.add_parser("read"); r.add_argument("--study"); r.add_argument("--kind", choices=KINDS)
    r.add_argument("--last", type=int, default=50)
    lk = sub.add_parser("lock"); lk.add_argument("sid"); lk.add_argument("--by", required=True)
    am = sub.add_parser("amend"); am.add_argument("sid"); am.add_argument("--by", required=True)
    am.add_argument("--reason", required=True)
    lg = sub.add_parser("ledger"); lg.add_argument("sid"); lg.add_argument("--id", required=True)
    lg.add_argument("--value", required=True); lg.add_argument("--file", required=True)
    lg.add_argument("--command", required=True)
    ob = sub.add_parser("objection"); ob.add_argument("sid"); ob.add_argument("--script", required=True)
    ob.add_argument("--by", required=True); ob.add_argument("--flips", required=True, choices=("yes", "no"))
    ob.add_argument("--note", required=True)
    rl = sub.add_parser("release"); rl.add_argument("sid"); rl.add_argument("--by", required=True)
    rl.add_argument("--cost-usd", type=float); rl.add_argument("--outcome", choices=OUTCOMES)
    stt = sub.add_parser("status"); stt.add_argument("sid", nargs="?")
    sub.add_parser("report")
    a = ap.parse_args()

    if a.cmd == "next":
        cid = cmd_next()
        print(cid or "agenda done: every candidate on lab.json has a study")
    elif a.cmd == "new":
        print(cmd_new(a.cid, a.by, a.title))
    elif a.cmd == "post":
        if bool(a.body) == bool(a.body_file):
            raise LabError("give exactly one of --body or --body-file")
        body = a.body if a.body else Path(a.body_file).read_text(encoding="utf-8")
        print(cmd_post(a.kind, a.study, a.by, body, a.changed).name)
    elif a.cmd == "read":
        for p in posts(a.study, a.kind)[-a.last:]:
            extra = f" changed={p['changed']}" if p.get("changed") else ""
            print(f"--- {p.get('at')}  {p.get('study')}  {p.get('kind')}  by {p.get('by')}{extra}\n{p['body']}\n")
    elif a.cmd == "lock":
        cmd_lock(a.sid, a.by); print(f"{a.sid} locked")
    elif a.cmd == "amend":
        cmd_amend(a.sid, a.by, a.reason); print(f"{a.sid} amended")
    elif a.cmd == "ledger":
        r = cmd_ledger(a.sid, a.id, a.value, a.file, a.command); print(f"ledger {r['id']} = {r['value']}")
    elif a.cmd == "objection":
        cmd_objection(a.sid, a.script, a.by, a.flips, a.note); print("objection recorded")
    elif a.cmd == "release":
        cmd_release(a.sid, a.by, a.cost_usd, a.outcome); print(f"{a.sid} released")
    elif a.cmd == "status":
        for s in ([state(a.sid)] if a.sid else all_states()):
            print(f"{s['sid']}  {s['status']:<9} from {s['from']}  author {s['author']}")
    elif a.cmd == "report":
        print(json.dumps(cmd_report(), indent=2))
    return 0


if __name__ == "__main__":
    main_wrapper(main)
