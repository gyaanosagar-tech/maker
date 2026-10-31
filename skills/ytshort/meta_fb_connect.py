"""
meta_fb_connect.py — Facebook Page ko poora auto-connect karo.

Aap sirf ek USER token do. Ye script baaki sab khud karti hai:
  1. user token extend (60 din / long-lived)  — app secret ho to
  2. /me/accounts se Page tokens nikaalo
  3. Page token save karo (.env)
  4. permissions verify karo
  5. GitHub Secrets update karo

    python meta_fb_connect.py --user-token EAAB...
    python meta_fb_connect.py --user-token EAAB... --page "Failtadka"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

import config

OK, BAD, WARN = "✔", "✘", "!"


def _call(path: str, **params) -> dict:
    url = f"https://graph.facebook.com/v21.0/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return {"_err": json.loads(body).get("error", {})}
        except Exception:
            return {"_err": {"message": body[:200]}}


def _err(d):
    e = d.get("_err") or {}
    return f"{e.get('message', d)} (code {e.get('code')})"


def extend(user_token: str) -> dict:
    """short-lived -> long-lived. App secret chahiye."""
    if not (config.META_APP_ID and config.META_APP_SECRET):
        return {"skip": "META_APP_ID / META_APP_SECRET nahi hue set"}
    d = _call("oauth/access_token",
              grant_type="fb_exchange_token",
              client_id=config.META_APP_ID,
              client_secret=config.META_APP_SECRET,
              fb_exchange_token=user_token)
    if "_err" in d:
        return {"error": _err(d)}
    return {"token": d.get("access_token"),
            "days": (d.get("expires_in") or 0) // 86400}


def pages(user_token: str) -> list[dict]:
    d = _call("me/accounts", access_token=user_token,
              fields="id,name,category,tasks,access_token")
    if "_err" in d:
        raise RuntimeError(_err(d))
    return d.get("data", [])


def page_details(page_token: str, page_id: str) -> dict:
    return _call(page_id, access_token=page_token,
                 fields="id,name,fan_count,followers_count")


def debug_token(token: str) -> dict:
    # app token banao (agar app secret hai), warna khud se
    app = None
    if config.META_APP_ID and config.META_APP_SECRET:
        app = f"{config.META_APP_ID}|{config.META_APP_SECRET}"
    d = _call("debug_token", input_token=token, access_token=app or token)
    if "_err" in d:
        return {"error": _err(d)}
    return d.get("data", {})


def save_env(page_id: str, page_token: str) -> bool:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    lines, seen = [], set()
    for line in open(path).read().splitlines():
        k = line.split("=", 1)[0] if "=" in line else ""
        if k in ("FB_PAGE_IDS", "FB_ACCESS_TOKEN"):
            continue
        lines.append(line)
        seen.add(k)
    lines.append(f"FB_PAGE_IDS={page_id}")
    lines.append(f"FB_ACCESS_TOKEN={page_token}")
    open(path, "w").write("\n".join(lines) + "\n")
    return True


def push_secrets(page_id: str, page_token: str) -> bool:
    gh = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not gh:
        return False
    try:
        import base64
        from nacl import encoding, public

        base = "https://api.github.com/repos/gyaanosagar-tech/ytshort/actions/secrets"
        hdr = {"Authorization": f"Bearer {gh}",
               "Accept": "application/vnd.github+json",
               "Content-Type": "application/json"}
        with urllib.request.urlopen(
                urllib.request.Request(base + "/public-key", headers=hdr)) as r:
            pk = json.loads(r.read().decode())
        box = public.SealedBox(public.PublicKey(pk["key"].encode(),
                                                encoding.Base64Encoder()))
        for name, val in (("FB_PAGE_IDS", page_id), ("FB_ACCESS_TOKEN", page_token)):
            enc = base64.b64encode(box.encrypt(val.encode())).decode()
            body = json.dumps({"encrypted_value": enc,
                               "key_id": pk["key_id"]}).encode()
            req = urllib.request.Request(f"{base}/{name}", data=body,
                                         headers=hdr, method="PUT")
            urllib.request.urlopen(req, timeout=25)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  {WARN} GitHub secrets push fail: {exc}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user-token", required=True,
                    help="EAAB... (Graph Explorer ka User Access Token)")
    ap.add_argument("--page", default="", help="Page ka naam (multiple ho to)")
    ap.add_argument("--save", action="store_true", help=".env + GitHub me likho")
    args = ap.parse_args()

    tok = args.user_token.strip()
    print("=" * 62)
    print(" FACEBOOK PAGE AUTO-CONNECT")
    print("=" * 62)

    if tok.startswith("IG"):
        print(f"\n{BAD} ye Instagram token hai — Facebook ke liye EAAB.../EAAG... chahiye")
        return 1

    print("\n[1] user token check")
    me = _call("me", access_token=tok, fields="id,name")
    if "_err" in me:
        print(f"  {BAD} token — {_err(me)}")
        print("\n  Graph Explorer se naya token lo (Purge karke dobara Generate)")
        return 1
    print(f"  {OK} user — {me.get('name')} (id={me.get('id')})")

    print("\n[2] extend (60 din / long-lived)")
    ext = extend(tok)
    if ext.get("error"):
        print(f"  {WARN} extend fail: {ext['error']}")
        print("     App Secret galat — par aage badh rahe hain")
    elif ext.get("skip"):
        print(f"  {WARN} {ext['skip']}")
    elif ext.get("token"):
        tok = ext["token"]
        print(f"  {OK} long-lived token ({ext['days']} din)")

    print("\n[3] pages")
    try:
        plist = pages(tok)
    except RuntimeError as exc:
        print(f"  {BAD} {exc}")
        return 1

    if not plist:
        print(f"  {BAD} koi Page nahi mila")
        print("     - aap us Page ke admin ho?")
        print("     - token me pages_show_list hai?")
        return 1

    for p in plist:
        has = "token ✅" if p.get("access_token") else "token ❌"
        print(f"  {OK} {p['name']}  id={p['id']}  {has}")

    chosen = plist[0]
    if args.page:
        match = [p for p in plist if args.page.lower() in p["name"].lower()]
        if not match:
            print(f"\n  {BAD} '{args.page}' naam ka Page nahi")
            return 1
        chosen = match[0]

    page_token = chosen.get("access_token")
    if not page_token:
        print(f"\n  {BAD} Page token nahi mila — debug karo")
        return 1

    print(f"\n[4] chuna: {chosen['name']} ({chosen['id']})")

    info = page_details(page_token, chosen["id"])
    if "_err" not in info:
        print(f"  {OK} fans={info.get('fan_count', '-')} "
              f"followers={info.get('followers_count', '-')}")

    # expiry check
    dbg = debug_token(page_token)
    if dbg.get("error"):
        print(f"  {WARN} debug fail: {dbg['error']}")
    else:
        import datetime
        ea = dbg.get("expires_at")
        if ea in (0, None):
            print(f"  {OK} Page token — KOI EXPIRY NAHI ✅")
        else:
            print(f"  {WARN} expires {datetime.datetime.fromtimestamp(ea):%Y-%m-%d}")
        scopes = dbg.get("scopes", [])
        need = ["pages_show_list", "pages_read_engagement", "pages_manage_posts"]
        for n in need:
            mark = OK if n in scopes else WARN
            print(f"  {mark} {n}" + ("" if n in scopes else " — missing"))

    # video edge test
    v = _call(f"{chosen['id']}/videos", access_token=page_token, fields="id", limit=1)
    if "_err" in v:
        print(f"  {BAD} video post nahi hoga — {_err(v)}")
    else:
        print(f"  {OK} video post possible")

    if args.save:
        print("\n[5] saving")
        save_env(chosen["id"], page_token)
        print(f"  {OK} .env updated")
        if push_secrets(chosen["id"], page_token):
            print(f"  {OK} GitHub secrets updated")

    print("\n" + "=" * 62)
    print(f" DONE — {chosen['name']} connected")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
