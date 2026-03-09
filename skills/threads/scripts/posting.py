#!/usr/bin/env python3
"""Manual-approval posting workflow for Threads.

This script is intentionally simple and file-based.

State machine:
- DRAFTED -> CONTENT_APPROVED -> PUBLISHED

Rules:
- 'approve' only marks the draft as approved (no API calls).
- 'publish' requires an approved draft and will create+publish the post.

It delegates network calls to the threads_cli module.

Usage examples:
  python3 posting.py draft --text "hello"
  python3 posting.py approve
  python3 posting.py publish
  python3 posting.py status
  python3 posting.py cancel

Env:
  Uses the same env file as threads_cli by default: ../.env

"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Reuse threads_cli internals (keeps behavior consistent)
# Make sure the CLI package is importable when running this script directly.
_CLI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cli")
if _CLI_DIR not in sys.path:
    sys.path.insert(0, _CLI_DIR)

from threads_cli.cli import get_env_file_path, load_env
from threads_cli.api import ThreadsAPI

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(SKILL_DIR, "state", "pending_posts.json")


@dataclass
class Draft:
    id: str
    text: str
    created_at: int
    content_approved: bool = False
    published: bool = False
    published_at: Optional[int] = None
    # Threads API results
    creation_id: Optional[str] = None
    media_id: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None


def _now() -> int:
    return int(time.time())


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return {"draft": None}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)


def get_draft(state: Dict[str, Any]) -> Optional[Draft]:
    d = state.get("draft")
    if not d:
        return None
    return Draft(**d)


def set_draft(state: Dict[str, Any], draft: Optional[Draft]) -> None:
    state["draft"] = None if draft is None else draft.__dict__


def die(message: str, code: int = 1, **details: Any) -> None:
    payload: Dict[str, Any] = {"error": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    raise SystemExit(code)


def out(data: Dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_draft(args: argparse.Namespace) -> None:
    state = load_state()
    text = (args.text or "").strip()
    if not text:
        die("Missing --text")

    draft = Draft(
        id=f"draft_{_now()}",
        text=text,
        created_at=_now(),
        content_approved=False,
        published=False,
    )
    set_draft(state, draft)
    save_state(state)

    out(
        {
            "status": "DRAFTED",
            "draft": {
                "id": draft.id,
                "created_at": draft.created_at,
                "text": draft.text,
                "length": len(draft.text),
            },
            "next": [
                "Run approve to approve the content (no publish)",
                "Then run publish after explicit public intent",
            ],
        }
    )


def cmd_approve(args: argparse.Namespace) -> None:
    state = load_state()
    draft = get_draft(state)
    if not draft:
        die("No draft to approve. Create one with: draft --text ...")
    if draft.published:
        die("Draft already published. Create a new draft.")

    draft.content_approved = True
    set_draft(state, draft)
    save_state(state)

    out(
        {
            "status": "CONTENT_APPROVED",
            "draft": {
                "id": draft.id,
                "text": draft.text,
                "length": len(draft.text),
            },
            "note": "Content approved. NOT published yet.",
            "next": ["Run publish only after explicit public intent."],
        }
    )


def cmd_publish(args: argparse.Namespace) -> None:
    state = load_state()
    draft = get_draft(state)
    if not draft:
        die("No draft to publish. Create one with: draft --text ...")
    if draft.published:
        die("Draft already published. Create a new draft.")
    if not draft.content_approved:
        die("Draft content is not approved yet. Run approve first.")

    env_file = get_env_file_path(args.env_file)
    token = load_env(env_file)
    api = ThreadsAPI(token)

    # Determine user id
    user_id = args.user_id
    if not user_id:
        # Try env
        from dotenv import load_dotenv

        load_dotenv(env_file)
        user_id = os.getenv("THREADS_USER_ID")
    if not user_id:
        # Fallback: fetch /me
        me = api.get_me()
        user_id = me.get("id")

    if not user_id:
        die("THREADS_USER_ID missing and unable to resolve via /me")

    # Create container (text-only) and publish
    creation = api.create_media_container(user_id=user_id, media_type="TEXT", text=draft.text)
    creation_id = creation.get("id") or creation.get("creation_id")
    if not creation_id:
        die("Create container did not return an id", response=creation)

    publish_resp = api.publish_media(user_id=user_id, creation_id=creation_id)

    # Graph responses differ; best-effort parse
    media_id = publish_resp.get("id") or publish_resp.get("media_id")

    draft.creation_id = creation_id
    draft.media_id = media_id
    draft.last_result = {
        "create": creation,
        "publish": publish_resp,
    }
    draft.published = True
    draft.published_at = _now()

    set_draft(state, draft)
    save_state(state)

    out(
        {
            "status": "PUBLISHED",
            "draft": {
                "id": draft.id,
                "published_at": draft.published_at,
                "creation_id": draft.creation_id,
                "media_id": draft.media_id,
                "text": draft.text,
            },
            "result": draft.last_result,
        }
    )


def cmd_status(args: argparse.Namespace) -> None:
    state = load_state()
    draft = get_draft(state)
    if not draft:
        out({"status": "EMPTY", "draft": None})
        return

    out(
        {
            "status": "PUBLISHED" if draft.published else ("CONTENT_APPROVED" if draft.content_approved else "DRAFTED"),
            "draft": {
                "id": draft.id,
                "created_at": draft.created_at,
                "content_approved": draft.content_approved,
                "published": draft.published,
                "published_at": draft.published_at,
                "creation_id": draft.creation_id,
                "media_id": draft.media_id,
                "length": len(draft.text),
                "text": draft.text,
            },
        }
    )


def cmd_cancel(args: argparse.Namespace) -> None:
    state = load_state()
    if not get_draft(state):
        out({"status": "EMPTY", "message": "Nothing to cancel"})
        return

    set_draft(state, None)
    save_state(state)
    out({"status": "CANCELED"})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Threads manual-approval posting workflow")
    p.add_argument(
        "--env-file",
        help="Path to .env file (default: ../.env relative to cli/).",
        default=None,
    )
    p.add_argument(
        "--user-id",
        help="Threads user id to publish as. If omitted, uses THREADS_USER_ID in env or resolves via /me.",
        default=None,
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("draft", help="Create/replace the pending draft")
    s.add_argument("--text", required=True, help="Draft text")
    s.set_defaults(func=cmd_draft)

    s = sub.add_parser("approve", help="Approve the pending draft content (no publish)")
    s.set_defaults(func=cmd_approve)

    s = sub.add_parser("publish", help="Publish the approved draft (creates container at publish time)")
    s.set_defaults(func=cmd_publish)

    s = sub.add_parser("status", help="Show current pending draft state")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("cancel", help="Cancel and clear the pending draft")
    s.set_defaults(func=cmd_cancel)

    return p


def main() -> None:
    try:
        args = build_parser().parse_args()
        args.func(args)
    except ValueError as e:
        die(str(e))
    except Exception as e:
        die("Unhandled error", exception=str(e))


if __name__ == "__main__":
    main()
