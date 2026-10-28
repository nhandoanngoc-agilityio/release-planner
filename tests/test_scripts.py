"""scripts/lint_tickets.py and scripts/score_kickoff.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from conftest import GOOD_TICKET, kickoff_folder  # noqa: E402
from lint_tickets import lint  # noqa: E402
from score_kickoff import render  # noqa: E402

MATRIX = """\
| ID | Ticket | Scenario | Type | Preconditions | Input | Expected | Planned test |
|---|---|---|---|---|---|---|---|
| M-001 | T-01 | S1 | happy | Moth, active | instagram, 2026-12-01 | listed | `tests/test_posts.py::test_a` |
| M-002 | T-01 | S2 | negative | instagram only | tiktok | error | `tests/test_posts.py::test_b` |
"""


def folder_with(project, ticket=GOOD_TICKET, name="T-01-schedule-a-post.md"):
    folder = kickoff_folder(project)
    (folder / "tickets" / name).write_text(ticket)
    return folder


def test_good_ticket_passes(project):
    assert lint(folder_with(project)) == []


def test_bad_file_name(project):
    problems = lint(folder_with(project, name="schedule.md"))
    assert any("file name" in p for p in problems)


def test_missing_then(project):
    problems = lint(folder_with(project, GOOD_TICKET.replace('Then I see the error', 'And I see')))
    assert any("S2: missing a 'Then' line" in p for p in problems)


def test_tbd_rejected(project):
    problems = lint(folder_with(project, GOOD_TICKET.replace("Publishing", "TBD publishing")))
    assert any("TBD" in p for p in problems)


def test_too_many_scenarios(project):
    extra = "".join(f"\n### S{n} More\n\nGiven a\nWhen b\nThen c\n" for n in range(3, 8))
    ticket = GOOD_TICKET.replace("\n## Out of scope", extra + "\n## Out of scope")
    assert any("split the ticket" in p for p in lint(folder_with(project, ticket)))


def test_question_lines(project):
    ticket = GOOD_TICKET.replace(
        "- None yet.",
        "- [B] (dev, iter 1) Which time zone? → answered in ticket body (iter 1)\n"
        "- [N] (dev, iter 1) Newest first? → BA decision: yes, because upcoming matters most.\n"
        "- [B] (qa, iter 0) What if the campaign is finished?\n"
        "- [B] (dev, iter 5) bad iteration\n"
        "- what about this",
    )
    problems = lint(folder_with(project, ticket))
    assert any("iter 1-3" in p for p in problems)
    assert any("bad question line" in p for p in problems)
    assert len(problems) == 2


def test_ready_with_open_blocking_rejected(project):
    ticket = GOOD_TICKET.replace("Status: draft", "Status: ready").replace(
        "- None yet.", "- [B] (qa, iter 0) What if finished?"
    )
    assert any("blocking question(s) are open" in p for p in lint(folder_with(project, ticket)))


def test_intake_needs_client_lines(project):
    folder = kickoff_folder(project)
    (folder / "intake.md").write_text(
        "# Intake\n\n## Open questions\n### Q1 Time zone\nWhich?\n- client:\n### Q2 Repeat\nWhat?\n"
    )
    assert lint(folder) == ["intake.md: Q2 Repeat: missing '- client:' line"]
    assert "intake.md: Q1 Time zone: client hasn't answered" in lint(folder, answered=True)


def test_matrix_coverage(project):
    folder = folder_with(project)
    (folder / "test-matrix.md").write_text(MATRIX)
    assert lint(folder) == []
    (folder / "test-matrix.md").write_text(MATRIX.replace("| S2 | negative", "| S1 | edge"))
    problems = lint(folder)
    assert "test-matrix.md: T-01 S2 has no row" in problems
    assert "test-matrix.md: T-01 has no negative row" in problems


def test_scorecard_ready_rounds_and_recall(project):
    t1 = GOOD_TICKET.replace("Status: draft", "Status: ready\nDev rounds: 2").replace(
        "- None yet.",
        "- [B] (dev, iter 1) Which time zone? → answered in ticket body (iter 1)\n"
        "- [N] (dev, iter 2) Sort order? → BA decision: soonest first, because launches.",
    )
    t2 = GOOD_TICKET.replace("T-01", "T-02").replace("Status: draft", "Status: ready\nDev rounds: 1")
    folder = folder_with(project, t1)
    folder_with(project, t2, "T-02-edit-a-post.md")
    (folder / "intake.md").write_text(
        "# Intake\n\n## Open questions\n### Q1 a\n- client: yes\n### Q2 b\n- client: you decide\n\n"
        "## BA decisions\n- D1 soonest first, because launches.\n\n"
        "## Contradictions\n- Brief said weekly, Q1 said daily; followed Q1.\n"
    )
    (folder / "recall.md").write_text(
        "| H | Requirement | Hidden | Covered by | Verdict |\n|---|---|---|---|---|\n"
        "| H1 | a | no | T-01 S1 | covered |\n| H2 | b | yes | T-02 S1 | partial |\n"
        "| H3 | c | yes | - | missed |\n| H4 | d | no | T-01 S2 | covered |\n"
    )
    card = render(folder)
    assert "| T-01 | 0 | 1/0 | 0/1 | 0 | round 2 | ready |" in card
    assert "| T-02 | 0 | 0/0 | - | 0 | round 1 | ready |" in card
    assert "Ready at round 1: 1/2 (50%)" in card
    assert "Contradiction flagged by the BA: yes" in card
    assert "BA recall: 2.5/4 (62%)" in card
    assert "Hidden requirements recall: 0.5/2 (25%)" in card
    assert "Missed: H3" in card


def test_scorecard_before_any_tickets(project):
    card = render(kickoff_folder(project))
    assert "No tickets yet." in card
    assert "Not revealed yet" in card
