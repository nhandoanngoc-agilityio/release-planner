"""record_approval.py and gate_guard.py: gates are approved only by the user's own words."""

import json

import pytest

from conftest import kickoff_folder, run_hook, set_state


def approve(project, prompt):
    result = run_hook("record_approval.py", {"prompt": prompt}, project)
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"] if result.stdout else ""


def test_approval_recorded_for_waiting_gate(project):
    note = approve(project, "approve gate 1")
    record = kickoff_folder(project) / "approvals" / "gate-1.md"
    assert record.exists()
    assert "approve gate 1" in record.read_text()
    assert "run the next" in note


@pytest.mark.parametrize("prompt", ["Approve Gate 1", "  approve gate-1 please add Q3 about time zones"])
def test_approval_phrase_variants(project, prompt):
    approve(project, prompt)
    assert (kickoff_folder(project) / "approvals" / "gate-1.md").exists()


@pytest.mark.parametrize("prompt", ["looks good", "ok go ahead", "I will approve gate 1 later"])
def test_other_words_are_not_approval(project, prompt):
    assert approve(project, prompt) == ""
    assert not (kickoff_folder(project) / "approvals").exists()


def test_wrong_gate_not_recorded(project):
    note = approve(project, "approve gate 2")
    assert not (kickoff_folder(project) / "approvals").exists()
    assert "waiting at gate '1'" in note


def test_no_kickoff_no_record(project):
    (project / "intent" / "CURRENT").unlink()
    assert "no kickoff" in approve(project, "approve gate 1")


def issue(project, tool="Bash", **tool_input):
    return run_hook("gate_guard.py", {"tool_name": tool, "tool_input": tool_input}, project)


@pytest.mark.parametrize(
    "command",
    [
        "gh issue create --title 'T-01 Schedule' --body-file t.md",
        "gh api repos/o/r/issues -f title=x",
        "gh api -X POST repos/o/r/issues --input t.json",
    ],
)
def test_issue_creation_blocked_before_gate_3(project, command):
    assert issue(project, command=command).returncode == 2


def test_mcp_issue_creation_blocked_before_gate_3(project):
    assert issue(project, tool="mcp__github__create_issue").returncode == 2
    assert issue(project, tool="mcp__github__issue_write").returncode == 2


def test_reads_are_fine(project):
    assert issue(project, command="gh issue list").returncode == 0
    assert issue(project, command="gh api repos/o/r/issues").returncode == 0
    assert issue(project, tool="mcp__github__list_issues").returncode == 0


def test_issue_creation_allowed_after_gate_3(project):
    set_state(project, next="promote", gate="3")
    approve(project, "approve gate 3")
    assert issue(project, command="gh issue create --title x --body y").returncode == 0
