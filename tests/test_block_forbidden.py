"""Tests for the Claude Code PreToolUse hook in .claude/hooks/block_forbidden.py."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".claude" / "hooks" / "block_forbidden.py"


def run_hook(command: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    if cwd:
        payload["cwd"] = cwd
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf build",
        "rm -fr build",
        "rm -r -f build",
        "rm --recursive --force build",
        "sudo rm -Rf /tmp/x",
        "cd app && rm -rf __pycache__",
        'bash -c "rm -rf build"',
        "git push --force origin fix/1-x",
        "git push -f origin fix/1-x",
        "git push origin +fix/1-x",
        "git push origin main",
        "git push origin HEAD:main",
        "git push origin HEAD:refs/heads/main",
        "git push origin refs/heads/main",
        "git reset --hard HEAD~1",
        "git -C . reset --hard",
        "git push --all origin",
        "git push --mirror origin",
        "git push --branches origin",
    ],
)
def test_blocks_forbidden_commands(command):
    result = run_hook(command)
    assert result.returncode == 2
    assert "Blocked by team policy" in result.stderr


@pytest.mark.parametrize(
    "command",
    [
        "uv run pytest",
        "rm build/old.log",
        "rm -r empty_dir",
        "git push origin fix/14-nfd-titles",
        "git push --force-with-lease origin fix/14-nfd-titles",
        "git reset --soft HEAD~1",
        "git status && git diff",
        "echo 'rm -rf is dangerous'",
        "grep -rf patterns.txt app",
    ],
)
def test_allows_safe_commands(command):
    result = run_hook(command)
    assert result.returncode == 0, result.stderr


def test_blocks_commit_on_main_but_not_on_branch(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    assert run_hook("git commit -m x", cwd=str(tmp_path)).returncode == 2

    git("checkout", "-b", "fix/1-x")
    assert run_hook("git commit -m x", cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "git checkout main && git commit -m x",
        "git switch main; git commit -m x",
        "git checkout fix/1-x && git checkout main && git commit -am x",
    ],
)
def test_blocks_commit_after_switching_to_main_in_same_command(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    git("checkout", "-b", "fix/1-x")
    assert run_hook(command, cwd=str(tmp_path)).returncode == 2


def test_allows_commit_after_switching_away_from_main(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    assert run_hook("git checkout -b fix/2-y && git commit -m x", cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin",
        "git push origin HEAD",
        "git push -u origin HEAD",
        "git push origin @",
        "git checkout fix/1-x && git checkout main && git push",
    ],
)
def test_blocks_implicit_push_from_main(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    assert run_hook(command, cwd=str(tmp_path)).returncode == 2


@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin",
        "git push -u origin HEAD",
        "git push origin @",
        "git checkout main && git checkout fix/1-x && git push",
    ],
)
def test_allows_implicit_push_from_branch(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    git("checkout", "-b", "fix/1-x")
    assert run_hook(command, cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "git merge fix/1-x",
        "git merge --no-ff fix/1-x",
        "git cherry-pick abc123",
        "git revert HEAD",
        "git rebase fix/1-x",
        "git checkout fix/1-x && git checkout main && git merge fix/1-x",
    ],
)
def test_blocks_history_changes_on_main(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    result = run_hook(command, cwd=str(tmp_path))
    assert result.returncode == 2
    assert "Blocked by team policy" in result.stderr


@pytest.mark.parametrize(
    "command",
    [
        "git merge --abort",
        "git rebase --continue",
        "git cherry-pick --abort",
        "git revert --quit",
        "git merge --ff-only origin/main",
    ],
)
def test_allows_finishing_or_fast_forwarding_on_main(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    assert run_hook(command, cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
    "command",
    ["git merge main", "git rebase main", "git cherry-pick abc123", "git revert HEAD"],
)
def test_allows_history_changes_on_branch(tmp_path, command):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    git("checkout", "-b", "fix/1-x")
    assert run_hook(command, cwd=str(tmp_path)).returncode == 0


@pytest.mark.parametrize(
    "command",
    [
        "uv add sqlalchemy",
        "uv add --dev pytest-cov",
        "cd app && uv add redis",
        "uv pip install redis",
        "pip install psycopg",
        "python -m pip install requests",
        "uv --project . add redis",
        "uv --directory=app add redis",
        "uv -q add redis",
        "pip3.11 install redis",
    ],
)
def test_asks_before_adding_a_dependency(command):
    result = run_hook(command)
    assert result.returncode == 0
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "ask"
    assert "dependency" in decision["permissionDecisionReason"]


@pytest.mark.parametrize("command", ["uv sync", "uv run pytest", "uv remove httpx", "pip list"])
def test_does_not_ask_for_other_package_commands(command):
    result = run_hook(command)
    assert result.returncode == 0
    assert result.stdout == ""


def test_block_wins_over_ask():
    result = run_hook("uv add redis && git push --force origin fix/1-x")
    assert result.returncode == 2


def test_malformed_input_never_blocks():
    result = subprocess.run(
        [sys.executable, str(HOOK)], input="not json", capture_output=True, text=True
    )
    assert result.returncode == 0
