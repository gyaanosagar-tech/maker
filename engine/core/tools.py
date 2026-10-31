"""Tools — every capability we own, in one place.

Each adapter answers three questions honestly:
    1. is it installed?
    2. what does it do for us?
    3. what happens when it is not there?

Nothing in here pretends to work. `status()` is the truth table.
"""
import json, os, re, shutil, subprocess, urllib.request, urllib.parse

TIMEOUT = 30

# ---------------------------------------------------------------- detection

def _which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None

def _cmd_ok(args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=TIMEOUT)
        return r.returncode == 0
    except Exception:
        return False

def status() -> dict:
    """What is actually available on this machine / runner."""
    s = {}
    s["ffmpeg"]   = _which("ffmpeg")
    s["ffprobe"]  = _which("ffprobe")
    s["earshot"]  = _which("earshot")
    s["npx"]      = _which("npx")
    s["node"]     = _which("node")
    s["piper"]    = _which("piper")
    s["espeak"]   = _which("espeak-ng", "espeak")
    s["git"]      = _which("git")
    s["python"]   = _which("python3", "python")
    s["fonts"]    = os.path.isdir(os.environ.get("MAKER_FONTS",
                                    os.path.expanduser("~/assets/fonts")))
    s["skills"]   = {d: os.path.isdir(repo_root(d)) for d in ("openmontage", "hyperframes", "earshot")}
    s["network"]  = _net()
    s["wikimedia"] = _probe(WM_API + "?action=query&format=json&meta=siteinfo")
    s["openverse"] = _probe("https://api.openverse.org/v1/images/?q=a&page_size=1")
    return s

def repo_root(sub: str) -> str:
    """skills/<sub> lives at the repo root, four levels above core/."""
    here = os.path.dirname(os.path.abspath(__file__))          # .../engine/core
    return os.path.normpath(os.path.join(here, "..", "..", "skills", sub))

def _probe(url: str, timeout: int = 12) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "maker/1.0 (+video engine)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 300
    except Exception:
        return False

def _net():
    """Any usable media source? Wikimedia is the one that matters."""
    return _probe(WM_API + "?action=query&format=json&meta=siteinfo")

# ---------------------------------------------------------------- media search

# ---------------------------------------------------------------- wikimedia
# The primary source. Apache/CC-friendly, no key, and the same place our
# earlier licensed images came from. Every record carries its licence text.

WM_API = "https://commons.wikimedia.org/w/api.php"
GOOD_LICENSES = ("cc0", "cc by", "cc-by", "public domain", "pd-", "pdm")

def _wm_ok(lic: str) -> bool:
    l = (lic or "").lower()
    if any(bad in l for bad in ("nc", "-nd", "noncommercial", "no derivative")):
        return False
    return any(g in l for g in GOOD_LICENSES)

