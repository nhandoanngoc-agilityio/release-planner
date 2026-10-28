# T-02 Upcoming and Past posts on the film page

Status: ready
Issue: #3
Dev rounds: 2
Spec: [Film page posts](../spec.md#film-page-posts)

## Story

As a marketer
I want a film's posts split into what is coming up and what has already gone by
So that I see at a glance what I must post next and nothing slips before release day

Rules for this ticket:

- "Today" comes from the one `today()` function added in T-01. It takes the current instant from a `now_utc()` function in the same module, converts it into the IANA time zone named by `APP_TIMEZONE` (default `UTC`) with `zoneinfo` (daylight saving time applies), and returns that date. Page and API tests set "today" by patching `today()`. S3 tests patch `now_utc()` and check `today()` and the page.
- If `APP_TIMEZONE` is not a valid IANA time zone name, the app does not start: the app factory `create_app()` reads `APP_TIMEZONE` when it is called and raises `ValueError` whose message is exactly `APP_TIMEZONE "<value>" is not a valid time zone.` (for example `APP_TIMEZONE "Mars/Base" is not a valid time zone.`).
- `APP_TIMEZONE` unset or set to the empty string `""` both mean `UTC`. Any other value is checked as given.
- Unknown campaign on the API: `GET /api/campaigns/{id}/posts` returns 404 with the body `{"detail": "Campaign not found."}`.
- Text in a row is shown as stored (after the 80-character cut) and HTML-escaped, with no other processing: newlines are not turned into `<br>` and runs of spaces are not changed in the HTML; the browser's normal whitespace display applies.
- Upcoming: posts with `post_date` today or later, ordered by `post_date` ascending. Past: posts with `post_date` before today, ordered by `post_date` descending. In **both** sections, posts on the same day are ordered by `created_at` ascending, then `id` ascending (the order they were added). "Most recent first" in Past is about days only.
- Each row shows the day as `YYYY-MM-DD`, the channel name, and the text (shortened as in S5). The "Edit" link (T-03) and the `Channel removed` flag (T-04) are added by those tickets.
- `GET /api/campaigns/{id}/posts` is added in this ticket. It returns 200 `{"upcoming": [post…], "past": [post…]}` with the post JSON from the spec, in the same order as the page, and the **full, unshortened** text.

## Scenarios

### S1 Posts split into Upcoming and Past

Given today is 2026-12-03 in `APP_TIMEZONE` (`UTC`)
And the film "Moth" has the campaign "Launch" (channel `instagram`) with these `instagram` posts, added in this order: 2026-11-28 "Trailer out", 2026-12-01 "Four days to go", 2026-12-03 "Two days to go", 2026-12-05 "Out today", 2026-12-01 "Teaser clip"
When the marketer opens `/films/{id}`
Then "Upcoming" lists `2026-12-03` `instagram` "Two days to go", then `2026-12-05` `instagram` "Out today"
And "Past" lists `2026-12-01` "Four days to go", then `2026-12-01` "Teaser clip", then `2026-11-28` "Trailer out" (days most recent first; same day in the order added)
And `GET /api/campaigns/{id}/posts` returns 200 with the same posts in `upcoming` and `past` in the same order
And `GET /api/campaigns/999/posts` for an unknown campaign returns 404 with `{"detail": "Campaign not found."}`

### S2 A post moves to Past the day after its day

Given the post "Two days to go" on 2026-12-03 is under "Upcoming" when today is 2026-12-03
When today becomes 2026-12-04 in `APP_TIMEZONE`
Then the post is listed under "Past" and no longer under "Upcoming", on the page and in `GET /api/campaigns/{id}/posts`
And the post itself is unchanged: its entry in `past` from `GET /api/campaigns/{id}/posts` has the same `post_date` `"2026-12-03"`, channel and text as before, and no status field

### S3 Today is read in the app's time zone

Given `APP_TIMEZONE` is `America/New_York`
And a post is on 2026-12-03 and it is the campaign's only post
When `now_utc()` returns 2026-12-04 02:00 UTC (2026-12-03 21:00 in New York) and the marketer opens the film page
Then `today()` returns 2026-12-03 and the post is under "Upcoming"
And no "Past" heading is shown (there are no past posts)
And when `now_utc()` returns 2026-12-04 05:00 UTC (2026-12-04 00:00 in New York), `today()` returns 2026-12-04 and the post is under "Past", with "Upcoming" showing `No upcoming posts.`
And with `APP_TIMEZONE` set to `Mars/Base`, calling `create_app()` raises `ValueError` with the message `APP_TIMEZONE "Mars/Base" is not a valid time zone.`
And with `APP_TIMEZONE` set to `""`, `create_app()` succeeds and, when `now_utc()` returns 2026-12-04 02:00 UTC, `today()` returns 2026-12-04 (UTC is used)

### S4 Empty sections

Given today is 2026-12-20 in `APP_TIMEZONE` (`UTC`) and "Launch" has only the posts 2026-11-28 "Trailer out" and 2026-12-05 "Out today"
When the marketer opens the film page
Then the "Upcoming" heading is shown with the text `No upcoming posts.` under it
And "Past" lists `2026-12-05` "Out today", then `2026-11-28` "Trailer out"
And `GET /api/campaigns/{id}/posts` returns `{"upcoming": [], "past": [<Out today>, <Trailer out>]}`
And when the campaign has no posts at all, the "Posts" section shows only `No posts yet.`: no "Upcoming" heading, no `No upcoming posts.`, no "Past" heading; and the API returns `{"upcoming": [], "past": []}`

### S5 Long text is shortened in the list

Given a post whose text is 120 characters long
When the marketer opens the film page
Then its row shows the first 80 characters of the text exactly as stored, followed by the single character `…` (U+2026)
And a post whose text is exactly 80 characters is shown in full without `…`; 81 characters shows 80 plus `…`
And characters are counted as characters, not bytes: a text of 81 `é` shows 80 `é` plus `…`
And nothing is trimmed before adding `…`: a text whose 80th character is a space shows that space before `…`
And the text is HTML-escaped: a post with text `<b>Moth</b>` shows the literal `<b>Moth</b>`, not bold text
And a post with text `Line one\nLine  two` (`\n` is one newline character, then two spaces) appears in the page HTML as `Line one\nLine  two`, with no `<br>` added and the spaces unchanged
And `GET /api/campaigns/{id}/posts` returns the full 120-character text, not shortened

### S6 Release date change does not move posts

Given today is 2026-11-10, the film "Moth" releases on 2026-12-05 and has a post on 2026-12-04
When the marketer changes the release date to 2026-12-12 on the baseline film edit form, or with `PATCH /api/films/{id}` `{"release_date": "2026-12-12"}`
Then the post is still on 2026-12-04, with the same text and channel, and listed in the same place under "Upcoming"
And `GET /api/campaigns/{id}/posts` returns the post with `post_date` `"2026-12-04"`
And no new code is expected for this: the test guards that the baseline film edit leaves posts untouched

## Out of scope

- Posted / missed status or ticking posts as done.
- Reminders or notifications.
- A calendar, or posts across all films, or posts on the films list.
- Paging or filtering the lists.
- Moving or warning about posts when the release date changes.
- The "Edit" link on each row and `GET /api/posts/{id}`: T-03. The `Channel removed` flag on rows: T-04.
- Showing the full text of a long post on the film page (it is seen on the edit page, T-03).

## Questions

- [B] (dev, iter 1) S1/S4 and the spec say the Past heading is hidden when there are no past posts and "No posts yet." replaces both headings when the campaign has no posts. Which wins in S4's "Upcoming heading shows `No upcoming posts.`" case, and is "No posts yet." the only text when there are zero posts (no Upcoming heading at all)? Please confirm that zero posts shows only "No posts yet." and that S4's empty-Upcoming message applies only when at least one post exists. → answered in ticket body (iter 1)
- [B] (dev, iter 1) S3 gives the time zone only as `APP_TIMEZONE`, but how do tests set "now"? Should "today" come from an injectable clock or function (for example `app.clock.today()`) that tests can patch, and is the date compared after converting the current UTC instant into `APP_TIMEZONE` (IANA name, with DST)? What happens if `APP_TIMEZONE` is invalid? → BA decision: `today()` (from T-01) converts the instant from a patchable `now_utc()` into the IANA zone in `APP_TIMEZONE` with DST, page tests patch `today()`, and an invalid `APP_TIMEZONE` stops the app from starting with `APP_TIMEZONE "<value>" is not a valid time zone.`, because the client never sees this and failing at start is safer than showing posts in the wrong section.
- [N] (dev, iter 1) S5: is the 80-character cut counted in characters (code points), not bytes, with no trimming of trailing spaces before adding `…`? I assume the text is cut as stored, and HTML-escaped in the page. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S5: is the full text returned untruncated in the API JSON? I assume only the film page row shortens it. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S1: do posts on the same day in the same section order by `created_at` ascending in both Upcoming and Past, as the spec says? The ticket's "most recent first" for Past could be read as reversing that. I assume the spec rule applies, and the ticket's note refers only to the day order. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S6: the film edit form and `PATCH /api/films/{id}` are baseline. Should I add a test that they leave posts untouched, with no new code needed? I assume yes. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S1: does each row also show the channel, the `Channel removed` flag and the Edit link as in the spec? The ticket only mentions date and text. I assume rows follow the spec's row format and the ticket tests only check date, text and order. → answered in ticket body (iter 1)
- [N] (dev, iter 2) S3: "creating the app" is assumed to mean calling the app factory, `create_app()`, which reads `APP_TIMEZONE` at that moment. The error is assumed to be a `ValueError` with exactly the given message. Is that right? → BA decision: `create_app()` reads `APP_TIMEZONE` when called and raises `ValueError` with exactly that message, because the client never sees this and a standard error type is the simplest to test.
- [N] (dev, iter 2) S1: should `GET /api/campaigns/999/posts` for an unknown campaign return the same 404 body as the baseline's other API 404s, for example `{"detail": ...}`? I would reuse the baseline format. → BA decision: 404 with `{"detail": "Campaign not found."}`, because the baseline names no 404 body and FastAPI's `detail` shape with a clear message is the least surprising choice.
- [N] (dev, iter 2) S5: post text may contain newlines or runs of spaces. The row shows the first 80 characters as stored and escaped, and the browser's normal whitespace collapsing applies, so I would add no special handling. Is that fine? → BA decision: no special handling; text is cut and HTML-escaped only, with no `<br>` and spaces unchanged, because the client asked only for a short preview and the full text is on the edit page (T-03).
- [N] (dev, iter 2) S3: if `APP_TIMEZONE` is set but empty, should it fall back to `UTC` or raise the invalid-time-zone error? I would treat empty as unset and use `UTC`. → BA decision: empty means unset and `UTC` is used, because the baseline already defaults to `UTC` and an empty variable is a common deployment leftover, not a wrong zone.
