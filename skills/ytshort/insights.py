"""
insights.py — aapka performance data nikaal ke CSV me daalna.

Ye wo hissa hai jisse "level kaisa chal raha hai" pata chalta hai:
  YT  : views, likes, comments, avg view duration, retention proxy
  IG  : reach, plays, likes, saves, shares, follows (trial vs normal)
  FB  : page video views/reactions

Important: ye read-only hai. Upload ke liye alag scope hai, isliye YT
analytics ke liye `will_provide.py --analytics` chala ke token dobara lena hoga.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, timedelta

import requests

import config
import state_store
from state_store import IST


def _init_csv(path: str, fields: list[str]) -> None:
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=fields).writeheader()


YT_FIELDS = ["fetched_ist", "video_id", "title", "published", "views", "likes",
             "comments", "avg_view_duration_sec", "avg_view_percentage", "watch_hours"]


# ------------------------------------------------------------------ YouTube
def youtube_analytics(days: int = 30) -> list[dict]:
    """YT Analytics API — scope chahiye: yt-analytics.readonly."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            None,
            refresh_token=config.YT_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.YT_CLIENT_ID,
            client_secret=config.YT_CLIENT_SECRET,
            scopes=[config.YT_ANALYTICS_SCOPE, "https://www.googleapis.com/auth/youtube.readonly"],
        )
        analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        end = datetime.now(IST).date()
        start = end - timedelta(days=days)
        resp = analytics.reports().query(
            ids="channel==MINE",
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            metrics="views,likes,comments,averageViewDuration,averageViewPercentage,estimatedMinutesWatched",
            dimensions="video",
            sort="-views",
            maxResults=200,
        ).execute()
        headers = [h["name"] for h in resp.get("columnHeaders", [])]
        rows = []
        for row in resp.get("rows", []):
            item = dict(zip(headers, row))
            rows.append({
                "fetched_ist": state_store.fmt(state_store.now_ist()),
                "video_id": item.get("video"),
                "title": "",
                "published": "",
                "views": item.get("views"),
                "likes": item.get("likes"),
                "comments": item.get("comments"),
                "avg_view_duration_sec": round(float(item.get("averageViewDuration") or 0), 1),
                "avg_view_percentage": round(float(item.get("averageViewPercentage") or 0), 1),
                "watch_hours": round(float(item.get("estimatedMinutesWatched") or 0) / 60, 1),
            })
        return rows
    except Exception as exc:
        msg = str(exc)
        print(f"[insights] YT analytics skip: {msg[:200]}")
        if "insufficient" in msg.lower() or "scope" in msg.lower():
            state_store.learn("YT analytics scope missing — `python will_provide.py --analytics` "
                              "chala ke naya refresh token daalo")
        return []


# ------------------------------------------------------------------ Instagram
IG_METRICS = "reach,views,likes,comments,saved,shares,total_interactions"


def instagram_insights(limit: int = 50) -> list[dict]:
    if not config.IG_USER_IDS:
        return []
    ig_id = config.IG_USER_IDS[0]
    rows: list[dict] = []
    try:
        resp = requests.get(
            f"{config.GRAPH}/{ig_id}/media",
            params={"fields": "id,caption,media_product_type,timestamp,permalink",
                    "limit": limit, "access_token": config.IG_ACCESS_TOKEN},
            timeout=60,
        )
        data = resp.json()
        if "error" in data:
            print(f"[insights] IG media list fail: {data['error'].get('message')}")
            return []
        for media in data.get("data", [])[:limit]:
            ins = requests.get(
                f"{config.GRAPH}/{media['id']}/insights",
                params={"metric": IG_METRICS, "access_token": config.IG_ACCESS_TOKEN},
                timeout=60,
            ).json()
            values = {m["name"]: (m.get("values") or [{}])[0].get("value")
                      for m in ins.get("data", [])}
            rows.append({
                "fetched_ist": state_store.fmt(state_store.now_ist()),
                "media_id": media["id"],
                "caption_head": (media.get("caption") or "")[:60].replace("\n", " "),
                "posted": media.get("timestamp", "")[:16],
                "media_product": media.get("media_product_type", ""),
                "reach": values.get("reach"),
                "views": values.get("views"),
                "likes": values.get("likes"),
                "comments": values.get("comments"),
                "saves": values.get("saved"),
                "shares": values.get("shares"),
                "follows": values.get("follows"),
                "trial": "unknown",
            })
    except Exception as exc:
        print(f"[insights] IG fail: {exc}")
    return rows