def search_images_wikimedia(q: str, n: int = 10, min_px: int = 1200) -> list:
    """Search Wikimedia Commons. Returns only records with a clean licence."""
    params = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": "6", "gsrlimit": str(n * 3),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "1600",
    })
    req = urllib.request.Request(f"{WM_API}?{params}",
                                 headers={"User-Agent": "maker/1.0 (+video engine)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)

    out = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        ii = (page.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {}) or {}
        def g(k):
            v = meta.get(k, {})
            return (v.get("value") if isinstance(v, dict) else "") or ""
        lic = g("LicenseShortName") or g("License")
        if not _wm_ok(lic):
            continue
        if ii.get("width", 0) < min_px or ii.get("height", 0) < min_px:
            continue
        artist = g("Artist")
        artist = re.sub(r"<[^>]+>", "", artist).strip() or "unknown"
        title = (page.get("title") or "").replace("File:", "")
        url = ii.get("thumburl") or ii.get("url")
        out.append({
            "provider": "wikimedia",
            "id": str(page.get("pageid")),
            "title": title,
            "creator": artist,
            "license": lic,
            "license_version": "",
            "source": "Wikimedia Commons",
            "url": url,
            "landing": ii.get("descriptionurl"),
            "width": ii.get("thumbwidth") or ii.get("width"),
            "height": ii.get("thumbheight") or ii.get("height"),
            "attribution": f'"{title}" by {artist} — {lic}, via Wikimedia Commons',
        })
        if len(out) >= n:
            break
    return out


LICENSES = ("cc0", "pdm", "by", "by-sa")   # never nc, never nd, never unknown

def _ov(kind: str, q: str, n: int = 12) -> list:
    """Openverse — CC0 / public-domain / CC BY only. Returns credit records."""
    lic = "&".join(f"license={l}" for l in LICENSES)
    url = f"https://api.openverse.org/v1/{kind}/?q={urllib.parse.quote(q)}&{lic}&page_size={n}"
    req = urllib.request.Request(url, headers={"User-Agent": "maker/1.0 (+video engine)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = json.load(r)
    out = []
    for x in data.get("results", []):
        if x.get("watermarked") or x.get("deleted_image") or x.get("removed_from_source"):
            continue                       # unusable regardless of licence
        lic = (x.get("license") or "").lower()
        if lic not in LICENSES:
            continue                       # belt and braces: filter client-side too
        out.append({
            "id": x.get("id"),
            "title": x.get("title") or "",
            "creator": x.get("creator") or "unknown",
            "license": (x.get("license") or "").upper(),
            "license_version": x.get("license_version"),
            "source": x.get("source") or x.get("foreign_landing_url"),
            "url": x.get("url"),
            "landing": x.get("foreign_landing_url"),
            # Openverse returns a ready attribution on some endpoints; build our
            # own when it does not, so a credit always exists.
            "attribution": x.get("attribution") or
                           f'"{x.get("title") or ""}" by {x.get("creator") or "unknown"} '
                           f'({(x.get("license") or "").upper()} {x.get("license_version") or ""}) '
                           f'via {x.get("source") or "Openverse"}',
        })
    return out

def search_images(q: str, n: int = 12, provider: str = "auto") -> list:
    """Wikimedia first (it resolves everywhere), Openverse second."""
    if provider in ("auto", "wikimedia"):
        try:
            got = search_images_wikimedia(q, n)
            if got or provider == "wikimedia":
                return got
        except Exception:
            pass
    if provider in ("auto", "openverse"):
        try:
            return _ov("images", q, n)
        except Exception:
            return []
    return []

def search_audio(q: str, n: int = 12) -> list:
    """Audio has no Wikimedia equivalent worth using; Openverse only."""
    try:
        return _ov("audio", q, n)
    except Exception:
        return []

def download(rec: dict, dest_dir: str) -> dict:
    os.makedirs(dest_dir, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(rec["url"]).path)[1] or ".bin"
    name = f"{str(rec.get('id') or 'item')[:12]}{ext}"
    path = os.path.join(dest_dir, name)
    if not os.path.exists(path):
        req = urllib.request.Request(rec["url"], headers={"User-Agent": "maker/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
            shutil.copyfileobj(r, f)
    rec = dict(rec, path=path, bytes=os.path.getsize(path))
    return rec

# ---------------------------------------------------------------- earshot

class Earshot:
    """Ears. Real if installed, absent otherwise — never simulated."""
    @staticmethod
    def available() -> bool:
        return bool(shutil.which("earshot"))

    @staticmethod
    def describe(path: str) -> str:
        if not Earshot.available():
            return "[earshot not installed]"
        r = subprocess.run(["earshot", "describe", path], capture_output=True, text=True)
        return r.stdout.strip() or r.stderr.strip()

    @staticmethod
    def timeline(video: str) -> str:
        if not Earshot.available():
            return "[earshot not installed]"
        r = subprocess.run(["earshot", "timeline", video], capture_output=True, text=True)
        return r.stdout.strip() or r.stderr.strip()

    @staticmethod
    def kit(video: str, out: str) -> bool:
        if not Earshot.available():
            return False
        r = subprocess.run(["earshot", "kit", video, "--out", out],
                           capture_output=True, text=True)
        return r.returncode == 0

    @staticmethod
    def forge(spec: str, out: str) -> bool:
        if not Earshot.available():
            return False
        r = subprocess.run(["earshot", "forge", spec, "--out", out],
                           capture_output=True, text=True)
        return r.returncode == 0

# ---------------------------------------------------------------- hyperframes

class HyperFrames:
    @staticmethod
    def available() -> bool:
        return bool(shutil.which("npx"))

    @staticmethod
    def media_use(kind: str, intent: str, project: str) -> dict:
        """Resolve a media asset through the HyperFrames media-use skill."""
        if not HyperFrames.available():
            return {"ok": False, "reason": "npx not installed"}
        r = subprocess.run(["npx", "hyperframes", "media-use", "resolve",
                            "--type", kind, "--intent", intent, "--project", project],
                           capture_output=True, text=True, timeout=180)
        return {"ok": r.returncode == 0, "out": r.stdout.strip(), "err": r.stderr[-500:]}

# ---------------------------------------------------------------- speech

def tts(text: str, out: str, voice: str = None) -> bool:
    """Local, free, offline. Piper first, espeak fallback. Never a cloud key."""
    if shutil.which("piper"):
        cmd = ["piper", "--output_file", out]
        if voice:
            cmd += ["--model", voice]
        r = subprocess.run(cmd, input=text, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(out):
            return True
    if shutil.which("espeak-ng") or shutil.which("espeak"):
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        r = subprocess.run([exe, "-w", out, "-s", "150", text], capture_output=True, text=True)
        return r.returncode == 0 and os.path.exists(out)
    return False

def tts_available() -> str:
    if shutil.which("piper"):
        return "piper"
    if shutil.which("espeak-ng") or shutil.which("espeak"):
        return "espeak"
    return "none"

# ---------------------------------------------------------------- report

def report() -> str:
    s = status()
    lines = ["tool              present  role"]
    lines.append("-" * 62)
    rows = [
        ("ffmpeg",     s["ffmpeg"],  "encode, mux, loudness"),
        ("ffprobe",    s["ffprobe"], "verify every output"),
        ("earshot",    s["earshot"], "hear a film; forge SFX"),
        ("npx/node",   s["npx"],     "hyperframes render + media-use"),
        ("piper",      s["piper"],   "offline voice"),
        ("espeak",     s["espeak"],  "offline voice (fallback)"),
        ("fonts",      s["fonts"],   "typography"),
        ("wikimedia",  s["wikimedia"], "primary image source (CC0/PD/CC BY/SA)"),
        ("openverse",  s["openverse"], "secondary (often blocked on CI)"),
    ]
    for name, val, role in rows:
        lines.append(f"{name:17s} {'yes' if val else 'no':7s}  {role}")
    for k, v in s["skills"].items():
        lines.append(f"skills/{k:<10s} {'yes' if v else 'no':7s}  reference material")
    lines.append("")
    lines.append(f"voice: {tts_available()}")
    if not s["network"]:
        lines.append("network: no usable media source — fetch_assets will fail, "
                     "supply local images instead")
    return "\n".join(lines)
