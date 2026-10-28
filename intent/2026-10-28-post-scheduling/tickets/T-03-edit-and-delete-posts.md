# T-03 Edit and delete posts

Status: ready
Issue: #4
Dev rounds: 2
Spec: [Edit and delete](../spec.md#edit-and-delete)

## Story

As a marketer
I want to change a planned post's channel, day and text, or delete it
So that my plan stays right when things change

Rules for this ticket:

- The edit page `GET /posts/{id}/edit` is the new post form from T-01, filled in: the post's saved channel is selected, Day holds its saved day, Text holds its saved text, and the count under Text shows its length (for example `14 / 280` for "Moth is coming") and follows what is typed. Cancel goes back to `/films/{film_id}`.
- The edit form is a plain HTML form that submits `POST /posts/{id}/edit` with the form fields `channel`, `post_date` (`YYYY-MM-DD`) and `text`. Success answers 303 and redirects to `/films/{film_id}`, with no success message: the film page just shows the updated row. Any validation error re-renders the form at that path with HTTP status 422, every error next to its field, and the channel, day and text kept exactly as sent. Nothing is saved when any field fails.
- The edit form and `PATCH /api/posts/{id}` use the same rules and messages as creating a post (T-01 and spec [Validation](../spec.md#validation)), with two edit exceptions:
  - `Day must be today or later.` is given only when the day sent is before today **and** differs from the post's saved day. Sending the saved day unchanged is always allowed, even if it is already past.
  - `Choose one of this campaign's channels.` is given when the channel sent is not one of the campaign's ticked channels **and** differs from the post's saved channel. (Posts whose channel was removed from the campaign: T-04.)
- Field rules on edit, exactly as on create: `text` missing from the form, empty, whitespace only (e.g. "   "), JSON `null` or not a string gives `Text is required.`; over 280 characters gives `Text must be 280 characters or fewer.` (length counted in characters as typed, text stored as typed). `post_date` empty, JSON `null`, `""`, not a `YYYY-MM-DD` string (`"banana"`, `"02/12/2026"`), not a real date (`"2026-02-30"`) or not a string gives `Day is required.` A `channel` that is empty, JSON `null`, not a string or differs in case (`"Instagram"`) is treated as not one of the campaign's channels.
- All failing fields are reported at once, one entry per field: the form shows every message, the API returns 422 `{"errors": {"<field>": "<message>", …}}` with keys `channel`, `post_date`, `text`.
- `PATCH /api/posts/{id}` changes only the fields present in the body. Fields not sent stay as they are; `{}` returns 200 with the post unchanged. A field sent as `null` is validated (and fails) like any other value. Any other key in the body (`id`, `campaign_id`, `created_at`, `channel_removed`, or unknown keys) is ignored: it is never changed and causes no error. A post can never move to another campaign.
- Delete: the edit page has a "Delete post" button in a form that submits `POST /posts/{id}/delete`. Before submitting, the browser shows its own confirm dialog with the text `Delete this post? This can't be undone.` (for example via HTMX `hx-confirm` or the form's `onsubmit`); that text appears in the edit page's HTML. Cancel in the dialog sends nothing. `POST /posts/{id}/delete` deletes the post and answers 303 to `/films/{film_id}`.
- On a form re-render after an error, the Channel dropdown selects the channel sent if it is one of the dropdown's options; if the channel sent is not an option (empty, unknown, wrong case), no option is selected. Day and Text are still kept exactly as sent.
- `PATCH /api/posts/{id}` with a body that is not a JSON object (a list such as `[]`, a string such as `"hi"`, or invalid JSON such as `{"text":`) returns 422 with the same three errors as T-01 gives for that case, `{"errors": {"channel": "Choose one of this campaign's channels.", "post_date": "Day is required.", "text": "Text is required."}}`, and changes nothing. It is never answered with 400 or 500.
- Unknown post ids: `GET /posts/{id}/edit`, `POST /posts/{id}/edit` and `POST /posts/{id}/delete` return a 404 page with the text `Post not found.` and a link to `/films`; `GET`, `PATCH` and `DELETE /api/posts/{id}` return 404 with the body `{"detail": "Post not found."}` (same shape as T-02's `{"detail": "Campaign not found."}`). Nothing changes.
- An id that is not a whole number (e.g. `/posts/abc/edit`, `/api/posts/abc`) is treated as an unknown id: the same 404 page or 404 `{"detail": "Post not found."}`, never a 422.
- The id is checked first: for an unknown id, the 404 is returned whatever the body or form fields contain, and no validation error is given.
- Deleting a film or a campaign keeps the baseline's confirm text and redirect; the confirm text does not mention posts.
- "Today" is the `today()` function from T-01 (current date in `APP_TIMEZONE`, default `UTC`); tests patch it.

## Scenarios

### S1 Edit a post

Given today is 2026-11-10 in `APP_TIMEZONE` (`UTC`)
And the campaign "Launch" (`active`, channels `instagram`, `newsletter`) of the film "Moth" has the post `instagram` on 2026-12-02 "Moth is coming"
When the marketer clicks "Edit" on that row, sees the form with `instagram` selected, 2026-12-02 in Day, "Moth is coming" in Text and `14 / 280` under it, changes the channel to `newsletter`, the day to 2026-12-04 and the text to "Moth streams from 5 December", and presses Save
Then the response is a 303 redirect to `/films/{film_id}`, and that page's row shows `2026-12-04`, `newsletter`, "Moth streams from 5 December", with no success message
And `GET /api/posts/{id}` returns the same `id`, `campaign_id` and `created_at` as before, with the new channel, day and text
And saving the day as 2026-11-10 (today) succeeds

### S2 Edit validation

Given today is 2026-11-10 and the post `instagram` on 2026-12-02 "Moth is coming" above
When the marketer saves the form with text "   " (spaces only), day 2026-11-09 and channel `instagram`
Then the response is 422, the post is unchanged in storage, and the form shows `Text is required.` next to Text and `Day must be today or later.` next to Day at the same time, keeping "   " and 2026-11-09 as typed
And text of 281 characters gives `Text must be 280 characters or fewer.`; exactly 280 characters saves
And `PATCH /api/posts/{id}` with `{"channel": "tiktok", "post_date": "banana", "text": null}` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels.", "post_date": "Day is required.", "text": "Text is required."}}` and changes nothing
And `PATCH` with `{"post_date": "2026-11-09"}` returns 422 `{"errors": {"post_date": "Day must be today or later."}}`
And saving the form with channel `tiktok` (not ticked on "Launch"), day 2026-12-02 and text "Moth is coming" returns 422 with `Choose one of this campaign's channels.` next to Channel, no option selected in the dropdown, and 2026-12-02 and "Moth is coming" kept
And `PATCH` with the body `[]`, `"hi"` or the invalid JSON `{"text":` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels.", "post_date": "Day is required.", "text": "Text is required."}}` and the post is unchanged

### S3 A post already in the past can still be edited

Given today is 2026-12-10 and the post `instagram` "Trailer out" is on 2026-12-01
When the marketer changes only its text to "Trailer out now" and saves (the form sends Day 2026-12-01 unchanged)
Then the save succeeds and the post stays on 2026-12-01 under "Past"
And `PATCH /api/posts/{id}` with `{"post_date": "2026-12-01", "text": "Trailer out again"}` returns 200
And changing its day to 2026-12-02 is refused with `Day must be today or later.` and the post keeps 2026-12-01
And changing its day to 2026-12-10 (today) succeeds and the post moves to "Upcoming"

### S4 Delete a post with confirm

Given the post "Moth is coming" exists on the film "Moth"
When the marketer opens its edit page
Then the page has a "Delete post" button whose confirm text is `Delete this post? This can't be undone.`
And `POST /posts/{id}/delete` answers 303 to `/films/{film_id}`, and that page no longer lists the row
And choosing Cancel in the browser dialog sends no request, so the post is still listed
And `DELETE /api/posts/{id}` returns 204 with an empty body, and a second `DELETE` of the same id returns 404 `{"detail": "Post not found."}`; `POST /posts/{id}/delete` for that deleted id shows the 404 page `Post not found.`

### S5 Deleting the film or the campaign deletes its posts

Given the film "Moth" with campaign "Launch" and 3 posts
When the marketer deletes the campaign (or deletes the film), through the page or `DELETE /api/campaigns/{id}` (`DELETE /api/films/{id}`)
Then none of the 3 posts exist any more: `GET /api/posts/{id}` returns 404 `{"detail": "Post not found."}` for each
And the baseline's delete confirm text and redirect are unchanged
And `GET /api/posts/999` for an id that never existed returns 404 `{"detail": "Post not found."}`, and `/posts/999/edit` shows a 404 page with `Post not found.` and a link to `/films`
And `GET /api/posts/abc` returns 404 `{"detail": "Post not found."}` and `/posts/abc/edit` shows the same 404 page, not a 422

### S6 PATCH changes only the fields sent

Given today is 2026-11-10 and the post `instagram` on 2026-12-02 "Moth is coming"
When `PATCH /api/posts/{id}` is sent with `{"text": "New text"}`
Then it returns 200 with the full post JSON, `text` `"New text"`, and `channel`, `post_date`, `campaign_id`, `created_at` unchanged
And `PATCH` with `{}` returns 200 and the post is unchanged
And `PATCH` with `{"text": "Hi", "campaign_id": 42, "id": 5, "created_at": "2020-01-01T00:00:00", "channel_removed": true, "colour": "red"}` returns 200 with only `text` changed to "Hi"; the other keys are ignored and no error is given
And `PATCH /api/posts/999` returns 404 `{"detail": "Post not found."}`, also when the body is invalid (`{"text": ""}` or `[]`); `POST /posts/999/edit` with an empty text shows the 404 page `Post not found.`, not the form

## Out of scope

- Undo after delete; bulk edit or delete; duplicating a post; moving a post to another campaign.
- A success message after Save or delete.
- Editing rules on finished campaigns and for posts whose channel was removed (including the `<channel> (removed)` dropdown entry): T-04.
- "Draft with AI" on the edit form: T-05.

## Questions

- [B] (qa, iter 0) What does `PATCH /api/posts/{id}` return when the body is `{}` or has `"text": null` / `"post_date": null`: 200 with nothing changed, or 422 with the field's required message? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S2 and the PATCH rules: when editing, if the text is over 280 characters, should the 422 be `Text must be 280 characters or fewer.` (the spec Validation table says so, but S2 doesn't list it), and should whitespace-only text on edit give `Text is required.`? (I would assume yes to both.) → answered in ticket body (iter 1)
- [B] (dev, iter 1) S2/S3: when a PATCH or form save sends several invalid fields at once (e.g. empty text and a past day), should 422 list all failing fields (`{"errors": {...}}` with one entry each, per the spec) and the form show every error at once? And does "Day must be today or later." apply when the day is sent unchanged but the post is already past? (S3 says no, unchanged is OK.) → answered in ticket body (iter 1)
- [B] (dev, iter 1) S1/S5: the post's `campaign_id` cannot be changed by edit or PATCH. If a PATCH body includes `campaign_id`, `id`, `created_at` or `channel_removed`, should it be ignored or rejected with 422? → BA decision: ignored (never changed, no error), as are unknown keys, because the client never sees these fields and ignoring them keeps a valid edit from failing.
- [B] (dev, iter 1) S4: the "Delete post" confirm on the edit page. Is it a browser `confirm()` dialog or an on-page confirmation step? And what is the HTML route that performs the delete (for example `POST /posts/{id}/delete`), and what happens if it is hit for an id that no longer exists (404 page)? → BA decision: the browser's own confirm dialog with `Delete this post? This can't be undone.`, the form posts to `POST /posts/{id}/delete` which answers 303 to the film page, and an unknown id gives the 404 page `Post not found.`, because the client only asked for an "are you sure" confirm and the baseline's film delete already uses a confirm.
- [N] (dev, iter 1) S1: after a successful Save, the redirect goes to `/films/{film_id}`. Do you want a flash/success message, or just the page with the updated row? → BA decision: no message, just the film page with the updated row, because the client didn't ask for one and the changed row is the confirmation.
- [N] (dev, iter 1) S2: on a failed form save, should the HTML response status be 422 or 200 with the form re-rendered? (I would use 422, as the other forms probably do.) → answered in ticket body (iter 1)
- [N] (dev, iter 1) S2: with an invalid `post_date` value in a PATCH (e.g. "banana") or a bad type, the message is `Day is required.` per spec. Confirm that this also applies on edit. → answered in ticket body (iter 1)
- [N] (dev, iter 1) S3: for a post whose channel was removed from the campaign, the edit page lists `<channel> (removed)`. Should that dropdown option be preselected? Also, should the edit form's text box show the live `n / 280` count? → answered in ticket body (iter 1)
- [N] (dev, iter 1) S5: when the film or campaign is deleted, do the existing delete confirm texts and the redirect stay as in the baseline, with no mention of the posts being deleted? → BA decision: yes, the baseline confirm texts and redirects stay unchanged, because the client asked only that the posts go with the film and didn't ask for a warning.
- [N] (dev, iter 1) S5: for the edit page of an unknown post, what does the 404 page show (a generic "Not found" page, or text with a link back to the films list)? → BA decision: a 404 page with `Post not found.` and a link to `/films`, because the marketer needs a way back and the films list is the app's start page.
- [N] (dev, iter 2) Should `PATCH /api/posts/{id}` with a body that is not a JSON object (a list, a string, invalid JSON) return 422, and with which error shape? I would return 422 with a generic error, since no message exists for it. → BA decision: 422 with the same three errors T-01 gives for a non-object create body (`channel`, `post_date`, `text`), nothing changed, because it keeps one error shape for every bad post request and adds no new message.
- [N] (dev, iter 2) When both the id is unknown and the body is invalid, does 404 win over 422 on `PATCH /api/posts/{id}` and `POST /posts/{id}/edit`? I would return 404. → BA decision: 404 wins (`{"detail": "Post not found."}` on the API, the `Post not found.` page on the form), because there is no post to validate against and the marketer needs to know it's gone.
- [N] (dev, iter 2) On a failed form save where the channel sent is not one of the campaign's channels, which option is selected on the re-rendered form, if any? "Kept exactly as sent" can't apply when the value isn't an option. I would select nothing. → BA decision: no option is selected, while Day and Text are kept as sent, because a value that is not in the list can't be shown and the error next to Channel asks the marketer to pick one.
- [N] (dev, iter 2) For a non-integer id such as `/posts/abc/edit` or `/api/posts/abc`, should the response be the same 404 (`Post not found.` page, or API 404) rather than FastAPI's default 422? I would return 404. → BA decision: the same 404 as an unknown id (the `Post not found.` page, or 404 `{"detail": "Post not found."}`), because to the marketer it is a link to a post that doesn't exist.
