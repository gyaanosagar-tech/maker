"""
youtube_uploader.py — YT ke saare steps ek jagah.

Rule jo aapne diye:
  1. notifySubscribers = FALSE har upload pe (default true hota hai, isliye force)
  2. Random playlist nahi — aapki di hui exact playlist me hi daalna

Yaad rakho: notifySubscribers sirf upload ke waqt set hota hai.
Baad me API se badla nahi ja sakta (sirf Studio se) — isliye lock kiya hai.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import config
import state_store

# youtube.force-ssl ek hi scope me saare write kaam cover karta hai:
#   videos.insert (upload), playlistItems.insert (playlist),
#   videos.update (backfill), captions/ratings bhi.
# Iske saath `youtube` / `youtube.upload` / `youtube.readonly` maangna
# overlapping scopes hai — Google reject kar sakta hai. Isliye sirf ye do.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
RETRIABLE = (500, 502, 503, 504)


def service(scopes: list[str] | None = None):
    creds = Credentials(
        None,
        refresh_token=config.YT_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.YT_CLIENT_ID,
        client_secret=config.YT_CLIENT_SECRET,
        scopes=scopes or SCOPES,
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


# ------------------------------------------------------------------ playlist
def resolve_playlist(built: dict) -> str | None:
    """
    Playlist rule: random nahi.
    1. text me diya `playlist` naam/ID
    2. PLAYLIST_MAP me category
    3. PLAYLIST_IDS ka pehla
    Na mile to None -> upload hoga par playlist me nahi (aur log me warning).
    """
    wanted = built.get("playlist")
    if wanted and wanted.startswith("PL"):
        return wanted
    if wanted and wanted in config.PLAYLIST_MAP:
        return config.PLAYLIST_MAP[wanted]
    if wanted:
        # naam diya hai — channel ki playlists me dhoondo
        found = find_playlist_by_name(wanted)
        if found:
            return found
    if "default" in config.PLAYLIST_MAP:
        return config.PLAYLIST_MAP["default"]
    return config.PLAYLIST_IDS[0] if config.PLAYLIST_IDS else None


def find_playlist_by_name(name: str) -> str | None:
    """Channel ki apni playlists me naam se dhundo (exact match pehle)."""
    try:
        yt = service()
        token = None
        playlists: list[dict] = []
        while True:
            resp = yt.playlists().list(
                part="id,snippet", mine=True, maxResults=50, pageToken=token
            ).execute()
            playlists.extend(resp.get("items", []))
            token = resp.get("nextPageToken")
            if not token:
                break
        lowered = name.strip().lower()
        for p in playlists:
            if p["snippet"]["title"].strip().lower() == lowered:
                return p["id"]
        for p in playlists:
            if lowered in p["snippet"]["title"].strip().lower():
                return p["id"]
        print(f"[youtube] playlist '{name}' nahi mili — channel me ye hain: "
              f"{[p['snippet']['title'] for p in playlists][:8]}")
    except HttpError as exc:
        print(f"[youtube] playlist lookup fail: {exc}")
    return None


def add_to_playlist(video_id: str, playlist_id: str) -> bool:
    """video ko exact playlist me daalo (50 quota units)."""
    try:
        service().playlistItems().insert(
            part="snippet",
            body={"snippet": {"playlistId": playlist_id,
                              "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
        ).execute()
        print(f"[youtube] playlist me daal diya: {playlist_id}")
        return True
    except HttpError as exc:
        # quota khatam / playlist private / already present
        state_store.learn(f"playlist insert fail ({video_id} -> {playlist_id}): {exc}")
        print(f"[youtube] playlist insert FAIL: {exc}")
        return False


# ------------------------------------------------------------------ upload
class PrivacyNotSet(Exception):
    """Job me privacy likha hi nahi — upload band. User ka rule."""


VALID_PRIVACY = ("public", "private", "unlisted")


def resolve_privacy(built: dict, publish_at_ist: datetime | None) -> str:
    """
    Privacy SIRF job file se aati hai. Code khud se kuch nahi chunta.

    Job me likhna hoga:
        "privacy": "public"                 -> public
        "privacy": "private"                -> private
        "privacy": "unlisted"               -> unlisted
        "privacy": "scheduled" + "when"     -> private + publishAt

    Kuch bhi nahi likha -> PrivacyNotSet (upload hi nahi hoga).
    Ye jaan-boojh ke fail-closed hai: galti se kuch live na jaye.
    """
    raw = str(built.get("privacy") or "").strip().lower()

    if not raw:
        raise PrivacyNotSet(
            'job me "privacy" nahi likha — upload rok diya. '
            'Likho: "privacy": "public" | "private" | "unlisted" | "scheduled"'
        )

    if raw not in VALID_PRIVACY + ("scheduled",):
        raise PrivacyNotSet(
            f'privacy="{raw}" galat. Sirf: public, private, unlisted, scheduled'
        )

    if raw == "scheduled":
        if not publish_at_ist:
            raise PrivacyNotSet('privacy="scheduled" hai par "when" (IST time) nahi diya')
        return "private"          # publishAt ke saath YT khud public karega

    if publish_at_ist and raw == "public":
        # schedule + public maanga -> publishAt ke liye private chahiye
        return "private"

    return raw


def build_body(built: dict, publish_at_ist: datetime | None) -> dict:
    privacy = resolve_privacy(built, publish_at_ist)
    status: dict = {
        "privacyStatus": privacy,
        "selfDeclaredMadeForKids": False,
        "madeForKids": False,
    }
    if publish_at_ist:
        status["publishAt"] = publish_at_ist.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "snippet": {
            "title": built["title"],
            "description": built["description"],
            "tags": built["tags"],
            "categoryId": "22",
        },
        "status": status,
    }


def upload(file_path: str, built: dict, publish_at_ist: datetime | None = None) -> str:
    """
    Upload + playlist + notification OFF. video_id deta hai.
    publish_at_ist diya to private + publishAt (YT khud public karega).
    """
    yt = service()
    media = MediaFileUpload(file_path, chunksize=8 * 1024 * 1024, resumable=True)
    request = yt.videos().insert(
        part="snippet,status",
        body=build_body(built, publish_at_ist),
        media_body=media,
        notifySubscribers=config.NOTIFY_SUBSCRIBERS,   # <- rule 1: hamesha False
    )

    response = None
    attempt = 0
    while response is None:
        attempt += 1
        try:
            status, response = request.next_chunk()
            if status:
                print(f"[youtube] upload {int(status.progress() * 100)}%")
        except HttpError as exc:
            if exc.resp.status in RETRIABLE and attempt < 6:
                wait = min(2 ** attempt, 60)
                print(f"[youtube] {exc.resp.status} — {wait}s baad retry")
                time.sleep(wait)
                continue
            raise

    video_id = response["id"]
    print(f"[youtube] uploaded https://youtu.be/{video_id} "
          f"(notify={config.NOTIFY_SUBSCRIBERS}, "
          f"{'scheduled ' + state_store.fmt(publish_at_ist) if publish_at_ist else 'public'})")

    _check_privacy_override(video_id, publish_at_ist)

    playlist_id = resolve_playlist(built)
    if playlist_id:
        add_to_playlist(video_id, playlist_id)
    else:
        state_store.learn(f"{video_id}: playlist set nahi thi — random playlist me nahi daala")
        print("[youtube] WARN playlist nahi mili — rule ke hisaab se skip kiya (random nahi)")
    return video_id


def _check_privacy_override(video_id, publish_at_ist) -> None:
    """Unverified project -> YouTube uploads ko private kar sakta hai. Warn karo."""
    state = verify(video_id)
    privacy = state.get("privacy")
    if privacy == "private" and not publish_at_ist:
        msg = (f"{video_id}: public maanga, YouTube ne PRIVATE rakha - "
               "project ka API audit pending ho sakta hai (YouTube API compliance audit)")
        print(f"[youtube] !! {msg}")
        state_store.learn(msg)
    else:
        print(f"[youtube] privacy check: {privacy}")


def verify(video_id: str) -> dict:
    try:
        resp = service().videos().list(part="status,snippet", id=video_id).execute()
        items = resp.get("items", [])
        if not items:
            return {"state": "missing"}
        status = items[0]["status"]
        return {
            "privacy": status.get("privacyStatus"),
            "publishAt": status.get("publishAt"),
            "uploadStatus": status.get("uploadStatus"),
            "title": items[0]["snippet"]["title"],
        }
    except HttpError as exc:
        return {"state": f"error: {exc}"}


def publish_at_ok(slot: datetime | None, now: datetime | None = None) -> bool:
    """publishAt kam se kam ~15 min future chahiye, warna YT reject karta hai."""
    if slot is None:
        return False
    now = now or state_store.now_ist()
    return (slot - now) >= timedelta(minutes=15)
