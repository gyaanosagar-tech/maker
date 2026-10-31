#!/usr/bin/env python3
"""
connect_yt.py — YouTube token, bina local script chalane ke.

Do command:

  1)  python connect_yt.py link
      -> ek URL deta hai. Wo browser me kholo, Allow dabao.
         (redirect localhost pe jayega, page "site can't be reached" dikhega — normal)
         Address bar ka POORA URL copy karo.

  2)  python connect_yt.py code "<wo URL ya code>"
      -> code ko token me badal ke .env me likh deta hai.

client_secret.json (ya client_secret_xxx.json) isi folder me hona chahiye.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.parse

import requests

REDIRECT = "http://localhost:8085/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",   # upload + playlist
    "https://www.googleapis.com/auth/yt-analytics.readonly",  # insights
]
ENV_PATH = ".env"


# ------------------------------------------------------------------ client json
def find_client(path: str | None = None) -> tuple[str, dict]:
    """client_secret*.json dhundo aur andar ka 'installed' block return karo."""
    candidates = [path] if path else (
        glob.glob("client_secret*.json") + glob.glob("*.apps.googleusercontent.com.json")
    )
    candidates = [c for c in candidates if c and os.path.exists(c)]
    if not candidates:
        sys.exit(
            "client_secret JSON nahi mila.\n"
            "Google Cloud → Clients → apna Desktop client → DOWNLOAD JSON → isi folder me rakho."
        )
    for candidate in candidates:
        with open(candidate, encoding="utf-8") as fh:
            data = json.load(fh)
        block = data.get("installed") or data.get("web")
        if not block:
            continue
        if "web" in data:
            print(f"WARN: {candidate} ek 'Web application' client hai. "
                  "Desktop app client chahiye (warna redirect mismatch hoga).")
        return candidate, block
    sys.exit("JSON me 'installed' block nahi mila — Desktop app ka client_secret chahiye.")


def client_block(path: str | None = None) -> dict:
    """Pehle .env se, na mile to JSON se."""
    if not path:
        env = read_env()
        if env.get("YT_CLIENT_ID") and env.get("YT_CLIENT_SECRET"):
            return {"client_id": env["YT_CLIENT_ID"], "client_secret": env["YT_CLIENT_SECRET"]}
    return find_client(path)[1]


# ------------------------------------------------------------------ env io
def read_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    values[key.strip()] = val.strip()
    return values


def write_env(pairs: dict[str, str]) -> None:
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    seen, out = set(), []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in pairs:
            out.append(f"{key}={pairs[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, val in pairs.items():
        if key not in seen:
            out.append(f"{key}={val}")
    with open(ENV_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


# ------------------------------------------------------------------ commands
def cmd_link(args) -> int:
    block = client_block(args.client)
    params = {
        "client_id": block["client_id"],
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    print("1) Ye URL browser me kholo (jis Gmail pe channel hai):\n")
    print(url)
    print("\n2) Gmail chuno → 'Google hasn't verified this app' → Advanced → Go to ... (unsafe)")
    print("3) Saare checkbox tick rahne do → Allow")
    print("4) Page khulega: 'localhost refused to connect' — ye NORMAL hai")
    print("5) ADDRESS BAR ka poora URL copy karo (usme ?code=... hoga)")
    print("\nPhir ye chalao:\n")
    print('   python connect_yt.py code "<paste kiya hua URL>"')
    return 0


def redirect_from_url(raw: str) -> str | None:
    """
    Aap jo URL paste karte ho usme se redirect_uri nikaal lo.
    Kyunki code sirf usi redirect ke saath chalta hai jo link banate waqt use hua tha
    (8080 / 8085 / kuch bhi — jo bhi aapke browser me dikhe).
    """
    raw = (raw or "").strip().strip('"').strip("'")
    if not raw.startswith("http"):
        return None
    parsed = urllib.parse.urlparse(raw)
    if not parsed.query:
        return None
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", "", ""))


def cmd_code(args) -> int:
    block = client_block(args.client)
    code = extract_code(args.value)
    redirect = args.redirect or redirect_from_url(args.value) or REDIRECT
    if not code:
        sys.exit("code nahi mila. Poora URL paste karo (usme ?code=... hota hai)")

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": block["client_id"],
            "client_secret": block["client_secret"],
            "redirect_uri": redirect,
            "grant_type": "authorization_code",
        },
        timeout=60,
    )
    data = resp.json()

    if "error" in data:
        print(f"FAIL: {data.get('error')} — {data.get('error_description')}")
        hints = {
            "invalid_grant": "Code ek hi baar chalta hai / expire ho gaya. "
                             "`connect_yt.py link` se naya link banao.",
            "redirect_uri_mismatch": "Link jis client/redirect se bana tha, usse match nahi hua. "
                                     "Pooora URL dobara paste karo (jaisa address bar me tha), "
                                     "ya `--redirect http://localhost:8080/` de do.",
            "invalid_client": "client_id / client_secret galat — JSON check karo.",
        }
        hint = hints.get(data.get("error"))
        if hint:
            print(f"HINT: {hint}")
        return 1

    refresh = data.get("refresh_token")
    if not refresh:
        sys.exit(
            "refresh_token nahi mila.\n"
            "Iska matlab: is app ko pehle bhi allow kar chuke ho.\n"
            "Fix: https://myaccount.google.com/permissions pe jaake 'sulbot' remove karo, "
            "phir `connect_yt.py link` se naya code lo."
        )

    write_env({
        "YT_CLIENT_ID": block["client_id"],
        "YT_CLIENT_SECRET": block["client_secret"],
        "YT_REFRESH_TOKEN": refresh,
    })
    print("✔ .env me YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN likh diye")
    print("✔ scope: upload + readonly + yt-analytics")
    print("\nAb verify karo:  python doctor.py --yt")
    return 0


def extract_code(raw: str) -> str | None:
    """URL / query string / plain code — teeno se code nikaalo."""
    raw = (raw or "").strip().strip('"').strip("'")
    if not raw:
        return None
    if raw.startswith("http"):
        query = urllib.parse.urlparse(raw).query or raw.split("?", 1)[-1]
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            return params["code"][0]
        if "error" in params:
            sys.exit(f"Google ne error diya: {params['error'][0]} "
                     "(aapne Allow nahi kiya, ya test user add nahi hai)")
    if raw.startswith("code="):
        return urllib.parse.parse_qs(raw)["code"][0]
    if "code=" in raw:
        tail = raw.split("code=", 1)[1].split("&")[0]
        return urllib.parse.unquote(tail) or None
    return raw if len(raw) > 20 and " " not in raw else None


def main() -> int:
    ap = argparse.ArgumentParser(description="YouTube OAuth, code-paste method")
    ap.add_argument("--client", help="client_secret*.json ka path")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("link", help="consent URL banao")
    code = sub.add_parser("code", help="code ko token me badlo")
    code.add_argument("value", help="redirect URL ya code")
    code.add_argument("--redirect", help="redirect_uri override (auto-detect hota hai)")
    args = ap.parse_args()
    return cmd_link(args) if args.cmd == "link" else cmd_code(args)


if __name__ == "__main__":
    sys.exit(main())
