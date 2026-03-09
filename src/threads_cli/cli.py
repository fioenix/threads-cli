#!/usr/bin/env python3
"""Main CLI entry point for Threads API CLI."""

import argparse
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .api import ThreadsAPI
from .auth import run_auth_local


def get_env_file_path(args_env_file: Optional[str] = None) -> str:
    """Get the env file path, using default if not specified."""
    if args_env_file:
        return args_env_file
    # Default to ../.env relative to this file's location
    cli_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(cli_dir, "..", ".env")


def load_env(env_file: str) -> str:
    """Load environment and return access token.

    Compatibility:
    - Prefer THREADS_ACCESS_TOKEN (standardized long-lived token).
    - Fall back to THREADS_ACCESS_TOKEN_LONG if user generated tokens with older helpers.
    """
    load_dotenv(env_file)

    access_token = os.getenv("THREADS_ACCESS_TOKEN")
    if not access_token:
        access_token = os.getenv("THREADS_ACCESS_TOKEN_LONG")

    if not access_token:
        raise ValueError(
            "THREADS_ACCESS_TOKEN not found in environment. "
            "Set THREADS_ACCESS_TOKEN to your long-lived token, or run 'python -m threads_cli auth-local'."
        )

    return access_token


def output_json(data: dict) -> None:
    """Output data as JSON."""
    print(json.dumps(data, indent=2))


def cmd_me(args) -> None:
    """Get current user profile."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_me()
    output_json(result)


def cmd_debug_token(args) -> None:
    """Debug the current access token."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.debug_token(args.input_token)
    output_json(result)


def cmd_token_refresh(args) -> None:
    """Refresh the access token."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.refresh_token()
    output_json(result)


def cmd_publish_create(args) -> None:
    """Create a media container."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)

    user_id = args.user_id or "me"
    result = api.create_media_container(
        user_id=user_id,
        media_type=args.media_type,
        text=args.text,
        image_url=args.image_url,
        video_url=args.video_url,
        reply_to_id=args.reply_to,
        quote_post_id=args.quote_post
    )
    output_json(result)


def cmd_publish_publish(args) -> None:
    """Publish a media container."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)

    user_id = args.user_id or "me"
    result = api.publish_media(user_id, args.creation_id)
    output_json(result)


def cmd_publish_status(args) -> None:
    """Get status of a media container."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_container_status(args.container_id)
    output_json(result)


def cmd_publish_delete(args) -> None:
    """Delete a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.delete_media(args.media_id)
    output_json(result)


def cmd_publish_repost(args) -> None:
    """Repost a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.repost_media(args.media_id)
    output_json(result)


def cmd_media_get(args) -> None:
    """Get a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_media(args.media_id)
    output_json(result)


def cmd_media_keyword_search(args) -> None:
    """Search media by keyword."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.search_media(
        q=args.query,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_replies_list(args) -> None:
    """Get user replies."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user_replies(
        user_id=args.user_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_replies_for_media(args) -> None:
    """Get replies for a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_media_replies(
        media_id=args.media_id,
        limit=args.limit,
        before=args.before,
        after=args.after,
    )
    output_json(result)


def cmd_replies_conversation(args) -> None:
    """Get conversation for a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_conversation(
        media_id=args.media_id,
        reverse=args.reverse,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_replies_pending(args) -> None:
    """Get pending replies."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_pending_replies(
        media_id=args.media_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_replies_manage(args) -> None:
    """Manage a reply (approve/hide)."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.manage_reply(args.reply_id, args.action)
    output_json(result)


def cmd_replies_manage_pending(args) -> None:
    """Manage a pending reply."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.manage_pending_reply(args.reply_id, args.action)
    output_json(result)


def cmd_user_get(args) -> None:
    """Get a user's profile."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user(args.user_id)
    output_json(result)


def cmd_user_threads(args) -> None:
    """Get user's threads."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user_threads(
        user_id=args.user_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_user_publishing_limit(args) -> None:
    """Get user's publishing limit."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_publishing_limit(args.user_id)
    output_json(result)


def cmd_user_replies(args) -> None:
    """Get user's replies."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user_replies(
        user_id=args.user_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_user_mentions(args) -> None:
    """Get user's mentions."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user_mentions(
        user_id=args.user_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_user_ghost_posts(args) -> None:
    """Get user's ghost posts."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_ghost_posts(
        user_id=args.user_id,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_user_profile_lookup(args) -> None:
    """Look up a profile by username."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.profile_lookup(args.username)
    output_json(result)


def cmd_user_profile_posts(args) -> None:
    """Get posts from a specific profile."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_profile_posts(
        username=args.username,
        limit=args.limit,
        before=args.before,
        after=args.after
    )
    output_json(result)


