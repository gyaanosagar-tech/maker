"""
drive_helper.py — Drive se file uthana, IG ke liye public copy, archive.

Aap file ka link doge (ya file ID) — bas wahi use hota hai. Folder scan nahi
(aapne bola: "jo mai bolu wahi").
"""
from __future__ import annotations

import base64
import json
import os
import re
import tempfile

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import config

SCOPES = ["https://www.googleapis.com/auth/drive"]
_SERVICE = None


def _creds():
    if config.GOOGLE_SERVICE_ACCOUNT_JSON_B64:
        info = json.loads(base64.b64decode(config.GOOGLE_SERVICE_ACCOUNT_JSON_B64))
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if config.GOOGLE_SERVICE_ACCOUNT_JSON:
        return service_account.Credentials.from_service_account_file(
            config.GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
        )
    raise RuntimeError("Drive creds missing: GOOGLE_SERVICE_ACCOUNT_JSON(_B64) set karo "
                       "(service account ko file/folder pe Editor/Viewer share karna hoga)")


def service():
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = build("drive", "v3", credentials=_creds(), cache_discovery=False)
    return _SERVICE


DRIVE_ID_RE = re.compile(r"[A-Za-z0-9_-]{25,}")


def extract_id(ref: str) -> str | None:
    """https://drive.google.com/file/d/<ID>/view | open?id=<ID> | plain ID"""
    ref = (ref or "").strip()
    for pattern in (r"/file/d/([A-Za-z0-9_-]{25,})",
                    r"/folders/([A-Za-z0-9_-]{25,})",
                    r"[?&]id=([A-Za-z0-9_-]{25,})"):
        match = re.search(pattern, ref)
        if match:
            return match.group(1)
    if DRIVE_ID_RE.fullmatch(ref):
        return ref
    return None


def meta(file_id: str) -> dict:
    return service().files().get(
        fileId=file_id, fields="id,name,size,mimeType", supportsAllDrives=True
    ).execute()


def download(file_id: str, dest: str) -> str:
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    request = service().files().get_media(fileId=file_id, supportsAllDrives=True)
    with open(dest, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=16 * 1024 * 1024)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    if os.path.getsize(dest) == 0:
        raise RuntimeError(f"Download 0 bytes: {file_id}")
    return dest


def temp_download(file_id: str, name: str = "video.mp4") -> str:
    os.makedirs(config.TMP_DIR, exist_ok=True)
    suffix = os.path.splitext(name)[1] or ".mp4"
    fd, path = tempfile.mkstemp(suffix=suffix, dir=config.TMP_DIR)
    os.close(fd)
    return download(file_id, path)


def upload(local_path: str, folder_id: str, name: str | None = None) -> str:
    if not folder_id:
        raise RuntimeError("Folder ID khaali hai")
    created = service().files().create(
        body={"name": name or os.path.basename(local_path), "parents": [folder_id]},
        media_body=MediaFileUpload(local_path, resumable=True),
        fields="id", supportsAllDrives=True,
    ).execute()
    return created["id"]


def ensure_public(file_id: str) -> None:
    """IG ko public URL chahiye — link pe 'anyone with link' permission."""
    try:
        service().permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
            supportsAllDrives=True,
        ).execute()
    except Exception as exc:
        print(f"[drive] ensure_public skip: {exc}")


def public_link(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def resolve(ref: str) -> tuple[str, str, str, bool]:
    """
    Local path / GitHub Release / Drive link / Drive ID
        -> (file_ref, local_path, filename, cleanup)

    GitHub Release sabse pehle — kyunki GitHub Actions me Drive creds nahi hote.
    """
    ref = (ref or "").strip()
    if os.path.exists(ref):
        name = os.path.basename(ref)
        return f"local:{name}", ref, name, False

    import release_helper

    if release_helper.is_release_ref(ref):
        return release_helper.resolve(ref)

    file_id = extract_id(ref)
    if not file_id:
        raise ValueError(f"'{ref}' na local file hai na Drive link/ID")
    info = meta(file_id)
    name = info["name"]
    path = temp_download(file_id, name)
    return file_id, path, name, True
