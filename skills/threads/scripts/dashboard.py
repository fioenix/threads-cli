#!/usr/bin/env python3
"""Threads Slack Dashboard generator (PNG charts + JSON summary).

Generates:
- Daily views chart for last N days via user insights
- Top N posts by views for last M days via user threads + media insights

Charts are rendered via quickchart.io (no local matplotlib dependency).

Usage:
  python3 dashboard.py --env-file ~/.openclaw/workspace/skills/threads/.env \
    --days 7 --top-days 30 --top-n 10

Outputs:
- Prints a JSON summary to stdout
- Writes PNG charts to skills/threads/state/

"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import subprocess
from typing import Any, Dict, List, Optional, Tuple

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(SKILL_DIR, "state")
CHARTS_DIR = os.path.join(STATE_DIR, "charts")

# Ensure threads_cli import works when running directly
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


def parse_iso8601ish(s: str) -> dt.datetime:
    # Example: 2026-03-02T08:00:00+0000
    # Python %z expects +0000
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")


def to_day_label(d: dt.datetime, tz: dt.tzinfo) -> str:
    return d.astimezone(tz).strftime("%m-%d")


def quickchart_png(config: Dict[str, Any], out_path: str, width: int = 900, height: int = 450) -> str:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    qc = {
        "width": width,
        "height": height,
        "format": "png",
        "chart": config,
        # Background for Slack dark/light
        "backgroundColor": "white",
    }

    # Use GET with URL-encoded config (fine for small configs)
    q = urllib.parse.quote(json.dumps(qc, separators=(",", ":")))
    url = f"https://quickchart.io/chart?c={q}"

    # Download with curl (available on macOS)
    cmd = ["curl", "-L", "-sS", url, "-o", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("Failed to download chart image", stderr=r.stderr, url=url)

    return out_path


def get_user_id(env_file: str, api: ThreadsAPI) -> str:
    load_dotenv(env_file)
    uid = os.getenv("THREADS_USER_ID")
    if uid:
        return uid
    me = api.get_me()
    uid = me.get("id")
    if not uid:
        die("Unable to resolve THREADS_USER_ID via env or /me", me=me)
    return uid


def fetch_user_daily_insights(api: ThreadsAPI, user_id: str, metrics: str, since_ts: int, until_ts: int) -> Dict[str, Any]:
    return api.get_user_insights(user_id=user_id, metrics=metrics, since=str(since_ts), until=str(until_ts))


def extract_daily_series(insights: Dict[str, Any], metric_name: str, tz: dt.tzinfo) -> List[Tuple[str, int]]:
    # Return list of (day_label, value)
    for item in insights.get("data", []):
        if item.get("name") != metric_name:
            continue
        values = item.get("values")
        if not values:
            return []
        series: List[Tuple[str, int]] = []
        for v in values:
            end_time = v.get("end_time")
            val = int(v.get("value") or 0)
            if not end_time:
                continue
            d = parse_iso8601ish(end_time)
            series.append((to_day_label(d, tz), val))
        return series
    return []


def extract_total(insights: Dict[str, Any], metric_name: str) -> Optional[int]:
    for item in insights.get("data", []):
        if item.get("name") != metric_name:
            continue
        tv = item.get("total_value")
        if isinstance(tv, dict) and "value" in tv:
            return int(tv.get("value") or 0)
    return None


def list_recent_threads(api: ThreadsAPI, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    resp = api.get_user_threads(user_id=user_id, limit=limit)
    data = resp.get("data")
    if isinstance(data, list):
        return data
    return []


def within_days(ts_iso: str, days: int, now_utc: dt.datetime) -> bool:
    # timestamp like 2026-03-09T07:00:00+0000 or with Z? Usually +0000.
    try:
        d = parse_iso8601ish(ts_iso)
    except Exception:
        return False
    return (now_utc - d.astimezone(dt.timezone.utc)) <= dt.timedelta(days=days)


def get_media_views(insights: Dict[str, Any]) -> int:
    for item in insights.get("data", []):
        if item.get("name") == "views":
            vals = item.get("values") or []
            if vals:
                return int(vals[0].get("value") or 0)
    return 0


def get_media_likes(insights: Dict[str, Any]) -> int:
    for item in insights.get("data", []):
        if item.get("name") == "likes":
            vals = item.get("values") or []
            if vals:
                return int(vals[0].get("value") or 0)
    return 0


def get_media_replies(insights: Dict[str, Any]) -> int:
    for item in insights.get("data", []):
        if item.get("name") == "replies":
            vals = item.get("values") or []
            if vals:
                return int(vals[0].get("value") or 0)
    return 0


def build_views_line_chart(labels: List[str], values: List[int], title: str) -> Dict[str, Any]:
    return {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Views",
                    "data": values,
                    "borderColor": "#4C6EF5",
                    "backgroundColor": "rgba(76,110,245,0.2)",
                    "fill": True,
                    "tension": 0.35,
                    "pointRadius": 3,
                }
            ],
        },
        "options": {
            "plugins": {
                "title": {"display": True, "text": title},
                "legend": {"display": False},
            },
            "scales": {"y": {"beginAtZero": True}},
        },
    }


def build_top_posts_bar_chart(labels: List[str], values: List[int], title: str) -> Dict[str, Any]:
    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Views",
                    "data": values,
                    "backgroundColor": "#12B886",
                }
            ],
        },
        "options": {
            "indexAxis": "y",
            "plugins": {
                "title": {"display": True, "text": title},
                "legend": {"display": False},
            },
            "scales": {"x": {"beginAtZero": True}},
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Generate Threads dashboard charts")
    p.add_argument("--env-file", default=None, help="Path to .env")
    p.add_argument("--days", type=int, default=7, help="Daily range for user insights")
    p.add_argument("--top-days", type=int, default=30, help="Range for top posts")
    p.add_argument("--top-n", type=int, default=10, help="Number of top posts")
    p.add_argument("--metrics", default="views,likes,replies", help="Core metrics")
    p.add_argument("--limit", type=int, default=50, help="How many recent posts to scan")
    args = p.parse_args()

    env_file = get_env_file_path(args.env_file)
    token = load_env(env_file)
    api = ThreadsAPI(token)

    user_id = get_user_id(env_file, api)

    now = int(time.time())
    since_ts = now - args.days * 86400

    # Use local timezone for labels (Asia/Saigon)
    tz = dt.timezone(dt.timedelta(hours=7))

    # A) daily insights
    user_ins = fetch_user_daily_insights(api, user_id=user_id, metrics=args.metrics, since_ts=since_ts, until_ts=now)
    daily_views = extract_daily_series(user_ins, "views", tz)
    total_likes = extract_total(user_ins, "likes")
    total_replies = extract_total(user_ins, "replies")

    # C) top posts (last top-days)
    now_utc = dt.datetime.now(dt.timezone.utc)
    posts = list_recent_threads(api, user_id=user_id, limit=args.limit)
    recent_posts = [p for p in posts if p.get("id") and p.get("timestamp") and within_days(p["timestamp"], args.top_days, now_utc)]

    enriched: List[Dict[str, Any]] = []
    for post in recent_posts:
        mid = post.get("id")
        try:
            ins = api.get_media_insights(mid, metrics=args.metrics)
        except Exception as e:
            # Skip but record
            enriched.append({"id": mid, "timestamp": post.get("timestamp"), "text": post.get("text"), "error": str(e)})
            continue

        enriched.append(
            {
                "id": mid,
                "timestamp": post.get("timestamp"),
                "text": post.get("text"),
                "views": get_media_views(ins),
                "likes": get_media_likes(ins),
                "replies": get_media_replies(ins),
            }
        )

    ranked = sorted([e for e in enriched if "views" in e], key=lambda x: x.get("views", 0), reverse=True)
    top = ranked[: args.top_n]

    # Render charts
    os.makedirs(CHARTS_DIR, exist_ok=True)

    chart_paths: Dict[str, str] = {}

    if daily_views:
        labels = [d for d, _ in daily_views]
        vals = [v for _, v in daily_views]
        cfg = build_views_line_chart(labels, vals, title=f"Threads: Daily Views (last {args.days}d)")
        out_path = os.path.join(CHARTS_DIR, f"daily_views_{args.days}d.png")
        chart_paths["daily_views"] = quickchart_png(cfg, out_path)

    if top:
        # Label as MM-DD + short id
        labels = []
        vals = []
        for e in top:
            ts = e.get("timestamp")
            day = "?"
            if ts:
                try:
                    day = to_day_label(parse_iso8601ish(ts), tz)
                except Exception:
                    pass
            labels.append(f"{day} · {str(e['id'])[-6:]}")
            vals.append(int(e.get("views") or 0))

        cfg = build_top_posts_bar_chart(labels, vals, title=f"Top {len(top)} Posts by Views (last {args.top_days}d)")
        out_path = os.path.join(CHARTS_DIR, f"top_posts_{args.top_days}d.png")
        chart_paths["top_posts"] = quickchart_png(cfg, out_path, width=900, height=max(450, 60 * len(top)))

    summary = {
        "generated_at": now,
        "user_id": user_id,
        "range": {"days": args.days, "top_days": args.top_days, "top_n": args.top_n},
        "daily": {
            "views_series": daily_views,
            "likes_total": total_likes,
            "replies_total": total_replies,
        },
        "top_posts": top,
        "chart_paths": chart_paths,
    }

    out(summary)


if __name__ == "__main__":
    main()
