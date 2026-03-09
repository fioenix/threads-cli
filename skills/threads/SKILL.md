---
name: threads
description: "Use this skill whenever the user wants to set up, authenticate, test, or operate the official Meta Threads API (graph.threads.net). Covers end-to-end Meta app setup, OAuth (local auth flow), token refresh/debug, publishing (create/publish/status/delete/repost), media retrieval (get/keyword_search), user/profile endpoints, replies & moderation (conversation/pending/manage), insights, locations/search, and oEmbed. Also use this skill when the user says they want the assistant to post to Threads on their behalf, manage mentions/replies, or fetch analytics."
---

# Threads API Skill (Official)

This skill provides:
1) **Step-by-step setup** for Meta Threads API (app, redirect URI, roles/testers)
2) A **Python CLI** (`threads-cli`) that maps closely to Threads API endpoints
3) Operational guidance to safely post and manage Threads **from the assistant**

> **Scope note:** The official Threads API does **not** provide Home feed / For You / Following feed reading. Do not claim to fetch "top feed posts" via official API.

---

## Installation

### Via pipx (recommended)

```bash
pipx install threads-cli
```

### Via pip

```bash
pip install threads-cli
```

### From source

```bash
git clone https://github.com/fioenix/threads-cli.git
cd threads-cli
pip install -e .
```

---

## Files & locations

- Skill root: `~/.openclaw/workspace/skills/threads/`
- Config env file (secrets): `~/.openclaw/workspace/skills/threads/.env`

CLI is invoked as:

```bash
# Using installed CLI
threads --env-file ~/.openclaw/workspace/skills/threads/.env <command>

# Or from source
python -m threads_cli --env-file ~/.openclaw/workspace/skills/threads/.env <command>
```

---

## Safety: strict publish approval gate

When the user asks to draft a post, treat it as a **draft** until explicitly told to publish.

- **"OK" / "looks good"** = approves the *draft content only*.
- Only publish when the user clearly expresses **public intent**, e.g.:
  - English: `publish`, `post it`, `post now`, `go live`
  - Vietnamese: `đăng bài`, `post bài`, `public lên`, `đẩy lên`

Before publishing, always echo the final text payload and ask for explicit publish confirmation.

---

## Content style notes (Threads)

Threads supports up to ~500 characters per post, but **short posts (1–4 lines)** often outperform for reach.

Guidelines when drafting for virality:
- Prefer **1 idea per post**.
- Use a **calm, quoteable closing line** (good for repost/quote).
- If the idea is longer, convert to a **mini-series** (2–5 posts) rather than one long block.
- Keep formatting simple: 1 hook line + 1–2 supporting lines + 1 question/CTA.

Common short-form patterns:
- **Hook → contrast:** "Mọi người nghĩ X. Thực ra Y."
- **Rule of 3:** "3 điều tao làm để…: A / B / C."
- **Reframe:** "Không phải thiếu kỷ luật. Là thiếu 'đường ray'."

## References

- Setup guide: `references/setup-meta-app.md`
- Endpoint map: `references/endpoints.md`

## Setup checklist (Meta app → working token)

### 1) Create Meta app + enable Threads API
- Go to Meta Developer Portal.
- Create an app.
- Add/enable **Threads API** product.

### 2) Configure OAuth Redirect URI
You must add your redirect URI to the app settings.

Common local redirect URI:
- `http://localhost:8080/callback`

**Important:** redirect URI must match exactly (scheme/host/port/path).

### 3) Roles/Testers (avoid error 1349245)
If the app is in **Development** mode, your user must be added as a developer/tester and must accept the invite.

If you see:
`Invalid Request: The user has not accepted the invite to test the app. (1349245)`

Fix:
- Add the user under App Roles (Testers/Developers)
- Accept the invite from the user account

### 4) Create skill env file
Copy the example:

```bash
cd ~/.openclaw/workspace/skills/threads
cp .env.example .env
```

Fill:
- `THREADS_APP_ID`
- `THREADS_APP_SECRET`
- `THREADS_REDIRECT_URI`
- `THREADS_SCOPES` (optional; comma-separated)

### 5) Run local OAuth flow to store long-lived token

```bash
threads --env-file ~/.openclaw/workspace/skills/threads/.env auth-local
```

This should write/update in the env file:
- `THREADS_ACCESS_TOKEN` (long-lived, ~60 days)
- `THREADS_USER_ID`

### 6) Test connection

```bash
threads --env-file ~/.openclaw/workspace/skills/threads/.env me
```

---

## Common operations (CLI mapping)

### Identity / debug
- `me` → GET `/me`
- `debug-token` → GET `/debug_token`
- `token refresh` → GET `/refresh_access_token`

