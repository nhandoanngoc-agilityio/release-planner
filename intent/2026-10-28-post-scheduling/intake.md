# Intake: Post scheduling

Brief: [brief.md](brief.md)

## Requirements

- R1 The marketer can create posts under a film's campaign, each for one channel. (brief: "plan the actual posts inside Release Planner")
- R2 Each post has the day it should go out, and the marketer sets that day. (brief: "with the day each one should go out")
- R3 A film has at most one post per channel. (brief: "one post per channel for a film is plenty")
- R4 The marketer can ask the tool for a first draft of a post's text, and then edit it. (brief: "help me write a first version of the text")
- R5 For a film, the marketer can see which posts are coming up next, soonest first, without opening each post. (brief: "see at a glance what's coming up next")
- R6 The feature must make it hard for a planned post to be forgotten around release day. (brief: "missed posts cost us viewers on launch week")

## Assumptions

- A1 The app only plans posts; the marketer still publishes them by hand on each network: confirm in Q1
- A2 After a post's day passes, it should show whether it went out or was missed: confirm in Q2
- A3 "One post per channel" is a hard limit, not just a typical amount: confirm in Q3
- A4 Posts can only be planned for channels the campaign has selected: confirm in Q4
- A5 A post has a day only, no time of day, in the app's time zone: confirm in Q5
- A6 Days in the past are not allowed when planning a post: confirm in Q6
- A7 Posts can be planned on campaigns in any status, and stay when the campaign is finished: confirm in Q7
- A8 The draft uses the film's title, synopsis, release date and the channel: confirm in Q8
- A9 The draft is made for one channel at a time and never overwrites text without asking: confirm in Q9
- A10 "At a glance" means a list on the film's page, not a calendar across all films: confirm in Q10
- A11 Post text has a per-channel length limit (for example 280 characters for X): confirm in Q11
- A12 Posts can be edited and deleted, and deleting the film or campaign deletes its posts: confirm in Q12
- A13 A post is text only, no images or links: confirm in Q13
- A14 Changing a film's release date doesn't move its posts: confirm in Q14
- A15 The feature is done when the client can replace the spreadsheet for one film: confirm in Q15

## Conflicts with the baseline

- None found. The baseline lists posts and scheduling as "not in the baseline", which this feature adds on purpose. It also lists "publishing to real social networks" as not in the baseline; Q1 checks that the brief doesn't expect it. The draft-writing help would be the app's first AI feature, which the baseline allows (one module, key from `ANTHROPIC_API_KEY`).

## Open questions

### Q1 Does the app send the posts, or only plan them?
When a post's day comes, what should happen?
(a) Nothing automatic: the app is a plan, and you post by hand on Instagram, TikTok, etc.
(b) The app posts it for you on the network.
(c) The app reminds you somehow (say how) and you post by hand.
- client: (a). Just a plan, I post by hand. No reminders for now.

### Q2 After the day: posted, missed, or nothing?
Once a post's day has passed, what do you want to see?
(a) You tick "posted" yourself; anything not ticked after its day shows as "missed".
(b) It just moves to a "past" list, no status.
(c) It disappears from the view.
- client: (b). It just goes to a "Past" list, no ticking.

### Q3 Exactly one post per channel?
"One post per channel for a film is plenty". Should the app stop you from adding a second Instagram post for the same film, or is one per channel just what you usually do?
(a) Hard limit: one post per channel per film, the app refuses a second.
(b) Usually one, but allow more if I need them.
- client: (b). Actually no, several on the same channel are fine, even on the same day. I'd post on Instagram many times.

### Q4 Which channels can a post be for?
The campaign already has a list of chosen channels (for example only Instagram and the newsletter).
(a) Posts only for the campaign's chosen channels.
(b) Any of the four channels, whatever the campaign says.
And if you later untick a channel on the campaign that already has a post, what should happen to that post (kept, deleted, warned)?
- client: (a), only the campaign's channels. If I untick a channel, keep its posts but show a "channel removed" flag on them. Don't delete anything.

