# Client truth: Post scheduling with AI drafts

Folder: intent/2026-10-28-post-scheduling

## What I really want
A place to plan the individual social and newsletter posts for each film's campaign, with the date each should go out, so nothing is forgotten around a release. An AI-drafted first version of the text saves me time writing for four channels.

## Requirements
- H1 A marketer can add a post to a film's campaign with one channel (from the campaign's channels), a date and text.
- H2 Post text is required, 1-280 characters; errors are shown inline on the form.
- H3 Each film shows its posts in one list, soonest date first, split into "Upcoming" (today or later) and "Past".
- H4 A "Draft with AI" button on the post form fills the text box using the film title, synopsis and chosen channel; the marketer can edit it, and nothing is saved until they press save.
- H5 If the AI draft fails, the form shows a plain message and the marketer can still type text by hand.
- H6 A post can be edited (channel, date, text) and deleted (with confirm).
- H7 (hidden) Once a campaign is `finished`, no new posts can be added; existing posts stay visible.
- H8 (hidden) If a channel is removed from the campaign, its existing posts are kept and shown with a "channel removed" flag, not deleted.
- H9 A new post's date must be today or later (any distance in the future, even after release); a post already saved may end up in the past.
- H10 Deleting a film deletes its posts.

## "You decide"
- Order of posts that share the same date
- Wording and look of the "Draft with AI" button and the character counter
- How the AI draft's tone is phrased (as long as it is friendly and short)

## Planned contradiction
- Brief says: just one post per channel for a film, keep it simple.
- Later answer says: no, several posts on the same channel are fine, even on the same day; I'd post on Instagram many times.

## Not wanted
- Actually publishing to the social networks
- Approval workflow or reminders/notifications
- Analytics on how posts performed

## Added during answers
- Posts allowed while campaign is draft (and active); only finished blocks new posts.
- Past posts: just a "Past" list, no posted/missed status.
- Day only, no time of day.
- Text only, no links or media.
- Film release date change: posts stay where they are.
- Empty state: short friendly "no posts yet".
- Done = add a few posts to one film, AI draft for one, edit and save, see all on film page.
