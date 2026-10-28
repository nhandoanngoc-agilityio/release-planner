# Test matrix format

`intent/<folder>/test-matrix.md`, written by the QA agent. `scripts/lint_tickets.py` checks coverage.

## Table

One row per test case:

| ID | Ticket | Scenario | Type | Preconditions | Input | Expected | Planned test |
|---|---|---|---|---|---|---|---|
| M-001 | T-01 | S1 | happy | Film "Moth" with campaign "Launch" (`active`, channels `instagram`) | Schedule post for `instagram` on release date − 3 days | Post listed under "Upcoming" with that date | `tests/test_posts.py::test_schedule_future_post` |

- **ID**: `M-NNN`, unique, in order.
- **Scenario**: `S<n>` from the ticket, or `edge` for a case QA derived that no scenario covers yet.
- **Type**: `happy`, `edge` or `negative`.
- **Expected**: observable, same rule as a ticket's Then.
- **Planned test**: `tests/<file>.py::test_<name>`. Names only; the tests are written on Day 13+.

## Rules

- Every scenario of every ticket has at least one row.
- Every ticket has at least one `negative` row.
- QA derives edge cases: boundaries (lengths, dates such as today, past, month end, time zone midnight), empty states, repeats (doing the same action twice), deletes of parent data.
- If the ticket doesn't say what should happen in an edge case, QA does **not** guess. QA adds a `[B] (qa, iter 0)` question to that ticket and writes `blocked by question` in Expected.
