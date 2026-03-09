#!/usr/bin/env python3
"""Threads inbox digest: mentions + your replies.

This script does NOT perform moderation actions.
It produces a JSON digest that the assistant can summarize.

Usage:
  python3 inbox.py --env-file ~/.openclaw/workspace/skills/threads/.env --limit 20

"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_DIR = os.path.join(SKILL_DIR, "cli")
if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)

from dotenv import load_dotenv

from threads_cli.cli import get_env_file_path, load_env
from threads_cli.api import ThreadsAPI


def die(msg: str, code: int = 1, **details: Any) -> None:
    payload: Dict[str, Any] = {"error": msg}
    if details:
        payload["details"] = details
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    raise SystemExit(code)


def out(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def resolve_user_id(env_file: str, api: ThreadsAPI) -> str:
    load_dotenv(env_file)
    uid = os.getenv("THREADS_USER_ID")
    if uid:
        return uid
    me = api.get_me()
    uid = me.get("id")
    if not uid:
        die("Unable to resolve THREADS_USER_ID", me=me)
    return uid


def main() -> None:
    p = argparse.ArgumentParser(description="Threads inbox digest")
    p.add_argument("--env-file", default=None, help="Path to .env")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--mentions", action="store_true", help="Only mentions")
    p.add_argument("--replies", action="store_true", help="Only replies")
    args = p.parse_args()

    env_file = get_env_file_path(args.env_file)
    token = load_env(env_file)
    api = ThreadsAPI(token)
    user_id = resolve_user_id(env_file, api)

    limit = args.limit

    include_mentions = args.mentions or (not args.mentions and not args.replies)
    include_replies = args.replies or (not args.mentions and not args.replies)

    result: Dict[str, Any] = {
        "generated_at": int(time.time()),
        "user_id": user_id,
        "limit": limit,
        "mentions": None,
        "replies": None,
    }

    if include_mentions:
        try:
            result["mentions"] = api.get_user_mentions(user_id=user_id, limit=limit)
        except Exception as e:
            result["mentions"] = {"error": str(e)}

    if include_replies:
        try:
            result["replies"] = api.get_user_replies(user_id=user_id, limit=limit)
        except Exception as e:
            result["replies"] = {"error": str(e)}

    out(result)


if __name__ == "__main__":
    main()
