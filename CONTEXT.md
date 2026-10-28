# Context

Glossary for Release Planner. Terms only; how things are built lives in CLAUDE.md, `docs/baseline.md` and the specs.

## Product

- **Film**: a title the company is releasing, with a release date and a short synopsis.
- **Release date**: the day a film becomes watchable on the platform. Stored as a calendar date, no time.
- **Campaign**: the marketing plan for one film's release. A film has at most one campaign in the baseline.
- **Campaign status**: `draft`, `active` or `finished`.
- **Channel**: where marketing goes out: `instagram`, `tiktok`, `x`, `newsletter`. A fixed list in the baseline.
- **Post**: one piece of marketing content (text only, 1–280 characters) on one channel, planned for one day, under a film's campaign. Added by the post-scheduling feature. The marketer publishes it by hand; the app only plans it.
- **Post day**: the calendar date a post should go out (`post_date`). A date only, no time, read in `APP_TIMEZONE`.
- **Upcoming posts**: a film's posts whose post day is today or later (in `APP_TIMEZONE`), soonest first.
- **Past posts**: a film's posts whose post day is before today, most recent first. No posted/missed status.
- **Channel removed**: a flag shown on a post whose channel is no longer ticked on its campaign. The post is kept.
- **AI draft**: a first version of a post's text written by the Claude API on request ("Draft with AI"), filled into the form for the marketer to edit. Not saved until the marketer saves.

## Kickoff

- **Kickoff**: one run of the planning pipeline for one feature, in one `intent/` folder.
- **Lead / client**: the agent playing the person who wants the feature. Briefs vaguely on purpose.
- **Brief**: the Lead's first, deliberately vague description of the feature (`brief.md`).
- **Client truth**: the Lead's private list of what they actually want (`client-truth.md`). Hidden until the reveal.
- **Intake**: the BA's pass over the brief: extracted requirements, assumptions, open questions (`intake.md`).
- **Open question**: a question the BA sends back to the client.
- **BA decision**: an answer the BA chose when the client said "you decide", with a one-line reason.
- **Ticket**: one vertical slice of the feature: user story, Given/When/Then scenarios, out of scope, questions.
- **Ticket pack**: all tickets for one feature, plus `spec.md`.
- **Test matrix**: QA's table of test cases derived from the tickets' scenarios (`test-matrix.md`).
- **Dev round**: fresh Dev agents read each ticket cold and list the questions they'd need answered.
- **Iteration**: one Dev round over a ticket. At most 3 per ticket.
- **Blocking question** `[B]`: a question where a dev would have to guess, and could guess wrong.
- **Non-blocking question** `[N]`: nice to know; a dev could build correctly without it.
- **Ready ticket**: a ticket whose latest iteration has 0 open blocking questions.
- **Gate**: a stop where the user approves (`approve gate N`) or sends questions back. Gates 1, 2 and 3.
- **Reveal**: the last stage: the client truth is shown and BA recall is scored.
- **BA recall**: hidden requirements the ticket pack covered, out of all hidden requirements.
