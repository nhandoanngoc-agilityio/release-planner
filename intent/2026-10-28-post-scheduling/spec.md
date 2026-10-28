# Spec: Post scheduling

Intake: [intake.md](intake.md) · Baseline: [docs/baseline.md](../../docs/baseline.md)

## Summary

The marketer plans posts inside Release Planner instead of a spreadsheet. A post belongs to a film's campaign, is for one of the campaign's channels, has a post day and a text of 1–280 characters. The film page lists the film's posts split into "Upcoming" (soonest first) and "Past". On the post form, "Draft with AI" fills the text box with a first version written by the Claude API, which the marketer edits before saving. The app never publishes anything; the marketer posts by hand.

Done for the client: add a few posts to one film, get an AI draft for one, edit and save it, and see them all on the film page with upcoming first.

## Behaviour

### Posts

New entity, stored in SQLite next to films and campaigns.

| Field | Type | Rules |
|---|---|---|
| `id` | integer | Assigned by the app. |
| `campaign_id` | integer | The campaign the post belongs to. Required. |
| `channel` | text | One of `instagram`, `tiktok`, `x`, `newsletter`. On create, must be one of the campaign's currently ticked channels. |
| `post_date` | date | The post day. Required. On create, must be today or later (see [Time](#time)). Any distance after the release date is allowed. |
| `text` | text | Required, 1–280 characters, same limit for every channel. Stored exactly as typed. Text made only of spaces/whitespace counts as empty. Length counts characters, not bytes. |
| `created_at` | datetime | Set on create. Used to order posts on the same day. |

- No limit on how many posts a campaign has, and several posts may share the same channel and the same day.
- A post is text only: no links field, no images, no video.
- There is no posted/missed status. A post never changes on its own; it only moves from Upcoming to Past as days pass.
- A post can be added to a campaign in status `draft` or `active`. A campaign in status `finished` refuses new posts; its existing posts stay visible and can still be edited and deleted (see [Campaign rules](#campaign-rules)).

### Validation

Errors are shown inline on the form, next to the field, and the form keeps what the marketer typed. The API returns 422 with body `{"errors": {"<field>": "<message>"}}`, one entry per failing field.

| Field | When | Message |
|---|---|---|
| `text` | missing, empty or whitespace only | `Text is required.` |
| `text` | over 280 characters | `Text must be 280 characters or fewer.` |
| `post_date` | missing or not a valid date | `Day is required.` |
| `post_date` | before today, on create, or changed to a day before today on edit | `Day must be today or later.` |
| `channel` | not one of the campaign's ticked channels (on create, or changed on edit) | `Choose one of this campaign's channels.` |
| `campaign` | creating a post on a `finished` campaign | `This campaign is finished; new posts can't be added.` |

Creating a post on a `finished` campaign returns 422 with only the `campaign` entry; no other field is checked.

Editing rules:
- The `campaign` error never applies to edits; a post on a `finished` campaign is edited under the same rules as any other post.
- If the post's saved `post_date` is already in the past and the edit leaves it unchanged, the save is allowed.
- If the post's channel has been removed from the campaign and the edit leaves the channel unchanged, the save is allowed. Changing to another channel requires one of the campaign's ticked channels.

### Time

- "Today" is the current date in `APP_TIMEZONE` (default `UTC`).
- A post whose `post_date` is today is Upcoming. On the next day (in `APP_TIMEZONE`) it is Past.
- Changing a film's release date doesn't change any post's `post_date`.

### Film page posts

On the film detail page (`/films/{id}`), below the campaign, a "Posts" section, shown only when the film has a campaign.

- If the campaign is `draft` or `active` and has at least one channel ticked: an "Add post" button linking to `/campaigns/{id}/posts/new`.
- If the campaign is `draft` or `active` and has no channels ticked: no button; the text `Choose channels on the campaign to add posts.`
- If the campaign is `finished`: no button; the text `This campaign is finished; new posts can't be added.`
- No posts at all: the text `No posts yet.` and no Upcoming/Past headings.
- Otherwise two headings:
  - **Upcoming**: posts with `post_date` today or later, ordered by `post_date` ascending, then `created_at` ascending. If none, the text `No upcoming posts.` under the heading.
  - **Past**: posts with `post_date` before today, ordered by `post_date` descending, then `created_at` ascending. The heading is shown only if there is at least one past post.
- Each row shows: the day as `YYYY-MM-DD`, the channel name (`instagram`, `tiktok`, `x`, `newsletter`), the first 80 characters of the text followed by `…` if the text is longer than 80 characters, the flag `Channel removed` if applicable, and an "Edit" link to `/posts/{id}/edit`.
- All posts are listed; no paging.

### Campaign rules

- Status `finished` blocks new posts (page and API). Changing the status back to `draft` or `active` allows adding again.
- Unticking a channel on the campaign keeps all posts on that channel. Each such post shows `Channel removed` on the film page and has `"channel_removed": true` in the API. Ticking the channel again removes the flag. The flag is not stored; it is worked out from the campaign's current channels.
- Deleting a campaign deletes its posts. Deleting a film deletes its campaign and therefore its posts.

### Edit and delete

- The edit page lets the marketer change channel, day and text (rules in [Validation](#validation)). Save returns to the film page.
- The edit page has a "Delete post" button. It asks `Delete this post? This can't be undone.`; on confirm the post is deleted and the marketer returns to the film page; on cancel nothing changes.

### AI draft

See [AI](#ai).

## Pages and API

Changes to `docs/baseline.md`.

### Pages

| Page | Path | What it shows / does |
|---|---|---|
| Film detail (changed) | `/films/{id}` | Adds the "Posts" section described in [Film page posts](#film-page-posts). |
| New post | `/campaigns/{id}/posts/new` | Form: Channel (dropdown of the campaign's ticked channels, no default selection), Day (date input, empty), Text (text box with a live count `n / 280`), "Draft with AI" button, Save, Cancel (back to film page). Save on success redirects to `/films/{film_id}`. Opening it for a finished campaign, or a campaign with no ticked channels, returns 200 with a short page showing the matching film page message (finished wins) and a "Back to film" link to `/films/{film_id}`, instead of the form. |
| Edit post | `/posts/{id}/edit` | Same form, filled in. If the post's channel was removed from the campaign, the dropdown also lists it as `<channel> (removed)`. Adds "Delete post" with confirm. |

### API

Post JSON:

```json
{"id": 7, "campaign_id": 2, "channel": "instagram", "post_date": "2026-12-02", "text": "…", "channel_removed": false, "created_at": "2026-10-28T09:15:00"}
```

| Method and path | Body | Success | Errors |
|---|---|---|---|
| `GET /api/campaigns/{id}/posts` | | 200 `{"upcoming": [post…], "past": [post…]}`, ordered as on the film page | 404 unknown campaign |
| `POST /api/campaigns/{id}/posts` | `{"channel", "post_date", "text"}` | 201 post | 404 unknown campaign; 422 per [Validation](#validation) |
| `GET /api/posts/{id}` | | 200 post | 404 |
| `PATCH /api/posts/{id}` | any of `channel`, `post_date`, `text` | 200 post | 404; 422 per [Validation](#validation) |
| `DELETE /api/posts/{id}` | | 204 | 404 |
| `POST /api/campaigns/{id}/posts/draft` | `{"channel"}` | 200 `{"text": "…"}` (trimmed); nothing stored. Any of the four channels is accepted whether or not it is ticked on the campaign, and for any campaign status. | 404 unknown campaign; 422 `{"errors": {"channel": "Choose a channel first."}}` if the body is not a JSON object or `channel` is missing, not a string, or not exactly one of the four channel names; 503 `{"error": "The AI draft isn't available right now. You can type the text yourself."}` |

`DELETE /api/campaigns/{id}` and `DELETE /api/films/{id}` now also delete the posts.

## AI

- One module, `app/ai.py`, with `draft_post_text(title: str, synopsis: str, channel: str) -> str`. It raises `DraftUnavailable` on any failure. The API key comes from `ANTHROPIC_API_KEY`.
- **Inputs**: the film's title, the film's synopsis (left out of the prompt when empty) and the channel name. Not sent: release date, campaign name, existing text, other posts.
- **Instructions in the prompt**: write one post for that channel promoting the film; friendly and short; plain text in English; at most 280 characters; return only the post text.
- **Output**: the returned text with leading/trailing whitespace trimmed. If it is empty or longer than 280 characters after trimming, it counts as a failure. The endpoint applies this trim and check to whatever `draft_post_text` returns (so it also applies to the fake). The 15-second limit is enforced inside `draft_post_text`.
- **Failure**: no API key, network error, API error, no answer within 15 seconds, or bad output → `DraftUnavailable` → the endpoint returns 503 and the form shows `The AI draft isn't available right now. You can type the text yourself.` under the text box. The text box keeps what it had and the marketer can type and save as usual.
- **On the form**: the button sends the currently selected channel (on the edit form this may be a removed channel). If no channel is selected, no call is made and the form shows `Choose a channel first.` under the Channel dropdown. Each press clears the draft messages of the previous press. Pressing the button changes only the text box, its count and the draft messages; Channel, Day and any earlier Save errors are left as they were. While waiting, the button shows `Drafting…` and is disabled. On success the text box is replaced with the draft (any text in it is overwritten without asking) and the count updates. Nothing is saved until Save.
- **Fake in tests**: tests replace `draft_post_text` with a fake that returns a fixed string (e.g. `"Moth arrives 5 Dec. Don't miss it!"`) or raises `DraftUnavailable`. No test calls the real API.

## Out of scope

- Publishing to Instagram, TikTok, X or sending newsletters; the marketer posts by hand.
- Reminders or notifications of any kind.
- Posted / missed status or ticking posts as done.
- Times of day and per-post time zones.
- Links, images, video or other attachments in posts.
- Per-channel text limits (all channels use 1–280).
- Drafting all channels at once, a custom note for the AI, or AI drafts for anything other than post text.
- A calendar or a page of posts across all films; posts on the films list.
- Moving posts when a film's release date changes, or warning about it.
- Bulk edit, duplicate or reorder of posts.

## Tickets

- [T-01](tickets/T-01-add-post-to-campaign.md) Add a post to a film's campaign and see it under Upcoming on the film page.
- [T-02](tickets/T-02-upcoming-and-past-posts.md) Split the film's posts into Upcoming and Past as days pass.
- [T-03](tickets/T-03-edit-and-delete-posts.md) Edit a post's channel, day and text, and delete posts.
- [T-04](tickets/T-04-campaign-status-and-channels.md) Finished campaigns refuse new posts; removed channels flag their posts.
- [T-05](tickets/T-05-draft-post-with-ai.md) "Draft with AI" fills the post text box from the film and channel.
