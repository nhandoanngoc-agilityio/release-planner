#!/usr/bin/env python3
"""PreToolUse hook: keep each kickoff role inside the files it is allowed to see.

The whole point of the kickoff is that roles talk only through files, so a Dev that
can read the brief, or a BA that can read the client's private notes, would make the
scores meaningless. Each agent's `tools` list limits *which* tools it has; this hook
limits *which paths* those tools touch.

Hook input carries `agent_type` (the subagent's `name`) when the call comes from a
subagent; it's absent in the main conversation.

Rules:
- lead / ba / qa / dev: may read and write only the paths in READ / WRITE below.
  Glob and Grep need a `path` inside the allowed area. No Bash.
- Everyone else (the main conversation, other subagents):
  - can't read `.kickoff-private/` before the `reveal` stage,
  - can't write `.kickoff-private/` at all (Bash `mv` at reveal is allowed).
- Nobody writes `intent/*/approvals/`: only the user's `approve gate N` creates those
  (see record_approval.py).

Denials return a JSON permission decision with the reason, which Claude sees.
"""

from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kickoff import current_folder, project_dir, read_payload, read_state, relative  # noqa: E402

COMMON = ["docs/*", "CONTEXT.md", "intent/CURRENT"]
READ = {
    "lead": COMMON + [".kickoff-private/*", "intent/*/brief.md", "intent/*/intake.md"],
    "ba": COMMON
    + [
        ".claude/rules/*",
        "intent/*/brief.md",
        "intent/*/intake.md",
        "intent/*/spec.md",
        "intent/*/tickets/*",
        "intent/*/test-matrix.md",
    ],
    "qa": COMMON
    + [".claude/rules/*", "intent/*/spec.md", "intent/*/tickets/*", "intent/*/test-matrix.md"],
    "dev": COMMON
    + [".claude/rules/*", "intent/*/spec.md", "intent/*/tickets/*", "app/*", "tests/*"],
}
WRITE = {
    "lead": [".kickoff-private/client-truth.md", "intent/*/brief.md", "intent/*/intake.md"],
    "ba": ["intent/*/intake.md", "intent/*/spec.md", "intent/*/tickets/*.md", "CONTEXT.md"],
    "qa": ["intent/*/test-matrix.md", "intent/*/tickets/*.md"],
    "dev": [],
}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
SEARCH_TOOLS = {"Glob", "Grep"}
PRIVATE = ".kickoff-private"
APPROVALS = re.compile(r"(^|/)intent/[^/]+/approvals(/|$)")
REVEALED = {"reveal", "done"}
BASH_WRITES = re.compile(r">|\b(rm|mv|cp|touch|tee|sed|mkdir|python3?|echo|printf|install|ln|dd|truncate)\b")


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def target_path(tool: str, tool_input: dict) -> str:
    if tool in SEARCH_TOOLS:
        return tool_input.get("path") or ""
    return tool_input.get("file_path") or tool_input.get("notebook_path") or ""


def check_role(role: str, tool: str, rel: str, raw: str) -> str | None:
    if tool == "Bash":
        return f"the {role} agent has no shell; work through files"
    if tool in WRITE_TOOLS:
        if not rel or not matches(rel, WRITE[role]):
            allowed = ", ".join(WRITE[role]) or "nothing (read-only role)"
            return f"the {role} agent may write only: {allowed}"
        return None
    if tool in SEARCH_TOOLS and not raw:
        return f"the {role} agent must pass a `path` to {tool}, inside: {', '.join(READ[role])}"
    # a directory is fine when something allowed lives under it, e.g. Glob in intent/x/tickets
    ok = rel and (matches(rel, READ[role]) or matches(rel + "/x", READ[role]))
    if not ok:
        return f"the {role} agent may read only: {', '.join(READ[role])}"
    return None


def check_everyone(tool: str, rel: str, command: str, stage: str) -> str | None:
    if tool in WRITE_TOOLS and APPROVALS.search(rel):
        return "approval files are written only when the user types `approve gate N`"
    if tool == "Bash" and "approvals" in command and BASH_WRITES.search(command):
        return "approval files are written only when the user types `approve gate N`"
    return None


def check_others(tool: str, rel: str, command: str, stage: str) -> str | None:
    private = rel == PRIVATE or rel.startswith(PRIVATE + "/")
    if tool in WRITE_TOOLS and private:
        return "only the lead agent writes the client's private notes"
    if stage not in REVEALED:
        if private:
            return "the client's private notes stay hidden until the reveal stage"
        if tool == "Bash" and PRIVATE in command:
            return "the client's private notes stay hidden until the reveal stage"
    return None


def decide(payload: dict) -> str | None:
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    root = project_dir(payload)
    raw = target_path(tool, tool_input)
    rel = relative(root, raw, payload.get("cwd")) if raw else ""
    command = (tool_input.get("command") or "") if tool == "Bash" else ""
    stage = read_state(current_folder(root))["next"]

    reason = check_everyone(tool, rel, command, stage)
    if reason:
        return reason
    role = payload.get("agent_type") or ""
    if role in READ:
        return check_role(role, tool, rel, raw)
    return check_others(tool, rel, command, stage)


def main() -> int:
    payload = read_payload()
    reason = decide(payload)
    if reason:
        decision = {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Kickoff policy: {reason}.",
        }
        print(json.dumps({"hookSpecificOutput": decision}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