### Publishing
- `publish create` → POST `/{threads-user-id}/threads`
- `publish publish` → POST `/{threads-user-id}/threads_publish`
- `publish status` → GET `/{threads-container-id}?fields=status`
- `publish delete` → DELETE `/{threads-media-id}`
- `publish repost` → POST `/{threads-media-id}/repost`

### Media retrieval
- `media get` → GET `/{threads-media-id}`
- `media keyword-search` → GET `/keyword_search`

### Replies & moderation
- `replies conversation` → GET `/{threads-media-id}/conversation`
- `replies pending` → GET `/{threads-media-id}/pending_replies`
- `replies manage` → POST `/{threads-reply-id}/manage_reply`
- `replies manage-pending` → POST `/{threads-reply-id}/manage_pending_reply`

### User endpoints
- `user get` → GET `/{threads-user-id}`
- `user threads` → GET `/{threads-user-id}/threads`
- `user publishing-limit` → GET `/{threads-user-id}/threads_publishing_limit`
- `user replies` → GET `/{threads-user-id}/replies`
- `user mentions` → GET `/{threads-user-id}/mentions`
- `user ghost-posts` → GET `/{threads-user-id}/ghost_posts`
- `user profile-lookup` → GET `/profile_lookup`
- `user profile-posts` → GET `/profile_posts`

### Insights
- `insights media` → GET `/{threads-media-id}/insights`
- `insights user` → GET `/{threads-user-id}/threads_insights`

### Locations
- `locations get` → GET `/{location-id}`
- `locations search` → GET `/location_search`

### oEmbed
- `oembed` → GET `/oembed?url=...`

---

## Troubleshooting

### Port already in use (Errno 48)
If local callback server fails with `OSError: [Errno 48] Address already in use`:
- Change port in `THREADS_REDIRECT_URI` (e.g. `http://localhost:8788/callback`) and update Meta app redirect list.
- Or kill the process using the port.

### Token missing
If CLI says `THREADS_ACCESS_TOKEN not found`:
- Ensure `~/.openclaw/workspace/skills/threads/.env` exists
- Run `auth-local` again

---

## Posting workflow (manual approval)

Use the built-in posting helper:

- Script: `~/.openclaw/workspace/skills/threads/scripts/posting.py`
- State file: `~/.openclaw/workspace/skills/threads/state/pending_posts.json`

Commands:

```bash
# Create/replace draft
python3 ~/.openclaw/workspace/skills/threads/scripts/posting.py draft --text "..."

# Approve content (NO publish)
python3 ~/.openclaw/workspace/skills/threads/scripts/posting.py approve

# Publish (ONLY after explicit public intent)
python3 ~/.openclaw/workspace/skills/threads/scripts/posting.py --env-file ~/.openclaw/workspace/skills/threads/.env publish

# Check current state
python3 ~/.openclaw/workspace/skills/threads/scripts/posting.py status

# Cancel
python3 ~/.openclaw/workspace/skills/threads/scripts/posting.py cancel
```

Notes:
- Put `--env-file ...` **before** the subcommand (argparse rule).
- Default behavior: create the container only at publish time (safer).

## Phase 2: Inbox + Insights dashboards (manual send only)

### Rule: do not proactively send reports
Only send dashboards/reports to Slack **when the user explicitly asks** (examples: "run dashboard", "generate report", "send the dashboard to Slack").

If the user is just configuring or discussing metrics, generate files locally and explain how to run them; do **not** post.

### Dashboard generator
- Script: `~/.openclaw/workspace/skills/threads/scripts/dashboard.py`
- Generates JSON summary + optional PNG charts (via quickchart.io) into `skills/threads/state/charts/`.

Examples:

```bash
# Generate daily 7d + top 10 posts (30d). Writes PNGs to state/charts/
python3 ~/.openclaw/workspace/skills/threads/scripts/dashboard.py \
  --env-file ~/.openclaw/workspace/skills/threads/.env \
  --days 7 --top-days 30 --top-n 10
```

### Inbox digest (mentions/replies)
- Script: `~/.openclaw/workspace/skills/threads/scripts/inbox.py`
- Pulls recent mentions + your recent replies into a single JSON digest.
- Note: if `mentions` returns HTTP 500, treat it as an upstream API issue; the script will still return JSON with an error field and you can retry later.

```bash
python3 ~/.openclaw/workspace/skills/threads/scripts/inbox.py \
  --env-file ~/.openclaw/workspace/skills/threads/.env \
  --limit 20
```

## Assistant workflow (recommended)

1) Run `threads me` to validate auth.
2) When user requests posting, create a draft and ask for confirmation.
3) Treat "OK" as content approval only.
4) Publish only on explicit public intent.
5) After publishing, return the `media_id` / permalink (if available), and optionally fetch insights later.
6) For dashboards/inbox: generate locally; only send to Slack if explicitly requested.