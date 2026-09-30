"""Program control state (STATE.json). Every lab skill reads it first and writes it last.

    python -m lab.tools.state new       <thread-path> --owner meir --path algorithm|use-case
    python -m lab.tools.state validate  <thread>
    python -m lab.tools.state show      <thread>
    python -m lab.tools.state set       <thread> --by /qml-screen [--stage screen] [--phase P1]
                                        [--frozen-question "…"] [--phases P1,P2,P3]
    python -m lab.tools.state open-cp   <thread> CP1 --author agent:screen-analyst --brief briefs/…md
    python -m lab.tools.state budget    <thread> --phase P1 --planned cpu_h=40,wall_days=3
    python -m lab.tools.state spend     <thread> --phase P1 cpu_h=2.5,tokens_m=0.4
    python -m lab.tools.state block     <thread> --what "…" --command "…"
    python -m lab.tools.state escalate  <thread> --type budget_2x --to adi --brief briefs/…md
    python -m lab.tools.state check     <thread> --need lock|cp:CP1|stage:prereg|file:SCREEN.md

`stage` changes only through /qml-lab. `check` exits non-zero with the missing precondition —
skills call it before doing work.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .common import (CHECKPOINTS, CONFIG, PHASES, STAGES, TEMPLATES, LabError, git, main_wrapper,
                     now, read_json, resolve_thread, write_json)
from .validate import validate_json


def load(thread: Path) -> dict:
    path = thread / "STATE.json"
    if not path.exists():
        raise LabError(f"no STATE.json in {thread} — create the program with `/qml-lab new`")
    errs = validate_json(path, "state")
    if errs:
        raise LabError("STATE.json invalid:\n  " + "\n  ".join(errs))
    return read_json(path)


def save(thread: Path, state: dict, by: str) -> None:
    state["updated_by"], state["updated_at"] = by, now()
    write_json(thread / "STATE.json", state)
    errs = validate_json(thread / "STATE.json", "state")
    if errs:
        raise LabError("refusing to leave an invalid STATE.json:\n  " + "\n  ".join(errs))


def new(thread: Path, owner: str, entry_path: str) -> dict:
    if (thread / "STATE.json").exists():
        raise LabError(f"{thread} already has a STATE.json")
    for d in ("00_inputs", "briefs"):
        (thread / d).mkdir(parents=True, exist_ok=True)
    rel = thread.name if thread.parent.name == "experiments" else f"{thread.parent.name}/{thread.name}"
    state = {"schema": "qml-lab/state@1", "thread": rel,
             "branch": "lab/" + rel.replace("/", "-"), "owner": owner, "entry_path": entry_path,
             "frozen_question": None, "stage": "intake", "current_phase": None, "phases_planned": [],
             "checkpoints": {}, "lock": None, "budget": {"planned": {}, "spent": {}},
             "blockers": [], "escalations": [], "history": [{"at": now(), "event": "created", "by": owner}],
             "updated_by": "/qml-lab new", "updated_at": now()}
    save(thread, state, "/qml-lab new")
    for name in ("decision_log.md", "change_log.md", "env.md"):
        p = thread / name
        if not p.exists():
            title = {"decision_log.md": "Decision log\n\n| Date | Stage | Decision | Reason | Who |\n|---|---|---|---|---|\n",
                     "change_log.md": "Change log\n\n| Date | What changed | Why | Effect on conclusions |\n|---|---|---|---|\n",
                     "env.md": "Environment\n\n"}[name]
            p.write_text(f"# {title}")
    return state


def checkpoint_mode(cp: str) -> str:
    cfg = read_json(CONFIG / "lab_autonomy.json")
    return cfg["checkpoints"][cp]["mode"]


def open_cp(thread: Path, cp: str, author: str, brief: str | None) -> dict:
    if cp not in CHECKPOINTS:
        raise LabError(f"unknown checkpoint {cp}")
    st = load(thread)
    key = cp if cp != "CP3" else f"CP3:{st.get('current_phase')}"
    if key in st["checkpoints"] and st["checkpoints"][key]["status"] == "open":
        raise LabError(f"{key} is already open")
    st["checkpoints"][key] = {"mode": checkpoint_mode(cp), "status": "open", "author": author,
                              "signer": None, "outcome": None, "decision": None, "minutes": None,
                              "brief": brief, "opened_at": now(), "closed_at": None}
    st["history"].append({"at": now(), "event": f"open {key}", "mode": st["checkpoints"][key]["mode"]})
    save(thread, st, "/qml-lab")
    return st["checkpoints"][key]


def check(thread: Path, need: str) -> None:
    st = load(thread)
    kind, _, arg = need.partition(":")
    if kind == "lock":
        if not (thread / "PREREG.lock.json").exists():
            raise LabError("precondition failed: the pre-registration is not frozen (no PREREG.lock.json) — CP2 first")
        from .lock import verify
        verify(thread)
    elif kind == "cp":
        approved = [k for k, v in st["checkpoints"].items() if k.split(":")[0] == arg.split(":")[0]
                    and (":" not in arg or k == arg) and v["status"] == "approved"]
        if not approved:
            raise LabError(f"precondition failed: checkpoint {arg} not approved")
    elif kind == "stage":
        if st["stage"] != arg:
            raise LabError(f"precondition failed: stage is '{st['stage']}', this step needs '{arg}'")
    elif kind == "file":
        if not (thread / arg).exists():
            raise LabError(f"precondition failed: {arg} does not exist")
    else:
        raise LabError(f"unknown precondition {need}")


def _kv(s: str) -> dict:
    out = {}
    for part in s.split(","):
        if part.strip():
            k, v = part.split("=", 1)
            out[k.strip()] = float(v)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("thread"); n.add_argument("--owner", required=True)
    n.add_argument("--path", required=True, choices=["algorithm", "use-case"])
    for c in ("validate", "show"):
        sub.add_parser(c).add_argument("thread")
    s = sub.add_parser("set"); s.add_argument("thread"); s.add_argument("--by", required=True)
    s.add_argument("--stage", choices=STAGES); s.add_argument("--phase", choices=PHASES)
    s.add_argument("--frozen-question"); s.add_argument("--phases")
    o = sub.add_parser("open-cp"); o.add_argument("thread"); o.add_argument("cp")
    o.add_argument("--author", required=True); o.add_argument("--brief")
    b = sub.add_parser("budget"); b.add_argument("thread"); b.add_argument("--phase", required=True); b.add_argument("--planned", required=True)
    sp = sub.add_parser("spend"); sp.add_argument("thread"); sp.add_argument("--phase", required=True); sp.add_argument("amounts")
    bl = sub.add_parser("block"); bl.add_argument("thread"); bl.add_argument("--what", required=True); bl.add_argument("--command", default="")
    e = sub.add_parser("escalate"); e.add_argument("thread"); e.add_argument("--type", required=True)
    e.add_argument("--to", required=True); e.add_argument("--brief", default="")
    ch = sub.add_parser("check"); ch.add_argument("thread"); ch.add_argument("--need", required=True)
    a = ap.parse_args()

    if a.cmd == "new":
        t = Path(a.thread).expanduser().resolve()
        st = new(t, a.owner, a.path)
        print(f"created {t}/STATE.json (branch {st['branch']})")
        return 0
    thread = resolve_thread(a.thread)
    if a.cmd == "validate":
        load(thread); print("STATE.json valid")
    elif a.cmd == "show":
        st = load(thread)
        print(f"{st['thread']}  owner={st['owner']}  stage={st['stage']}  phase={st['current_phase']}")
        for k, v in st["checkpoints"].items():
            print(f"  {k:<8} {v['status']:<9} {v['mode']:<16} author={v.get('author')} signer={v.get('signer')}")
        for esc in st["escalations"]:
            if esc["status"] == "open":
                print(f"  ESCALATION {esc['type']} → {esc.get('to')}  {esc.get('brief', '')}")
    elif a.cmd == "set":
        st = load(thread)
        if a.stage:
            st["history"].append({"at": now(), "event": f"stage {st['stage']} → {a.stage}", "by": a.by})
            st["stage"] = a.stage
        if a.phase:
            st["current_phase"] = a.phase
            st["history"].append({"at": now(), "event": f"phase {a.phase} started", "commit": git(thread, "rev-parse", "HEAD")})
        if a.frozen_question:
            st["frozen_question"] = a.frozen_question
        if a.phases:
            st["phases_planned"] = [p.strip() for p in a.phases.split(",")]
        save(thread, st, a.by); print("STATE updated")
    elif a.cmd == "open-cp":
        cp = open_cp(thread, a.cp, a.author, a.brief)
        print(f"{a.cp} open, mode {cp['mode']}")
    elif a.cmd == "budget":
        st = load(thread); st["budget"]["planned"][a.phase] = _kv(a.planned); save(thread, st, "/qml-prereg")
        print("budget planned")
    elif a.cmd == "spend":
        st = load(thread)
        cur = st["budget"]["spent"].setdefault(a.phase, {})
        for k, v in _kv(a.amounts).items():
            cur[k] = cur.get(k, 0) + v
        planned = st["budget"]["planned"].get(a.phase, {})
        over = [k for k, v in cur.items() if planned.get(k) and v > 2 * planned[k]]
        save(thread, st, "/qml-run")
        if over:
            raise LabError(f"budget_2x: {a.phase} spent more than twice the plan on {over} — halt and escalate")
        print("spend recorded")
    elif a.cmd == "block":
        st = load(thread); st["blockers"].append({"what": a.what, "command": a.command, "since": now()})
        save(thread, st, "blocker"); print("blocker recorded")
    elif a.cmd == "escalate":
        st = load(thread)
        st["escalations"].append({"type": a.type, "to": a.to, "brief": a.brief, "status": "open", "at": now()})
        save(thread, st, "/qml-lab"); print(f"escalation {a.type} → {a.to}")
    elif a.cmd == "check":
        check(thread, a.need); print(f"ok: {a.need}")
    return 0


if __name__ == "__main__":
    main_wrapper(main)
