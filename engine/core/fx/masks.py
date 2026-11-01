"""Masks — the foundation. Six of the twelve effects need one.

The rule that makes masking look expensive: do not cut a hard-edged rectangle.
Feather the edge by 1-3 px and lift the matte slightly, or the composite reads
as a sticker instead of a photograph.
"""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

def _np(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("RGB"), dtype=np.float32)

def _pil(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def _feather(mask: np.ndarray, px: float = 2.0) -> np.ndarray:
    m = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
    m = m.filter(ImageFilter.GaussianBlur(max(0.5, px)))
    return np.asarray(m, dtype=np.float32) / 255.0

def subject_mask(im: Image.Image, *, mode: str = "auto",
                 feather: float = 2.0) -> np.ndarray:
    """Foreground mask, 0..1 float.

    auto: try rembg (U2-Net) if installed; otherwise a luminance/saturation
    heuristic that works for the silhouette-style references (dark subject on a
    bright plate). Returns the mask, never raises.
    """
    if mode in ("auto", "rembg"):
        try:
            from rembg import remove
            cut = remove(im.convert("RGB"))
            a = np.asarray(cut.split()[-1], dtype=np.float32) / 255.0
            if a.max() > 0.05:
                return _feather(a, feather)
        except Exception:
            if mode == "rembg":
                raise
    # heuristic: subject is the dark, saturated part
    a = _np(im) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    sat = a.max(axis=2) - a.min(axis=2)
    score = (1.0 - lum) * 0.75 + sat * 0.25
    lo, hi = np.percentile(score, 55), np.percentile(score, 97)
    m = np.clip((score - lo) / max(1e-5, hi - lo), 0, 1)
    return _feather(m, feather)

def cutout(im: Image.Image, mask: np.ndarray) -> Image.Image:
    """RGBA with the mask as alpha."""
    out = im.convert("RGBA").copy()
    a = (np.clip(mask, 0, 1) * 255).astype(np.uint8)
    out.putalpha(Image.fromarray(a))
    return out

def silhouette(im: Image.Image, mask: np.ndarray,
               color=(0, 0, 0)) -> Image.Image:
    """Fill the subject with a flat colour — the reference look."""
    rgba = cutout(im, mask)
    flat = Image.new("RGBA", im.size, tuple(color) + (255,))
    flat.putalpha(rgba.split()[-1])
    return flat

def chroma_red_mask(im: Image.Image, tol: float = 0.18) -> np.ndarray:
    """Mask of the one red element in a mostly-grey frame.

    This is the selective-colour primitive: desaturate everything, keep this.
    """
    a = _np(im) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = np.clip((r - np.maximum(g, b)) / max(tol, 1e-3), 0, 1)
    return _feather(red, 1.5)

def text_mask(size, lines, font, pad: int = 8) -> Image.Image:
    """Type as a window: a white alpha matte of the words.

    Used for the MALEVOLENT knockout — the photograph shows through the letters.
    """
    w, h = size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    y = pad
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=font)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), ln, font=font, fill=255)
        y += int(font.size * 1.06)
    return m
