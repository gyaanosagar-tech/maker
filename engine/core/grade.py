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

def auto_expose(im: Image.Image, target: float = 118.0, gamma: float = 0.85) -> Image.Image:
    """Pull the image's mean luma toward `target`. gamma<1 is gentler on darks."""
    m = max(mean_luma(im), 1.0)
    k = (target / m) ** gamma
    return ImageEnhance.Brightness(im).enhance(max(0.45, min(2.8, k)))

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

def cinematic(im: Image.Image, *, sat=1.22, contrast=1.14, target=118.0,
              do_vignette=True, do_scrim=True) -> Image.Image:
    im = auto_expose(im, target)
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    if do_vignette:
        im = vignette(im)
    if do_scrim:
        im = scrim(im)
    return im