### Q5 A day, or a day and a time?
(a) Just the day ("5 December").
(b) Day and time of day ("5 December, 18:00").
If a time: whose time zone should it be in?
- client: (a), just the day.

### Q6 Which days are allowed?
(a) Only today or later; past days are refused.
(b) Any day, including the past (for recording what already went out).
Also: should posts be allowed after the film's release date (for example a "now streaming" post a week later), and is there a limit on how far before or after?
- client: (a), today or later for a new post. After the release date is fine, and no limit on how far ahead. A saved post can end up in the past as time goes by, that's fine.

### Q7 Posts and the campaign's status
Campaigns are draft, active or finished.
- Can you plan posts while the campaign is still a draft?
- When a campaign is finished, should its upcoming posts still show as coming up, be hidden, or be cancelled?
- client: Yes, draft is fine. Once a campaign is finished, no new posts can be added, but the existing ones stay visible.

### Q8 Writing help: what should the first draft be based on?
When you ask for a draft, what should the tool know and aim for?
(a) Just the film's title, synopsis, release date and the channel.
(b) The same plus a short note you type each time (for example "focus on the director").
Any tone or style rules (for example "no emojis", "always end with the release date")?
- client: (a), title, synopsis and the channel. Tone: you decide, just friendly and short.

### Q9 Writing help: one channel or all at once, and replacing text
(a) One click drafts the text for one post.
(b) One click drafts text for every channel's post at once.
If the post already has text, should a new draft replace it, ask first, or never touch it? And if the writing help is unavailable for a moment, what do you expect to see?
- client: (a), one post at a time, with a "Draft with AI" button on the post form. It fills the text box and I can edit it. Nothing is saved until I press save. If it fails, show a plain message and let me type the text myself.

### Q10 What does "at a glance" look like?
Where and how do you want to see what's coming up?
(a) On each film's page: its posts, soonest first.
(b) On the films list: the next post for each film next to it.
(c) One page with upcoming posts across all films.
How many should it show (next one, next week, all), and what should it say when nothing is planned?
- client: (a), on the film's page, one list soonest first, split into "Upcoming" and "Past". Show all of them. Nothing planned: a short friendly "no posts yet" is fine.

### Q11 Text length limits
Should the app stop you from saving text that's too long for the channel (for example over 280 characters for X), just warn you, or not check at all? Is a post allowed to be saved with no text yet (just the day planned)?
- client: Text is required, 1 to 280 characters, same for every channel. Stop me from saving otherwise and show the error right on the form.

### Q12 Changing and removing posts
Can you change a post's day, channel and text after planning it, and delete it? If you delete a film or its campaign, should its posts go with it?
- client: Yes, I can edit channel, day and text, and delete with a "are you sure" confirm. Deleting a film deletes its posts.

### Q13 What's in a post besides text?
(a) Text only.
(b) Text plus a link.
(c) Text plus an image or video.
- client: (a), text only.

### Q14 When a film's release date moves
If a film's release date changes, what happens to its planned posts?
(a) They stay on their days; I move them myself.
(b) They move by the same number of days.
(c) They stay, but the app warns me.
- client: (a), they stay where they are.

### Q15 What does "done" look like for you?
At the end of this feature, what would you do in the app to say "yes, this replaces my spreadsheet"? For example: "plan four posts for one film, get drafts for each, and see the next one on the film page."
- client: Add a few posts to one film, get an AI draft for one, edit and save it, and see them all on the film page with upcoming first.

## Contradictions

