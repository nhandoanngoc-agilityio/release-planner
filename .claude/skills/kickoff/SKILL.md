---
name: kickoff
description: Runs the feature kickoff pipeline (Lead → BA → QA → Dev) one stage per call, stopping at the user's three gates. Use when the user types /kickoff, says "next stage", or approves a gate with "approve gate N".
---

# Kickoff

Turns a client's vague feature request into a ticket pack that a developer can build without blocking questions. Four subagents do the work: `lead`, `ba`, `qa`, `dev` (`.claude/agents/`). You are the orchestrator: you run stages, pass file paths, and stop at gates. You don't write the brief, the intake, the spec, the tickets or the matrix yourself.

**One call = one stage.** Read the state, run the next stage, update the state, stop, and tell the user what to look at. Never run two stages in one call, except the automatic step right after a gate approval (see "Gates").

## State

- `intent/CURRENT`: one line, the active folder (`intent/2026-10-28-post-scheduling`). Missing = no kickoff yet.
- `<folder>/state.md`:

  ```markdown
  # Kickoff state

  next: intake
  gate: none
  dev_rounds: T-01=1, T-02=2

  ## Log
  - 2026-10-28 16:02 brief: "Schedule posts for a release" (lead)
  ```

  `next` is the stage to run: `brief`, `intake`, `answers`, `pack`, `dev-round`, `promote`, `reveal`, `done`. `gate` is `none` or the gate number that must be approved before `next` can run.

- `<folder>/approvals/gate-N.md`: written **only** by the `record_approval` hook when the user types `approve gate N`. You never create, edit or delete these files; a hook blocks it anyway.

## Each call

1. Read `intent/CURRENT` and `state.md`. Missing → `next: brief`.
2. If `gate` is a number and `approvals/gate-<gate>.md` doesn't exist:
   - If the user's message has questions or change requests, re-run the stage **before** the gate with those notes passed to the agent word for word (Gate 1 → BA `intake`; Gate 2 → BA `pack` and/or QA; Gate 3 → BA `dev-round` on the named tickets). Then stop at the same gate again.
   - Otherwise, remind them what is waiting and how to approve (`approve gate <n>`), and stop.
3. Run the `next` stage below, append a log line, update `next` / `gate`, and stop with the stage's message.

## Stages

### `brief`
Spawn `lead` with: `Stage brief. Today is <YYYY-MM-DD>.` It replies with the feature name and folder. Write the folder to `intent/CURRENT`, create `state.md` with `next: intake`, `gate: none`.
Tell the user: the brief is in `<folder>/brief.md`; they can peek at `.kickoff-private/client-truth.md` (agents can't); run `/kickoff` to start intake. Don't quote the client truth.

### `intake`
Spawn `ba` with: `Stage intake. Folder: <folder>.` Then run `uv run python scripts/lint_tickets.py <folder>`; if it reports intake errors, send them back to `ba` once.
Set `next: answers`, `gate: 1`.
Tell the user: **Gate 1** — review the open questions in `intake.md`. Add, cut or reword by replying, or type `approve gate 1`.

### `answers`
Spawn `lead` with: `Stage answers. Folder: <folder>.` Then run the linter with `--answered`.
Set `next: pack`, `gate: none`. Tell the user how many answers came back and to run `/kickoff`.

### `pack`
1. Spawn `ba` with: `Stage pack. Folder: <folder>.`
2. Spawn `qa` with: `Folder: <folder>.`
3. Run the linter. On ticket errors, send the output to `ba` (ticket format) or `qa` (matrix coverage) and lint again, at most twice.

Set `next: dev-round`, `gate: 2`.
Tell the user: **Gate 2** — review `spec.md`, `tickets/` and `test-matrix.md`, listing tickets and how many QA questions each got. Reply with changes, or type `approve gate 2`.

### `dev-round`
Repeat up to 3 iterations, while some ticket is not ready:

1. For every ticket with `Status: draft` and fewer than 3 dev rounds: bump its round `n` in `dev_rounds` and set its `Dev rounds: n` line. Spawn a **fresh** `dev` per ticket, in parallel, with: `Ticket: <path>. Iteration: <n>.` Never resume a previous Dev agent: a Dev that remembers earlier answers would fake a clean read.
2. Append each Dev's lines to that ticket's `## Questions` exactly as returned (replace `- None yet.`). For `NO QUESTIONS`, append nothing.
3. A ticket whose iteration-`n` Dev raised no `[B]` and has no open `[B]` line: the BA sets `Status: ready` in step 4 (or you ask it to).
4. For each ticket with open questions, spawn `ba` with `Stage dev-round. Folder: <folder>. Ticket: <path>. Iteration: <n>.` One at a time: they may all write to `intake.md`.
5. If the BA added `## Questions for the client (dev round)` to `intake.md`, spawn `lead` (`Stage answers. Folder: <folder>.`), then `ba` again for the affected tickets to fold the answers in.

Then run `uv run python scripts/score_kickoff.py <folder>`. Set `next: promote`, `gate: 3`.
Tell the user: **Gate 3** — the scorecard summary (ready at iteration 1/2/3, not ready, blocking questions per iteration), and which tickets will become issues. Not-ready tickets stay files unless the user says to include them. Type `approve gate 3` to create the issues.

### `promote`
For each ready ticket (plus any the user named), in order, create a GitHub issue: title = the ticket's H1 without the `#`, body = the ticket file's content plus a link line to `<folder>/spec.md`. Use the GitHub MCP tools if they're available, else `gh issue create --title … --body-file <ticket>`. A hook blocks this before Gate 3 is approved. Add `Issue: #<n>` under each ticket's `Status:` line.
Set `next: reveal`, `gate: none`. Tell the user the issue numbers and to run `/kickoff` for the reveal.

### `reveal`
1. Move `.kickoff-private/client-truth.md` to `<folder>/client-truth.md` (only now; a hook blocks reading it earlier).
2. Write `<folder>/recall.md`:

   ```markdown
   # Recall

   | H | Requirement | Hidden | Covered by | Verdict |
   |---|---|---|---|---|
   | H1 | … | no | T-01 S2 | covered |
   ```

   Verdict is `covered` (a scenario states it), `partial` (touched but a detail differs or is missing) or `missed`. Include `## Added during answers` items as H-rows too, marked `added`.
3. Run the scorer again and show the user the recall line, the contradiction line, and the rows marked `partial` or `missed`. Ask them to check the verdicts: they're your judgement, and the user has the final say. Apply any corrections they send, then re-run the scorer.

Set `next: done`. Suggest committing the folder on a `kickoff/<slug>` branch and opening a PR.

### `done`
Say the kickoff is finished. Start a new one only if the user asks (`/kickoff new`): run `brief`, which points `intent/CURRENT` at the new folder. Old folders stay as they are.

## Gates

When the `record_approval` hook reports an approval (it adds a note to the user's `approve gate N` message), continue straight into the stage the gate was holding, in the same turn. Words like "ok", "looks good" or "go ahead" are **not** approvals: answer with the exact phrase to type.

## Rules

- Pass agents **file paths**, never pasted file content: each role must read only what its own file access allows.
- Don't summarise the brief, the intake or the client's answers to the BA, QA or Dev. They read files.
- Before `reveal`, never read or quote `client-truth.md`, and never let any agent but `lead` see it.
- If a subagent fails or returns something off-format, retry it once with the error; then stop and tell the user.
