"""Shared helpers for lab tools: paths, config, JSON/markdown IO, git, hashing."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]          # qml_researcher/
CONFIG = Path(os.environ.get("LAB_CONFIG_DIR", REPO / "config"))   # override for tests
TEMPLATES = REPO / "artifacts" / "lab" / "templates"
SCHEMAS = REPO / "artifacts" / "lab" / "schemas"

CHECKPOINTS = ("CP1", "CP2", "CP3", "CP4", "CP5")
MODES = ("HUMAN_APPROVE", "HUMAN_SPOTCHECK", "AGENT")
OUTCOMES = ("unchanged", "minor", "material")
STAGES = ("intake", "screen", "prereg", "run", "panel2", "verdict", "audit",
          "variants", "promote", "closed")
PHASES = ("P1", "P2", "P3", "P4", "P5")
PHASE_DIRS = {"P1": "P1_toy", "P2": "P2_medium", "P3": "P3_real", "P4": "P4_noise", "P5": "P5_hardware"}
VERDICTS = ("GO", "CONDITIONAL-GO", "NO-GO-FINAL", "NO-GO-PROVISIONAL", "BLOCKED")
LEGACY_VERDICTS = ("GO", "NO_GO", "CLOSED_NO", "CLOSED_YES", "PROVISIONAL")


class LabError(Exception):
    """A rule violation or invalid input. Printed as a one-line error; exit code 1."""


def today() -> str:
    return _dt.date.today().isoformat()


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def output_root() -> Path:
    if os.environ.get("LAB_OUTPUT_ROOT"):                                   # override for tests
        return Path(os.environ["LAB_OUTPUT_ROOT"])
    cfg = json.loads((REPO / "config" / "workspace.json").read_text())
    return Path(cfg["output_root"]).expanduser()


def experiments_root() -> Path:
    return output_root() / "experiments"


def resolve_thread(thread: str | Path) -> Path:
    """Accept an absolute path, a path relative to cwd, or `<thread>/<NN_name>` under experiments/."""
    p = Path(thread).expanduser()
    if p.is_absolute() and p.exists():
        return p
    if p.exists():
        return p.resolve()
    cand = experiments_root() / p
    if cand.exists():
        return cand
    raise LabError(f"thread not found: {thread} (looked in cwd and {experiments_root()})")


def read_json(path: Path):
    return json.loads(Path(path).read_text())


def write_json(path: Path, data) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(cwd: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(cwd), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    """Minimal frontmatter reader: top-level `key: value` lines only (values kept as strings)."""
    text = Path(path).read_text()
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line and not line.startswith((" ", "#")) and ":" in line:
            k, v = line.split(":", 1)
            v = v.split(" #")[0].strip()
            fm[k.strip()] = v.strip('"')
    return fm, text[m.end():]


def parse_list(value: str) -> list[str]:
    """Parse an inline YAML list like `[a, b]`; a bare scalar becomes a one-item list."""
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
    return [v] if v else []


def main_wrapper(fn) -> None:
    """Run a CLI main; turn LabError into a clean one-line failure."""
    try:
        sys.exit(fn() or 0)
    except LabError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