- Brief "one post per channel for a film is plenty" (R3) vs Q3 "several on the same channel are fine, even on the same day". Followed Q3: there is no per-channel limit. It is the later, more specific answer. R3 is dropped and its opposite is a scenario in T-01.
- Brief "missed posts cost us viewers" and A2 (show posted/missed) vs Q2 "It just goes to a Past list, no ticking". Followed Q2: no posted/missed status. R6 is met by the Upcoming list on the film page (soonest first); reminders are out of scope (Q1).
- Q8 option (a) listed "title, synopsis, release date and the channel" but the client wrote "title, synopsis and the channel". Followed the client's own words: the AI draft prompt gets title, synopsis and channel, not the release date. It is the more specific statement.

## BA decisions

- D1 AI draft tone: friendly and short, plain text in English, written for the chosen channel, at most 280 characters, because the client asked for "friendly and short" and left the rest to us, and 280 is the post text limit.
- D2 "Today" means the current date in `APP_TIMEZONE`; a post whose day is today is Upcoming, and it moves to Past the day after, because the baseline shows all times in that zone and the client plans whole days.
- D3 Upcoming is ordered by day ascending, then by creation (oldest first); Past is ordered by day descending (most recent first), then by creation, because the client wants "soonest first" for what is coming and the most recent past post is the most useful one to see next.
- D4 Deleting a campaign deletes its posts, because posts belong to the campaign and the client said nothing should be left over when a film is deleted; a post without a campaign has nowhere to show.
- D5 On a finished campaign, existing posts can still be edited and deleted (only adding is blocked), because the client only asked to block new posts and said the existing ones stay.
- D6 When editing, a post whose saved day is already in the past may be saved with that same day unchanged; changing the day requires today or later, because the client said a saved post may end up in the past and the "today or later" rule is for planning.
- D7 When editing a post whose channel was removed from the campaign, the post can be saved with its current channel; switching to another channel requires one of the campaign's current channels, because the client said "keep its posts" and wants nothing lost.
- D8 Text of only spaces counts as empty; text is stored exactly as typed and its length is counted in characters, because the client wants text required and the baseline stores titles exactly as typed.
- D9 "Draft with AI" replaces whatever is in the text box without asking, because the client said it "fills the text box" and nothing is saved until Save, so nothing is lost.
- D10 If the AI call fails, takes over 15 seconds, or returns empty or over-280-character text, the text box is left as it was and the form shows "The AI draft isn't available right now. You can type the text yourself.", because the client asked for a plain message and to keep typing.
- D11 On the film page the list shows each post's day, channel and the first 80 characters of its text (with "…" if longer), because "at a glance" means not opening each post, and full text would make the list long.
- D12 If the campaign has no channels selected, "Add post" is replaced by the text "Choose channels on the campaign to add posts.", because posts must use the campaign's channels.
- D13 Creating a post on a `finished` campaign returns only the `campaign` error, no other field is checked, because no fix to the other fields could make it succeed (T-04, dev round 1).
- D14 Opening the new-post page for a finished or no-channel campaign shows a short page with the film page message and a "Back to film" link (200), and the finished message wins over the no-channels one, because it is a normal state reached from an old link, not an error (T-04, dev round 1).
- D15 "Draft with AI" works for any of the four channels, ticked or unticked, and on campaigns in any status, because the draft stores nothing and the channel and campaign rules are applied on Save; this keeps the button useful on the edit form of a post whose channel was removed or whose campaign is finished (T-05, dev round 1).
- D16 The draft endpoint answers 422 `Choose a channel first.` for any body that doesn't carry exactly one of the four channel names (missing, null, empty, wrong type, wrong case, not JSON), because to the marketer each of these means no usable channel was chosen (T-05, dev round 1).
- D17 `Choose a channel first.` is shown under the Channel dropdown, and draft messages are cleared at the next press of "Draft with AI"; pressing the button never touches Channel, Day or earlier Save errors, because form errors sit next to their field and the draft only fills the text box (T-05, dev round 1).
- D18 The AI answer is trimmed by the endpoint before the empty/280 check and before it is shown, and the 15-second limit lives in `draft_post_text`, because the count must match what is in the box and the fake must exercise the same checks (T-05, dev round 1).
