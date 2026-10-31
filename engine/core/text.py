"""Text — measured, auto-fitting, never overflowing.

Every string is measured before it is drawn. If it does not fit the safe
width, the font shrinks. Nothing ships clipped.
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.environ.get("MAKER_FONTS", os.path.expanduser("~/assets/fonts"))

# Fallbacks so the engine runs on a bare CI runner with only DejaVu.
FALLBACKS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]

ROLES = {
    "display":   ("BarlowCondensed-ExtraBold.ttf", "ArchivoBlack-Regular.ttf"),
    "headline":  ("Inter-ExtraBold.otf",           "Inter-Bold.otf"),
    "body":      ("Inter-Bold.otf",                "Inter-ExtraBold.otf"),
    "caption":   ("Inter-ExtraBold.otf",           "Inter-Bold.otf"),
    "credit":    ("Inter-Bold.otf",                "Inter-Bold.otf"),
    "devanagari":("NotoSansDevanagari-Black.ttf",  "Inter-Bold.otf"),
}

def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    for name in ROLES.get(role, ROLES["body"]):
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for p in FALLBACKS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def width(d: ImageDraw.ImageDraw, text: str, f) -> float:
    return d.textlength(text, font=f)

def fit(role: str, text: str, max_w: int, start: int, min_size: int = 28):
    """Largest size at which `text` fits `max_w` on one line."""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    s = start
    while s > min_size:
        f = font(role, s)
        if width(d, text, f) <= max_w:
            return f
        s -= 4
    return font(role, min_size)

def wrap(role: str, text: str, max_w: int, size: int, max_lines: int = 3):
    """Greedy wrap, shrinking until it fits within max_lines."""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    while True:
        f = font(role, size)
        lines, cur = [], ""
        for w_ in text.split():
            t = (cur + " " + w_).strip()
            if width(d, t, f) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines or size <= 40:
            return f, _balance(lines, max_w, f, d)
        size -= 6

def _balance(lines, max_w, f, d):
    """Move words between lines so the shorter line is at least ~55% of the
    longer. A one-word last line reads as a mistake, not a choice."""
    if len(lines) < 2:
        return lines
    while len(lines[-1].split()) <= 1 and len(lines) > 1:
        prev = lines[-2].split()
        if len(prev) <= 1:
            break
        moved = prev[-1]
        cand_prev = " ".join(prev[:-1])
        cand_last = (moved + " " + lines[-1]).strip()
        if width(d, cand_prev, f) <= max_w and width(d, cand_last, f) <= max_w:
            lines = lines[:-2] + [cand_prev, cand_last]
        else:
            break
    return lines

def draw_block(d: ImageDraw.ImageDraw, lines, f, cx: int, y: int, lh: float,
               fill=(255, 255, 255, 255), shadow=(0, 0, 0, 240), shadow_off: int = 5):
    for i, ln in enumerate(lines):
        w = width(d, ln, f)
        x = cx - w / 2
        yy = y + i * lh
        if shadow:
            d.text((x + shadow_off, yy + shadow_off), ln, font=f, fill=shadow)
        d.text((x, yy), ln, font=f, fill=fill)

def typewriter_lines(lines, total_reveal: float):
    """Return the same lines truncated for a 0..1 reveal level."""
    n = int(sum(len(l) + 1 for l in lines) * max(0.0, min(1.0, total_reveal)))
    out, used = [], 0
    for l in lines:
        take = max(0, n - used)
        out.append(l[:take])
        used += len(l) + 1
    return out
