"""
instagram_uploader.py — IG Reels (trial + normal) + FB Page video.

Teen sach jo isme chhupe hain:
 1. IG me native scheduling NAHI hai -> bot cron se sahi time pe publish karta hai.
 2. Trial reel ke liye 200+ followers chahiye aur `trial_params` chahiye
    (Insta khud decide nahi karti — hum flag lagate hain).
 3. Bada file (21M+) `FINISHED` nahi deta -> re-encode karke 5-6M banate hain.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from datetime import datetime, timezone

import requests

import config
import drive_helper
import state_store


class IgError(RuntimeError):
    pass


# ------------------------------------------------------------------ account
def account_info(ig_user_id: str) -> dict:
    """Username + followers — trial allowed hai ya nahi, ye isi se tay hota hai."""
    resp = requests.get(
        f"{config.GRAPH}/{ig_user_id}",
        params={"fields": "username,followers_count,media_count",
                "access_token": config.IG_ACCESS_TOKEN},
        timeout=30,
    )
    data = _check(resp, "account_info")
    return {
        "username": data.get("username"),
        "followers": int(data.get("followers_count") or 0),
        "media_count": int(data.get("media_count") or 0),
    }


def trial_allowed(ig_user_id: str) -> tuple[bool, str]:
    """Trial reel ka gate: 200+ followers (aapke account pe abhi nahi hai)."""
    try:
        info = account_info(ig_user_id)
    except IgError as exc:
        return False, f"account info nahi mila: {exc}"
    if info["followers"] < config.TRIAL_MIN_FOLLOWERS:
        return False, (f"@{info['username']} pe {info['followers']} followers hain "
                       f"(trial ke liye {config.TRIAL_MIN_FOLLOWERS}+) — sab normal reels")
    return True, f"@{info['username']} pe {info['followers']} followers — trial chalu"


def publishing_quota(ig_user_id: str) -> dict | None:
    resp = requests.get(
        f"{_graph_base(config.IG_ACCESS_TOKEN)}/{ig_user_id}/content_publishing_limit",
        params={"fields": "quota_usage,config", "access_token": config.IG_ACCESS_TOKEN},
        timeout=30,
    )
    try:
        data = resp.json()
        return data["data"][0] if data.get("data") else None
    except (ValueError, KeyError, IndexError):
        return None


# ------------------------------------------------------------------ helpers
def _check(resp: requests.Response, what: str) -> dict:
    try:
        data = resp.json()
    except ValueError:
        raise IgError(f"{what}: non-JSON {resp.status_code} {resp.text[:200]}")
    if "error" in data:
        err = data["error"]
        msg = f"{what}: {err.get('message')} (code={err.get('code')}, sub={err.get('error_subcode')})"
        code = err.get("code")
        if code == 100:
            msg += ("\n  HINT: #100 No permission — System User ko Pages pe pages_manage_posts,"
                    " IG pe instagram_content_publish assign karo aur token dobara generate karo")
        elif code == 9007:
            msg += "\n  HINT: #9007 video URL fetch nahi hua — re-encode/public link check karo"
        elif code in (10, 200) and "trial" in str(err.get("message", "")).lower():
            msg += "\n  HINT: trial reel fail — followers 200+ hain? daily trial cap?"
        raise IgError(msg)
    return data


def reencode(src: str) -> str:
    """720x1280 baseline — 21M -> 5-6M, warna IG FINISHED nahi deta."""
    if not config.IG_REENCODE:
        return src
    if not shutil.which("ffmpeg"):
        raise IgError("ffmpeg install nahi hai (CI: apt-get install -y ffmpeg)")
    dst = os.path.splitext(src)[0] + "_ig.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, *config.IG_FFMPEG_ARGS, dst]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise IgError(f"ffmpeg fail: {result.stderr[-600:]}")
    print(f"[ig] re-encode {os.path.getsize(src)/1e6:.1f}M -> {os.path.getsize(dst)/1e6:.1f}M")
    return dst


def fb_token_status() -> dict:
    """FB Page token kitna din bacha. 1 din se kam -> alarm."""
    tok = config.FB_ACCESS_TOKEN
    if not tok:
        return {"ok": False, "error": "FB_ACCESS_TOKEN khaali"}
    try:
        r = requests.get(f"{config.GRAPH}/debug_token",
                         params={"input_token": tok, "access_token": tok}, timeout=20)
        d = (r.json().get("data") or {})
        ea = d.get("expires_at")
        if ea in (0, None):
            return {"ok": True, "permanent": True, "scopes": d.get("scopes", [])}
        import datetime as _dt
        left = _dt.datetime.fromtimestamp(ea) - _dt.datetime.now()
        return {"ok": True, "permanent": False, "days_left": left.days,
                "expires": _dt.datetime.fromtimestamp(ea).strftime("%Y-%m-%d %H:%M"),
                "scopes": d.get("scopes", [])}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def _graph_base(token: str) -> str:
    """Instagram Login token (IG...) -> graph.instagram.com; warna facebook."""
    if token.startswith("IG"):
        return "https://graph.instagram.com/v21.0"
    return config.GRAPH


# ------------------------------------------------------------------ IG publish
def post_reel(ig_user_id: str, local_path: str, caption: str,
              trial: bool = False) -> dict:
    """
    IG reel post — RESUMABLE upload (rupload.facebook.com).
    Koi public URL / Drive folder / hosting nahi chahiye.

    Zaroorat: Facebook Login Page token (EAAG.../EABA...), jisme
    instagram_content_publish ho. Page se IG account juda hona chahiye.

    trial=True -> trial_params (200+ followers chahiye)
    """
    if trial and state_store.count_today_trial() >= config.TRIAL_DAILY_CAP:
        print(f"[ig] trial daily cap ({config.TRIAL_DAILY_CAP}) hit — normal reel bana rahe hain")
        trial = False

    pub_path = reencode(local_path)
    size = os.path.getsize(pub_path)
    size_mb = size / 1e6
    if size_mb > 100:
        print(f"[ig] WARN {size_mb:.0f}M — IG reject kar sakta hai")

    token = config.FB_ACCESS_TOKEN or config.IG_ACCESS_TOKEN
    if not token:
        raise IgError("FB_ACCESS_TOKEN / IG_ACCESS_TOKEN khaali")

    # 1) resumable container
    payload = {
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption,
        "share_to_feed": "true",
        "access_token": token,
    }
    if trial:
        payload["trial_params"] = f'{{"graduation_strategy":"{config.TRIAL_GRADUATION}"}}'
        print(f"[ig] TRIAL reel (graduation={config.TRIAL_GRADUATION})")

    resp = requests.post(f"{config.GRAPH}/{ig_user_id}/media", data=payload, timeout=120)
    created = _check(resp, "create_container")
    container_id = created["id"]
    uri = created.get("uri")
    print(f"[ig] container {container_id}")

    # 2) bytes -> rupload
    if uri:
        with open(pub_path, "rb") as fh:
            up = requests.post(uri, headers={
                "Authorization": f"OAuth {token}",
                "offset": "0",
                "file_size": str(size),
            }, data=fh, timeout=1800)
        _check(up, "rupload")
        print(f"[ig] uploaded {size_mb:.1f}M (resumable)")

    # 3) poll + 4) publish
    _poll(container_id)

    resp = requests.post(
        f"{config.GRAPH}/{ig_user_id}/media_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=120,
    )
    media_id = _check(resp, "media_publish")["id"]
    print(f"[ig] published media {media_id} (trial={trial}, {size_mb:.1f}M)")
    return {
        "media_id": media_id,
        "container_id": container_id,
        "trial": trial,
        "size_mb": round(size_mb, 1),
    }


def _poll(container_id: str) -> None:
    for attempt in range(1, config.IG_POLL_TRIES + 1):
        resp = requests.get(
            f"{_graph_base(config.IG_ACCESS_TOKEN)}/{container_id}",
            params={"fields": "status_code,status", "access_token": config.IG_ACCESS_TOKEN},
            timeout=60,
        )
        data = _check(resp, "poll")
        code = data.get("status_code")
        print(f"[ig] poll {attempt}/{config.IG_POLL_TRIES}: {code}")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise IgError(f"container {code}: {data.get('status')}")
        time.sleep(config.IG_POLL_SLEEP)
    raise IgError("container FINISHED nahi hua — video specs/URL check karo")


# ------------------------------------------------------------------ FB
def post_fb_video(page_id: str, local_path: str, description: str,
                  title: str | None = None,
                  scheduled_publish_time: int | None = None) -> str:
    """
    FB Page video (FB pe trial ka concept nahi hai — sab normal).
    scheduled_publish_time = unix ts -> FB khud us time publish karega.
    """
    if not page_id:
        raise IgError("FB_PAGE_IDS khaali hai")
    payload = {
        "description": description[:5000],
        "title": (title or os.path.basename(local_path))[:255],
        "access_token": config.FB_ACCESS_TOKEN or config.IG_ACCESS_TOKEN,
    }
    if scheduled_publish_time:
        payload["published"] = "false"
        payload["scheduled_publish_time"] = str(int(scheduled_publish_time))
        print(f"[fb] scheduled {datetime.fromtimestamp(scheduled_publish_time, timezone.utc)}")
    with open(local_path, "rb") as fh:
        resp = requests.post(
            f"{config.GRAPH}/{page_id}/videos",
            data=payload,
            files={"source": (os.path.basename(local_path), fh, "video/mp4")},
            timeout=900,
        )
    video_id = str(_check(resp, "fb_upload_video").get("id"))
    print(f"[fb] video {video_id}")
    return video_id
