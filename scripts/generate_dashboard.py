#!/usr/bin/env python3
"""
generate_dashboard.py — QueLabs Analytics Dashboard generator

Reads: {analytics_folder}/events.jsonl + ~/.hermes/state.db + qml_artifacts git log
Writes: {analytics_folder}/dashboard.md

Run hourly via Hermes cron.
"""

import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent  # qml_researcher/
WORKSPACE_JSON = REPO_ROOT / "config" / "workspace.json"
TEAM_JSON = REPO_ROOT / "config" / "team.json"
STATE_DB = Path.home() / ".hermes" / "state.db"


def load_config():
    with open(WORKSPACE_JSON) as f:
        cfg = json.load(f)
    return Path(cfg["analytics_folder"]), Path(cfg["output_root"])


def load_team():
    if not TEAM_JSON.exists():
        return {"local_user": "Tsahi", "platform_users": {}}
    with open(TEAM_JSON) as f:
        return json.load(f)


def resolve_user(team, source, user_id):
    if source in ("cli", "tui") or not user_id:
        return team.get("local_user", "Tsahi")
    return team.get("platform_users", {}).get(source, {}).get(str(user_id), user_id)


# ── Events reader ──────────────────────────────────────────────────────────

def read_events(events_path: Path, days: int = 30):
    """Read JSONL events, keeping only those within `days` days. Reads full file."""
    if not events_path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    events = []
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = ev.get("ts", "")
            try:
                ev_dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ev_dt < cutoff:
                    continue
            except (ValueError, AttributeError):
                pass
            events.append(ev)

    def sort_key(ev):
        try:
            return datetime.fromisoformat(ev.get("ts", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.min.replace(tzinfo=timezone.utc)

    events.sort(key=sort_key)
    return events


# ── State.db reader ────────────────────────────────────────────────────────

def read_sessions(days: int = 30):
    """Return list of session rows, or None if state.db is unavailable."""
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True, timeout=3)
        conn.execute("PRAGMA busy_timeout = 3000")
        cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
        rows = conn.execute("""
            SELECT source, user_id, model,
                   input_tokens, output_tokens, reasoning_tokens,
                   estimated_cost_usd, started_at, ended_at
            FROM sessions
            WHERE started_at > ?
            ORDER BY started_at DESC
        """, (cutoff_ts,)).fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"  state.db error: {e}", file=sys.stderr)
        return None


# ── Git log reader ─────────────────────────────────────────────────────────

def read_git_activity(repo_path: Path, days: int = 7):
    """Return {card_type: {total, week}} from git log."""
    try:
        new_files_result = subprocess.run(
            ["git", "-C", str(repo_path), "log",
             "--name-only", f"--format=", f"--since={days} days ago", "--diff-filter=A"],
            capture_output=True, text=True, timeout=10
        )
        files_this_week = {
            line.strip() for line in new_files_result.stdout.splitlines()
            if line.strip() and not line.startswith("commit")
        }

        all_files_result = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            capture_output=True, text=True, timeout=10
        )
        all_files = [l.strip() for l in all_files_result.stdout.splitlines() if l.strip()]
    except Exception as e:
        print(f"  git error: {e}", file=sys.stderr)
        return {}

    def count(path_prefix):
        total = sum(1 for f in all_files if f.startswith(path_prefix))
        week = sum(1 for f in files_this_week if f.startswith(path_prefix))
        return {"total": total, "week": week}

    return {
        "paper-cards": count("cards/paper-cards/"),
        "hypotheses": count("cards/hypotheses/"),
        "organizations": count("cards/organizations/"),
        "persons": count("cards/persons/"),
    }


# ── Dashboard renderer ─────────────────────────────────────────────────────

