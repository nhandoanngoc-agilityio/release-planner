"""Shared helpers for the kickoff hooks: where the project is, which kickoff is active, its state.

Hooks receive the tool call or event as JSON on stdin. These helpers never raise on a
missing or malformed kickoff: no kickoff simply means "nothing to guard".
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def read_payload() -> dict:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def project_dir(payload: dict) -> Path:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return Path(root).resolve()


def current_folder(root: Path) -> Path | None:
    """The active intent folder named in intent/CURRENT, if it exists."""
    pointer = root / "intent" / "CURRENT"
    try:
        name = pointer.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    folder = (root / name).resolve()
    return folder if name and folder.is_dir() else None


def read_state(folder: Path | None) -> dict[str, str]:
    """`next`, `gate` and `dev_rounds` from <folder>/state.md; defaults if missing."""
    state = {"next": "brief", "gate": "none", "dev_rounds": ""}
    if folder is None:
        return state
    try:
        text = (folder / "state.md").read_text(encoding="utf-8")
    except OSError:
        return state
    for key in state:
        m = re.search(rf"^{key}:\s*(.*?)\s*$", text, re.M)
        if m:
            state[key] = m.group(1)
    return state


def gate_approved(folder: Path | None, gate: str | int) -> bool:
    return folder is not None and (folder / "approvals" / f"gate-{gate}.md").is_file()


def waiting_gate(folder: Path | None) -> str | None:
    """The gate number the kickoff is stopped at, or None."""
    gate = read_state(folder)["gate"]
    if gate.isdigit() and not gate_approved(folder, gate):
        return gate
    return None


def relative(root: Path, raw: str, cwd: str | None = None) -> str:
    """A tool's path argument as a POSIX path relative to the project ('' if outside it)."""
    if not raw:
        return ""
    path = Path(raw)
    if not path.is_absolute():
        path = Path(cwd or root) / path
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return ""
