"""Motion effects — wipe, flash, slomo, handheld, clone, invert, glow.

All take and return PIL images (or lists of them for retime), so they drop into
the existing compose/render path unchanged.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops


def _pil(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _np(im):
    return np.asarray(im.convert("RGB"), dtype=np.float32)


# ---------------------------------------------------------------- 2. wipe

def wipe(fg: Image.Image, bg: Image.Image, t: float, direction: str = "left",
         soft: float = 0.06) -> Image.Image:
    """Hard directional wipe with a soft edge. t 0..1.

    A wipe with a feathered edge reads as a lens move. A wipe with a hard edge
    reads as a PowerPoint transition — the difference is `soft`.
    """
    t = max(0.0, min(1.0, t))
    w, h = fg.size
    horiz = direction in ("left", "right")
    span = w if horiz else h
    edge = t * (span * (1 + soft))
    band = max(1.0, span * soft)

    ramp = np.arange(span, dtype=np.float32)
    fwd = np.clip((edge - ramp) / band, 0, 1)          # 0 left of edge -> 1 past
    if direction in ("left", "up"):
        line = fwd
    else:
        line = fwd[::-1]
    m = np.tile(line, (h, 1)) if horiz else np.tile(line[:, None], (1, w))
    m = m[..., None]
    return _pil(_np(fg) * m + _np(bg) * (1 - m))


# ---------------------------------------------------------------- 6. flash

def flash(frame: Image.Image, amount: float = 0.6, tint=(255, 255, 255)) -> Image.Image:
    """White (or tinted) blast on a beat. amount 0..1."""
    a = max(0.0, min(1.0, amount))
    f = _np(frame)
    k = a ** 0.85
    out = f * (1 - k) + np.array(tint, dtype=np.float32) * k
    return _pil(out)


# ---------------------------------------------------------------- 9. slomo

def slomo(frames: list, factor: float = 0.5) -> list:
    """Retime a frame list. factor<1 = slower.

    Blends neighbouring frames rather than duplicating them: a duplicate frame
    at 30 fps is visible as a stutter, a blend is not. Cheap motion blur, and
    it is what minterpolate does at 500x the cost.
    """
    factor = max(0.05, factor)
    n_out = max(1, int(round(len(frames) / factor)))
    out = []
    for i in range(n_out):
        src = i * factor
        i0 = int(src)
        i1 = min(i0 + 1, len(frames) - 1)
        f = src - i0
        a, b = _np(frames[i0]), _np(frames[i1])
        out.append(_pil(a * (1 - f) + b * f))
    return out


# ---------------------------------------------------------------- 10. handheld

def handheld(frame: Image.Image, seed: int, *, amp: float = 6.0,
             rot: float = 0.35, blur: float = 0.6) -> Image.Image:
    """Synthetic camera shake — position, rotation, and a touch of blur.

    Deterministic in `seed` so a re-render produces the identical frame.
    """
    rng = np.random.default_rng(seed)
    w, h = frame.size
    dx = rng.uniform(-amp, amp)
    dy = rng.uniform(-amp, amp)
    ang = rng.uniform(-rot, rot)

    pad = int(amp * 2 + 4)
    big = frame.resize((w + pad * 2, h + pad * 2), Image.BICUBIC)
    big = big.rotate(ang, resample=Image.BICUBIC, center=(big.width // 2, big.height // 2))
    x = pad + dx
    y = pad + dy
    out = big.crop((int(x), int(y), int(x) + w, int(y) + h))
    if blur > 0:
        out = out.filter(ImageFilter.GaussianBlur(blur))
    return out


# ---------------------------------------------------------------- 5. clone

def clone(frame: Image.Image, offset=(0.28, 0.0), scale: float = 0.62,
          alpha: float = 0.92, tint=None) -> Image.Image:
    """Repeat the subject beside itself.

    The trick is to place the copy *behind* and dim it, not beside and equal —
    equal copies read as a mistake, a dimmed offset copy reads as a ghost.
    """
    w, h = frame.size
    base = frame.convert("RGBA")
    cw, ch = int(w * scale), int(h * scale)
    dup = base.resize((cw, ch), Image.LANCZOS)
    if tint:
        ov = Image.new("RGBA", (cw, ch), tuple(tint) + (255,))
        dup = Image.blend(dup, ov, 0.45)
    a = dup.split()[-1].point(lambda v: int(v * alpha))
    dup.putalpha(a)

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = int(w * offset[0])
    y = int(h * offset[1]) + (h - ch) // 2
    canvas.alpha_composite(dup, (x, y))
    canvas.alpha_composite(base, (0, 0))
    return canvas.convert("RGB")


# ---------------------------------------------------------------- 11. invert

def invert(frame: Image.Image) -> Image.Image:
    return ImageChops.invert(frame.convert("RGB"))


# ---------------------------------------------------------------- 12. glow

def glow(frame: Image.Image, radius: float = 22, strength: float = 0.85,
         threshold: int = 176) -> Image.Image:
    """Bloom: bright areas only, blurred and screened back.

    Threshold matters. Glowing the whole frame is fog; glowing only what is
    already bright is a lens.
    """
    f = frame.convert("RGB")
    g = f.convert("L").point(lambda v: 255 if v > threshold else 0)
    g = g.filter(ImageFilter.GaussianBlur(radius))
    halo = Image.composite(f, Image.new("RGB", f.size, (0, 0, 0)),
                           g.point(lambda v: int(v * strength * 1.6) if v else 0))
    halo = halo.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return ImageChops.screen(f, halo)
