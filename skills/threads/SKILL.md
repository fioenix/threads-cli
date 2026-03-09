---
name: threads
description: "Use this skill whenever the user mentions Meta Threads API / graph.threads.net, wants to authenticate, refresh/debug tokens, publish/delete/repost posts, manage replies/moderation, fetch insights, or needs a safe workflow for drafting vs publishing on Threads. This skill is agent-agnostic: it works in OpenClaw, Claude Code, and similar agent runtimes by driving the `threads` CLI from this repo."
---

# Threads API Skill (Official)

This is an **agent-agnostic** skill for operating the official Meta **Threads API**.

It assumes you will use the `threads` CLI from this repo (installable via `pipx`) and an `.env` file containing tokens.

> Scope: The official Threads API does **not** provide Home / For You / Following feed reading. Don’t claim it can fetch those.

## Quick start (recommended)

```bash
pipx install threads-cli
cp examples/threads/env.example skills/threads/.env
threads --env-file skills/threads/.env me
```

## Inputs / files

- Skill folder: `skills/threads/`
- Secrets env file (local only): `skills/threads/.env` (do **not** commit)

If your agent runs in another working directory, use an **absolute** path for `--env-file`.

## Safety rule (publish approval gate)

Treat all user requests as **draft-first**.

- User saying **“OK / looks good”** = approves the *draft text only*.
- Only publish when the user clearly expresses **public intent**:
  - EN: `publish`, `post it`, `go live`
  - VI: `đăng bài`, `post bài`, `public lên`, `đẩy lên`

Before publishing, always echo the final payload and ask for explicit confirmation.

## Workflow (decision tree)

1) **Setup / OAuth / tokens** → read: `references/setup-meta-app.md`
2) **Which endpoint/field to use** → read: `references/endpoints.md`
3) **How to run the CLI commands** → read: `references/cli-cheatsheet.md`

## What to do when triggered

### A) Validate env + connection
Run:

```bash
threads --env-file skills/threads/.env me
```

If missing token, instruct user to run:

```bash
threads --env-file skills/threads/.env auth-local
```

### B) Drafting content (no publish)
- Produce 1–3 draft options.
- Keep Threads posts short (1–4 lines often win).
- Ask for confirmation **only** when user wants to publish.

### C) Publishing (only after explicit publish intent)
Use the CLI flow (create → publish). Exact commands/examples are in `references/cli-cheatsheet.md`.

### D) Moderation + replies
Use `replies for-media`, `conversation`, `pending`, and `manage` via CLI.

### E) Insights
Use `insights media` and `insights user` via CLI.

## Troubleshooting (common)

- Error: tester invite not accepted (1349245)
  - Fix: add user as tester/developer and accept invite. See `references/setup-meta-app.md`.

## Bundled resources

- `references/setup-meta-app.md` — Meta app + OAuth setup checklist
- `references/endpoints.md` — endpoint map
- `references/cli-cheatsheet.md` — copy/paste CLI commands (auth, publish, replies, insights)

---

## Minimal examples (copy/paste)

```bash
# Debug token / refresh
threads --env-file skills/threads/.env debug-token
threads --env-file skills/threads/.env token refresh

# Publish (after user explicitly confirms)
threads --env-file skills/threads/.env publish create --media-type TEXT --text "Hello Threads"
# then publish using returned creation_id
```
