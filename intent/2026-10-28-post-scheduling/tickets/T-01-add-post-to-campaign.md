# T-01 Add a post to a film's campaign

Status: ready
Issue: #2
Dev rounds: 2
Spec: [Posts](../spec.md#posts)

## Story

As a marketer
I want to plan a post for a film's campaign with its channel, day and text
So that my posting plan lives in Release Planner instead of a spreadsheet

Rules for this ticket:

- The new post form is a plain HTML form that submits `POST /campaigns/{id}/posts/new` with the form fields `channel`, `post_date` (`YYYY-MM-DD`, from the date input) and `text`. Success answers 303 and redirects to `/films/{film_id}`. Any validation error re-renders the form at that path with HTTP status 422, every error next to its field, and the chosen channel, day and text kept exactly as sent.
- The API and the form use the same rules and the same messages (spec [Validation](../spec.md#validation)). All failing fields are reported at once, one entry per field. The error key for the day is `post_date`.
- "Today" is the current date in `APP_TIMEZONE` (default `UTC`). The app reads it through one `today()` function; tests set "today" by patching that function.
- T-01 does not check campaign status and does not hide "Add post" for campaigns with no channels; both come in T-04 (see Out of scope).

## Scenarios

### S1 Post added and listed under Upcoming

Given today is 2026-11-10 in `APP_TIMEZONE` (`UTC`)
And the film "Moth" (release date 2026-12-05) has the campaign "Launch" in status `active` with channels `instagram` and `newsletter`
And the campaign has no posts
When the marketer opens `/campaigns/{id}/posts/new` from "Add post" on the film page, picks channel `instagram`, day 2026-12-02, text "Moth is coming to the platform on 5 December." and presses Save
Then the response is a 303 redirect to `/films/{id}`, and that page's "Upcoming" heading lists one row: `2026-12-02`, `instagram`, "Moth is coming to the platform on 5 December."
And `POST /api/campaigns/{id}/posts` with the JSON body `{"channel": "instagram", "post_date": "2026-12-02", "text": "Moth is coming to the platform on 5 December."}` returns 201 with the full post JSON from the spec: `id`, `campaign_id`, `channel` `"instagram"`, `post_date` `"2026-12-02"`, `text` as sent, `channel_removed` `false`, `created_at` (ISO datetime such as `"2026-11-10T09:15:00"`, in `APP_TIMEZONE`, stored and returned at whole-second precision: no microseconds and no UTC offset)
And `channel_removed` is never stored: it is worked out from the campaign's current channels each time a post is returned
And for an unknown campaign id 999, `GET /campaigns/999/posts/new`, `POST /campaigns/999/posts/new` and `POST /api/campaigns/999/posts` all return 404 and store nothing

### S2 Several posts on the same channel and day, soonest first

Given the campaign "Launch" above
When the marketer adds, in this order, `instagram` on 2026-12-05 "Out today", `instagram` on 2026-12-01 "Four days to go", `instagram` on 2026-12-05 "Watch it tonight"
Then all three are saved
And "Upcoming" lists them in the order: 2026-12-01 "Four days to go", 2026-12-05 "Out today", 2026-12-05 "Watch it tonight"
And posts on the same day are ordered by `created_at` ascending, then by `id` ascending, so equal timestamps still keep the order they were added

### S3 Text is required and at most 280 characters

Given the campaign "Launch" above
When the marketer saves a post with channel `instagram`, day 2026-12-02 and text "   " (spaces only)
Then no post is stored, the form comes back with status 422, shows `Text is required.` next to Text, and keeps `instagram` selected, 2026-12-02 in Day and "   " in Text
And when the text is 281 characters the form shows `Text must be 280 characters or fewer.`; exactly 280 characters saves
And text made only of whitespace is "empty" whatever its length: 300 spaces shows `Text is required.` and not the 280 message (the empty check comes first, and only one message is given per field)
And length counts characters as typed, including leading and trailing spaces, not bytes: "  a  " is 5 characters and is stored as "  a  " unchanged; 278 letters with one space before and one after (280) saves; "é" counts as 1 character
And the API returns 422 `{"errors": {"text": "<message>"}}` with the same messages; a missing `text`, `null` or a non-string value such as `42` gives `Text is required.`
And the form shows a count `0 / 280` under Text when opened, and the count follows what is typed (for example `5 / 280` after typing "Hello")

### S4 Day must be today or later

Given today is 2026-11-10 in `APP_TIMEZONE`
When the marketer saves a post with day 2026-11-09
Then no post is stored and the form shows `Day must be today or later.`
And a post with day 2026-11-10 (today) saves and is listed under "Upcoming"
And a post with day 2027-06-01 (after the release date) saves
And a post with no day shows `Day is required.`
And through the API, `post_date` that is missing, `null`, `""`, not a `YYYY-MM-DD` string (`"tomorrow"`, `"02/12/2026"`), not a real date (`"2026-13-45"`, `"2026-02-30"`) or not a string (`20261202`) returns 422 `{"errors": {"post_date": "Day is required."}}`
And only the exact 10-character form `YYYY-MM-DD` with zero padding is accepted: `"2026-1-5"`, `"2026-12-02T00:00"` and `" 2026-12-02"` all return `Day is required.`

### S5 Only the campaign's channels are allowed, and all errors show at once

Given the campaign "Launch" has channels `instagram` and `newsletter`
When the marketer opens the new post form
Then the Channel dropdown offers only `instagram` and `newsletter`, with none preselected
And `POST /api/campaigns/{id}/posts` with channel `tiktok` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels."}}` and stores nothing
And the same message is given when no channel is chosen on the form, or the API `channel` is missing, `null`, `""`, not a string, or differs in case (`"Instagram"`)
And saving the form with no channel, no day and text "" shows all three messages at once, each next to its field; the API with `{}` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels.", "post_date": "Day is required.", "text": "Text is required."}}`
And a body that is not a JSON object (a list such as `[]`, a string such as `"hi"`, or invalid JSON such as `{"channel":`) gets the same 422 with all three errors as `{}` and stores nothing; it is never answered with 400 or 500

### S6 Film with a campaign but no posts

Given the film "Moth" has the campaign "Launch" with no posts
When the marketer opens `/films/{id}`
Then the "Posts" section shows the text `No posts yet.` and an "Add post" button, and no "Upcoming" or "Past" heading
And a film with no campaign shows no "Posts" section (only "Create campaign", as in the baseline)
And in this ticket "Add post" is shown for every campaign, whatever its status or channels

## Out of scope

- Past list, moving posts to Past, the `No upcoming posts.` text and shortening long text to 80 characters with `…`: T-02. In T-01 every row under "Upcoming" shows the full text.
- `GET /api/campaigns/{id}/posts`: T-02. `GET /api/posts/{id}`, the "Edit" link on each row, editing and deleting posts: T-03.
- Finished campaigns refusing posts, hiding "Add post" for finished campaigns or campaigns with no channels, and the `Channel removed` flag on the page: T-04. In T-01 a `finished` campaign still accepts posts, and a campaign with no channels shows an empty Channel dropdown so every save fails with `Choose one of this campaign's channels.`
- "Draft with AI": T-05. In this ticket the button may be absent.
- Links, images or video in posts; per-channel text limits; times of day.
- Publishing to the networks or reminders.

## Questions

- [B] (dev, iter 1) S1/S2/S3/S4: the ticket gives no way to pick the channel for the "same body" API call beyond JSON; for the HTML form, on a validation error should the page re-render at `/campaigns/{id}/posts/new` with status 422 or 200 (and does the dropdown keep the chosen channel)? Pick one status for the form tests. → BA decision: the form posts to `POST /campaigns/{id}/posts/new` and re-renders there with status 422, keeping the chosen channel, day and text; the API body is the JSON shown in S1, because 422 matches the API and the client asked for errors on the form without losing input.
- [B] (dev, iter 1) S1: when the campaign is `finished` or has no channels, T-04 owns the rules, but T-01's POST/new page must do something for them now. Should T-01 already implement the finished refusal (422 `campaign` error / film page message) and the "no channels" Add post hiding, or leave them entirely out until T-04? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S1: the API returns `channel_removed: false` and `created_at`. Should T-01 return the full post JSON from the spec (`id`, `campaign_id`, `created_at` included), with `channel_removed` always computed from current channels? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S3: if several fields are invalid at once (e.g. empty text and no day and no channel), should all errors be returned/shown together (one per field), and what is the error text for a missing/empty `channel` (the spec only has `Choose one of this campaign's channels.`; is that used for "none selected" too)? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S4: what does the API return for `post_date` that is not a valid date (e.g. `"2026-13-45"`, `"tomorrow"`) or wrong type, and for text that is not a string (null, number)? Same `Day is required.` / `Text is required.` messages? → BA decision: yes, any `post_date` that is not a real `YYYY-MM-DD` date string gives `Day is required.` and any `text` that is not a string gives `Text is required.`, because the spec maps "not a valid date" to `Day is required.` and one message per field keeps the form and API consistent.
- [B] (dev, iter 1) S3: is the 280 limit applied to the text as typed (untrimmed, so "  a  " counts 5 chars) and is the text stored untrimmed? The spec says "stored exactly as typed" but also that whitespace-only counts as empty. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S2: ties on same day are ordered by `created_at` ascending; since `created_at` may have equal timestamps in fast tests, I'd add `id` ascending as a final tiebreaker. OK? → BA decision: yes, `created_at` then `id` ascending, because ids follow creation order and the client only cares that same-day posts keep the order they were added.
- [N] (dev, iter 1) S1: the film page row shows the text truncated to 80 chars with `…` per spec; T-01 scenarios don't mention truncation or the "Edit" link (T-03). Should T-01 include the truncation and an Edit link, or just the three values? → answered in ticket body (iter 1)
- [N] (dev, iter 1) S6: with posts present but none upcoming, "No upcoming posts." is a T-02 matter; for T-01 I would just render it per spec. OK? → BA decision: leave it to T-02 and don't test it in T-01; rendering it per spec early is fine, because every post created in T-01 is today or later.
- [N] (dev, iter 1) S1: "today" is mocked via what mechanism (injectable clock / env)? I would add a `today()` function in one module reading `APP_TIMEZONE` that tests patch. → BA decision: one `today()` function reading `APP_TIMEZONE`, patched by tests, because the client doesn't see it and T-02 relies on the same function.
- [N] (dev, iter 1) S1: `GET /api/campaigns/{id}/posts` and `GET /api/posts/{id}` are in the spec but not in this ticket; should I build them now or leave them to later tickets? → answered in ticket body (iter 1)
- [N] (dev, iter 1) S5: for an unknown campaign id on `/campaigns/{id}/posts/new` and the POST routes, I would return 404; confirm. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S3: the live count `n / 280` on the form is in the spec but not in this ticket; include it? → BA decision: include it in T-01, because the client set the 280 limit and the count is part of the new post form in the spec.
- [N] (dev, iter 2) S3: for a text of only whitespace that is also longer than 280 characters (e.g. 300 spaces), I'd show `Text is required.` and not the "280 or fewer" message. OK? → answered in ticket body (iter 2)
- [N] (dev, iter 2) S1: should `created_at` be stored and returned at whole-second precision (like `"2026-11-10T09:15:00"`), without microseconds or a UTC offset? I'd rely on `id` for same-second ordering. → BA decision: whole seconds, no microseconds, no offset, with `id` as the same-second tiebreaker, because it matches the spec's example and the client never sees the time part.
- [N] (dev, iter 2) S4/S5: if the API body is not a JSON object (a list, a string, or invalid JSON), should it return 422 `{"errors": {"channel": …, "post_date": …, "text": …}}` as for `{}`? I'd do that. → BA decision: yes, the same 422 with all three errors as for `{}`, because it keeps one error shape for every bad create request, as the draft endpoint already does for non-object bodies.
- [N] (dev, iter 2) S4: is a date written without zero padding (`"2026-1-5"`) or with a time part (`"2026-12-02T00:00"`) "not a `YYYY-MM-DD` string", so it gets `Day is required.`? I'd accept only the exact 10-character form. → BA decision: only the exact zero-padded 10-character `YYYY-MM-DD` form is accepted, because the form's date input always sends that form and the spec's post JSON uses it.