# ------------------------------------------------------------------ write
def collect(days: int = 30) -> dict:
    """Sab platform ka data nikaal ke analysis/performance.csv me append karo."""
    state_store.ensure_dirs()
    _init_csv(config.INSIGHTS_CSV, YT_FIELDS + ["platform"])
    yt_rows = youtube_analytics(days)
    ig_rows = instagram_insights()

    with open(config.INSIGHTS_CSV, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=YT_FIELDS + ["platform"], extrasaction="ignore")
        for row in yt_rows:
            writer.writerow({**row, "platform": "youtube"})
        for row in ig_rows:
            writer.writerow({**row, "platform": "instagram"})

    summary = {
        "youtube_rows": len(yt_rows),
        "instagram_rows": len(ig_rows),
        "csv": config.INSIGHTS_CSV,
    }
    state_store.learn(f"insights: YT {len(yt_rows)} rows, IG {len(ig_rows)} rows")
    return summary


def quick_summary() -> str:
    """
    Bot ke liye chhota report — main (assistant) isko padh ke level batata hoon.
    """
    rows = []
    if os.path.exists(config.INSIGHTS_CSV):
        with open(config.INSIGHTS_CSV, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

    lines = ["# Performance snapshot", ""]
    yt = [r for r in rows if r.get("platform") == "youtube"]
    ig = [r for r in rows if r.get("platform") == "instagram"]

    if yt:
        def num(r, key):
            try:
                return float(r.get(key) or 0)
            except ValueError:
                return 0.0

        top = sorted(yt, key=lambda r: num(r, "views"), reverse=True)[:5]
        lines += ["## YouTube (last fetch)", "",
                  "| video | views | avg % dekha | watch hrs |", "|---|---|---|---|"]
        for r in top:
            lines.append(f"| {r.get('video_id')} | {int(num(r,'views'))} | "
                         f"{num(r,'avg_view_percentage'):.0f}% | {num(r,'watch_hours'):.1f} |")
        avg_pct = sum(num(r, "avg_view_percentage") for r in yt) / max(len(yt), 1)
        lines += ["", f"Average view percentage: **{avg_pct:.0f}%** "
                      "(<50% = hook weak, 70%+ = strong)"]
    else:
        lines += ["## YouTube", "", "_data nahi — `python bot.py insights` chalao_", ""]

    if ig:
        def num2(r, key):
            try:
                return float(r.get(key) or 0)
            except ValueError:
                return 0.0

        top = sorted(ig, key=lambda r: num2(r, "views"), reverse=True)[:5]
        lines += ["", "## Instagram", "", "| media | views | reach | saves | shares |",
                  "|---|---|---|---|---|"]
        for r in top:
            lines.append(f"| {r.get('caption_head') or r.get('media_id')} | "
                         f"{int(num2(r,'views'))} | {int(num2(r,'reach'))} | "
                         f"{int(num2(r,'saves'))} | {int(num2(r,'shares'))} |")
    else:
        lines += ["", "## Instagram", "", "_data nahi_"]
    return "\n".join(lines) + "\n"


def write_report() -> str:
    path = os.path.join(config.ANALYSIS_DIR, "report.md")
    os.makedirs(config.ANALYSIS_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(quick_summary())
    return path


if __name__ == "__main__":
    state_store.ensure_dirs()
    print(collect())
    print(write_report())
