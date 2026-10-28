#!/usr/bin/env python3
"""UserPromptSubmit hook: turn the user's `approve gate N` message into an approval file.

Gates are human decisions, so the approval has to come from something the user typed,
not from Claude deciding that "looks good" means yes. This hook runs before Claude
sees the prompt. When the prompt starts with `approve gate N` and the active kickoff is
waiting at gate N, it writes `intent/<folder>/approvals/gate-N.md` with the time and the
user's exact words, and tells Claude to carry on. path_guard.py stops Claude from
writing those files itself.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kickoff import current_folder, gate_approved, project_dir, read_payload, read_state  # noqa: E402

APPROVE = re.compile(r"^\s*/?approve\s+gate\s*-?\s*([123])\b", re.I)


def context(text: str) -> None:
    out = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}
    print(json.dumps(out))


def main() -> int:
    payload = read_payload()
    prompt = payload.get("prompt") or ""
    m = APPROVE.match(prompt)
    if not m:
        return 0
    gate = m.group(1)
    folder = current_folder(project_dir(payload))
    if folder is None:
        context(f"Kickoff hook: the user typed 'approve gate {gate}', but no kickoff is running "
                "(intent/CURRENT is missing). Nothing was recorded.")
        return 0
    waiting = read_state(folder)["gate"]
    if gate_approved(folder, gate):
        context(f"Kickoff hook: gate {gate} of {folder.name} was already approved. Nothing new recorded.")
        return 0
    if waiting != gate:
        context(f"Kickoff hook: the user typed 'approve gate {gate}', but {folder.name} is waiting at "
                f"gate '{waiting}'. Nothing was recorded; tell the user which gate is waiting.")
        return 0

    approvals = folder / "approvals"
    approvals.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (approvals / f"gate-{gate}.md").write_text(
        f"# Gate {gate} approved\n\n"
        f"- When: {now}\n"
        f"- Session: {payload.get('session_id', 'unknown')}\n"
        f"- Typed by the user:\n\n> {prompt.strip()}\n",
        encoding="utf-8",
    )
    context(f"Kickoff hook: the user approved gate {gate} of {folder.name}; recorded in "
            f"{folder.name}/approvals/gate-{gate}.md. Clear `gate` in state.md and run the next "
            "kickoff stage now. Any text after 'approve gate N' is the user's note for that stage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
