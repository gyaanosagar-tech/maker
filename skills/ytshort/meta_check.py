"""
meta_check.py — Instagram + Facebook connection checker.

Kuch bhi post nahi karta. Sirf batata hai: kaunsi cheez chal rahi hai,
kaunsi nahi, aur exactly kya karna hai.

    python meta_check.py
    python meta_check.py --token EAAG... --ig 17841... --page 1029...

Bina arguments ke .env se padhta hai (IG_ACCESS_TOKEN, IG_USER_IDS, FB_PAGE_IDS).
"""
from __future__ import annotations

import argparse
import json
import sys

import requests

import config

OK = "✔"
BAD = "✘"
WARN = "!"

problems: list[str] = []


def line(mark: str, label: str, msg: str = "") -> None:
    print(f"  {mark} {label}" + (f" — {msg}" if msg else ""))


def host_for(token: str) -> str:
    """IGAA... = Instagram Login (graph.instagram.com) | EAAG... = Facebook Login."""
    return ("https://graph.instagram.com" if token.startswith("IG")
            else config.GRAPH)


def graph_get(path: str, token: str, **params) -> tuple[int, dict]:
    params["access_token"] = token
    try:
        r = requests.get(f"{host_for(token)}/{path}", params=params, timeout=20)
        return r.status_code, (r.json() if r.content else {})
    except Exception as exc:  # noqa: BLE001
        return 0, {"error": {"message": str(exc)}}


def err_text(data: dict) -> str:
    e = data.get("error") or {}
    parts = [str(e.get("message", data))]
    if e.get("code"):
        parts.append(f"code={e['code']}")
    if e.get("error_subcode"):
        parts.append(f"subcode={e['error_subcode']}")
    return " | ".join(parts)[:220]


def check_token(token: str) -> dict | None:
    print("\n[1] TOKEN")
    if not token:
        line(BAD, "IG_ACCESS_TOKEN", "khaali hai — META_SETUP.md dekho")
        problems.append("IG_ACCESS_TOKEN khaali")
        return None

    code, data = graph_get("me", token, fields="id,name")
    if code != 200:
        line(BAD, "token", err_text(data))
        problems.append("token valid nahi")
        return None
    kind = "Instagram Login (IGAA)" if token.startswith("IG") else "Facebook Login (EAAG)"
    line(OK, "token valid", f"id={data.get('id')}")
    line(OK, "login type", kind)

    # token ki expiry + scopes
    code, dbg = graph_get("debug_token", token, input_token=token)
    if code == 200 and dbg.get("data"):
        d = dbg["data"]
        scopes = d.get("scopes", [])
        expires = d.get("expires_at")
        line(OK, "scopes", ", ".join(scopes) if scopes else "koi nahi")
        if expires == 0:
            line(OK, "expiry", "kabhi nahi khatam (long-lived)")
        elif expires:
            import datetime
            dt = datetime.datetime.fromtimestamp(expires)
            line(WARN, "expiry", dt.strftime("%Y-%m-%d %H:%M") + " — jaldi refresh karo")

        need = {
            "instagram_basic": "IG account padhna",
            "instagram_content_publish": "reel post karna",
            "instagram_manage_contents": "post delete karna (optional)",
            "pages_show_list": "Page list",
            "pages_read_engagement": "Page padhna",
            "pages_manage_posts": "FB pe post karna",
        }
        missing = [s for s in need if s not in scopes]
        for s in missing:
            line(WARN, f"scope missing: {s}", need[s])
        if "instagram_content_publish" in missing:
            problems.append("instagram_content_publish nahi hai — post nahi hoga")
        if "pages_manage_posts" in missing:
            problems.append("pages_manage_posts nahi hai — FB post nahi hoga")
    return data


def check_pages(token: str) -> list[dict]:
    print("\n[2] FACEBOOK PAGE")
    code, data = graph_get("me/accounts", token, fields="id,name,access_token,tasks")
    if code != 200:
        line(BAD, "me/accounts", err_text(data))
        problems.append("Page list nahi mili")
        return []

    pages = data.get("data", [])
    if not pages:
        line(BAD, "koi Page nahi", "aap admin ho kisi Page ka?")
        problems.append("koi FB Page nahi mila")
        return []

    for p in pages:
        tasks = ", ".join(p.get("tasks", []))
        line(OK, f"Page: {p['name']}", f"id={p['id']} tasks=[{tasks}]")
        if "page_token" not in str(p):
            pass
    return pages


