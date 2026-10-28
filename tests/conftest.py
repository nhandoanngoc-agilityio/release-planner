"""Fixtures for the kickoff harness tests: a throwaway project with an active kickoff."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
HOOKS = REPO / ".claude" / "hooks"

GOOD_TICKET = """\
# T-01 Schedule a post for a campaign

Status: draft
Spec: [Posts](../spec.md#behaviour)

## Story

As a marketer
I want to schedule a post on one of my campaign's channels
So that launch content goes out on the right day

## Scenarios

### S1 Post scheduled on a future date

Given the film "Moth" with an active campaign on instagram
When I schedule a post for instagram on 2026-12-01
Then the campaign page lists the post under "Upcoming" dated 2026-12-01

### S2 Channel not in the campaign

Given the campaign for "Moth" uses only instagram
When I schedule a post for tiktok
Then I see the error "This campaign doesn't use tiktok" and nothing is saved

## Out of scope

- Publishing to the real network.

## Questions

- None yet.
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A project root with intent/CURRENT pointing at an intake-stage kickoff."""
    folder = tmp_path / "intent" / "2026-10-28-post-scheduling"
    (folder / "tickets").mkdir(parents=True)
    (tmp_path / "intent" / "CURRENT").write_text("intent/2026-10-28-post-scheduling\n")
    set_state(tmp_path, next="answers", gate="1")
    (tmp_path / ".kickoff-private").mkdir()
    (tmp_path / ".kickoff-private" / "client-truth.md").write_text("# Client truth\n")
    shutil.copytree(REPO / "scripts", tmp_path / "scripts")
    return tmp_path


def kickoff_folder(root: Path) -> Path:
    return root / "intent" / "2026-10-28-post-scheduling"


def set_state(root: Path, next: str, gate: str = "none") -> None:
    (kickoff_folder(root) / "state.md").write_text(
        f"# Kickoff state\n\nnext: {next}\ngate: {gate}\ndev_rounds:\n\n## Log\n"
    )


def run_hook(name: str, payload: dict, root: Path, *args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}
    payload = {"cwd": str(root), **payload}
    return subprocess.run(
        [sys.executable, str(HOOKS / name), *args],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def denied(result: subprocess.CompletedProcess) -> bool:
    if not result.stdout.strip():
        return False
    out = json.loads(result.stdout)
    return out.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
