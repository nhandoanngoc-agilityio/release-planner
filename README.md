# Release Planner

Plan the marketing for indie film releases: films, campaigns, channels and scheduled posts.

This repo is also a working example of an **AI-native SDLC** with Claude Code: a "client" asks for a feature, and four automated roles (Lead, BA, QA, Dev) turn a vague brief into a ticket pack that a developer can build without asking a single question. A human approves every gate.

Status: Day 12, kickoff and planning. The app is described in [`docs/baseline.md`](docs/baseline.md); product code starts on Day 13.

## Run a kickoff

Open the repo in Claude Code (trust the folder so project hooks and agents load), then:

```text
/kickoff                 start, or advance one stage
approve gate 1           approve the stage Claude stopped at (1, 2 or 3)
```

Instead of approving, you can reply with questions or changes; `/kickoff` re-runs that stage with your notes.

| Stage | Who | Writes | Then |
|---|---|---|---|
| `brief` | Lead | `.kickoff-private/client-truth.md`, `brief.md` | continue |
| `intake` | BA | `intake.md` (requirements, assumptions, open questions) | **Gate 1** |
| `answers` | Lead | client answers in `intake.md` | continue |
| `pack` | BA, then QA | `spec.md`, `tickets/`, `test-matrix.md` | **Gate 2** |
| `dev-round` | Dev × ticket, BA | questions in tickets, BA revisions, `scorecard.md` | continue |
| `promote` | Claude | GitHub issues from ready tickets | **Gate 3** before |
| `reveal` | Claude | client truth into the intent folder, BA recall in `scorecard.md` | done |

## How Claude Code is used

| Feature | Where |
|---|---|
| Subagents | `.claude/agents/`: each role has its own context, tools and model |
| Skills | `.claude/skills/kickoff`, `write-ticket`, `test-matrix` |
| Hooks | `.claude/hooks/`: role file access, ticket lint, gate approval, issue guard, notifications, session state |
| Rules | `.claude/rules/tickets.md`, `tests.md` |
| MCP | `.mcp.json`: GitHub (issues at the `promote` stage) |
| Status line | shows the kickoff stage and whether a gate is waiting |

## Harness tests

```bash
uv sync
uv run pytest
```
