"""Transitions — whip pan, impact flash, cross-cut.

These run on frames, not on a timeline object, so they work with any
renderer: PIL, ffmpeg, or a browser canvas.
"""
from PIL import Image, ImageFilter

def whip_pan(frame: Image.Image, t: float, direction: int = 1, strength: float = 0.55):
    """t 0..1 through the wipe. Pulls the frame sideways with motion blur."""
    if t >= 1:
        return frame
    w, h = frame.size
    p = (1 - t) ** 1.7
    off = int(w * strength * p)
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    canvas.paste(frame, (off if direction > 0 else -off, 0))
    return canvas.filter(ImageFilter.GaussianBlur(max(0.0, 5 * p)))

def impact_flash(frame: Image.Image, amount: float = 0.5, tint=(255, 255, 255)):
    return Image.blend(frame, Image.new("RGB", frame.size, tint), max(0.0, min(1.0, amount)))

def fade_from_black(frame: Image.Image, t: float):
    return Image.blend(Image.new("RGB", frame.size, (0, 0, 0)), frame, max(0.0, min(1.0, t)))

def fade_to_black(frame: Image.Image, t: float):
    return Image.blend(frame, Image.new("RGB", frame.size, (0, 0, 0)), max(0.0, min(1.0, t)))
