# T-05 Draft post text with AI

Status: ready
Issue: #6
Dev rounds: 2
Spec: [AI](../spec.md#ai)

## Story

As a marketer
I want a "Draft with AI" button that writes a first version of a post's text for the chosen channel
So that writing for four channels stops being the slowest part of planning

## Scenarios

Rules used below:
- `POST /api/campaigns/{id}/posts/draft` accepts a body that is a JSON object with `channel` set to exactly one of the strings `instagram`, `tiktok`, `x`, `newsletter` (lowercase, exact match). Any other field in the body is ignored. Anything else (no `channel`, `null`, `""`, a number, an unknown name such as `radio` or `Instagram`, a body that is not a JSON object, or a body that is not valid JSON) returns 422 `{"errors": {"channel": "Choose a channel first."}}` and the AI is not called.
- The draft endpoint does not check whether the channel is ticked on the campaign, and does not check the campaign's status. It works the same for `draft`, `active` and `finished` campaigns and for a channel that has been unticked. It stores nothing; the channel and campaign rules are checked only when the post is saved (T-01, T-03, T-04). Unknown campaign id: 404.
- The endpoint trims leading and trailing whitespace from the text that `draft_post_text` returns, then checks it: empty after trimming, or over 280 characters after trimming, is treated as `DraftUnavailable` (503). Exactly 280 characters after trimming is accepted. The response `{"text": …}`, the text box and the `n / 280` count all use the trimmed text.
- The 15-second limit is enforced inside `draft_post_text`, which raises `DraftUnavailable` when it is exceeded. The endpoint waits for `draft_post_text` to return or raise.
- Pressing "Draft with AI" only changes the text box, its `n / 280` count and the draft messages. It does not submit the form, does not validate Day or Text, and leaves the Channel and Day values and any inline errors from an earlier Save exactly as they were. How the page is updated (partial update or script) is the developer's choice.
- Draft messages: `Choose a channel first.` is shown under the Channel dropdown; `The AI draft isn't available right now. You can type the text yourself.` is shown under the text box. Each press of "Draft with AI" first clears any draft message from the previous press; a successful draft shows no message.
- Character counting: the 280 limit and the `n / 280` count both count Unicode code points (Python `len()`), so "🎬" counts as 1. The browser count must match the server (e.g. count with `[...text].length`, not `text.length`).
- Any outcome of the draft request other than a 200 with `{"text": …}` or the 422 channel error (a 503, a 500, a network drop, a response that isn't the expected JSON) is shown on the form as `The AI draft isn't available right now. You can type the text yourself.` under the text box. The text box keeps its text and the button returns to "Draft with AI", enabled.
- Model and prompt: `draft_post_text` uses a small, fast Claude model of the developer's choice, set in one constant in `app/ai.py`. The prompt wording is the developer's choice as long as it carries the inputs and instructions in [spec AI](../spec.md#ai). Tests never check the model name or the prompt wording beyond what S1 and S6 state (inputs passed, no synopsis line when empty).

### S1 Draft fills the text box

Given the film "Moth" (synopsis "A night-shift nurse befriends a moth that knows the future.") has the campaign "Launch" with channel `instagram`
And the AI fake returns "  Moth arrives 5 Dec. Don't miss it!\n"
When the marketer, on the new post form, picks channel `instagram` and presses "Draft with AI"
Then the fake was called once with title "Moth", that synopsis and channel `instagram` (no release date)
And `POST /api/campaigns/{id}/posts/draft` with `{"channel": "instagram"}` returns 200 `{"text": "Moth arrives 5 Dec. Don't miss it!"}` (trimmed)
And the text box contains "Moth arrives 5 Dec. Don't miss it!" and the count shows `34 / 280`
And no post is stored until the marketer presses Save

### S2 Edit the draft and save

Given the text box was filled by "Draft with AI" as in S1
When the marketer changes the text to "Moth arrives 5 December. Don't miss it!", picks day 2026-12-02 and presses Save
Then the post is stored with the edited text and is listed under "Upcoming"

### S3 Edit form: existing text is replaced, any channel or campaign status

Given the edit form of a post whose text box holds "Old text"
When the marketer presses "Draft with AI"
Then the text box holds the new draft, with no confirmation asked
And the stored post still has "Old text" until Save is pressed
And the button calls the draft endpoint of the post's own campaign with the channel currently selected in the dropdown
And when the campaign "Launch" is `finished`, has only `instagram` ticked, and the post's channel is `x` (shown as `x (removed)` and selected), the button sends `{"channel": "x"}`, the fake is called with channel `x`, and the endpoint returns 200 with the draft
And `POST /api/campaigns/{id}/posts/draft` with `{"channel": "tiktok"}` on that same campaign returns 200 with the draft and stores nothing

### S4 AI unavailable

Given the AI fake raises `DraftUnavailable` (no key, network error, API error, or no answer within 15 seconds)
And the text box holds "My own words"
When the marketer presses "Draft with AI"
Then the form shows `The AI draft isn't available right now. You can type the text yourself.` under the text box
And the text box still holds "My own words" and Save still works
And `POST /api/campaigns/{id}/posts/draft` returns 503 `{"error": "The AI draft isn't available right now. You can type the text yourself."}`
And the same 503 and message follow when the fake returns `"   \n"` (empty after trimming) or a text of 281 characters after trimming
And when the fake returns a text of exactly 280 characters, the endpoint returns 200 with it and the count shows `280 / 280`
And when the fake returns 279 "a" characters followed by "🎬" (280 code points), the endpoint returns 200 and the count shows `280 / 280`
And when the browser gets a 500 or no response at all from the draft endpoint, the form shows the same message under the text box, the text box still holds "My own words", and the button reads "Draft with AI" and is enabled
And pressing "Draft with AI" again with the fake now returning "Moth arrives 5 Dec. Don't miss it!" fills the text box and the message is gone

### S5 No channel chosen

Given the new post form with no channel selected
When the marketer presses "Draft with AI"
Then the AI is not called and `Choose a channel first.` is shown under the Channel dropdown
And when the marketer then picks `instagram` and presses "Draft with AI" again, the message is gone and the text box holds the draft
And `POST /api/campaigns/{id}/posts/draft` with any of `{}`, `{"channel": null}`, `{"channel": ""}`, `{"channel": 5}`, `{"channel": "radio"}`, `{"channel": "Instagram"}`, `[]` or a body that is not valid JSON returns 422 `{"errors": {"channel": "Choose a channel first."}}` and the fake is not called

### S6 Film with empty synopsis, and while waiting

Given the film "Moth" has an empty synopsis
And the new post form has Day empty and an inline error `Text is required.` left from an earlier Save
When the marketer presses "Draft with AI" for `x`
Then the fake is called with title "Moth", an empty synopsis and channel `x`, and the prompt has no synopsis line
And while the call runs the button reads `Drafting…` and is disabled, and returns to "Draft with AI" afterwards
And afterwards Day is still empty, channel `x` is still selected, and the `Text is required.` error is still shown until the next Save

## Out of scope

- Drafting all channels at once.
- A custom note or tone choice for the AI.
- Sending the release date, campaign name or other posts to the AI.
- Saving drafts automatically, or keeping a history of drafts.
- Calling the real Claude API in tests: tests always use the fake.
- Refusing drafts for unticked channels or `finished` campaigns: the draft stores nothing, and saving applies the channel and campaign rules.
- Cancelling a draft request that is running, or a timeout other than the 15 seconds inside `draft_post_text`.
- Letting the marketer choose the Claude model, or tests that check the model name or exact prompt wording.

## Questions

- [B] (qa, iter 0) What does `POST /api/campaigns/{id}/posts/draft` do with a valid channel name (e.g. `tiktok`) that is not ticked on that campaign: return a draft, or 422 `Choose a channel first.` or `Choose one of this campaign's channels.`? → BA decision: return a draft (200) for any of the four channels, ticked or not, because the draft stores nothing and the channel rule is checked on Save; this also lets the edit form draft for a removed channel (S3).
- [B] (qa, iter 0) Does `POST /api/campaigns/{id}/posts/draft` work on a `finished` campaign (return a draft), or is it refused like new posts? → answered in ticket body (iter 1)
- [B] (dev, iter 1) S1/S6 say the fake is called with the film's title and synopsis and the channel, but what does the draft endpoint do with a channel that is valid but not ticked on the campaign? (This is the same as QA's open question, restated only because the 422 message list in the spec doesn't cover it.) Skipping this one as already in Questions. → answered in ticket body (iter 1)
- [B] (dev, iter 1) The API `POST /api/campaigns/{id}/posts/draft` body is `{"channel"}` only, but S3 says the button works on the edit form where the post's channel may be "(removed)". Should the button send a removed channel and get a draft, or return 422 `Choose a channel first.`? → answered in ticket body (iter 1)
- [B] (dev, iter 1) What does the draft endpoint return when the channel value is the wrong type (e.g. `{"channel": 5}`, `null`, or empty string `""`) or the body is not valid JSON? Is it the same 422 `Choose a channel first.`? → BA decision: yes, the same 422 `{"errors": {"channel": "Choose a channel first."}}` for any body that doesn't carry exactly one of the four channel names, including invalid JSON (S5), because from the marketer's side every one of these means no usable channel was chosen.
- [N] (dev, iter 1) Is the whitespace-trimmed AI answer what gets returned and shown in the count (S1 shows `34 / 280`), and is the 280 limit checked after trimming? → answered in ticket body (iter 1)
- [N] (dev, iter 1) Where exactly on the new post form does the `Choose a channel first.` message appear (under the channel dropdown or under the text box like the AI error)? And is the error cleared when the next draft succeeds or the channel is picked? → BA decision: under the Channel dropdown, cleared at the next press of "Draft with AI" (S5), because it is a channel error and form errors sit next to their field.
- [N] (dev, iter 1) Is the AI call made synchronously with a 15-second timeout enforced inside `draft_post_text`, and should the HTMX request replace only the text box and its message area (partial update)? → BA decision: the 15-second limit lives inside `draft_post_text` and the endpoint waits for it; the update mechanism is the developer's choice as long as only the text box, count and draft messages change, because the client only sees the result.
- [N] (dev, iter 1) What does the film page or edit page show while the form's other fields (day, channel) have errors and "Draft with AI" is pressed: should draft ignore other fields and leave their errors untouched? → answered in ticket body (iter 1)
- [N] (dev, iter 2) Should the `n / 280` count and the 280 limit use Unicode characters (Python code points), so that an emoji counts as 1 even though the browser's `.length` counts it as 2? → BA decision: count Unicode code points on both server and browser (rule in Story context, S4), because the spec counts characters, not bytes, and the count the marketer sees must agree with what Save accepts.
- [N] (dev, iter 2) Which Claude model and prompt wording should `draft_post_text` use? The spec lists the instructions but not the model or exact text, so I would pick a small fast model. → BA decision: a small, fast Claude model of the developer's choice in one constant in `app/ai.py`, prompt wording free within the spec's inputs and instructions (rule in Story context, Out of scope), because the client only sees the draft and tests use the fake.
- [N] (dev, iter 2) If the draft request fails in the browser (network drop, or a 500 instead of the 503 JSON), should the form show the same `The AI draft isn't available right now…` message and re-enable the button? → answered in ticket body (iter 2)
