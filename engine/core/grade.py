"""Grade — auto-exposure + cinematic look, independent of source image.

The rule that matters: every image gets its own exposure correction.
A single fixed filter across mixed sources produces the 'cheap montage'
look. Measure the source, then correct it toward a target.
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageStat

def cover(im: Image.Image, w: int, h: int) -> Image.Image:
    r = max(w / im.width, h / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def mean_luma(im: Image.Image) -> float:
    return sum(ImageStat.Stat(im.convert("L")).mean)

def pct_luma(im: Image.Image, p: float = 0.95) -> float:
    """95th-percentile luma — tells us whether highlights are already clipped."""
    h = im.convert("L").histogram()
    total = sum(h)
    target = total * p
    acc = 0
    for v, c in enumerate(h):
        acc += c
        if acc >= target:
            return float(v)
    return 255.0

def auto_expose(im: Image.Image, target: float = 108.0, ceil: float = 246.0) -> Image.Image:
    """Correct toward `target` mean, but never push highlights past `ceil`.

    A bright subject on a dark background has a low mean and already-clipped
    highlights. Correcting on the mean alone blows it out — which is exactly
    how the first pepper frame looked. Measure both, take the stricter limit.
    """
    m = max(mean_luma(im), 1.0)
    p95 = max(pct_luma(im, 0.95), 1.0)

    k_mean = target / m
    k_hi = ceil / p95
    k = min(k_mean, max(k_hi, 0.55))       # never brighter than the highlights allow
    k = max(0.50, min(2.20, k))

    if abs(k - 1.0) < 0.04:
        return im
    return ImageEnhance.Brightness(im).enhance(k)

def vignette(im: Image.Image, strength: float = 0.30, feather: int = 34) -> Image.Image:
    """Darken corners. Centre stays untouched — the opposite of a mistake
    that is easy to make and hard to notice."""
    w, h = im.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    for i in range(feather):
        t = i / (feather - 1)
        d.ellipse([-w * strength + w * strength * t, -h * strength * 0.6 + h * strength * 0.6 * t,
                   w * (1 + strength) - w * strength * t, h * (1 + strength * 0.6) - h * strength * 0.6 * t],
                  fill=int(255 * t))
    return Image.composite(im, Image.new("RGB", (w, h), (4, 4, 6)), mask)

def scrim(im: Image.Image, top_frac: float = 0.30, top_a: int = 150,
          bot_frac: float = 0.62, bot_a: int = 232) -> Image.Image:
    """Dark gradient bands only where text goes. Not a full-frame darkening."""
    w, h = im.size
    band = Image.new("L", (1, h), 0)
    p = band.load()
    for y in range(h):
        a = 0
        if y < h * top_frac:
            a = int(top_a * (1 - y / (h * top_frac)) ** 1.5)
        if y > h * bot_frac:
            a = max(a, int(bot_a * ((y - h * bot_frac) / (h * (1 - bot_frac))) ** 1.15))
        p[0, y] = a
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), im, band.resize((w, h)))

def cinematic(im: Image.Image, *, sat=1.18, contrast=1.10, target=108.0,
              do_vignette=True, do_scrim=True) -> Image.Image:
    im = auto_expose(im, target)
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    if do_vignette:
        im = vignette(im)
    if do_scrim:
        im = scrim(im)
    return im
