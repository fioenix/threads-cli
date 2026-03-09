#!/usr/bin/env python3
"""Create a Slack-ready report payload (TEXT + image paths).

This script DOES NOT send to Slack.
It outputs JSON so the assistant can decide whether to send (only on explicit user request).

Usage:
  python3 report_payload.py --env-file ~/.openclaw/workspace/skills/threads/.env --days 7 --top-days 30 --top-n 10

Output schema:
{
  "text": "...",
  "images": ["/abs/path/a.png", "/abs/path/b.png"],
  "data": { ...raw summary... }
}

"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import dashboard generator
from dashboard import main as _dashboard_main  # type: ignore


def run_dashboard_and_capture(argv: list[str]) -> Dict[str, Any]:
    # Run dashboard.py as a subprocess to capture JSON stdout.
    import subprocess

    cmd = [sys.executable, os.path.join(SKILL_DIR, "scripts", "dashboard.py")] + argv
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or r.stdout.strip() or f"dashboard failed: {r.returncode}")
    return json.loads(r.stdout)


def fmt_summary(summary: Dict[str, Any]) -> str:
    daily = summary.get("daily", {})
    series = daily.get("views_series") or []
    likes = daily.get("likes_total")
    replies = daily.get("replies_total")

    daily_line = " | ".join([f"{d} {v}" for d, v in series])

    top = summary.get("top_posts") or []
    top_lines = []
    for i, p in enumerate(top, start=1):
        top_lines.append(
            f"{i}) {p.get('timestamp','?')[:10]} · {p.get('id')} — {p.get('views',0)} views / {p.get('likes',0)} likes / {p.get('replies',0)} replies"
        )

    return (
        "Threads Dashboard\n\n"
        f"Daily (last {summary.get('range',{}).get('days','?')}d):\n"
        f"- Views: {daily_line}\n"
        f"- Likes total: {likes}\n"
        f"- Replies total: {replies}\n\n"
        f"Top posts (last {summary.get('range',{}).get('top_days','?')}d):\n"
        + "\n".join(top_lines)
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Slack-ready report payload (no send)")
    p.add_argument("--env-file", default=None)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--top-days", type=int, default=30)
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()

    argv = []
    if args.env_file:
        argv += ["--env-file", args.env_file]
    argv += ["--days", str(args.days), "--top-days", str(args.top_days), "--top-n", str(args.top_n), "--limit", str(args.limit)]

    summary = run_dashboard_and_capture(argv)
    chart_paths = summary.get("chart_paths", {})
    images = [p for p in [chart_paths.get("daily_views"), chart_paths.get("top_posts")] if p]

    payload = {
        "text": fmt_summary(summary),
        "images": images,
        "data": summary,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
