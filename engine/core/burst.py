"""Bursts — short kinetic inserts dropped into the middle of a video.

The references do not run effects for their whole runtime. They run a calm
body and then punch: a 0.4-2.0 s burst of strobe, glitch or type at the moment
that matters. That is the shape this module implements.

A burst is defined by:
    at          when it starts (seconds)
    dur         how long (seconds)
    style       flash | strobe | invert | glitch | slam | stack | wipe
    hits        internal hits per second (0 = style default)
    intensity   0..1

Everything is deterministic in (frame index, seed) so a re-render is identical.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import text as T


def _pil(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _np(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32)


# ---------------------------------------------------------------- primitives

def glitch(im: Image.Image, amount: float, seed: int = 0) -> Image.Image:
    """Datamosh-style corruption: channel offset + band displacement.

    Bands are what sell it. A pure RGB split reads as a 3D anaglyph; moving
    horizontal slices of the frame reads as a broken codec.
    """
    rng = np.random.default_rng(seed)
    a = _np(im)
    h, w, _ = a.shape

    shift = int(round(3 + 22 * amount))
    a[..., 0] = np.roll(a[..., 0], shift, axis=1)
    a[..., 2] = np.roll(a[..., 2], -shift, axis=1)

    n_bands = int(3 + 9 * amount)
    for _ in range(n_bands):
        y0 = int(rng.integers(0, max(1, h - 8)))
        bh = int(rng.integers(6, max(8, int(h * 0.06))))
        dx = int(rng.normal(0, 26 * amount))
        a[y0:y0 + bh] = np.roll(a[y0:y0 + bh], dx, axis=1)

    if amount > 0.55:
        k = int(rng.integers(0, h - 20))
        a[k:k + int(h * 0.02)] = 255 - a[k:k + int(h * 0.02)]

    return _pil(a)


def stack(im: Image.Image, subs: list, seed: int = 0) -> Image.Image:
    """Tile 3-4 images into a collage card, the @MARCELGRAUU look."""
    rng = np.random.default_rng(seed)
    w, h = im.size
    n = len(subs)
    if n < 2:
        return im
    cols = 2
    rows = int(np.ceil(n / cols))
    canvas = Image.new("RGB", (w, h), (242, 240, 236))
    gap = int(w * 0.012)
    cw = (w - gap * (cols + 1)) // cols
    ch = (h - gap * (rows + 1)) // rows
    for i, s in enumerate(subs[:cols * rows]):
        c, r = i % cols, i // cols
        tile = s.convert("RGB").resize((cw, ch), Image.LANCZOS)
        if rng.random() < 0.35:
            tile = ImageChops.invert(tile)
        canvas.paste(tile, (gap + c * (cw + gap), gap + r * (ch + gap)))
    return canvas.rotate(float(rng.uniform(-2.5, 2.5)), resample=Image.BICUBIC,
                         fillcolor=(242, 240, 236))


def slam(im: Image.Image, word: str, t: float, seed: int = 0) -> Image.Image:
    """Type arrives huge, overshoots, settles, leaves. t is 0..1 through the burst."""
    from PIL import ImageFont
    f = im.convert("RGBA")
    w, h = f.size
    d = ImageDraw.Draw(f)

    # in (0-0.18), hold (0.18-0.72), out (0.72-1.0)
    if t < 0.18:
        p = t / 0.18
        scale = 0.4 + 2.4 * p
        alpha = int(255 * min(1.0, p * 1.6))
    elif t < 0.72:
        scale, alpha = 1.0, 255
    else:
        p = (t - 0.72) / 0.28
        scale = 1.0 + 0.35 * p
        alpha = int(255 * (1 - p))

    size = max(20, int(h * 0.16 * scale))
    fnt = T.fit("display", word.upper(), int(w * 0.94), size, 40)
    tw = d.textlength(word.upper(), font=fnt)
    x = (w - tw) / 2
    y = h * 0.42 - fnt.size / 2

    if alpha > 8:
        d.text((x + 8, y + 8), word.upper(), font=fnt, fill=(0, 0, 0, alpha))
        d.text((x, y), word.upper(), font=fnt, fill=(255, 255, 255, alpha))
    return f.convert("RGB")


# ---------------------------------------------------------------- the styles

def default_hits(style: str) -> float:
    return {"flash": 1.0, "strobe": 8.0, "invert": 4.0, "glitch": 12.0,
            "slam": 1.0, "stack": 1.0, "wipe": 2.0}.get(style, 2.0)


def apply(im: Image.Image, style: str, t: float, dur: float,
          intensity: float = 0.8, word: str = "", seed: int = 0,
          subs: list = None) -> Image.Image:
    """One frame of a burst. t is seconds into the burst, dur is its length."""
    p = max(0.0, min(1.0, t / max(dur, 1e-3)))
    k = intensity

    if style == "flash":
        # hit hard, decay — brightest in the first 3 frames
        a = k * (1 - p) ** 2.2
        f = _np(im) * (1 - a) + 255 * a
        return _pil(f)

    if style == "invert":
        beat = int(t * default_hits("invert")) % 2
        return ImageChops.invert(im) if beat else im

    if style == "strobe":
        beat = int(t * (4 + 10 * k)) % 2
        j = im.convert("RGB")
        if beat:
            j = _pil(_np(j) * (1 - 0.55 * k) + 255 * 0.55 * k)
        else:
            arr = _np(j)
            arr[..., 0] = np.clip(arr[..., 0] * (1 + 0.9 * k), 0, 255)
            j = _pil(arr)
        return j

    if style == "glitch":
        amt = k * (1.0 - 0.35 * p)
        return glitch(im, amt, seed + int(t * 24))

    if style == "slam":
        return slam(im, word or "GO", p, seed)

    if style == "stack":
        if not subs:
            return im
        return stack(im, subs, seed)

    if style == "wipe":
        # horizontal blur sweep across the frame
        strength = k * (1 - abs(2 * p - 1))
        sm = im.filter(ImageFilter.GaussianBlur(1 + 16 * strength))
        arr = _np(im)
        b = _np(sm)
        m = np.zeros((im.size[1], im.size[0], 1), dtype=np.float32)
        centre = p * im.size[0]
        width = im.size[0] * 0.28
        xs = np.arange(im.size[0])[None, :, None]
        m[:] = np.clip(1 - np.abs(xs - centre) / width, 0, 1)
        return _pil(arr * (1 - m) + b * m)

    return im


def schedule(bursts: list) -> list:
    """Normalise a burst list into [(start, dur, style, hits, intensity, word)]."""
    out = []
    for b in bursts:
        style = b.get("style", "flash")
        out.append({
            "at": float(b.get("at", 0)),
            "dur": float(b.get("dur", 0.8)),
            "style": style,
            "hits": float(b.get("hits", default_hits(style))),
            "intensity": float(b.get("intensity", 0.8)),
            "word": b.get("word", ""),
        })
    return sorted(out, key=lambda x: x["at"])


def active(bursts: list, t: float):
    """Which burst covers time t, or None."""
    for b in bursts:
        if b["at"] <= t < b["at"] + b["dur"]:
            return b, t - b["at"]
    return None, 0.0
