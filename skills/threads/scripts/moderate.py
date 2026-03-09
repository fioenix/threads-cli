#!/usr/bin/env python3
"""Reply moderation helper with explicit intent.

This script is intentionally explicit: you must choose an action and provide a reply_id.
It performs NO automatic actions.

Usage:
  python3 moderate.py --env-file ~/.openclaw/workspace/skills/threads/.env manage --reply-id <id> --action approve|hide
  python3 moderate.py --env-file ~/.openclaw/workspace/skills/threads/.env manage-pending --reply-id <id> --action approve|hide|delete

"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_DIR = os.path.join(SKILL_DIR, "cli")
if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)

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


def cmd_manage(args: argparse.Namespace) -> None:
    env_file = get_env_file_path(args.env_file)
    token = load_env(env_file)
    api = ThreadsAPI(token)
    out(api.manage_reply(args.reply_id, args.action))


def cmd_manage_pending(args: argparse.Namespace) -> None:
    env_file = get_env_file_path(args.env_file)
    token = load_env(env_file)
    api = ThreadsAPI(token)
    out(api.manage_pending_reply(args.reply_id, args.action))


def main() -> None:
    p = argparse.ArgumentParser(description="Threads reply moderation helper")
    p.add_argument("--env-file", default=None)

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("manage", help="Manage a reply")
    s.add_argument("--reply-id", required=True)
    s.add_argument("--action", required=True, choices=["approve", "hide"])
    s.set_defaults(func=cmd_manage)

    s = sub.add_parser("manage-pending", help="Manage a pending reply")
    s.add_argument("--reply-id", required=True)
    s.add_argument("--action", required=True, choices=["approve", "hide", "delete"])
    s.set_defaults(func=cmd_manage_pending)

    try:
        args = p.parse_args()
        args.func(args)
    except Exception as e:
        die("Unhandled error", exception=str(e))


if __name__ == "__main__":
    main()
