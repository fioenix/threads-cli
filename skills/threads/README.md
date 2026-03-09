# Threads API CLI

A command-line interface for the Threads API.

## Installation

```bash
cd cli
pip install -e .
```

Or use directly with:

```bash
python -m threads_cli [command]
```

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Create a Threads app in the [Meta Developer Portal](https://developers.facebook.com/apps/)

3. Add your credentials to `.env`:
   ```
   THREADS_APP_ID=your_app_id
   THREADS_APP_SECRET=your_app_secret
   THREADS_REDIRECT_URI=http://localhost:8080/callback
   THREADS_SCOPES=threads_basic,threads_content_publish
   ```

4. Run the local auth flow to get access tokens:
   ```bash
   python -m threads_cli auth-local
   ```

   This saves `THREADS_ACCESS_TOKEN` (long-lived), `THREADS_REFRESH_TOKEN`, and `THREADS_USER_ID` to your `.env` file.

## Usage

### Global Options

- `--env-file` - Path to .env file (default: `../.env` relative to cli/)

### Commands

#### User Commands

```bash
# Get current user profile
python -m threads_cli me

# Get a specific user's profile
python -m threads_cli user get <user_id>

# Get user's threads
python -m threads_cli user threads --user-id <user_id> [--limit N]

# Get user's publishing limit
python -m threads_cli user publishing-limit <user_id>

# Get user's replies
python -m threads_cli user replies --user-id <user_id> [--limit N]

# Get user's mentions
python -m threads_cli user mentions --user-id <user_id> [--limit N]

# Get user's ghost posts
python -m threads_cli user ghost-posts --user-id <user_id> [--limit N]

# Look up a profile by username
python -m threads_cli user profile-lookup --username <username>

# Get posts from a profile
python -m threads_cli user profile-posts --username <username>
```

#### Publishing Commands

```bash
# Create a text post container
python -m threads_cli publish create --media-type TEXT --text "Hello, Threads!"

# Create an image post container
python -m threads_cli publish create --media-type IMAGE --image-url <url> --text "Caption"

# Create a video post container
python -m threads_cli publish create --media-type VIDEO --video-url <url> --text "Caption"

# Create a reply container
python -m threads_cli publish create --media-type TEXT --text "Reply text" --reply-to <post_id>

# Create a quote post container
python -m threads_cli publish create --media-type TEXT --text "Quote text" --quote-post <post_id>

# Publish a container
python -m threads_cli publish publish <creation_id>

# Check container status
python -m threads_cli publish status <container_id>

# Delete a post
python -m threads_cli publish delete <media_id>

# Repost a post
python -m threads_cli publish repost <media_id>
```

#### Media Commands

```bash
# Get a media post
python -m threads_cli media get <media_id>

# Search media by keyword
python -m threads_cli media keyword-search --query "keyword"
```

#### Replies Commands

```bash
# Get user's replies
python -m threads_cli replies list --user-id <user_id>

# Get replies for a media post
python -m threads_cli replies for-media <media_id> [--limit N]

# Get conversation for a post
python -m threads_cli replies conversation <media_id> [--reverse]

# Get pending replies for a media post
python -m threads_cli replies pending <media_id>

# Manage a reply
python -m threads_cli replies manage <reply_id> --action approve|hide

# Manage a pending reply
python -m threads_cli replies manage-pending <reply_id> --action approve|hide|delete
```

#### Insights Commands

```bash
# Get insights for a media post
python -m threads_cli insights media <media_id> [--metrics views,likes,replies]

# Get insights for a user
python -m threads_cli insights user <user_id> [--metrics views,likes] [--since timestamp] [--until timestamp]
```

#### Location Commands

```bash
# Get location info
python -m threads_cli locations get <location_id>

# Search locations
python -m threads_cli locations search --query "query"
```

#### Token Commands

```bash
# Debug current token
python -m threads_cli debug-token

# Refresh access token
python -m threads_cli token refresh
```

#### Other Commands

```bash
# Get oEmbed for a URL
python -m threads_cli oembed <url>

# Run local OAuth flow
python -m threads_cli auth-local [--port 8080]
```

## Output

All commands output JSON to stdout.

## Error Handling

Errors are returned as JSON with an `error` key:

```json
{
  "error": "Error message"
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `THREADS_APP_ID` | Your Threads app ID (from Meta Developer Portal) |
| `THREADS_APP_SECRET` | Your Threads app secret (from Meta Developer Portal) |
| `THREADS_REDIRECT_URI` | OAuth redirect URI (must match your app settings) |
| `THREADS_SCOPES` | OAuth scopes (comma-separated, optional) |
| `THREADS_ACCESS_TOKEN` | Long-lived access token (obtained via auth-local) |
| `THREADS_REFRESH_TOKEN` | Refresh token (optional, obtained via auth-local) |
| `THREADS_USER_ID` | Your Threads user ID (optional, auto-detected during auth) |

### Token Lifecycle

The `auth-local` command performs a complete OAuth flow:

1. **Authorization**: Opens browser for user to grant permissions
2. **Short-lived token**: Exchanges authorization code for short-lived token
3. **Long-lived token**: Exchanges short-lived token for long-lived token (~60 day expiry)
4. **User ID**: Fetches and saves your Threads user ID

Long-lived tokens are valid for approximately 60 days. Use `token refresh` to refresh before expiry.

## Development

```bash
# Run tests
cd cli
python -m pytest

# Run with specific env file
python -m threads_cli --env-file /path/to/.env me
```

## API Reference

This CLI wraps the [Threads API](https://developers.facebook.com/docs/threads). See the official documentation for detailed API information.