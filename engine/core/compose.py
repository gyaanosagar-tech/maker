"""Compose — one frame in, one frame out.

Draw order is fixed and this is why nothing ever renders on top of type:
    image -> grade -> ken burns -> scrim -> tag -> headline -> body -> caption -> credit -> pips
"""
from PIL import Image, ImageDraw
import grid as G
import grade as GR
import kburns as KB
import text as T
import transition as TR

def frame_for(beat, src: Image.Image, t: float, idx: int, total: int,
              *, tag_color=(255, 214, 0, 255), credit: str = ""):
    W, H = G.W, G.H
    base = GR.cover(src, int(W * KB.MAX_Z) + 2, int(H * KB.MAX_Z) + 2)
    base = KB.crop_for(base, W, H, t, beat.move)
    base = GR.cinematic(base)
    img = base.convert("RGBA")
    d = ImageDraw.Draw(img)
    cx = W // 2
    maxw = W - G.SAFE.left - G.SAFE.right

    if beat.tag:
        f = T.fit("body", beat.tag.upper(), maxw, 54, 34)
        tw = T.width(d, beat.tag.upper(), f)
        pad_x, pad_y = 30, 16
        bx = (W - tw) / 2 - pad_x
        by = G.fy(G.Y.tag)
        d.rounded_rectangle([bx, by, bx + tw + pad_x * 2, by + f.size + pad_y * 2 + 6],
                            radius=(f.size + pad_y * 2) // 2, fill=tag_color)
        d.text(((W - tw) / 2, by + pad_y - 2), beat.tag.upper(), font=f, fill=(16, 16, 18, 255))

    if beat.line:
        f, lines = T.wrap("headline", beat.line, maxw, 116, 2)
        lh = f.size * 1.10
        T.draw_block(d, lines, f, cx, G.fy(G.Y.headline), lh)

    if credit:
        f = T.font("credit", 30)
        w = T.width(d, credit, f)
        T.draw_block(d, [credit], f, cx, G.fy(G.Y.credit), 0, fill=(235, 235, 240, 190))

    if total > 1:
        r, gap = 6, 18
        tot = total * (r * 2) + (total - 1) * gap
        x0 = (W - tot) / 2
        y = G.fy(G.Y.pips)
        for i in range(total):
            on = i <= idx
            d.ellipse([x0 + i * (r * 2 + gap), y, x0 + i * (r * 2 + gap) + r * 2, y + r * 2],
                      fill=(255, 255, 255, 230) if on else (255, 255, 255, 70))
    return img.convert("RGB")
