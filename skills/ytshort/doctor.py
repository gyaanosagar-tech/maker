"""
doctor.py — "connect" hua ya nahi, ek command me pata karo.

    python doctor.py              # sab check
    python doctor.py --yt         # sirf YouTube
    python doctor.py --ig         # sirf Instagram/FB
    python doctor.py --drive      # sirf Drive

Kuch bhi upload nahi karta. Sirf batata hai kya missing/tuta hai.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

import config

OK = "\033[92m✔\033[0m"
BAD = "\033[91m✘\033[0m"
WARN = "\033[93m!\033[0m"

problems: list[str] = []


def line(mark: str, label: str, detail: str = "") -> None:
    print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))


# ------------------------------------------------------------------ tools
def check_tools() -> None:
    print("\n[1] Tools")
    ff = shutil.which("ffmpeg")
    line(OK if ff else BAD, "ffmpeg", ff or "missing — IG re-encode fail hoga")
    if not ff:
        problems.append("ffmpeg install karo: `sudo apt install ffmpeg` (Mac: brew install ffmpeg)")
    for mod in ("googleapiclient", "google_auth_oauthlib", "dotenv", "requests"):
        try:
            __import__(mod)
            line(OK, f"python: {mod}")
        except ImportError:
            line(BAD, f"python: {mod}")
            problems.append("pip install -r requirements.txt")


# ------------------------------------------------------------------ youtube
def check_youtube() -> dict | None:
    print("\n[2] YouTube")
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET and config.YT_REFRESH_TOKEN):
        line(BAD, "creds", "YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN missing")
        problems.append("YouTube connect: `python will_provide.py --analytics --env`")
        return None

    try:
        import youtube_uploader as yt

        yt_service = yt.service()
        resp = yt_service.channels().list(part="snippet,statistics", mine=True).execute()
        items = resp.get("items", [])
        if not items:
            line(WARN, "token valid", "par koi channel nahi mila (brand account?)")
            return None
        ch = items[0]
        stats = ch.get("statistics", {})
        line(OK, "channel", f"{ch['snippet']['title']} ({ch['id']})")
        line(OK, "subscribers", stats.get("subscriberCount", "hidden"))
        line(OK, "videos", stats.get("videoCount", "0"))
        line(OK, "notifySubscribers", f"{config.NOTIFY_SUBSCRIBERS} (rule: False)")
    except Exception as exc:
        msg = str(exc)
        line(BAD, "token", msg[:150])
        if "invalid_grant" in msg:
            problems.append(
                "Refresh token expire (Testing app = 7 din). `python will_provide.py --analytics --env` "
                "dobara chalao. Permanent fix: OAuth consent screen ko Published karo."
            )
        elif "insufficient" in msg.lower() or "scope" in msg.lower():
            problems.append("Scope kam hai — `will_provide.py --analytics` se token dobara")
        else:
            problems.append("YouTube: OAuth client Desktop app hai? YouTube Data API enable hai?")
        return None

    # playlist — rule: random nahi, exact
    try:
        import youtube_uploader as yt

        playlists, token = [], None
        while True:
            page = yt.service().playlists().list(
                part="id,snippet", mine=True, maxResults=50, pageToken=token
            ).execute()
            playlists.extend(page.get("items", []))
            token = page.get("nextPageToken")
            if not token:
                break
        if not playlists:
            line(WARN, "playlists", "channel pe ek bhi playlist nahi — pehle banao")
            problems.append("Channel pe playlist banao, phir uski ID .env me PLAYLIST_IDS daalo")
        else:
            line(OK, "playlists", f"{len(playlists)} mili:")
            for p in playlists[:12]:
                marker = " <-- configured" if p["id"] in config.PLAYLIST_IDS else ""
                print(f"       {p['id']}  {p['snippet']['title']}{marker}")
            if not config.PLAYLIST_IDS and not config.PLAYLIST_MAP:
                problems.append(f"PLAYLIST_IDS khaali — upar se ek ID chuno: {playlists[0]['id']}")
    except Exception as exc:
        line(WARN, "playlist lookup", str(exc)[:120])

    # analytics scope
    try:
        from datetime import datetime, timedelta

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials(
            None, refresh_token=config.YT_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET,
            scopes=[config.YT_ANALYTICS_SCOPE,
                    "https://www.googleapis.com/auth/youtube.force-ssl"],
        )
        analytics = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        end = datetime.now().date()
        analytics.reports().query(
            ids="channel==MINE",
            startDate=(end - timedelta(days=7)).isoformat(),
            endDate=end.isoformat(),
            metrics="views",
        ).execute()
        line(OK, "insights scope", "YouTube Analytics chal raha hai")
    except Exception as exc:
        line(WARN, "insights scope", str(exc)[:110])
        problems.append("Insights ke liye: `python will_provide.py --analytics --env` "
                        "(YouTube Analytics API bhi enable karo)")

    if config.YT_CHANNEL_ID:
        line(OK, "YT_CHANNEL_ID", config.YT_CHANNEL_ID)
    return {"ok": True}


# ------------------------------------------------------------------ instagram
def check_instagram() -> None:
    print("\n[3] Instagram / Facebook")
    if not config.IG_ACCESS_TOKEN:
        line(BAD, "token", "IG_ACCESS_TOKEN missing")
        problems.append("IG: Business Settings → System User → token (pages_manage_posts + "
                        "instagram_content_publish + instagram_insights)")
        return

    import requests

    try:
        me = requests.get(f"{config.GRAPH}/me",
                          params={"fields": "id,name", "access_token": config.IG_ACCESS_TOKEN},
                          timeout=30).json()
        if "error" in me:
            line(BAD, "token", str(me["error"].get("message"))[:140])
            problems.append("IG token invalid/expired — System User se dobara generate karo")
            return
        line(OK, "token", me.get("name", me.get("id")))
    except Exception as exc:
        line(BAD, "token", str(exc)[:140])
        return

    import instagram_uploader as ig

    for ig_id in config.IG_USER_IDS:
        try:
            info = ig.account_info(ig_id)
            line(OK, f"IG @{info['username']}",
                 f"{info['followers']} followers, {info['media_count']} posts")
            allowed, note = ig.trial_allowed(ig_id)
            line(OK if allowed else WARN, "trial reels", note)
            if not allowed:
                print(f"       → sab normal reels. {config.TRIAL_MIN_FOLLOWERS - info['followers']} "
                      f"followers aur chahiye, phir bot khud mix chalu kar dega")
            quota = ig.publishing_quota(ig_id)
            if quota:
                line(OK, "publish quota", f"{quota.get('quota_usage')} used / 24h")
        except Exception as exc:
            line(BAD, f"IG {ig_id}", str(exc)[:140])
            problems.append(f"IG {ig_id}: account FB Page se linked hai? "
                            "instagram_content_publish assign hai?")

    for page in config.FB_PAGE_IDS:
        try:
            data = requests.get(f"{config.GRAPH}/{page}",
                                params={"fields": "name", "access_token": config.IG_ACCESS_TOKEN},
                                timeout=30).json()
            if "error" in data:
                line(BAD, f"FB Page {page}", str(data["error"].get("message"))[:120])
                problems.append(f"FB Page {page}: pages_manage_posts assign karo")
            else:
                line(OK, f"FB Page {data.get('name')}", page)
        except Exception as exc:
            line(BAD, f"FB Page {page}", str(exc)[:120])


# ------------------------------------------------------------------ drive
def check_drive() -> None:
    print("\n[4] Drive")
    if not (config.GOOGLE_SERVICE_ACCOUNT_JSON or config.GOOGLE_SERVICE_ACCOUNT_JSON_B64):
        line(BAD, "creds", "GOOGLE_SERVICE_ACCOUNT_JSON missing")
        problems.append("Drive: service account JSON banao aur video file/folder uske email pe share karo")
        return
    try:
        import drive_helper

        about = drive_helper.service().about().get(fields="user").execute()
        line(OK, "service account", about.get("user", {}).get("emailAddress", "?"))
        if config.FOLDER_VIDEOS:
            try:
                meta = drive_helper.service().files().get(
                    fileId=config.FOLDER_VIDEOS, fields="id,name", supportsAllDrives=True
                ).execute()
                line(OK, "Videos folder", meta["name"])
                files = drive_helper.service().files().list(
                    q=f"'{config.FOLDER_VIDEOS}' in parents and trashed = false",
                    fields="files(id,name,size)", pageSize=100, supportsAllDrives=True
                ).execute().get("files", [])
                vids = [f for f in files if f["name"].lower().endswith(config.VIDEO_EXTS)]
                line(OK, "Videos folder me", f"{len(vids)} video, {len(files)} files")
                for f in vids[:10]:
                    print(f"       {f['name']} ({int(f.get('size', 0))/1e6:.1f} MB)")
            except Exception as exc:
                line(BAD, "Videos folder", str(exc)[:120])
                problems.append("Videos folder SA ko share nahi hua (Viewer)")
        if config.FOLDER_REENCODED:
            meta = drive_helper.service().files().get(
                fileId=config.FOLDER_REENCODED, fields="id,name", supportsAllDrives=True
            ).execute()
            line(OK, "FOLDER_REENCODED", meta["name"])
        else:
            line(WARN, "FOLDER_REENCODED", "khaali — IG upload fail hoga (public folder chahiye)")
            problems.append("Ek Drive folder public banao, ID FOLDER_REENCODED me daalo")
    except Exception as exc:
        line(BAD, "access", str(exc)[:160])
        problems.append("Drive: service account email ko file/folder pe Viewer share karo")


# ------------------------------------------------------------------ run
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yt", action="store_true")
    ap.add_argument("--ig", action="store_true")
    ap.add_argument("--drive", action="store_true")
    args = ap.parse_args()
    all_checks = not (args.yt or args.ig or args.drive)

    print("=== sulbot doctor ===")
    if all_checks:
        check_tools()
    if all_checks or args.yt:
        check_youtube()
    if all_checks or args.ig:
        check_instagram()
    if all_checks or args.drive:
        check_drive()

    print("\n=== Result ===")
    if problems:
        for i, p in enumerate(problems, 1):
            print(f"  {i}. {p}")
        return 1
    print("  Sab connected. `python bot.py upload <file> --job jobs/x.json --publish` chalao.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
