---
name: write-ticket
description: Writes or revises one kickoff ticket (story, Given/When/Then scenarios, out of scope, questions) so a developer can build it without blocking questions. Use when writing tickets/T-NN-*.md in an intent folder, or when the BA agent writes its ticket pack.
---

# Write a ticket

The format is in `.claude/rules/tickets.md`; `scripts/lint_tickets.py` checks it. This skill is about making the content survive a cold read.

## Slice

- One ticket = one thing a marketer can do or see, end to end (page, API, data). Not "the model", "the API" and "the UI" as three tickets.
- Order tickets so each builds on the last. T-01 is the thinnest useful slice.
- Over 6 scenarios → split by user outcome, not by layer.

## The zero-questions test

Before saving, read the ticket as a developer who has never heard of the feature and only has the ticket, `spec.md` and `docs/baseline.md`. For each scenario, try to write the first failing test. Every time you'd have to guess, the ticket isn't done. The usual guesses:

| Guess | Make it explicit with |
|---|---|
| Valid inputs | Exact limits: lengths, allowed values, required vs optional |
| What the user sees | The text, the list, the order, the empty state |
| Errors | Which input fails, the message or 422 field, what's kept |
| Time | Which time zone, is today allowed, past dates, at what moment status changes |
| Related data | What happens when the film or campaign changes or is deleted |
| Repeats | Doing the same action twice; two of the same item |
| AI calls | Inputs sent, output shape and limits, what the user sees if the call fails or is slow |
| Boundaries of the feature | Out of scope lines for the obvious next asks |

## Scenarios

- Concrete data, not placeholders: `Given the film "Moth" releases on 2026-12-05` beats `Given a film`.
- One behaviour per scenario. The Then says what's observable: page text, API status and body, stored data.
- Include at least one unhappy path per ticket.
- If the client's answer or a BA decision drove a scenario, the scenario states the outcome plainly; the reason lives in `intake.md`.

## Questions

- At `pack`: carry over anything still open with a `[B] (ba, iter 0)` line, never silently.
- At `dev-round`: answer by editing the body, then append `→ …` to the question line. Never delete question lines.
