# Recall

| H | Requirement | Hidden | Covered by | Verdict |
|---|---|---|---|---|
| H1 | Add a post to a film's campaign with one channel (from the campaign's channels), a date and text | no | T-01 S1, S5 | covered |
| H2 | Text required, 1–280 characters; errors shown inline on the form | no | T-01 S3, S5 | covered |
| H3 | Each film shows its posts in one list, soonest date first, split into "Upcoming" (today or later) and "Past" | no | T-02 S1, S2 ("Past" is ordered most recent first per BA decision D3, not soonest first) | partial |
| H4 | "Draft with AI" fills the text box from film title, synopsis and chosen channel; editable; nothing saved until Save | no | T-05 S1, S2, S3 | covered |
| H5 | If the AI draft fails, a plain message shows and the marketer can still type by hand | no | T-05 S4 | covered |
| H6 | A post can be edited (channel, date, text) and deleted (with confirm) | no | T-03 S1, S4 | covered |
| H7 | Once a campaign is `finished`, no new posts can be added; existing posts stay visible | yes | T-04 S2, S3 | covered |
| H8 | A channel removed from the campaign keeps its posts, shown with a "channel removed" flag | yes | T-04 S4, S5 | covered |
| H9 | A new post's date must be today or later (any distance ahead, even after release); a saved post may end up in the past | no | T-01 S4, T-02 S2, T-03 S3 | covered |
| H10 | Deleting a film deletes its posts | no | T-03 S5 | covered |
| H11 | Posts allowed while campaign is draft (and active); only finished blocks new posts | added | T-04 S1, S2 | covered |
| H12 | Past posts: just a "Past" list, no posted/missed status | added | T-02 S1, S2 | covered |
| H13 | Day only, no time of day | added | T-01 S4 (`YYYY-MM-DD` only), T-01 Out of scope | covered |
| H14 | Text only, no links or media | added | T-01 Out of scope | covered |
| H15 | Film release date change: posts stay where they are | added | T-02 S6 | covered |
| H16 | Empty state: short friendly "no posts yet" | added | T-01 S6, T-02 S4 | covered |
| H17 | Done = add a few posts to one film, AI draft for one, edit and save, see all on film page | added | T-01 S1–S2, T-05 S1–S2, T-03 S1, T-02 S1 | covered |
