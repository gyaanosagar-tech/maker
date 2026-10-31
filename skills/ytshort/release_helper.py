"""
release_helper.py — GitHub Release se video uthana (Drive ki jagah).

Kyun: GitHub Actions ke andar Drive service-account nahi chahiye. Video ek
GitHub Release me asset ban ke padi hoti hai; runner use download kar leta hai.

Reference formats jo chalte hain:
    gh:tag/asset           -> gh:v1/type2_ep1.mp4
    gh:tag                 -> us tag ka pehla video asset
    <asset name>           -> latest release me naam se dhoondo
    <release asset URL>    -> https://github.com/<owner>/<repo>/releases/download/<tag>/<file>

Env:
    GH_RELEASE_REPO   default gyaanosagar-tech/ytshort
    GH_TOKEN / GITHUB_TOKEN  private repo ho to (public me optional)
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request

import config

API = "https://api.github.com"
DEFAULT_REPO = os.getenv("GH_RELEASE_REPO", "gyaanosagar-tech/ytshort")
VIDEO_EXTS = config.VIDEO_EXTS


def _token() -> str:
    return (os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()


def _api(path: str):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "sulbot",
        **({"Authorization": f"Bearer {_token()}"} if _token() else {}),
    })
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"GitHub API {path} -> {exc.code}: {exc.read().decode()[:200]}") from exc


def is_release_ref(ref: str) -> bool:
    ref = (ref or "").strip()
    return ref.startswith("gh:") or "/releases/download/" in ref


def _find_asset(release: dict, wanted: str | None) -> dict:
    assets = [a for a in release.get("assets", [])
              if a["name"].lower().endswith(VIDEO_EXTS)]
    if not assets:
        raise RuntimeError(f"release '{release.get('tag_name')}' me koi video asset nahi")
    if not wanted:
        return assets[0]
    for a in release.get("assets", []):
        if a["name"].lower() == wanted.lower():
            return a
    raise RuntimeError(
        f"'{wanted}' release '{release.get('tag_name')}' me nahi. "
        f"Available: {', '.join(a['name'] for a in assets)}"
    )


def _download_asset(asset: dict) -> str:
    os.makedirs(config.TMP_DIR, exist_ok=True)
    suffix = os.path.splitext(asset["name"])[1] or ".mp4"
    fd, path = tempfile.mkstemp(suffix=suffix, dir=config.TMP_DIR)
    os.close(fd)
    req = urllib.request.Request(asset["url"], headers={
        "Accept": "application/octet-stream",
        "User-Agent": "sulbot",
        **({"Authorization": f"Bearer {_token()}"} if _token() else {}),
    })
    with urllib.request.urlopen(req, timeout=120) as resp, open(path, "wb") as fh:
        shutil.copyfileobj(resp, fh, length=1024 * 256)
    if os.path.getsize(path) == 0:
        raise RuntimeError(f"Release asset download 0 bytes: {asset['name']}")
    return path


def resolve(ref: str) -> tuple[str, str, str, bool]:
    """
    gh:tag/asset | gh:tag | asset-name | release URL
        -> (file_ref, local_path, filename, cleanup)
    """
    raw = (ref or "").strip()

    if "/releases/download/" in raw:
        # https://github.com/o/r/releases/download/tag/name
        tail = raw.split("/releases/download/", 1)[1]
        tag, name = tail.split("/", 1)
        release = _api(f"/repos/{DEFAULT_REPO}/releases/tags/{tag}")
        asset = _find_asset(release, name)
        return raw, _download_asset(asset), asset["name"], True

    body = raw[3:] if raw.startswith("gh:") else raw
    tag, wanted = (body.split("/", 1) + [None])[:2] if "/" in body else (None, body)

    if tag:
        release = _api(f"/repos/{DEFAULT_REPO}/releases/tags/{tag}")
    elif _token() or os.getenv("GH_RELEASE_REPO"):
        release = _api(f"/repos/{DEFAULT_REPO}/releases/latest")
        wanted = wanted if wanted and wanted != body else (body or None)
        # gh:type2_ep1.mp4  -> latest release me naam se
        wanted = wanted if wanted else None
    else:
        classes = _api(f"/repos/{DEFAULT_REPO}/releases")
        if not classes:
            raise RuntimeError("koi GitHub release nahi mila")
        release = classes[0]

    asset = _find_asset(release, wanted if wanted and "." in (wanted or "") else None)
    return raw, _download_asset(asset), asset["name"], True


def list_assets(limit: int = 5) -> list[dict]:
    releases = _api(f"/repos/{DEFAULT_REPO}/releases")
    out = []
    for rel in releases[:limit]:
        for a in rel.get("assets", []):
            out.append({"tag": rel["tag_name"], "name": a["name"],
                        "size": a["size"], "url": a["browser_download_url"]})
    return out
