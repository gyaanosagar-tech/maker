"""
meta_token.py — Meta token ko apne aap taaza rakho.

Kyun: Meta ka long-lived token ~60 din chalta hai. Uske baad sab fail ho jaata hai.
Isliye har run pe check karo; expiry ke 7 din pehle khud refresh kar lo.

Aapko ek baar token dena hai. Uske baad ye script sambhal lega.

    python meta_token.py --status          # kitna din bacha
    python meta_token.py --refresh         # abhi refresh karo

GitHub Actions me har run pe --status chalta hai. 7 din bache to --refresh
khud chalta hai aur naya token GitHub Secret me update kar deta hai.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

import config

GRAPH = config.GRAPH
REFRESH_WINDOW_DAYS = 7


def _get(path: str, params: dict) -> dict:
    url = f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=25) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": json.loads(exc.read().decode()).get("error", {})}


def _ig_get(path: str, params: dict) -> dict:
    url = f"https://graph.instagram.com/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=25) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return {"error": json.loads(exc.read().decode()).get("error", {})}


def debug(token: str) -> dict:
    data = _get("debug_token", {"input_token": token, "access_token": token})
    return data.get("data", {}) or {"error": data.get("error")}


def status(token: str) -> dict:
    if token.startswith("IG"):
        # Instagram Login: debug_token allowed nahi. Live call se check karo.
        me = _ig_get("me", {"fields": "id,username,media_count", "access_token": token})
        if me.get("error"):
            return {"ok": False, "error": me["error"].get("message", "invalid")}
        return {"ok": True, "permanent": False, "days_left": None,
                "expires": "unknown (Instagram Login — refresh se pata chalega)",
                "scopes": ["instagram_business_*"],
                "username": me.get("username")}

    d = debug(token)
    if d.get("error"):
        return {"ok": False, "error": d["error"].get("message", "unknown")}

    expires = d.get("expires_at")
    if expires in (0, None):
        return {"ok": True, "permanent": True, "days_left": None,
                "scopes": d.get("scopes", [])}

    end = datetime.datetime.fromtimestamp(expires)
    left = end - datetime.datetime.now()
    return {"ok": True, "permanent": False,
            "days_left": left.days, "expires": end.strftime("%Y-%m-%d %H:%M"),
            "scopes": d.get("scopes", [])}


def refresh_instagram(token: str) -> dict:
    """Instagram Login token refresh — app secret ki zaroorat NAHI.
    Condition: token kam se kam 24 ghante purana ho."""
    url = ("https://graph.instagram.com/refresh_access_token?"
           + urllib.parse.urlencode({"grant_type": "ig_refresh_token",
                                     "access_token": token}))
    try:
        with urllib.request.urlopen(url, timeout=25) as resp:
            d = json.loads(resp.read().decode())
        return {"ok": True, "token": d.get("access_token"),
                "expires_in_days": (d.get("expires_in") or 0) // 86400}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            msg = json.loads(body).get("error", {}).get("message", body[:200])
        except Exception:
            msg = body[:200]
        return {"ok": False, "error": msg}


def refresh(token: str) -> dict:
    """
    Short-lived -> long-lived (60 din).
    long-lived -> naya long-lived (agar 60 din se kam bacha ho).
    """
    if token.startswith("IG"):
        return refresh_instagram(token)

    data = _get("oauth/access_token", {
        "grant_type": "fb_exchange_token",
        "client_id": config.META_APP_ID,
        "client_secret": config.META_APP_SECRET,
        "fb_exchange_token": token,
    })
    if data.get("error"):
        return {"ok": False, "error": data["error"].get("message")}
    return {"ok": True, "token": data.get("access_token"),
            "expires_in_days": (data.get("expires_in") or 0) // 86400}


def save_local(token: str) -> bool:
    """Local .env me token update karo (dev ke liye)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return False
    lines = []
    found = False
    for line in open(path).read().splitlines():
        if line.startswith("IG_ACCESS_TOKEN="):
            lines.append(f"IG_ACCESS_TOKEN={token}")
            found = True
        else:
            lines.append(line)
    if not found:
        lines.append(f"IG_ACCESS_TOKEN={token}")
    open(path, "w").write("\n".join(lines) + "\n")
    return True


def update_github_secret(token: str) -> bool:
    """GitHub Secret update karo (cron ke liye zaroori)."""
    gh = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GH_RELEASE_REPO", "")
    if not gh or not repo:
        return False
    try:
        import base64
        from nacl import encoding, public  # type: ignore

        base = f"https://api.github.com/repos/{repo}/actions/secrets"
        hdr = {"Authorization": f"Bearer {gh}",
               "Accept": "application/vnd.github+json",
               "Content-Type": "application/json"}

        with urllib.request.urlopen(
                urllib.request.Request(base + "/public-key", headers=hdr)) as r:
            pk = json.loads(r.read().decode())

        box = public.SealedBox(public.PublicKey(pk["key"].encode(),
                                                encoding.Base64Encoder()))
        enc = base64.b64encode(box.encrypt(token.encode())).decode()
        body = json.dumps({"encrypted_value": enc, "key_id": pk["key_id"]}).encode()
        req = urllib.request.Request(base + "/IG_ACCESS_TOKEN", data=body,
                                     headers=hdr, method="PUT")
        urllib.request.urlopen(req, timeout=25)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[token] GitHub secret update fail: {exc}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Meta token health + refresh")
    ap.add_argument("--token", default=config.IG_ACCESS_TOKEN)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--update", action="store_true",
                    help="refresh ke baad .env + GitHub Secret update karo")
    args = ap.parse_args()

    if not args.token:
        print("IG_ACCESS_TOKEN khaali hai")
        return 1

    st = status(args.token)
    if not st.get("ok"):
        print(f"TOKEN PROBLEM: {st.get('error')}")
        return 1

    if st.get("permanent"):
        print("Token permanent hai — kabhi expire nahi hoga ✅")
        return 0

    if st.get("days_left") is None:
        print(f"Token OK — @{st.get('username','?')}  ({st['expires']})")
        print("Refresh har run pe chalega (Instagram Login).")
        if args.refresh:
            res = refresh(args.token)
            if not res.get("ok"):
                print(f"REFRESH FAIL: {res.get('error')}")
                return 1
            print(f"naya token ({res['expires_in_days']} din)")
            if args.update:
                save_local(res["token"]) and print("  .env update")
                update_github_secret(res["token"]) and print("  GitHub secret update")
        return 0

    print(f"Token expires: {st['expires']}  ({st['days_left']} din bache)")
    print(f"Scopes: {', '.join(st['scopes'])}")

    needs = st["days_left"] <= REFRESH_WINDOW_DAYS
    if args.refresh or needs:
        if needs and not args.refresh:
            print(f"\n{st['days_left']} din bache — auto refresh kar rahe hain")
        res = refresh(args.token)
        if not res.get("ok"):
            print(f"REFRESH FAIL: {res.get('error')}")
            return 1
        new = res["token"]
        print(f"naya token mila ({res['expires_in_days']} din)")

        if args.update:
            if save_local(new):
                print("  .env update ho gaya")
            if update_github_secret(new):
                print("  GitHub Secret update ho gaya")

            new_st = status(new)
            if new_st.get("ok") and not new_st.get("permanent"):
                print(f"  verify: {new_st['days_left']} din bache")
        else:
            print("  (--update nahi diya, kahin save nahi hua)")
    else:
        print(f"\n{st['days_left']} din bache — refresh ki zaroorat nahi")

    return 0


if __name__ == "__main__":
    sys.exit(main())
