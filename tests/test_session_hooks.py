"""load_state.py, notify_gate.py and lint_on_stop.py."""

import json

from conftest import GOOD_TICKET, kickoff_folder, run_hook, set_state


def test_session_start_reports_waiting_gate(project):
    out = json.loads(run_hook("load_state.py", {}, project).stdout)
    assert "Gate 1" in out["hookSpecificOutput"]["additionalContext"]


def test_statusline(project):
    line = run_hook("load_state.py", {}, project, "--statusline").stdout.strip()
    assert line == "kickoff 2026-10-28-post-scheduling · Gate 1 waiting"
    set_state(project, next="pack")
    assert run_hook("load_state.py", {}, project, "--statusline").stdout.strip().endswith("next: pack")


def test_statusline_without_kickoff(project):
    (project / "intent" / "CURRENT").unlink()
    assert run_hook("load_state.py", {}, project, "--statusline").stdout.strip() == "kickoff: none"


def test_notify_never_fails(project):
    assert run_hook("notify_gate.py", {}, project).returncode == 0


def write_ticket(project, text):
    (kickoff_folder(project) / "tickets" / "T-01-schedule-a-post.md").write_text(text)


def test_ba_kept_going_on_bad_ticket(project):
    write_ticket(project, GOOD_TICKET.replace("So that launch content goes out on the right day\n", ""))
    result = run_hook("lint_on_stop.py", {"agent_type": "ba"}, project)
    assert result.returncode == 2
    assert "So that" in result.stderr


def test_ba_may_stop_on_good_ticket(project):
    write_ticket(project, GOOD_TICKET)
    assert run_hook("lint_on_stop.py", {"agent_type": "ba"}, project).returncode == 0


def test_only_one_retry(project):
    write_ticket(project, "# T-01 broken\n")
    payload = {"agent_type": "ba", "stop_hook_active": True}
    assert run_hook("lint_on_stop.py", payload, project).returncode == 0


def test_qa_not_blamed_for_ticket_format(project):
    write_ticket(project, "# T-01 broken\n")
    (kickoff_folder(project) / "test-matrix.md").write_text(
        "| ID | Ticket | Scenario | Type | Pre | Input | Expected | Test |\n"
    )
    result = run_hook("lint_on_stop.py", {"agent_type": "qa"}, project)
    assert result.returncode == 2
    assert "tickets/" not in result.stderr
    assert "test-matrix.md" in result.stderr
