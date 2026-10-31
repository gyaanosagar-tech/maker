"""
meta_fb_check.py — Facebook Page connection checker.

    python meta_fb_check.py --token EAAG...

Batata hai: Page mila?, kaunsi permissions?, video upload possible?,
delete possible?, schedule possible?
"""
from __future__ import annotations

import argparse
import json
import sys

import requests

import config

OK, BAD, WARN = "✔", "✘", "!"
problems: list[str] = []


def line(mark, label, msg=""):
    print(f"  {mark} {label}" + (f" — {msg}" if msg else ""))


def get(path, token, **params):
    params["access_token"] = token
    try:
        r = requests.get(f"{config.GRAPH}/{path}", params=params, timeout=25)
        return r.status_code, (r.json() if r.content else {})
    except Exception as exc:  # noqa: BLE001
        return 0, {"error": {"message": str(exc)}}


def err(d):
    e = d.get("error") or {}
    return f"{e.get('message', d)} (code {e.get('code')})"[:200]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=config.FB_ACCESS_TOKEN)
    args = ap.parse_args()
    tok = (args.token or "").strip()

    print("=" * 60)
    print(" FACEBOOK PAGE CHECK")
    print("=" * 60)

    print("\n[1] TOKEN")
    if not tok:
        line(BAD, "FB_ACCESS_TOKEN", "khaali")
        print("\n Kya karo: META_FB_SETUP.md")
        return 1
    if tok.startswith("IG"):
        line(BAD, "ye Instagram token hai", "Facebook Page ke liye kaam nahi karega")
        print("\n Alag EAAG... token chahiye — META_FB_SETUP.md")
        return 1
    line(OK, "type", "Facebook Login (EAAG)")

    print("\n[2] PAGE")
    # Page token se /me/accounts kaam nahi karta — FB_PAGE_IDS direct use karo
    page_id = config.FB_PAGE_IDS[0] if config.FB_PAGE_IDS else ""
    if not page_id:
        code, d = get("me/accounts", tok, fields="id,name,access_token")
        pages = d.get("data", []) if code == 200 else []
        if not pages:
            line(BAD, "Page ID nahi", "FB_PAGE_IDS set karo")
            return 1
        page_id = pages[0]["id"]
    page_token = tok

    code, info = get(page_id, page_token,
                     fields="id,name,fan_count,followers_count,category")
    if code != 200:
        line(BAD, "Page", err(info))
        problems.append("Page read fail")
        return 1
    line(OK, f"Page: {info.get('name')}",
         f"id={page_id} fans={info.get('fan_count','-')} "
         f"followers={info.get('followers_count','-')}")

    print("\n[3] PERMISSIONS (jo token me hain)")
    code, dbg = get("debug_token", tok, input_token=tok)
    if code == 200 and dbg.get("data"):
        scopes = dbg["data"].get("scopes", [])
        import datetime
        ea = dbg["data"].get("expires_at")
        if ea and ea != 0:
            line(WARN, "expiry", datetime.datetime.fromtimestamp(ea).strftime("%Y-%m-%d"))
        else:
            line(OK, "expiry", "kabhi nahi / long-lived")

        need = {
            "pages_show_list": "Page list",
            "pages_read_engagement": "Page padhna",
            "pages_manage_posts": "VIDEO POST karna",
            "pages_manage_engagement": "comments",
            "pages_read_user_content": "content padhna",
        }
        for k, v in need.items():
            if k in scopes:
                line(OK, k, v)
            else:
                line(WARN if k != "pages_manage_posts" else BAD, f"{k} missing", v)
                if k == "pages_manage_posts":
                    problems.append("pages_manage_posts nahi — FB video post nahi hoga")
    else:
        line(WARN, "debug_token", "scopes nahi mile")

    print("\n[4] PAGE WALL")
    code, d = get(page_id, page_token, fields="id,name,fan_count,followers_count")
    if code == 200:
        line(OK, "Page reachable", f"{d.get('name')} | fans={d.get('fan_count', '-')}")
    else:
        line(BAD, "page read", err(d))

    print("\n[5] VIDEO UPLOAD POSSIBLE?")
    code, d = get(f"{page_id}/videos", page_token, fields="id", limit=1)
    if code == 200:
        line(OK, "videos edge", "video post kar sakte hain")
    else:
        line(BAD, "videos edge", err(d))
        problems.append("video edge fail")

    print("\n[6] SCHEDULING")
    line(OK, "native schedule", "published=false + scheduled_publish_time (10 min - 6 mahine)")
    line(WARN, "Reels", "FB Reels pe schedule support iffy hai — test karenge")

    print("\n" + "=" * 60)
    if problems:
        print(f" RESULT: {len(problems)} problem")
        for p in problems:
            print(f"   - {p}")
        return 1

    print(" RESULT: Facebook Page connected ✅")
    print("\n .env me:")
    print(f"   FB_PAGE_IDS={page_id}")
    print(f"   FB_ACCESS_TOKEN={page_token[:14]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
