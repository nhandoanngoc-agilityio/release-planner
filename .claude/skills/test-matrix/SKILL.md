---
name: test-matrix
description: Drafts a kickoff test matrix (test-matrix.md) from tickets' Given/When/Then scenarios, adding derived edge cases and raising a blocking question where a ticket leaves behaviour undefined. Use when writing or updating test-matrix.md in an intent folder, or when the QA agent runs.
---

# Draft a test matrix

The table format and coverage rules are in `.claude/rules/tests.md`; `scripts/lint_tickets.py` checks coverage.

## Steps

1. For each ticket in order, add one row per scenario (`happy` or `negative` as the scenario is), copying its Given into Preconditions, its When into Input and its Then into Expected, with concrete data.
2. Derive edge cases per ticket and add them as `edge` rows, linked to the scenario they extend, or `edge` in the Scenario column if none covers them. Work through this list and keep only what applies:
   - Boundaries: minimum and maximum lengths, zero, one, many.
   - Dates: today, yesterday, the release date itself, after the release, month end, midnight in `APP_TIMEZONE` vs UTC.
   - State: each campaign status (`draft`, `active`, `finished`); the feature used before and after a status change.
   - Repeats and duplicates: same action twice, double submit.
   - Deletes: parent film or campaign deleted while children exist.
   - Empty states: nothing created yet.
   - AI (if used): fake returns normal output, empty output, too-long output, an error, a timeout.
3. When the ticket and spec don't say what the expected result is, raise `[B] (qa, iter 0)` on the ticket and write `blocked by question` in Expected. One question per unknown, phrased so the answer is one sentence.
4. Name the planned test after the behaviour: `tests/test_<area>.py::test_<what_happens>`.

Keep the matrix to what the tickets promise. Don't add cases for features in a ticket's Out of scope.
