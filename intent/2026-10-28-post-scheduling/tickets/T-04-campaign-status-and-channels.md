# T-04 Campaign status and channels limit posts

Status: ready
Issue: #5
Dev rounds: 2
Spec: [Campaign rules](../spec.md#campaign-rules)

## Story

As a marketer
I want the campaign's status and channels to decide where new posts can go, without losing posts I already planned
So that finished campaigns stay closed and nothing I planned disappears

## Scenarios

In every scenario today is 2026-10-28 in `APP_TIMEZONE`. Rules used below:
- The `finished` check applies only to creating a post (page and `POST /api/campaigns/{id}/posts`). Editing or deleting a post on a `finished` campaign never raises the `campaign` error; its channel, day and text are validated exactly as in T-03 and [Validation](../spec.md#validation).
- `channel_removed` is not stored. It is worked out on every read from the campaign's currently ticked channels, so it is correct in the response of the same request that changed the post or the campaign.
- The campaign's status and channels are changed through the existing baseline campaign edit form (`/campaigns/{id}/edit`) or `PATCH /api/campaigns/{id}`. No new campaign UI.

### S1 Draft campaign accepts posts

Given the film "Moth" has the campaign "Launch" in status `draft` with channel `instagram`
When the marketer adds a post `instagram` on 2026-12-02 "Moth is coming"
Then the post is saved and listed under "Upcoming"

### S2 Finished campaign refuses new posts

Given the campaign "Launch" is `finished`, has channel `instagram`, and has 2 posts
When the marketer opens the film page
Then the "Posts" section has no "Add post" button and shows `This campaign is finished; new posts can't be added.`
And both posts are still listed
And `POST /api/campaigns/{id}/posts` with `{"channel": "instagram", "post_date": "2026-12-02", "text": "Moth is coming"}` returns 422 with exactly `{"errors": {"campaign": "This campaign is finished; new posts can't be added."}}` and stores nothing
And `POST /api/campaigns/{id}/posts` with `{"channel": "tiktok", "post_date": "2026-10-01", "text": ""}` returns 422 with exactly the same body: only the `campaign` entry, no other field is checked
And opening `/campaigns/{id}/posts/new` returns 200 with a page that shows that same message and a "Back to film" link to `/films/{film_id}`, and no form
And when the campaign is `finished` and also has no channels ticked, the film page and `/campaigns/{id}/posts/new` show only the finished message, never `Choose channels on the campaign to add posts.`
And when the `finished` campaign has no posts, the "Posts" section shows the finished message and also `No posts yet.`, with no "Upcoming" or "Past" heading

### S3 Existing posts on a finished campaign can be edited and deleted

Given the campaign "Launch" is `finished` with channel `instagram`, and has the post `instagram` on 2026-12-02 "Moth is coming" and a second post
When the marketer edits the first post's text to "Moth is here" and saves, then deletes the second post
Then the edit is saved (`PATCH /api/posts/{id}` returns 200) and the second post is gone
And `PATCH /api/posts/{id}` on the first post with `{"post_date": "2026-10-27"}` returns 422 with exactly `{"errors": {"post_date": "Day must be today or later."}}`, no `campaign` entry
And `PATCH /api/posts/{id}` with `{"post_date": "2026-12-03"}` returns 200 with `"post_date": "2026-12-03"`
And when the campaign status is changed back to `active` (campaign edit form or `PATCH /api/campaigns/{id}` with `{"status": "active"}`), the film page shows "Add post" again and `POST /api/campaigns/{id}/posts` with a valid body returns 201

### S4 Unticked channel keeps its posts with a flag

Given the campaign "Launch" has channels `instagram` and `x`, a post on `x` on 2026-12-02, and a post on `x` on 2026-10-20 (Past)
When the marketer unticks `x` on the campaign and saves the campaign
Then both `x` posts are still listed, each with the flag `Channel removed`, the first under "Upcoming" and the second under "Past"
And `GET /api/posts/{id}` returns `"channel_removed": true` for each of them
And `GET /api/campaigns/{id}/posts` returns `"channel_removed": true` on both posts, in `upcoming` and `past` respectively, and `false` on every `instagram` post
And when `x` is ticked again, the flag is gone from both rows and `channel_removed` is `false` in both endpoints

### S5 Editing a post whose channel was removed

Given the `x` post on 2026-12-02 with `Channel removed`, and the campaign has only `instagram`
When the marketer opens its edit page
Then the Channel dropdown shows `instagram` and `x (removed)`, with `x (removed)` selected; `tiktok` and `newsletter` are not listed
And saving with only the text changed succeeds and the post keeps channel `x` with the flag
And `PATCH /api/posts/{id}` with `{"channel": "tiktok"}` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels."}}` and the post keeps `x`
And changing the channel to `instagram` and saving succeeds; the `PATCH` response already has `"channel_removed": false`, the film page row has no flag, and reopening the edit page lists only `instagram` (no `x (removed)` entry)
And `<channel> (removed)` is listed only while the post's saved channel is not one of the campaign's ticked channels
And the dropdown always follows the fixed channel order `instagram`, `tiktok`, `x`, `newsletter`, with `<channel> (removed)` in its own place in that order: for a campaign with `instagram` and `newsletter` ticked and a post on `x`, the options are exactly `instagram`, `x (removed)`, `newsletter`, in that order

### S6 Campaign with no channels

Given the campaign "Launch" is `active` with no channels ticked, and has a post on `x` on 2026-12-02
When the marketer opens the film page
Then the "Posts" section has no "Add post" button and shows `Choose channels on the campaign to add posts.`, and the `x` post is listed with `Channel removed`
And `POST /api/campaigns/{id}/posts` with `{"channel": "instagram", "post_date": "2026-12-02", "text": "Moth is coming"}` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels."}}` and stores nothing
And opening `/campaigns/{id}/posts/new` returns 200 with a page that shows `Choose channels on the campaign to add posts.` and a "Back to film" link to `/films/{film_id}`, and no form
And the `x` post's edit page shows a Channel dropdown with only `x (removed)`, selected; saving with only the text changed succeeds and keeps channel `x`
And `PATCH /api/posts/{id}` with `{"channel": "instagram"}` returns 422 `{"errors": {"channel": "Choose one of this campaign's channels."}}`
And when the no-channel campaign has no posts, the "Posts" section shows `Choose channels on the campaign to add posts.` and also `No posts yet.`, with no "Upcoming" or "Past" heading

## Out of scope

- Deleting or moving posts automatically when a channel is unticked.
- Hiding or cancelling posts when a campaign is finished.
- Warnings when finishing a campaign that still has upcoming posts.
- Any change to `POST /api/campaigns/{id}/posts/draft` for finished or no-channel campaigns: it keeps the T-05 rules (it stores nothing, and the form that calls it isn't reachable for those campaigns).
- New UI for changing a campaign's status or channels; the baseline campaign edit form and `PATCH /api/campaigns/{id}` are used.

## Questions

- [B] (qa, iter 0) When `POST /api/campaigns/{id}/posts` hits a `finished` campaign that also has no channels ticked (or an otherwise invalid body), does the 422 body hold only the `campaign` error, or one entry per failing field as well? → BA decision: only the `campaign` entry, and no other field is checked (S2), because no fix to the other fields could make the request succeed, so extra errors would only mislead.
- [B] (dev, iter 1) S5/S3 edit rules: on `PATCH /api/posts/{id}` or the edit form for a post on a `finished` campaign, is a changed channel or day still validated normally (and no `campaign` error raised), i.e. does the finished-campaign error apply only to creating posts? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S6: on the edit page of a post in a campaign with no ticked channels, the dropdown would hold only `<channel> (removed)`. Is saving with unchanged channel allowed, and is changing channel then always a 422 `Choose one of this campaign's channels.`? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S4/S5: when `x` is unticked and the marketer changes a post from `x` to `instagram` on edit, is the flag recalculated on that save and the Channel dropdown then shows only ticked channels (no `x (removed)` entry)? Should `x (removed)` appear only while the post's saved channel is still removed? → answered in ticket body (iter 1)
- [N] (dev, iter 1) S2: when the campaign is `finished` and also has no channels ticked, which film-page text shows: the finished message or the "Choose channels" message? (Spec implies finished wins.) → answered in ticket body (iter 1)
- [N] (dev, iter 1) S2: the `/campaigns/{id}/posts/new` page for a finished campaign: which HTTP status does it return (200 with the message, or 4xx), and does it render the film page itself or a stub page with the message and a link back? → BA decision: 200 with a short page showing the message and a "Back to film" link, no form, because it is a normal state the marketer can reach from an old link, not an error.
- [N] (dev, iter 1) S4: does `GET /api/campaigns/{id}/posts` also include `channel_removed` per post, and does the flag show on the film page for posts in both Upcoming and Past lists? → answered in ticket body (iter 1)
- [N] (dev, iter 1) S3: is the status change back to `active` done via the existing campaign edit form or API `PATCH /api/campaigns/{id}`? (I assume the existing baseline mechanism, no new UI.) → answered in ticket body (iter 1)
- [N] (dev, iter 1) S6: should the draft-AI endpoint or the "Add post" page for a no-channel campaign be handled? (I assume `/campaigns/{id}/posts/new` with no channels shows `Choose channels on the campaign to add posts.` like the finished case.) → BA decision: `/campaigns/{id}/posts/new` shows `Choose channels on the campaign to add posts.` with a "Back to film" link (200, no form), and the draft endpoint is unchanged, because the form that calls it can't be reached and the draft stores nothing.
- [N] (dev, iter 2) S4/S5: in the edit-page Channel dropdown, I'd list the campaign's ticked channels in the fixed channel order (`instagram`, `tiktok`, `x`, `newsletter`), with `<channel> (removed)` in its place in that order, not appended last. Is that fine? → BA decision: yes, fixed order `instagram`, `tiktok`, `x`, `newsletter` with the removed channel in its own place (S5), because it keeps every channel list in the app in one predictable order and the client would not care.
- [N] (dev, iter 2) S2/S6: when the campaign is `finished` or has no channels and the film also has no posts, I'd show both the campaign message and `No posts yet.` in the Posts section. Is that right? → answered in ticket body (iter 2)
