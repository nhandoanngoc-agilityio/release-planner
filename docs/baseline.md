# Baseline: the app as it exists

Release Planner, before any briefed feature. Features are briefed and specified on top of this page. It is built on Day 13, before the first feature ticket; until then this page is the source of truth.

## Users

One kind of user: a **marketer** at a small indie film streaming company. There is no login in the baseline; anyone with the URL is the marketer. Times are shown in the server's configured time zone (`APP_TIMEZONE`, default `UTC`).

## Data

| Entity | Fields | Rules |
|---|---|---|
| Film | `id`, `title` (1–200 chars), `release_date` (date), `synopsis` (0–2000 chars), `created_at` | Title is required and stored exactly as typed. Release date may be in the past. |
| Campaign | `id`, `film_id`, `name` (1–120 chars), `status` (`draft`/`active`/`finished`), `channels` (subset of the channel list), `created_at` | At most one campaign per film. New campaigns start as `draft`. Any status can change to any other. |

Channels are a fixed list: `instagram`, `tiktok`, `x`, `newsletter`.

Data is stored in SQLite (`release_planner.db`). Deleting a film deletes its campaign.

## Pages

| Page | Path | What it shows / does |
|---|---|---|
| Films | `/films` | Table of films, sorted by release date (soonest first). "New film" button. |
| New / edit film | `/films/new`, `/films/{id}/edit` | Form for title, release date, synopsis. Errors shown inline. |
| Film detail | `/films/{id}` | Film fields, its campaign (or "Create campaign"), delete button with confirm. |
| New / edit campaign | `/films/{id}/campaign/new`, `/campaigns/{id}/edit` | Form for name, status, channels (checkboxes). |

There is also a JSON API mirroring the pages: `GET/POST /api/films`, `GET/PATCH/DELETE /api/films/{id}`, `GET/POST /api/films/{id}/campaign`, `PATCH/DELETE /api/campaigns/{id}`. Invalid input returns 422 with field errors.

## Stack

FastAPI, Jinja templates with HTMX for partial updates, SQLite through the standard library `sqlite3`, pytest with FastAPI's `TestClient`.

## AI

The baseline has no AI features. A feature may add a call to the Claude API. If it does, the call goes through one module so tests can replace it with a fake, and the API key comes from the `ANTHROPIC_API_KEY` environment variable.

## Not in the baseline

Posts, scheduling, publishing to real social networks, users and roles, notifications, analytics, file uploads.