def cmd_insights_media(args) -> None:
    """Get insights for a media post."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_media_insights(args.media_id, args.metrics)
    output_json(result)


def cmd_insights_user(args) -> None:
    """Get insights for a user."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_user_insights(
        user_id=args.user_id,
        metrics=args.metrics,
        since=args.since,
        until=args.until
    )
    output_json(result)


def cmd_locations_get(args) -> None:
    """Get location info."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_location(args.location_id)
    output_json(result)


def cmd_locations_search(args) -> None:
    """Search for locations."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.search_locations(
        q=args.query,
        limit=args.limit
    )
    output_json(result)


def cmd_oembed(args) -> None:
    """Get oEmbed for a URL."""
    env_file = get_env_file_path(args.env_file)
    access_token = load_env(env_file)
    api = ThreadsAPI(access_token)
    result = api.get_oembed(args.url)
    output_json(result)


def cmd_auth_local(args) -> None:
    """Run local OAuth flow to get tokens."""
    env_file = get_env_file_path(args.env_file)
    result = run_auth_local(env_file, args.port)
    output_json(result)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="threads_cli",
        description="Threads API CLI - A command-line interface for the Threads API",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to .env file (default: ../.env relative to cli/)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # me command
    parser_me = subparsers.add_parser("me", help="Get current user profile")
    parser_me.set_defaults(func=cmd_me)

    # debug-token command
    parser_debug = subparsers.add_parser("debug-token", help="Debug access token")
    parser_debug.add_argument("--input-token", help="Token to debug (uses current token if not specified)")
    parser_debug.set_defaults(func=cmd_debug_token)

    # token subcommands
    parser_token = subparsers.add_parser("token", help="Token management")
    token_subparsers = parser_token.add_subparsers(dest="token_command", help="Token commands")

    parser_refresh = token_subparsers.add_parser("refresh", help="Refresh access token")
    parser_refresh.set_defaults(func=cmd_token_refresh)

    # publish subcommands
    parser_publish = subparsers.add_parser("publish", help="Publishing commands")
    publish_subparsers = parser_publish.add_subparsers(dest="publish_command", help="Publish commands")

    parser_create = publish_subparsers.add_parser("create", help="Create a media container")
    parser_create.add_argument("--media-type", required=True, choices=["TEXT", "IMAGE", "VIDEO", "CAROUSEL"], help="Type of media")
    parser_create.add_argument("--text", help="Text content")
    parser_create.add_argument("--image-url", help="Image URL (for IMAGE type)")
    parser_create.add_argument("--video-url", help="Video URL (for VIDEO type)")
    parser_create.add_argument("--reply-to", help="ID of post to reply to")
    parser_create.add_argument("--quote-post", help="ID of post to quote")
    parser_create.add_argument("--user-id", help="User ID (defaults to 'me')")
    parser_create.set_defaults(func=cmd_publish_create)

    parser_pub = publish_subparsers.add_parser("publish", help="Publish a media container")
    parser_pub.add_argument("creation_id", help="ID of the media container to publish")
    parser_pub.add_argument("--user-id", help="User ID (defaults to 'me')")
    parser_pub.set_defaults(func=cmd_publish_publish)

    parser_status = publish_subparsers.add_parser("status", help="Get status of media container")
    parser_status.add_argument("container_id", help="ID of the media container")
    parser_status.set_defaults(func=cmd_publish_status)

    parser_delete = publish_subparsers.add_parser("delete", help="Delete a media post")
    parser_delete.add_argument("media_id", help="ID of the media to delete")
    parser_delete.set_defaults(func=cmd_publish_delete)

    parser_repost = publish_subparsers.add_parser("repost", help="Repost a media post")
    parser_repost.add_argument("media_id", help="ID of the media to repost")
    parser_repost.set_defaults(func=cmd_publish_repost)

    # media subcommands
    parser_media = subparsers.add_parser("media", help="Media commands")
    media_subparsers = parser_media.add_subparsers(dest="media_command", help="Media commands")

    parser_media_get = media_subparsers.add_parser("get", help="Get a media post")
    parser_media_get.add_argument("media_id", help="ID of the media")
    parser_media_get.set_defaults(func=cmd_media_get)

    parser_search = media_subparsers.add_parser("keyword-search", help="Search media by keyword")
    parser_search.add_argument("--query", "-q", required=True, help="Search query")
    parser_search.add_argument("--limit", type=int, help="Maximum results")
    parser_search.add_argument("--before", help="Pagination cursor")
    parser_search.add_argument("--after", help="Pagination cursor")
    parser_search.set_defaults(func=cmd_media_keyword_search)

    # replies subcommands
    parser_replies = subparsers.add_parser("replies", help="Replies commands")
    replies_subparsers = parser_replies.add_subparsers(dest="replies_command", help="Replies commands")

    parser_list = replies_subparsers.add_parser("list", help="Get user replies")
    parser_list.add_argument("--user-id", required=True, help="User ID")
    parser_list.add_argument("--limit", type=int, help="Maximum results")
    parser_list.add_argument("--before", help="Pagination cursor")
    parser_list.add_argument("--after", help="Pagination cursor")
    parser_list.set_defaults(func=cmd_replies_list)

    parser_for_media = replies_subparsers.add_parser("for-media", help="Get replies for a media post")
    parser_for_media.add_argument("media_id", help="Media ID")
    parser_for_media.add_argument("--limit", type=int, help="Maximum results")
    parser_for_media.add_argument("--before", help="Pagination cursor")
    parser_for_media.add_argument("--after", help="Pagination cursor")
    parser_for_media.set_defaults(func=cmd_replies_for_media)

    parser_conv = replies_subparsers.add_parser("conversation", help="Get conversation for a media post")
    parser_conv.add_argument("media_id", help="Media ID")
    parser_conv.add_argument("--reverse", action="store_true", help="Reverse order")
    parser_conv.add_argument("--limit", type=int, help="Maximum results")
    parser_conv.add_argument("--before", help="Pagination cursor")
    parser_conv.add_argument("--after", help="Pagination cursor")
    parser_conv.set_defaults(func=cmd_replies_conversation)

    parser_pending = replies_subparsers.add_parser("pending", help="Get pending replies")
    parser_pending.add_argument("media_id", help="Media ID")
    parser_pending.add_argument("--limit", type=int, help="Maximum results")
    parser_pending.add_argument("--before", help="Pagination cursor")
    parser_pending.add_argument("--after", help="Pagination cursor")
    parser_pending.set_defaults(func=cmd_replies_pending)

    parser_manage = replies_subparsers.add_parser("manage", help="Manage a reply")
    parser_manage.add_argument("reply_id", help="Reply ID")
    parser_manage.add_argument("--action", required=True, choices=["approve", "hide"], help="Action to take")
    parser_manage.set_defaults(func=cmd_replies_manage)

    parser_manage_pending = replies_subparsers.add_parser("manage-pending", help="Manage a pending reply")
    parser_manage_pending.add_argument("reply_id", help="Reply ID")
    parser_manage_pending.add_argument("--action", required=True, choices=["approve", "hide", "delete"], help="Action to take")
    parser_manage_pending.set_defaults(func=cmd_replies_manage_pending)

    # user subcommands
    parser_user = subparsers.add_parser("user", help="User commands")
    user_subparsers = parser_user.add_subparsers(dest="user_command", help="User commands")

    parser_user_get = user_subparsers.add_parser("get", help="Get user profile")
    parser_user_get.add_argument("user_id", help="User ID")
    parser_user_get.set_defaults(func=cmd_user_get)

    parser_threads = user_subparsers.add_parser("threads", help="Get user's threads")
    parser_threads.add_argument("--user-id", required=True, help="User ID")
    parser_threads.add_argument("--limit", type=int, help="Maximum results")
    parser_threads.add_argument("--before", help="Pagination cursor")
    parser_threads.add_argument("--after", help="Pagination cursor")
    parser_threads.set_defaults(func=cmd_user_threads)

    parser_limit = user_subparsers.add_parser("publishing-limit", help="Get user's publishing limit")
    parser_limit.add_argument("user_id", help="User ID")
    parser_limit.set_defaults(func=cmd_user_publishing_limit)

    parser_replies = user_subparsers.add_parser("replies", help="Get user's replies")
    parser_replies.add_argument("--user-id", required=True, help="User ID")
    parser_replies.add_argument("--limit", type=int, help="Maximum results")
    parser_replies.add_argument("--before", help="Pagination cursor")
    parser_replies.add_argument("--after", help="Pagination cursor")
    parser_replies.set_defaults(func=cmd_user_replies)

    parser_mentions = user_subparsers.add_parser("mentions", help="Get user's mentions")
    parser_mentions.add_argument("--user-id", required=True, help="User ID")
    parser_mentions.add_argument("--limit", type=int, help="Maximum results")
    parser_mentions.add_argument("--before", help="Pagination cursor")
    parser_mentions.add_argument("--after", help="Pagination cursor")
    parser_mentions.set_defaults(func=cmd_user_mentions)

    parser_ghost = user_subparsers.add_parser("ghost-posts", help="Get user's ghost posts")
    parser_ghost.add_argument("--user-id", required=True, help="User ID")
    parser_ghost.add_argument("--limit", type=int, help="Maximum results")
    parser_ghost.add_argument("--before", help="Pagination cursor")
    parser_ghost.add_argument("--after", help="Pagination cursor")
    parser_ghost.set_defaults(func=cmd_user_ghost_posts)

    parser_lookup = user_subparsers.add_parser("profile-lookup", help="Look up a profile by username")
    parser_lookup.add_argument("--username", required=True, help="Username to look up")
    parser_lookup.set_defaults(func=cmd_user_profile_lookup)

    parser_profile_posts = user_subparsers.add_parser("profile-posts", help="Get posts from a profile")
    parser_profile_posts.add_argument("--username", required=True, help="Username to get posts from")
    parser_profile_posts.add_argument("--limit", type=int, help="Maximum results")
    parser_profile_posts.add_argument("--before", help="Pagination cursor")
    parser_profile_posts.add_argument("--after", help="Pagination cursor")
    parser_profile_posts.set_defaults(func=cmd_user_profile_posts)

    # insights subcommands
    parser_insights = subparsers.add_parser("insights", help="Insights commands")
    insights_subparsers = parser_insights.add_subparsers(dest="insights_command", help="Insights commands")

    parser_insights_media = insights_subparsers.add_parser("media", help="Get insights for a media post")
    parser_insights_media.add_argument("media_id", help="Media ID")
    parser_insights_media.add_argument("--metrics", default="views,likes,replies,reposts,quotes", help="Metrics to retrieve (comma-separated)")
    parser_insights_media.set_defaults(func=cmd_insights_media)

    parser_insights_user = insights_subparsers.add_parser("user", help="Get insights for a user")
    parser_insights_user.add_argument("user_id", help="User ID")
    parser_insights_user.add_argument("--metrics", default="views,likes,replies,reposts,quotes,followers_count", help="Metrics to retrieve (comma-separated)")
    parser_insights_user.add_argument("--since", help="Start timestamp (Unix)")
    parser_insights_user.add_argument("--until", help="End timestamp (Unix)")
    parser_insights_user.set_defaults(func=cmd_insights_user)

    # locations subcommands
    parser_locations = subparsers.add_parser("locations", help="Location commands")
    locations_subparsers = parser_locations.add_subparsers(dest="locations_command", help="Location commands")

    parser_loc_get = locations_subparsers.add_parser("get", help="Get location info")
    parser_loc_get.add_argument("location_id", help="Location ID")
    parser_loc_get.set_defaults(func=cmd_locations_get)

    parser_loc_search = locations_subparsers.add_parser("search", help="Search for locations")
    parser_loc_search.add_argument("--query", "-q", required=True, help="Search query")
    parser_loc_search.add_argument("--limit", type=int, help="Maximum results")
    parser_loc_search.set_defaults(func=cmd_locations_search)

    # oembed command
    parser_oembed = subparsers.add_parser("oembed", help="Get oEmbed for a URL")
    parser_oembed.add_argument("url", help="URL to get oEmbed for")
    parser_oembed.set_defaults(func=cmd_oembed)

    # auth-local command
    parser_auth = subparsers.add_parser("auth-local", help="Run local OAuth flow to get tokens")
    parser_auth.add_argument("--port", type=int, default=8080, help="Port for callback server")
    parser_auth.set_defaults(func=cmd_auth_local)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle subcommands that need navigation
    if args.command == "token" and not getattr(args, "token_command", None):
        parser_token.print_help()
        sys.exit(1)
    elif args.command == "publish" and not getattr(args, "publish_command", None):
        parser_publish.print_help()
        sys.exit(1)
    elif args.command == "media" and not getattr(args, "media_command", None):
        parser_media.print_help()
        sys.exit(1)
    elif args.command == "replies" and not getattr(args, "replies_command", None):
        parser_replies.print_help()
        sys.exit(1)
    elif args.command == "user" and not getattr(args, "user_command", None):
        parser_user.print_help()
        sys.exit(1)
    elif args.command == "insights" and not getattr(args, "insights_command", None):
        parser_insights.print_help()
        sys.exit(1)
    elif args.command == "locations" and not getattr(args, "locations_command", None):
        parser_locations.print_help()
        sys.exit(1)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except Exception as e:
            output_json({"error": str(e)})
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()