def check_ig(token: str, page_id: str | None) -> dict | None:
    print("\n[3] INSTAGRAM BUSINESS ACCOUNT")
    if not page_id:
        line(WARN, "skip", "Page ID nahi mila — pehle step 2")
        return None

    if token.startswith("IG"):
        code, data = graph_get("me", token,
                               fields="id,username,followers_count,media_count")
        if code == 200 and data.get("id"):
            line(OK, "IG account", f"@{data.get('username')} id={data.get('id')}")
            followers = int(data.get("followers_count") or 0)
            line(OK, "followers", str(followers))
            if followers < config.TRIAL_MIN_FOLLOWERS:
                line(WARN, "trial reels", f"{followers} < {config.TRIAL_MIN_FOLLOWERS} — trial band")
            else:
                line(OK, "trial reels", "allowed")
            return data
        line(BAD, "IG /me", err_text(data))
        return None

    code, data = graph_get(
        f"{page_id}", token,
        fields="instagram_business_account{id,username,followers_count,media_count}")
    if code != 200:
        line(BAD, "page link", err_text(data))
        problems.append("Page se IG link nahi mila")
        return None

    ig = data.get("instagram_business_account")
    if not ig:
        line(BAD, "IG account linked nahi",
             "Page ko Instagram Professional account se jodo")
        problems.append("Page se IG account joda nahi hai")
        return None

    line(OK, "IG account", f"@{ig.get('username')} id={ig.get('id')}")
    followers = int(ig.get("followers_count") or 0)
    line(OK, "followers", str(followers))
    line(OK, "media count", str(ig.get("media_count")))

    # trial gate
    if followers < config.TRIAL_MIN_FOLLOWERS:
        line(WARN, "trial reels", f"{followers} < {config.TRIAL_MIN_FOLLOWERS} — "
             "trial band, sab normal reel. 200+ hone pe khud on ho jaayega")
    else:
        line(OK, "trial reels", f"{followers} >= {config.TRIAL_MIN_FOLLOWERS} — allowed")
    return ig


def check_publish_limit(token: str, ig_id: str) -> None:
    print("\n[4] PUBLISHING LIMIT")
    code, data = graph_get(f"{ig_id}/content_publishing_limit", token,
                           fields="quota_usage,config")
    if code != 200:
        line(WARN, "limit check", err_text(data))
        return
    for item in data.get("data", []):
        used = item.get("quota_usage")
        total = (item.get("config") or {}).get("quota_total", "?")
        line(OK, "aaj publish hua", f"{used} / {total}")


def check_resumable(token: str, ig_id: str) -> None:
    """Resumable upload = Drive/hosting ki zaroorat nahi."""
    print("\n[5] RESUMABLE UPLOAD (hosting-free)")
    code, data = graph_get(f"{ig_id}", token, fields="id")
    if code == 200:
        line(OK, "graph reachable", "resumable path rupload.facebook.com use hoga")
        line(WARN, "note", "asli test pehli reel pe hoga (container banega)")
    else:
        line(BAD, "graph", err_text(data))


def main() -> int:
    ap = argparse.ArgumentParser(description="IG + FB connection checker")
    ap.add_argument("--token", default=config.IG_ACCESS_TOKEN)
    ap.add_argument("--ig", default=(config.IG_USER_IDS[0] if config.IG_USER_IDS else ""))
    ap.add_argument("--page", default=(config.FB_PAGE_IDS[0] if config.FB_PAGE_IDS else ""))
    args = ap.parse_args()

    print("=" * 62)
    print(" META CONNECTION CHECK — Instagram + Facebook")
    print("=" * 62)

    me = check_token(args.token)
    if not me:
        print("\n" + "=" * 62)
        print(" RUKA — token ke bina aage nahi")
        print("=" * 62)
        print("\nKya karo: META_SETUP.md — Step 1 se 6")
        return 1

    pages = check_pages(args.token)
    page_id = args.page or (str(pages[0]["id"]) if pages else None)
    if pages and not args.page:
        print(f"\n  -> pehla page use kar rahe hain: {page_id}")

    ig = check_ig(args.token, page_id)
    if ig:
        check_publish_limit(args.token, str(ig["id"]))
        check_resumable(args.token, str(ig["id"]))

    print("\n" + "=" * 62)
    if problems:
        print(f" RESULT: {len(problems)} problem")
        for p in problems:
            print(f"   - {p}")
        print("\n Guide: META_SETUP.md")
        return 1

    print(" RESULT: sab theek — IG + FB connected")
    if pages and ig:
        print("\n .env me ye daalo:")
        print(f"   IG_USER_IDS={ig['id']}")
        print(f"   FB_PAGE_IDS={page_id}")
        print("   IG_ACCESS_TOKEN=EAAG...   (jo token use kiya)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
