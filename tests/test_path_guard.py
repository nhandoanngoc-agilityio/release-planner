"""path_guard.py: each kickoff role stays inside its files."""

import pytest

from conftest import denied, run_hook, set_state

F = "intent/2026-10-28-post-scheduling"


def call(project, tool, agent=None, **tool_input):
    payload = {"tool_name": tool, "tool_input": tool_input}
    if agent:
        payload["agent_type"] = agent
    return run_hook("path_guard.py", payload, project)


@pytest.mark.parametrize(
    "agent, path",
    [
        ("dev", f"{F}/tickets/T-01-schedule-a-post.md"),
        ("dev", f"{F}/spec.md"),
        ("dev", "docs/baseline.md"),
        ("ba", f"{F}/brief.md"),
        ("ba", f"{F}/intake.md"),
        ("qa", f"{F}/tickets/T-01-schedule-a-post.md"),
        ("lead", ".kickoff-private/client-truth.md"),
    ],
)
def test_role_reads_its_files(project, agent, path):
    assert not denied(call(project, "Read", agent, file_path=str(project / path)))


@pytest.mark.parametrize(
    "agent, path",
    [
        ("dev", f"{F}/brief.md"),
        ("dev", f"{F}/intake.md"),
        ("dev", f"{F}/test-matrix.md"),
        ("ba", ".kickoff-private/client-truth.md"),
        ("qa", f"{F}/brief.md"),
        ("qa", f"{F}/intake.md"),
        ("dev", ".kickoff-private/client-truth.md"),
    ],
)
def test_role_blocked_from_other_files(project, agent, path):
    assert denied(call(project, "Read", agent, file_path=str(project / path)))


def test_relative_paths_are_resolved(project):
    assert denied(call(project, "Read", "dev", file_path=f"{F}/../{F.split('/')[1]}/brief.md"))


def test_dev_cannot_write_anything(project):
    assert denied(call(project, "Edit", "dev", file_path=str(project / F / "tickets/T-01-a-b.md")))


def test_ba_writes_tickets_but_not_matrix(project):
    assert not denied(call(project, "Write", "ba", file_path=str(project / F / "tickets/T-01-a-b.md")))
    assert denied(call(project, "Write", "ba", file_path=str(project / F / "test-matrix.md")))


def test_role_search_needs_allowed_path(project):
    assert denied(call(project, "Grep", "dev", pattern="client"))
    assert denied(call(project, "Grep", "dev", pattern="x", path=str(project / F)))
    assert not denied(call(project, "Glob", "dev", pattern="*.md", path=str(project / F / "tickets")))


def test_roles_have_no_shell(project):
    assert denied(call(project, "Bash", "ba", command="ls"))


def test_main_thread_cannot_read_truth_before_reveal(project):
    path = str(project / ".kickoff-private/client-truth.md")
    assert denied(call(project, "Read", file_path=path))
    assert denied(call(project, "Bash", command="cat .kickoff-private/client-truth.md"))
    set_state(project, next="reveal")
    assert not denied(call(project, "Read", file_path=path))
    assert not denied(call(project, "Bash", command=f"mv .kickoff-private/client-truth.md {F}/"))


def test_other_subagents_treated_like_main_thread(project):
    path = str(project / ".kickoff-private/client-truth.md")
    assert denied(call(project, "Read", "Explore", file_path=path))


def test_nobody_writes_approvals(project):
    path = str(project / F / "approvals/gate-1.md")
    assert denied(call(project, "Write", file_path=path))
    assert denied(call(project, "Bash", command=f"echo ok > {F}/approvals/gate-1.md"))
    assert not denied(call(project, "Bash", command=f"ls {F}/approvals"))


def test_main_thread_works_normally(project):
    assert not denied(call(project, "Write", file_path=str(project / F / "state.md")))
    assert not denied(call(project, "Bash", command="uv run pytest"))
