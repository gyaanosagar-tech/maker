"""Ken Burns — six move patterns, chosen so no two consecutive shots match.

A single slow push on every shot is the tell of an automated montage.
Rotating the move type (and the axis) is what makes it read as edited.

Hard rule: never crop outside the source. PIL pads with black instead of
raising, so an out-of-bounds crop becomes a black bar that survives all the
way to the final file. Everything below is clamped to the real image.
"""
from PIL import Image

MOVES = [
    # (z_start, z_end, drift_x, drift_y)  — drift is a fraction of frame size
    (1.00, 1.12,  0.00,  0.00),   # push in, centred
    (1.13, 1.01,  0.00,  0.00),   # pull out, centred
    (1.01, 1.13, -0.03,  0.02),   # push in, drift left-down
    (1.12, 1.02,  0.03, -0.02),   # pull out, drift right-up
    (1.00, 1.14,  0.02,  0.00),   # push in, drift right
    (1.14, 1.00, -0.02,  0.00),   # pull out, drift left
]

MAX_Z = max(max(z0, z1) for z0, z1, _, _ in MOVES)

def oversize(src: Image.Image, out_w: int, out_h: int) -> Image.Image:
    """Source must be at least MAX_Z larger than the frame, or the crop runs off."""
    need_w, need_h = int(out_w * MAX_Z + 2), int(out_h * MAX_Z + 2)
    if src.width >= need_w and src.height >= need_h:
        return src
    r = max(need_w / src.width, need_h / src.height)
    return src.resize((int(src.width * r) + 1, int(src.height * r) + 1), Image.LANCZOS)

def crop_for(src: Image.Image, out_w: int, out_h: int, t: float, move_idx: int) -> Image.Image:
    """src should already be oversize(). t is 0..1 through the shot."""
    src = oversize(src, out_w, out_h)
    bw, bh = src.size
    z0, z1, dx, dy = MOVES[move_idx % len(MOVES)]
    z = z0 + (z1 - z0) * max(0.0, min(1.0, t))

    cw = min(bw, max(out_w, int(out_w * z)))
    ch = min(bh, max(out_h, int(out_h * z)))

    cx = bw / 2 + dx * bw * t
    cy = bh / 2 + dy * bh * t
    x = int(max(0, min(bw - cw, cx - cw / 2)))
    y = int(max(0, min(bh - ch, cy - ch / 2)))
    return src.crop((x, y, x + cw, y + ch)).resize((out_w, out_h), Image.BILINEAR)
