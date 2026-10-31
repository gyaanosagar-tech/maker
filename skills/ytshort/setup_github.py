#!/usr/bin/env python3
"""
setup_github.py — GitHub ka poora kaam ek command me.

Ye script:
  1. gh CLI check karta hai (login bhi karwa leta hai)
  2. git init + commit
  3. repo banata hai (public/private) aur push karta hai
  4. .env se saare secrets GitHub me daal deta hai  <- haath se copy-paste nahi
  5. variables (playlist, folder) set karta hai
  6. Actions workflow ka link print karta hai

Chalao:
    python setup_github.py --dry-run          # kya hoga, bina kuch badle
    python setup_github.py                    # asli setup (private repo)
    python setup_github.py --public           # public repo (cron minutes free)
    python setup_github.py --repo sulbot-videos
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

SECRET_KEYS = [
    "YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN", "YT_CHANNEL_ID",
    "IG_ACCESS_TOKEN", "IG_USER_IDS", "FB_PAGE_IDS", "GOOGLE_SERVICE_ACCOUNT_JSON_B64",
]
VAR_KEYS = ["PLAYLIST_IDS", "PLAYLIST_MAP", "FOLDER_REENCODED"]


# ------------------------------------------------------------------ helpers
def run(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True,
                          capture_output=capture, cwd=os.path.dirname(os.path.abspath(__file__)))


def read_env(path: str = ".env") -> dict[str, str]:
    values: dict[str, str] = {}
    if not os.path.exists(path):
        return values
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def sa_b64(values: dict) -> str | None:
    """Service account JSON -> base64 (GitHub secret ke liye)."""
    import base64

    if values.get("GOOGLE_SERVICE_ACCOUNT_JSON_B64"):
        return values["GOOGLE_SERVICE_ACCOUNT_JSON_B64"]
    path = values.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    return None


# ------------------------------------------------------------------ checks
def check_gh(dry: bool) -> bool:
    print("\n[1] gh CLI")
    if not shutil.which("gh"):
        print("  ✘ gh CLI install nahi hai")
        print("    Windows: winget install --id GitHub.cli")
        print("    Mac:     brew install gh")
        print("    Linux:   sudo apt install gh")
        return False
    run(["gh", "--version"])
    status = subprocess.run(["gh", "auth", "status"], text=True, capture_output=True)
    if status.returncode != 0:
        print("  ! GitHub pe login nahi ho — ab login karwa rahe hain")
        if dry:
            print("  (dry-run) `gh auth login` chalta — browser me code daalna hota hai")
            return False
        subprocess.run(["gh", "auth", "login", "--web", "--git-protocol", "https"])
    print("  ✔ gh ready")
    return True


def check_git(dry: bool) -> None:
    print("\n[2] git repo")
    if os.path.isdir(".git"):
        print("  ✔ .git already hai")
        return
    if dry:
        print("  (dry-run) git init + first commit hoga")
        return
    run(["git", "init", "-q"])
    run(["git", "add", "."])
    run(["git", "commit", "-q", "-m", "init: sulbot"])
    print("  ✔ commit ho gaya")


def push_repo(repo: str, public: bool, dry: bool) -> str:
    print("\n[3] repo + push")
    visibility = "--public" if public else "--private"
    if dry:
        print(f"  (dry-run) gh repo create {repo} {visibility} --source . --push")
        return f"USER/{repo}"
    existing = subprocess.run(["gh", "repo", "view", repo], capture_output=True, text=True)
    if existing.returncode == 0:
        print(f"  ✔ repo already hai: {repo}")
        run(["git", "remote", "remove", "origin"], check=False)
        run(["git", "remote", "add", "origin",
             subprocess.run(["gh", "repo", "view", repo, "--json", "url", "-q", ".url"],
                            capture_output=True, text=True).stdout.strip() + ".git"])
        run(["git", "push", "-u", "origin", "HEAD"], check=False)
    else:
        run(["gh", "repo", "create", repo, visibility, "--source", ".", "--push",
             "--description", "Drive -> YouTube + Instagram + Facebook bot"])
    owner = subprocess.run(["gh", "api", "user", "-q", ".login"],
                           capture_output=True, text=True).stdout.strip() or "USER"
    print(f"  ✔ https://github.com/{owner}/{repo}")
    return f"{owner}/{repo}"


def set_secrets(full_repo: str, values: dict, dry: bool) -> None:
    print("\n[4] secrets")
    missing = []
    for key in SECRET_KEYS:
        value = values.get(key, "")
        if key == "GOOGLE_SERVICE_ACCOUNT_JSON_B64":
            value = sa_b64(values) or ""
        if not value:
            missing.append(key)
            print(f"  – {key}: .env me nahi hai (skip)")
            continue
        if dry:
            print(f"  (dry-run) gh secret set {key} --repo {full_repo} --body ****")
            continue
        res = subprocess.run(["gh", "secret", "set", key, "--repo", full_repo, "--body", value],
                             capture_output=True, text=True)
        print(f"  {'✔' if res.returncode == 0 else '✘'} {key}"
              + ("" if res.returncode == 0 else f" — {res.stderr.strip()[:80]}"))
    if missing:
        print(f"  ! {len(missing)} secret missing: {', '.join(missing)}")


def set_vars(full_repo: str, values: dict, dry: bool) -> None:
    print("\n[5] variables (playlist / folder)")
    for key in VAR_KEYS:
        value = values.get(key, "")
        if not value:
            print(f"  – {key}: khaali (skip)")
            continue
        if dry:
            print(f"  (dry-run) gh variable set {key} --repo {full_repo} --body {value}")
            continue
        res = subprocess.run(["gh", "variable", "set", key, "--repo", full_repo, "--body", value],
                             capture_output=True, text=True)
        print(f"  {'✔' if res.returncode == 0 else '✘'} {key} = {value[:20]}"
              + ("" if res.returncode == 0 else f" — {res.stderr.strip()[:80]}"))


def check_private_cron_budget(public: bool) -> None:
    if public:
        return
    print("\n[!] Private repo = GitHub Actions minutes (free 2,000/month) khaata hai.")
    print("    Hourly cron = ~2,160 min/month → limit cross ho sakti hai.")
    print("    Public repo me minutes bilkul free hain (code me koi secret nahi hota).")
    print("    Public chahiye to: python setup_github.py --public")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="sulbot")
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("=== GitHub setup (sulbot) ===")
    print("Bas ek kaam: aapko browser me ek baar 'Authorize' dabana hoga.")

    values = read_env(".env")
    if not values:
        print("\n!! .env nahi mila. Pehle YT token banao:")
        print("   python will_provide.py --analytics --env")
        return 1

    if not check_gh(args.dry_run):
        return 1
    check_git(args.dry_run)
    full_repo = push_repo(args.repo, args.public, args.dry_run)
    set_secrets(full_repo, values, args.dry_run)
    set_vars(full_repo, values, args.dry_run)
    check_private_cron_budget(args.public)

    print("\n=== Done ===")
    if args.dry_run:
        print("Dry-run khatam — kuch nahi badla. Asli ke liye --dry-run hatao.")
        return 0

    print(f"Actions: https://github.com/{full_repo}/actions")
    print("Wahan 'sulbot' workflow → 'Run workflow' → dry_run = true → Run")
    print("\nUske baad token 7 din me expire hoga; tab ye dobara chalao:")
    print(f"  gh secret set YT_REFRESH_TOKEN --repo {full_repo} --body \"<naya token>\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
