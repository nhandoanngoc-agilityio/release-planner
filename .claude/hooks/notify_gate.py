#!/usr/bin/env python3
"""Stop hook: tell the user when a kickoff gate is waiting for them.

Kickoff stages can take a while, so the user may step away. When Claude finishes a turn
and the active kickoff is stopped at a gate, show a desktop notification. Silent
otherwise, so ordinary turns don't ping.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kickoff import current_folder, project_dir, read_payload, waiting_gate  # noqa: E402

TITLE = "Release Planner kickoff"


def notify(message: str) -> None:
    system = platform.system()
    if system == "Darwin":
        script = f'display notification "{message}" with title "{TITLE}" sound name "Glass"'
        subprocess.run(["osascript", "-e", script], capture_output=True)
    elif shutil.which("notify-send"):
        subprocess.run(["notify-send", TITLE, message], capture_output=True)
    else:
        print("\a", end="", file=sys.stderr)


def main() -> int:
    payload = read_payload()
    folder = current_folder(project_dir(payload))
    gate = waiting_gate(folder)
    if gate:
        notify(f"Gate {gate} is waiting for you. Review, then type: approve gate {gate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
