---
paths:
  - "intent/**"
  - "scripts/lint_tickets.py"
---

# Ticket format

`scripts/lint_tickets.py` enforces this file. If you change one, change both.

## File

`intent/<folder>/tickets/T-NN-<slug>.md`, where `NN` is two digits and `<slug>` is 2–5 kebab-case words.

## Shape

```markdown
# T-01 Schedule a post for a campaign

Status: draft
Spec: [Posts](../spec.md#posts)

## Story

As a marketer
I want to …
So that …

## Scenarios

### S1 Post scheduled on a future date

Given …
When …
Then …

### S2 …

## Out of scope

- …

## Questions

- [B] (qa, iter 0) What happens when … ? → answered in ticket body (iter 1)
- [N] (dev, iter 1) Should the list … ? → BA decision: newest first, because the client looks at upcoming posts most.
```

## Rules

- `Status:` is `draft` or `ready`. Only the BA sets `ready`, and only when no blocking question is open.
- `Dev rounds: <n>` (0–3) is added under `Status:` by `/kickoff` at the first Dev round and bumped each round. `Issue: #<n>` is added at the `promote` stage. Agents don't edit these two lines.
- Story has all three lines: `As a`, `I want`, `So that`.
- 1–6 scenarios, numbered `S1`, `S2`, … Each has at least one `Given`, `When` and `Then` line (`And` lines are fine). Over 6 means the ticket should be split.
- Each Then is observable: a page shows something, an API returns something, data changes. "Works correctly" is not a Then.
- Out of scope has at least one line. Write `- Nothing excluded.` only if that's true.
- No `TBD`, `TODO` or `???` anywhere.
- Use `CONTEXT.md` terms. If a ticket needs a new term, the BA adds it to `CONTEXT.md` first.

## Questions

One line per question:

```
- [B|N] (<source>, iter <n>) <question>
```

- `[B]` blocking: a dev would have to guess and could guess wrong. `[N]` non-blocking.
- `<source>` is `ba`, `qa` or `dev`. BA lines are questions the BA sent to the client; QA and BA questions use `iter 0`; Dev questions use the Dev round's iteration (1–3).
- A question is **open** until its line has `→` followed by one of:
  - `answered in ticket body (iter <n>)`: the ticket text now answers it. Edit the body; don't answer in the line.
  - `client: <answer>`: the client answered (also put the answer into the body).
  - `BA decision: <choice>, because <reason>.`
  - `out of scope` (also add it to Out of scope).
- Never delete a question line. The history is what the scorecard counts.
- `## Questions` with no questions yet holds `- None yet.`
