"""
config.py — saari settings ek jagah.

Jo cheez badalni ho, yahin badlo. Secrets .env / GitHub Secrets se aate hain.
Sab time IST me — koi UTC confusion nahi.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------ YouTube
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "").strip()
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "").strip()
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "").strip()
YT_CHANNEL_ID = os.getenv("YT_CHANNEL_ID", "").strip()

# Rule: subscriber notification OFF (sul.md ka workflow kehta hai)
NOTIFY_SUBSCRIBERS = os.getenv("NOTIFY_SUBSCRIBERS", "false").lower() == "true"

# Rule: random playlist nahi — exact playlist. Aap channel pe bana ke ID do.
PLAYLIST_IDS = [p.strip() for p in os.getenv("PLAYLIST_IDS", "").split(",") if p.strip()]
# Kaunsi video kis playlist me: {"teaser": "PLxxx", "vlog": "PLyyy"}; "default" sab ke liye
PLAYLIST_MAP: dict[str, str] = {}
for _pair in os.getenv("PLAYLIST_MAP", "").split(","):
    if "=" in _pair:
        _k, _v = _pair.split("=", 1)
        PLAYLIST_MAP[_k.strip()] = _v.strip()

# YT quota ka sach (Oct 2026):
#  - videos.insert ka apna bucket: 100 uploads/day (June 2026 se)
#  - baaki methods (playlistItems.insert = 50 units) 10,000 units/day shared
YT_UPLOADS_PER_DAY = int(os.getenv("YT_UPLOADS_PER_DAY", "100"))
YT_QUOTA_DAILY = 10000
YT_PLAYLIST_UNITS = 50
VIDEOS_PER_DAY = min(YT_UPLOADS_PER_DAY, YT_QUOTA_DAILY // YT_PLAYLIST_UNITS)

# ------------------------------------------------------------------ SAFETY
# Rule (user, 25 Oct 2026): "Aage se mere command pr krna".
# PUBLIC upload sirf tab jab user ne us job me saaf-saaf allow kiya ho.
#   job JSON me:  "confirm_public": true
# Warna video PRIVATE jaayega. Ye default ko override nahi kiya ja sakta.
ALLOW_PUBLIC_DEFAULT = os.getenv("ALLOW_PUBLIC_DEFAULT", "false").lower() == "true"

# ------------------------------------------------------------------ Instagram / FB
META_APP_ID = os.getenv("META_APP_ID", "").strip()
META_APP_SECRET = os.getenv("META_APP_SECRET", "").strip()
IG_USER_IDS = [u.strip() for u in os.getenv("IG_USER_IDS", "").split(",") if u.strip()]
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "").strip()
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "").strip()
FB_PAGE_IDS = [p.strip() for p in os.getenv("FB_PAGE_IDS", "").split(",") if p.strip()]

GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v21.0")
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"

# Trial reels: 200+ followers chahiye. Kam ho to sab normal.
TRIAL_MIN_FOLLOWERS = int(os.getenv("TRIAL_MIN_FOLLOWERS", "200"))
# Mix ratio: 5 me se 3 normal, 2 trial  => trial_ratio 0.4
TRIAL_RATIO = float(os.getenv("TRIAL_RATIO", "0.4"))
# SS_PERFORMANCE = perform kare to Instagram khud followers ko dikha dega
# MANUAL        = aap app me jaa ke khud graduate karoge
TRIAL_GRADUATION = os.getenv("TRIAL_GRADUATION", "SS_PERFORMANCE")
# 24h ke andar kitne trial — Meta ka official number nahi hai, safe rakho
TRIAL_DAILY_CAP = int(os.getenv("TRIAL_DAILY_CAP", "10"))
IG_DAILY_LIMIT = int(os.getenv("IG_DAILY_LIMIT", "100"))

# IG ko re-encode chahiye — 21M ka file `FINISHED` nahi deta
IG_REENCODE = os.getenv("IG_REENCODE", "1") == "1"
IG_FFMPEG_ARGS = [
    "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
    "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.1",
    "-b:v", "2500k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
    "-movflags", "+faststart",
]
IG_POLL_TRIES = int(os.getenv("IG_POLL_TRIES", "40"))
IG_POLL_SLEEP = int(os.getenv("IG_POLL_SLEEP", "15"))

# ------------------------------------------------------------------ Drive
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_SERVICE_ACCOUNT_JSON_B64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64", "")
FOLDER_VIDEOS = os.getenv("FOLDER_VIDEOS", "")          # aapke videos (Viewer)
FOLDER_REENCODED = os.getenv("FOLDER_REENCODED", "")   # PURANA — ab zaroorat nahi.
# IG resumable upload (post_now.py) se file seedha Meta ke server pe jaati hai. Koi public URL nahi.

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".mkv", ".webm")

# ------------------------------------------------------------------ analysis
# Insights ke liye alag scope chahiye (upload scope se nahi aata)
YT_ANALYTICS_SCOPE = "https://www.googleapis.com/auth/yt-analytics.readonly"

# ------------------------------------------------------------------ paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
QUEUE_FILE = os.path.join(STATE_DIR, "jobs.json")
MASTER_LOG = os.path.join(STATE_DIR, "Master_Log.csv")
LEARNING_LOG = os.path.join(STATE_DIR, "LEARNING_LOG.md")
LOCK_FILE = os.path.join(STATE_DIR, ".lock")
TMP_DIR = os.path.join(STATE_DIR, "tmp")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")
INSIGHTS_CSV = os.path.join(ANALYSIS_DIR, "performance.csv")


def missing() -> list[str]:
    problems = []
    if not (YT_CLIENT_ID and YT_CLIENT_SECRET and YT_REFRESH_TOKEN):
        problems.append("YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN (will_provide.py)")
    if not IG_ACCESS_TOKEN:
        problems.append("IG_ACCESS_TOKEN")
    if not IG_USER_IDS:
        problems.append("IG_USER_IDS")
    if not PLAYLIST_IDS and not PLAYLIST_MAP:
        problems.append("PLAYLIST_IDS ya PLAYLIST_MAP (aapki playlist)")
    return problems
