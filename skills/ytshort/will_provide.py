"""
will_provide.py — ek baar chalao, YT_REFRESH_TOKEN milega.

Google Cloud me pehle:
  1. New Project -> APIs enable: YouTube Data API v3 (+ YouTube Analytics API, insights ke liye)
  2. OAuth consent screen -> External -> apna Gmail test user me add
  3. Credentials -> OAuth client ID -> Application type = Desktop app
  4. JSON download -> is folder me client_secret.json naam se rakho

Phir:
  python will_provide.py               # upload scope (default)
  python will_provide.py --analytics   # upload + analytics scope (insights ke liye)
  python will_provide.py --env         # seedha .env me likh do

Testing app ka refresh token 7 din me expire hota hai — tabhi `invalid_grant` aata hai.
Isliye har 5-6 din me dobara chalao, ya app ko Published kar do (permanent fix).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

UPLOAD = ["https://www.googleapis.com/auth/youtube.force-ssl"]  # upload + playlist
ANALYTICS = UPLOAD + ["https://www.googleapis.com/auth/yt-analytics.readonly"]


def run(client_path: str, analytics: bool = False, env_path: str | None = None) -> dict:
    if not os.path.exists(client_path):
        sys.exit(
            f"'{client_path}' nahi mila.\n"
            "Google Cloud -> Credentials -> OAuth client (Desktop app) -> Download JSON -> "
            "isi folder me client_secret.json naam se rakho."
        )
    with open(client_path, encoding="utf-8") as fh:
        data = json.load(fh)
    if "installed" not in data:
        print("WARN: 'Web application' client lagta hai. Desktop app use karo, "
              "warna refresh token jaldi expire hota hai.")

    scopes = ANALYTICS if analytics else UPLOAD
    flow = InstalledAppFlow.from_client_config(data, scopes)
    print(f"Scopes: {', '.join(s.split('/')[-1] for s in scopes)}")
    print("Browser khulega -> Gmail chuno -> Allow. (Chaho to sab tick kar dena.)")
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        sys.exit("refresh_token nahi mila — https://myaccount.google.com/permissions se "
                 "app revoke karke dobara chalao")

    section = data.get("installed") or {}
    values = {
        "YT_CLIENT_ID": section.get("client_id", ""),
        "YT_CLIENT_SECRET": section.get("client_secret", ""),
        "YT_REFRESH_TOKEN": creds.refresh_token,
    }
    print("\n--- .env me ye daalo ---")
    for key, val in values.items():
        print(f"{key}={val}")
    print("-------------------------")

    if env_path:
        _write_env(env_path, values)
        print(f"{env_path} update ho gaya")
    return values


def _write_env(path: str, values: dict) -> None:
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        lines = []
    keys = set(values)
    out, seen = [], set()
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in values:
            out.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            out.append(line)
    for key, val in values.items():
        if key not in seen:
            out.append(f"{key}={val}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default="client_secret.json")
    ap.add_argument("--analytics", action="store_true", help="insights scope bhi")
    ap.add_argument("--env", action="store_true", help="seedha .env me likho")
    args = ap.parse_args()
    run(args.client, analytics=args.analytics, env_path=".env" if args.env else None)
