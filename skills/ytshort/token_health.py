"""
token_health.py — saare tokens ki sehat ek jagah.

    python token_health.py

Check karta hai: YouTube refresh token, IG token, FB Page token.
Cron har run pe chalata hai. Token marne se pehle warn karta hai.
"""
from __future__ import annotations

import datetime
import sys

import config
import instagram_uploader as ig
import meta_token
import state_store


def yt_check() -> dict:
    try:
        import youtube_uploader as yt
        ch = yt.service().channels().list(part="snippet", mine=True).execute()
        name = ch["items"][0]["snippet"]["title"]
        return {"ok": True, "label": f"YouTube: {name}", "note": "refresh token chal raha hai"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "label": "YouTube", "error": str(exc)[:160]}


def ig_check() -> dict:
    tok = config.IG_ACCESS_TOKEN
    if not tok:
        return {"ok": False, "label": "Instagram", "error": "token khaali"}
    st = meta_token.status(tok)
    if not st.get("ok"):
        return {"ok": False, "label": "Instagram", "error": st.get("error")}
    if st.get("permanent"):
        return {"ok": True, "label": "Instagram", "note": "permanent token"}
    days = st.get("days_left")
    if days is None:
        return {"ok": True, "label": "Instagram",
                "note": f"@{st.get('username','?')} — auto-refresh active"}
    if days <= 1:
        return {"ok": False, "label": "Instagram",
                "error": f"SIRF {days} DIN — refresh abhi karo"}
    if days <= 7:
        return {"ok": True, "warn": True, "label": "Instagram",
                "note": f"{days} din bache — agla run refresh karega"}
    return {"ok": True, "label": "Instagram", "note": f"{days} din bache"}


def fb_check() -> dict:
    st = ig.fb_token_status()
    if not st.get("ok"):
        return {"ok": False, "label": "Facebook", "error": st.get("error")}
    if st.get("permanent"):
        return {"ok": True, "label": "Facebook", "note": "permanent — koi expiry nahi"}
    days = st.get("days_left")
    if days is None:
        return {"ok": True, "label": "Facebook", "note": "expiry unknown"}
    if days < 1:
        return {"ok": False, "label": "Facebook",
                "error": f"AAJ expire ho raha hai ({st.get('expires')}) — naya token lo"}
    if days <= 3:
        return {"ok": True, "warn": True, "label": "Facebook",
                "note": f"{days} din — jaldi naya token"}
    return {"ok": True, "label": "Facebook", "note": f"{days} din bache ({st.get('expires')})"}


def main() -> int:
    print("=" * 60)
    print(" TOKEN HEALTH")
    print("=" * 60)

    results = [yt_check(), ig_check(), fb_check()]
    bad = 0
    for r in results:
        if not r.get("ok"):
            mark, bad = "✘", bad + 1
        elif r.get("warn"):
            mark = "!"
        else:
            mark = "✔"
        text = r.get("error") or r.get("note") or ""
        print(f"  {mark} {r['label']:<22} {text}")

    print("=" * 60)
    if bad:
        print(f" {bad} token PROBLEM — dekho upar")
        try:
            state_store.learn(f"token health: {bad} problem — "
                              + "; ".join(r["label"] for r in results if not r.get("ok")))
        except Exception:  # noqa: BLE001
            pass
        return 1
    print(" Sab tokens theek")
    return 0


if __name__ == "__main__":
    sys.exit(main())
