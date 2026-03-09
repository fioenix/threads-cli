# Meta Threads API — App Setup (Development Mode)

This guide is intended to be followed step-by-step.

## 1) Create an app
1. Go to Meta Developer Portal: https://developers.facebook.com/apps/
2. Create a new app.
3. Add/enable **Threads API** for the app.

## 2) Configure OAuth Redirect URI
1. In your app settings, find OAuth / Redirect URIs.
2. Add the redirect URI you will use locally.

Recommended default for local auth:
- `http://localhost:8080/callback`

**Important:** Redirect URI must match EXACTLY (scheme/host/port/path). Trailing slashes matter.

## 3) Add App Roles (fix tester invite errors)
If the app is in **Development** mode, the authenticating user must be in the app roles and must accept the invite.

If you see error:
- `Invalid Request: The user has not accepted the invite to test the app. (1349245)`

Fix:
1. In Meta app dashboard: App Roles → add the user as Tester/Developer.
2. On the user account: accept the invite (Meta/Facebook notifications).

## 4) Configure scopes
In `skills/threads/.env`, set `THREADS_SCOPES` (comma-separated). Example:

- `threads_basic,threads_content_publish,threads_manage_replies,threads_read_replies,threads_manage_insights`

## 5) Generate tokens (long-lived)
From the skill CLI folder:

```bash
cd ~/.openclaw/workspace/skills/threads/cli
python3 -m threads_cli --env-file ../.env auth-local
```

This writes `THREADS_ACCESS_TOKEN` (long-lived) and `THREADS_USER_ID` into `skills/threads/.env`.

## 6) Verify

```bash
python3 -m threads_cli --env-file ../.env me
```
