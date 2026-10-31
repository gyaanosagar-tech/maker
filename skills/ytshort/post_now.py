"""
post_now.py — ek reel Instagram + Facebook pe turant post karo.

Instagram: resumable upload (rupload.facebook.com) — koi hosting/URL nahi chahiye.
Facebook : direct file upload.

    python post_now.py --file video.mp4 --ig-caption "..." --fb-caption "..."
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import requests

import config

IG_ID = "17841459943818819"   # @failtadka via Page
GRAPH = config.GRAPH


def _env() -> dict:
    d = {}
    for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k] = v.strip().strip('"').strip("'")
    return d


def _check(r, what):
    if r.status_code >= 400:
        try:
            e = r.json().get("error", {})
            raise RuntimeError(f"{what} FAIL {r.status_code}: {e.get('message')} "
                               f"(code {e.get('code')}, sub {e.get('error_subcode')})")
        except ValueError:
            raise RuntimeError(f"{what} FAIL {r.status_code}: {r.text[:200]}")
    return r.json()


# ------------------------------------------------------------------ instagram
def ig_post(path: str, caption: str, token: str) -> dict:
    size = os.path.getsize(path)
    print(f"[ig] file {size/1e6:.1f} MB")

    # 1. resumable container
    r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
        "media_type": "REELS",
        "upload_type": "resumable",
        "caption": caption,
        "share_to_feed": "true",
        "access_token": token,
    }, timeout=60)
    c = _check(r, "container")
    cid, uri = c["id"], c["uri"]
    print(f"[ig] container {cid}")

    # 2. upload bytes to rupload
    with open(path, "rb") as fh:
        up = requests.post(uri, headers={
            "Authorization": f"OAuth {token}",
            "offset": "0",
            "file_size": str(size),
        }, data=fh, timeout=900)
    _check(up, "rupload")
    print("[ig] bytes uploaded")

    # 3. poll
    for i in range(40):
        time.sleep(8)
        st = requests.get(f"{GRAPH}/{cid}", params={
            "fields": "status_code,status", "access_token": token}, timeout=40).json()
        code = st.get("status_code")
        print(f"[ig] {i+1}. {code}")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {code}: {st.get('status')}")
    else:
        raise RuntimeError("container timeout")

    # 4. publish
    r = requests.post(f"{GRAPH}/{IG_ID}/media_publish", data={
        "creation_id": cid, "access_token": token}, timeout=120)
    pub = _check(r, "media_publish")
    print(f"[ig] PUBLISHED {pub.get('id')}")

    info = requests.get(f"{GRAPH}/{pub['id']}", params={
        "fields": "permalink,media_type,timestamp", "access_token": token}, timeout=40).json()
    print(f"[ig] {info.get('permalink')}")
    return {"id": pub.get("id"), "permalink": info.get("permalink")}


# ------------------------------------------------------------------ facebook
def fb_post(path: str, caption: str, title: str, token: str, page_id: str) -> dict:
    size = os.path.getsize(path)
    print(f"[fb] uploading {size/1e6:.1f} MB")
    with open(path, "rb") as fh:
        r = requests.post(f"{GRAPH}/{page_id}/videos", data={
            "description": caption,
            "title": title,
            "access_token": token,
        }, files={"source": (os.path.basename(path), fh, "video/mp4")}, timeout=1800)
    v = _check(r, "fb_upload")
    vid = str(v.get("id"))
    print(f"[fb] uploaded {vid}")

    for i in range(30):
        time.sleep(10)
        st = requests.get(f"{GRAPH}/{vid}", params={
            "fields": "status", "access_token": token}, timeout=40).json()
        vs = (st.get("status") or {})
        phase = vs.get("video_status") or vs.get("processing_phase", {}).get("status")
        print(f"[fb] {i+1}. {phase or vs}")
        if phase == "ready":
            break
        if phase == "error":
            raise RuntimeError(f"fb processing error: {vs}")

    info = requests.get(f"{GRAPH}/{vid}", params={
        "fields": "permalink_url,created_time", "access_token": token}, timeout=40).json()
    print(f"[fb] {info.get('permalink_url')}")
    return {"id": vid, "url": info.get("permalink_url")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--ig-caption", default="")
    ap.add_argument("--fb-caption", default="")
    ap.add_argument("--fb-title", default="")
    ap.add_argument("--only", choices=["ig", "fb", "both"], default="both")
    args = ap.parse_args()

    env = _env()
    token = env.get("FB_ACCESS_TOKEN", "")
    page_id = env.get("FB_PAGE_IDS", "")
    if not token or not page_id:
        print("FB_ACCESS_TOKEN / FB_PAGE_IDS khaali")
        return 1

    out = {}
    if args.only in ("ig", "both") and args.ig_caption:
        print("\n" + "=" * 60)
        print(" INSTAGRAM")
        print("=" * 60)
        out["instagram"] = ig_post(args.file, args.ig_caption, token)

    if args.only in ("fb", "both") and args.fb_caption:
        print("\n" + "=" * 60)
        print(" FACEBOOK")
        print("=" * 60)
        out["facebook"] = fb_post(args.file, args.fb_caption,
                                  args.fb_title or "", token, page_id)

    print("\n" + json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
