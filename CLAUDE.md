# Release Planner

A web app for planning the marketing of indie film releases: films, campaigns, channels and scheduled posts. It is the practice product for Claude Code training, Day 12 onward.

Today the app exists only on paper: `docs/baseline.md` describes it. No product code is written until Day 13.

## Commands

- Install: `uv sync`
- Test the harness: `uv run pytest`
- Lint tickets: `uv run python scripts/lint_tickets.py intent/<folder>`
- Score a kickoff: `uv run python scripts/score_kickoff.py intent/<folder>`

## Layout

- `docs/baseline.md`: the app as it exists. Features are briefed on top of it.
- `intent/<date>-<slug>/`: one folder per feature kickoff (see "Kickoff" below). `intent/CURRENT` names the active folder.
- `.claude/agents/`: the four kickoff roles: `lead`, `ba`, `qa`, `dev`.
- `.claude/skills/`: `kickoff` (runs the pipeline), `write-ticket`, `test-matrix`.
- `.claude/hooks/`: deterministic guards for the kickoff, wired in `.claude/settings.json`. Tested in `tests/`.
- `.kickoff-private/`: the Lead's hidden notes. Gitignored until the reveal.
- `scripts/`: ticket linter and scorecard generator. Standard library only.

## Kickoff

A feature goes brief → intake → client answers → ticket pack → dev round → issues → reveal. Run `/kickoff`; each call advances one stage and stops. Details are in `.claude/skills/kickoff/SKILL.md`.

- Roles talk only through files. A Dev never sees the brief, the client's answers or the hidden notes: only one ticket, `spec.md` and `docs/baseline.md`.
- Dev questions go into the ticket. The BA answers by editing the ticket body, never by replying in chat.
- Gates are human. The user approves a gate by typing `approve gate 1` (2, 3). A hook records that in `approvals/`. Claude never writes approval files, and never treats "looks good" as an approval.
- Scores come from `scripts/score_kickoff.py`, not from an agent's opinion.

## Conventions

- Tickets: `tickets/T-NN-<slug>.md`, format in `.claude/rules/tickets.md`.
- Question lines: `- [B] (dev, iter 1) …` for blocking, `[N]` for non-blocking. Answered lines get `→ answered in ticket body (iter N)` or `→ BA decision: … because …`.
- Use the terms in `CONTEXT.md`. Add a term there before a ticket relies on it.
- Branch `kickoff/<slug>` or `feat/<issue>-<slug>` from `main`; PRs only.
- We work on GitHub. Open PRs with `gh pr create --base main`.

## Never do

- Never commit or push directly to `main`; everything goes through a PR.
- Never write, edit or delete anything under `approvals/`. Only the user's `approve gate N` message creates those files.
- Never open GitHub issues for a kickoff before `approvals/gate-3.md` exists.
- Never show `client-truth.md` to the BA, QA or Dev agents, or quote it before the `reveal` stage.
- Never write product code (`app/`) during kickoff stages.
- Never use `git push --force` or `git reset --hard`.
- Never add a dependency without asking first.
