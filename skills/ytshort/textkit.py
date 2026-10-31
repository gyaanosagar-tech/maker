"""
textkit.py — aapka text lagana, aur validate karna.

Text main (assistant) likhta hoon aur job file me daal deta hoon. Yahan koi
Gemini/LLM call nahi — sirf limits ke andar fit karna aur sensible default.

Har platform ki limit alag hai, isliye ek hi text se teeno ban jaate hain.
"""
from __future__ import annotations

import re

# Platform limits (2026 docs)
YT_TITLE_MAX = 100
YT_DESC_MAX = 5000
YT_TAGS_MAX = 15
IG_CAPTION_MAX = 2200
FB_DESC_MAX = 5000
IG_HASHTAG_GUIDE = 3  # IG caption me 3-5 hashtag kaafi (30+ spam lagta hai)


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def norm_tags(tags) -> list[str]:
    """
    ["#patna", "sadar bazaar"] / "patna, sadar bazaar" / "patna sadar bazaar"
    -> ["patna", "sadar bazaar"]

    Multi-word tag todna nahi hai (YouTube tags me space allowed hai).
    String me comma ho to comma se todo, warna space se.
    """
    if not tags:
        return []
    if isinstance(tags, str):
        parts = re.split(r",", tags) if "," in tags else re.split(r"\s+", tags)
    else:
        parts = [str(t) for t in tags]

    out: list[str] = []
    for tag in parts:
        tag = clean_text(tag.lstrip("#"))
        tag = re.sub(r"[^0-9A-Za-z\u0900-\u097F _]", "", tag).strip()
        if tag and tag.lower() not in (t.lower() for t in out):
            out.append(tag)
    return out[:YT_TAGS_MAX]


def build(text: dict, filename: str = "") -> dict:
    """
    Ek text dict -> teeno platform ke ready fields.

    text = {"title","description","tags","caption","hashtags","playlist"}
    """
    title = clean_text(text.get("title")) or fallback_title(filename)
    description = (text.get("description") or "").strip()
    tags = norm_tags(text.get("tags") or text.get("hashtags"))
    caption = (text.get("caption") or "").strip()

    if not description:
        description = title
        if tags:
            description += "\n\n" + " ".join(f"#{t}" for t in tags[:6])

    if not caption:
        caption = description
        if tags and "#" not in caption:
            caption += "\n\n" + " ".join(f"#{t}" for t in tags[:IG_HASHTAG_GUIDE])

    return {
        "title": title[:YT_TITLE_MAX],
        "description": description[:YT_DESC_MAX],
        "tags": tags,
        "caption": caption[:IG_CAPTION_MAX],
        "fb_description": description[:FB_DESC_MAX],
        "playlist": clean_text(text.get("playlist")) or None,
        # privacy user ka faisla hai — yahan se hoke jaani chahiye, drop nahi
        "privacy": (str(text.get("privacy") or "").strip().lower() or None),
    }


def fallback_title(filename: str) -> str:
    base = re.sub(r"\.(mp4|mov|m4v|mkv|webm)$", "", (filename or "").split("/")[-1], flags=re.I)
    base = re.sub(r"[_\-.]+", " ", base)
    base = re.sub(r"\b(final|copy|export|1080p|720p|h264|new|compressed)\b", "", base, flags=re.I)
    base = re.sub(r"\b\d{3,}\b", "", base)
    base = clean_text(base).title()
    return (base or "Daily Short")[:YT_TITLE_MAX]


def warnings(built: dict) -> list[str]:
    """Upload se pehle jo cheezein aapko batani chahiye."""
    out = []
    if len(built["title"]) < 25:
        out.append("title chhota hai — Shorts me hook pehle 30-40 char me aana chahiye")
    if not built["tags"]:
        out.append("tags khaali — YT pe tags ka asar kam hai, par bhar do (5-10)")
    hashtags = re.findall(r"#\w+", built["caption"])
    if len(hashtags) > 8:
        out.append(f"IG caption me {len(hashtags)} hashtag — 3-5 better hai")
    if len(built["caption"]) > IG_CAPTION_MAX - 50:
        out.append("IG caption limit ke bahut paas hai")
    return out


def daily_plan(videos: int, trial_ratio: float, trial_allowed: bool) -> list[bool]:
    """
    Kaunsi video trial jaayegi. 5 video, 0.4 ratio -> [F,F,T,F,T]
    Trial allowed nahi (followers < 200) -> sab False.
    """
    if not trial_allowed or trial_ratio <= 0:
        return [False] * videos
    trials = max(0, min(videos, round(videos * trial_ratio)))
    flags = [False] * videos
    if trials == 0:
        return flags
    # spread karo: 5 me 2 trial -> index 2 aur 4
    step = videos / trials
    for i in range(trials):
        idx = min(videos - 1, int(step * (i + 0.5)))
        flags[idx] = True
    return flags