def ts_to_dt(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def fmt_ts(ts_str):
    dt = ts_to_dt(ts_str)
    return dt.strftime("%Y-%m-%d %H:%M") if dt else (ts_str or "—")


def outcome_icon(outcome):
    return {"success": "✅", "done_with_concerns": "⚠️"}.get(outcome, "❌")


def render_dashboard(events, sessions, git_activity, team, generated_at):
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Build run map: run_id → {start, end, errors}
    runs = {}
    for e in events:
        rid = e.get("run_id", "")
        ev_type = e.get("event")
        if rid not in runs:
            runs[rid] = {"start": None, "end": None, "errors": []}
        if ev_type == "skill_start":
            runs[rid]["start"] = e
        elif ev_type == "skill_end":
            runs[rid]["end"] = e
        elif ev_type == "skill_error":
            runs[rid]["errors"].append(e)

    completed = [r for r in runs.values() if r["end"] is not None]
    completed_sorted = sorted(completed, key=lambda r: r["end"].get("ts", ""), reverse=True)

    lines = []
    lines += [
        "---",
        "title: Research Operations Dashboard",
        "tags: [dashboard, analytics]",
        "---",
        "",
        "# Research Operations Dashboard",
        "",
        f"> Generated: {generated_at}  |  Data window: last 30 days",
        "",
    ]

    # 1. Activity Feed
    lines += ["## Activity Feed", ""]
    if not completed_sorted:
        lines.append("_No skill runs recorded yet._")
    else:
        lines += [
            "| Date | Skill | Mode | Outcome | Duration |",
            "|------|-------|------|---------|----------|",
        ]
        for run in completed_sorted[:10]:
            end = run["end"]
            skill = end.get("skill", "—")
            mode = run["start"].get("mode", "—") if run["start"] else "—"
            outcome = end.get("outcome", "—")
            dur = end.get("duration_s")
            lines.append(
                f"| {fmt_ts(end.get('ts',''))} | {skill} | {mode} "
                f"| {outcome_icon(outcome)} {outcome} | {f'{dur}s' if dur is not None else '—'} |"
            )
    lines.append("")

    # 2. This Week
    lines += ["## This Week", ""]
    week_runs = [r for r in completed if
                 ts_to_dt(r["end"].get("ts", "")) and ts_to_dt(r["end"].get("ts", "")) >= week_ago]
    total = len(week_runs)
    success = sum(1 for r in week_runs if r["end"].get("outcome") == "success")
    rate = f"{100 * success // total}%" if total else "—"
    lines.append(f"- **Skill runs:** {total}  |  **Success rate:** {rate}")
    papers = sum(1 for r in week_runs if r["end"].get("skill") in
                 ("qml-paper-review", "qml-deep-research"))
    scouts = sum(1 for r in week_runs if r["end"].get("skill") == "qml-daily-scout")
    extractions = sum(1 for r in week_runs if r["end"].get("skill") == "extract-artifacts")
    lines.append(f"- **Research runs:** {papers}  |  **Scout runs:** {scouts}  |  **Extractions:** {extractions}")
    if git_activity:
        pc = git_activity.get("paper-cards", {})
        hyp = git_activity.get("hypotheses", {})
        lines.append(
            f"- **New paper cards:** +{pc.get('week', 0)} this week "
            f"({pc.get('total', 0)} total)  |  "
            f"**Hypotheses:** +{hyp.get('week', 0)} this week ({hyp.get('total', 0)} total)"
        )
    lines.append("")

    # 3. By Skill
    lines += ["## By Skill (last 30 days)", ""]
    skill_stats: dict = defaultdict(lambda: {"runs": 0, "success": 0, "durs": [], "last": ""})
    for run in completed:
        end = run["end"]
        s = end.get("skill", "unknown")
        skill_stats[s]["runs"] += 1
        if end.get("outcome") == "success":
            skill_stats[s]["success"] += 1
        dur = end.get("duration_s")
        if dur is not None:
            skill_stats[s]["durs"].append(dur)
        if end.get("ts", "") > skill_stats[s]["last"]:
            skill_stats[s]["last"] = end.get("ts", "")

    if skill_stats:
        lines += [
            "| Skill | Runs | Success rate | Avg duration | Last run |",
            "|-------|------|-------------|-------------|---------|",
        ]
        for skill, st in sorted(skill_stats.items()):
            r = f"{100 * st['success'] // st['runs']}%" if st["runs"] else "—"
            avg = f"{sum(st['durs']) // len(st['durs'])}s" if st["durs"] else "—"
            lines.append(f"| {skill} | {st['runs']} | {r} | {avg} | {fmt_ts(st['last'])} |")
    else:
        lines.append("_No data yet._")
    lines.append("")

    # 4. By Interface
    lines += ["## By Interface (state.db, last 30 days)", ""]
    if sessions is None:
        lines.append("_(state.db unavailable — retry next cycle)_")
    elif not sessions:
        lines.append("_No sessions yet._")
    else:
        iface: dict = defaultdict(int)
        for row in sessions:
            src = row[0] or "unknown"
            label = {"cli": "CLI (local)", "tui": "CLI (local)", "slack": "Slack",
                     "telegram": "Telegram", "whatsapp": "WhatsApp",
                     "cron": "Cron (automated)"}.get(src, src)
            iface[label] += 1
        for label, count in sorted(iface.items(), key=lambda x: -x[1]):
            lines.append(f"- **{label}:** {count} session(s)")
    lines.append("")

    # 5. By Team Member
    lines += ["## By Team Member (state.db, last 30 days)", ""]
    if sessions is None:
        lines.append("_(state.db unavailable)_")
    elif not sessions:
        lines.append("_No sessions yet._")
    else:
        members: dict = defaultdict(int)
        for row in sessions:
            members[resolve_user(team, row[0], row[1])] += 1
        for name, count in sorted(members.items(), key=lambda x: -x[1]):
            lines.append(f"- **{name}:** {count} session(s)")
    lines.append("")

    # 6. Token / Cost
    lines += ["## Token / Cost (state.db, last 30 days)", ""]
    if sessions is None:
        lines.append("_(state.db unavailable)_")
    elif not sessions:
        lines.append("_No sessions yet._")
    else:
        total_in = sum(r[3] or 0 for r in sessions)
        total_out = sum(r[4] or 0 for r in sessions)
        total_reasoning = sum(r[5] or 0 for r in sessions)
        total_cost = sum(r[6] or 0 for r in sessions)
        lines.append(f"- **Input tokens:** {total_in:,}")
        lines.append(f"- **Output tokens:** {total_out:,}")
        if total_reasoning:
            lines.append(f"- **Reasoning tokens:** {total_reasoning:,}")
        lines.append(f"- **Estimated cost:** ${total_cost:.4f} USD")
    lines.append("")

    # 7. Artifacts Pulse
    lines += ["## Artifacts Pulse", ""]
    if not git_activity:
        lines.append("_(git log unavailable)_")
    else:
        lines += [
            "| Type | Total | +This week |",
            "|------|-------|-----------|",
        ]
        for key, label in [("paper-cards", "Paper cards"), ("hypotheses", "Hypotheses"),
                            ("organizations", "Organizations"), ("persons", "Persons")]:
            d = git_activity.get(key, {"total": 0, "week": 0})
            lines.append(f"| {label} | {d['total']} | +{d['week']} |")
    lines.append("")

    # 8. Error Log
    lines += ["## Error Log (last 5)", ""]
    errors = [r for r in completed_sorted if r["end"].get("outcome") == "error"]
    if not errors:
        lines.append("_No errors recorded._ ✅")
    else:
        lines += ["| Date | Skill | Error |", "|------|-------|-------|"]
        for run in errors[:5]:
            end = run["end"]
            err_msg = end.get("error_summary") or (
                run["errors"][0].get("error_summary") if run["errors"] else "—"
            )
            lines.append(
                f"| {fmt_ts(end.get('ts',''))} | {end.get('skill','—')} "
                f"| {(err_msg or '—')[:80]} |"
            )
    lines.append("")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    analytics_folder, output_root = load_config()
    team = load_team()

    events_path = analytics_folder / "events.jsonl"
    dashboard_path = analytics_folder / "dashboard.md"

    print(f"Events:    {events_path}")
    events = read_events(events_path)
    print(f"           {len(events)} events in window")

    print(f"state.db:  {STATE_DB}")
    sessions = read_sessions()
    print(f"           {'unavailable' if sessions is None else f'{len(sessions)} sessions'}")

    print(f"git log:   {output_root}")
    git_activity = read_git_activity(output_root)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dashboard = render_dashboard(events, sessions, git_activity, team, generated_at)

    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(dashboard)
    print(f"Dashboard: {dashboard_path}")


if __name__ == "__main__":
    main()
