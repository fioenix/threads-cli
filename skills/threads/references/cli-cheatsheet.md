# threads-cli — CLI cheatsheet

Assumes you created `skills/threads/.env` locally and installed the CLI:

```bash
pipx install threads-cli
```

All commands below use:

```bash
threads --env-file skills/threads/.env <command>
```

## Auth / token

```bash
threads --env-file skills/threads/.env auth-local
threads --env-file skills/threads/.env me

threads --env-file skills/threads/.env debug-token
threads --env-file skills/threads/.env token refresh
```

## Publish

### Create (TEXT)
```bash
threads --env-file skills/threads/.env publish create --media-type TEXT --text "Hello Threads"
```

### Publish
Take `creation_id` from create response:

```bash
threads --env-file skills/threads/.env publish publish <creation_id>
```

### Status / delete / repost
```bash
threads --env-file skills/threads/.env publish status <container_id>
threads --env-file skills/threads/.env publish delete <media_id>
threads --env-file skills/threads/.env publish repost <media_id>
```

## Media

```bash
threads --env-file skills/threads/.env media get <media_id>
threads --env-file skills/threads/.env media keyword-search -q "openclaw" --limit 20
```

## Replies / moderation

```bash
threads --env-file skills/threads/.env replies for-media <media_id>
threads --env-file skills/threads/.env replies conversation <media_id>
threads --env-file skills/threads/.env replies pending <media_id>

threads --env-file skills/threads/.env replies manage <reply_id> --action approve
threads --env-file skills/threads/.env replies manage <reply_id> --action hide
threads --env-file skills/threads/.env replies manage-pending <reply_id> --action delete
```

## User

```bash
threads --env-file skills/threads/.env user get <user_id>
threads --env-file skills/threads/.env user threads --user-id <user_id> --limit 20
threads --env-file skills/threads/.env user mentions --user-id <user_id> --limit 20
threads --env-file skills/threads/.env user replies --user-id <user_id> --limit 20
threads --env-file skills/threads/.env user profile-lookup --username <username>
threads --env-file skills/threads/.env user profile-posts --username <username> --limit 20
```

## Insights

```bash
threads --env-file skills/threads/.env insights media <media_id> --metrics "views,likes,replies,reposts,quotes"

# since/until are Unix timestamps
threads --env-file skills/threads/.env insights user <user_id> --metrics "views,likes,replies,reposts,quotes,followers_count" --since <since> --until <until>
```

## Locations / oEmbed

```bash
threads --env-file skills/threads/.env locations search -q "Ho Chi Minh" --limit 10
threads --env-file skills/threads/.env oembed <url>
```
