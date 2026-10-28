#!/usr/bin/env python3
"""Check a kickoff folder against .claude/rules/tickets.md and .claude/rules/tests.md.

Usage: python scripts/lint_tickets.py intent/<folder> [--answered]

Checks whatever exists in the folder:
- intake.md: every open question has a `- client:` line (filled, with --answered).
- tickets/T-NN-*.md: shape, scenarios, question lines, status.
- test-matrix.md: every ticket scenario has a row, every ticket has a negative row.

Prints one line per problem as `<file>: <problem>` and exits 1 if there are any.
Standard library only, so hooks can import it with plain python3.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TICKET_NAME = re.compile(r"^T-(\d{2})-[a-z0-9]+(?:-[a-z0-9]+){1,4}\.md$")
QUESTION = re.compile(r"^- \[(B|N)\] \((ba|qa|dev), iter (\d)\) (.+)$")
RESOLUTION = re.compile(
    r"→ (answered in ticket body \(iter \d\)|client: .+|BA decision: .+|out of scope)\s*$"
)
FORBIDDEN = re.compile(r"\b(TBD|TODO)\b|\?\?\?")
MAX_SCENARIOS = 6


@dataclass
class Question:
    blocking: bool
    source: str
    iteration: int
    text: str

    @property
    def open(self) -> bool:
        return "→" not in self.text

    @property
    def resolved_ok(self) -> bool:
        return bool(RESOLUTION.search(self.text))


@dataclass
class Ticket:
    path: Path
    number: str = ""
    title: str = ""
    status: str = ""
    dev_rounds: int = 0
    scenarios: list[str] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def open_blocking(self) -> list[Question]:
        return [q for q in self.questions if q.blocking and q.open]


def sections(text: str) -> dict[str, str]:
    """Split markdown into {"Heading": body} on `## ` headings."""
    out: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            out[current] = ""
        elif current is not None:
            out[current] += line + "\n"
    return out


def parse_ticket(path: Path) -> Ticket:
    t = Ticket(path)
    text = path.read_text(encoding="utf-8")
    m = TICKET_NAME.match(path.name)
    if not m:
        t.problems.append("file name must be T-NN-<2-5 word slug>.md")
    t.number = f"T-{m.group(1)}" if m else path.stem[:4]

    lines = text.splitlines()
    h1 = next((ln for ln in lines if ln.startswith("# ")), "")
    if not h1.startswith(f"# {t.number} ") or len(h1) <= len(t.number) + 3:
        t.problems.append(f"first heading must be '# {t.number} <title>'")
    t.title = h1[2:].strip()

    status = re.search(r"^Status: (\S+)\s*$", text, re.M)
    t.status = status.group(1) if status else ""
    if t.status not in ("draft", "ready"):
        t.problems.append("needs a 'Status: draft' or 'Status: ready' line")
    rounds = re.search(r"^Dev rounds: (\S+)\s*$", text, re.M)
    if rounds:
        if rounds.group(1).isdigit() and 0 <= int(rounds.group(1)) <= 3:
            t.dev_rounds = int(rounds.group(1))
        else:
            t.problems.append("'Dev rounds:' must be 0-3")
    if not re.search(r"^Spec: .+", text, re.M):
        t.problems.append("needs a 'Spec: [<section>](../spec.md#<anchor>)' line")

    secs = sections(text)
    for name in ("Story", "Scenarios", "Out of scope", "Questions"):
        if name not in secs:
            t.problems.append(f"missing section '## {name}'")

    story = secs.get("Story", "")
    for opener in ("As a", "I want", "So that"):
        if not re.search(rf"^{opener}\b", story, re.M):
            t.problems.append(f"story needs an '{opener} …' line")

    check_scenarios(t, secs.get("Scenarios", ""))

    if "Out of scope" in secs and not re.search(r"^- \S", secs["Out of scope"], re.M):
        t.problems.append("out of scope needs at least one '- ' line")

    check_questions(t, secs.get("Questions", ""))

    if FORBIDDEN.search(text):
        t.problems.append("contains TBD, TODO or ???")
    if t.status == "ready" and t.open_blocking:
        t.problems.append(f"Status is ready but {len(t.open_blocking)} blocking question(s) are open")
    return t


def check_scenarios(t: Ticket, body: str) -> None:
    blocks = re.split(r"^### ", body, flags=re.M)[1:]
    if not blocks:
        t.problems.append("needs at least one scenario ('### S1 <name>')")
    for expected, block in enumerate(blocks, start=1):
        head, _, rest = block.partition("\n")
        sid = head.split()[0] if head.split() else ""
        if sid != f"S{expected}":
            t.problems.append(f"scenario '{head.strip()}' should be numbered S{expected}")
        t.scenarios.append(sid)
        for word in ("Given", "When", "Then"):
            if not re.search(rf"^{word}\b", rest, re.M):
                t.problems.append(f"{sid or head.strip()}: missing a '{word}' line")
    if len(blocks) > MAX_SCENARIOS:
        t.problems.append(f"{len(blocks)} scenarios; over {MAX_SCENARIOS} means split the ticket")


def check_questions(t: Ticket, body: str) -> None:
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip() or line == "- None yet.":
            continue
        m = QUESTION.match(line)
        if not m:
            t.problems.append(f"bad question line: {line[:70]}")
            continue
        blocking, source, iteration, text = m.groups()
        q = Question(blocking == "B", source, int(iteration), text)
        if source in ("ba", "qa") and q.iteration != 0:
            t.problems.append(f"{source} questions use iter 0: {line[:70]}")
        if source == "dev" and not 1 <= q.iteration <= 3:
            t.problems.append(f"dev questions use iter 1-3: {line[:70]}")
        if not q.open and not q.resolved_ok:
            t.problems.append(f"answer after → isn't a known form: {line[:70]}")
        t.questions.append(q)


def check_intake(path: Path, answered: bool) -> list[str]:
    problems = []
    text = path.read_text(encoding="utf-8")
    secs = sections(text)
    if "Open questions" not in secs:
        return [f"{path.name}: missing '## Open questions'"]
    blocks = re.split(r"^### ", secs["Open questions"], flags=re.M)[1:]
    if not blocks:
        problems.append(f"{path.name}: no questions ('### Q1 <title>')")
    for block in blocks:
        head = block.splitlines()[0].strip()
        client = re.search(r"^- client:(.*)$", block, re.M)
        if not client:
            problems.append(f"{path.name}: {head}: missing '- client:' line")
        elif answered and not client.group(1).strip():
            problems.append(f"{path.name}: {head}: client hasn't answered")
    return problems


def check_matrix(path: Path, tickets: list[Ticket]) -> list[str]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 8 and re.fullmatch(r"M-\d{3}", cells[0]):
            rows.append(cells)
    problems = []
    if not rows:
        return [f"{path.name}: no rows ('| M-001 | T-01 | S1 | happy | …')"]
    covered = {(r[1], r[2]) for r in rows}
    negatives = {r[1] for r in rows if r[3] == "negative"}
    for r in rows:
        if r[3] not in ("happy", "edge", "negative"):
            problems.append(f"{path.name}: {r[0]}: type must be happy, edge or negative")
    for t in tickets:
        for sid in t.scenarios:
            if (t.number, sid) not in covered:
                problems.append(f"{path.name}: {t.number} {sid} has no row")
        if t.number not in negatives:
            problems.append(f"{path.name}: {t.number} has no negative row")
    return problems


def load_tickets(folder: Path) -> list[Ticket]:
    tdir = folder / "tickets"
    return [parse_ticket(p) for p in sorted(tdir.glob("*.md"))] if tdir.is_dir() else []


def lint(folder: Path, answered: bool = False) -> list[str]:
    problems: list[str] = []
    if (folder / "intake.md").exists():
        problems += check_intake(folder / "intake.md", answered)
    tickets = load_tickets(folder)
    for t in tickets:
        problems += [f"tickets/{t.path.name}: {p}" for p in t.problems]
    if tickets and (folder / "test-matrix.md").exists():
        problems += check_matrix(folder / "test-matrix.md", tickets)
    return problems


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    folder = Path(args[0])
    if not folder.is_dir():
        print(f"no such folder: {folder}", file=sys.stderr)
        return 2
    problems = lint(folder, answered="--answered" in argv)
    for p in problems:
        print(p)
    if not problems:
        print(f"OK: {folder}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
