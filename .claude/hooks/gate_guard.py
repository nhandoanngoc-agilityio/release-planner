#!/usr/bin/env python3
"""PreToolUse hook: no GitHub issues for a kickoff until the user has approved Gate 3.

Creating issues is the one step of a kickoff that others can see and that can't be
quietly undone, so it waits for `intent/<folder>/approvals/gate-3.md`, which only the
user's `approve gate 3` message creates (record_approval.py).

Guarded calls:
- Bash: `gh issue create`, and `gh api` calls that POST to an `issues` endpoint.
- GitHub MCP tools whose name creates or writes an issue (create_issue, issue_write).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kickoff import current_folder, gate_approved, project_dir, read_payload  # noqa: E402

GH_ISSUE_CREATE = re.compile(r"\bgh\s+issue\s+create\b")
GH_API_ISSUES = re.compile(r"\bgh\s+api\b.*\bissues\b")
GH_API_WRITE = re.compile(r"(-X|--method)\s*(POST|PATCH|PUT)|\s-(f|F)\s|--field|--raw-field|--input")
MCP_ISSUE_WRITE = re.compile(r"^mcp__github.*__(create_issue|issue_write|sub_issue_write)$")


def creates_issue(tool: str, tool_input: dict) -> bool:
    if tool == "Bash":
        cmd = tool_input.get("command") or ""
        return bool(GH_ISSUE_CREATE.search(cmd) or (GH_API_ISSUES.search(cmd) and GH_API_WRITE.search(cmd)))
    return bool(MCP_ISSUE_WRITE.match(tool))


def main() -> int:
    payload = read_payload()
    if not creates_issue(payload.get("tool_name") or "", payload.get("tool_input") or {}):
        return 0
    folder = current_folder(project_dir(payload))
    if folder is None or gate_approved(folder, 3):
        return 0  # no kickoff running: ordinary issue work isn't this hook's business
    print(
        "Blocked by kickoff policy: GitHub issues are created only after Gate 3. "
        f"Ask the user to review {folder.name} and type `approve gate 3`.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
