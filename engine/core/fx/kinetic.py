"""Kinetic type — words that arrive on the syllable, not on the shot.

'Lyric Pop' in the reference menu. The difference between amateur and
professional word timing is about 60 ms; this module exists to remove the guess.
"""
import subprocess, json, os
import numpy as np
from PIL import Image


def word_times(audio: str, text: str = None, model: str = "base") -> list:
    """Word-level timestamps. Uses faster-whisper when available.

    Returns [{"word": str, "start": float, "end": float}]. If the transcriber
    is not installed this returns [] and callers must degrade gracefully —
    never invent timings.
    """
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return []
    try:
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(audio, word_timestamps=True, vad_filter=False)
        out = []
        for s in segs:
            for w in (s.words or []):
                out.append({"word": w.word.strip(), "start": float(w.start),
                            "end": float(w.end)})
        return out
    except Exception:
        return []


def pop_scale(t: float, *, overshoot: float = 1.18, decay: float = 0.55) -> float:
    """Scale multiplier for a word arriving at t=0.

    Overshoots then settles. A linear 0->1 scale looks like a mistake; the
    overshoot is what sells the pop.
    """
    if t < 0:
        return 0.0
    if t > decay * 3:
        return 1.0
    p = t / max(decay, 1e-3)
    return 1.0 + (overshoot - 1.0) * np.exp(-3.2 * p) * np.cos(5.5 * p)


def lyric_pop(frame: Image.Image, words: list, t: float, *,
              font, fill=(255, 255, 255, 255), stroke=6,
              stroke_fill=(0, 0, 0, 255), y_frac: float = 0.78,
              max_w_frac: float = 0.88) -> Image.Image:
    """Draw the currently-spoken word(s), popping in as they are said.

    words: [{"word","start","end"}] already synced to this audio.
    t: playhead seconds.
    """
    from PIL import ImageDraw
    active = [w for w in words if w["start"] - 0.04 <= t <= w["end"] + 0.22]
    if not active:
        return frame

    f = frame.convert("RGBA")
    w, h = f.size
    d = ImageDraw.Draw(f)
    max_w = int(w * max_w_frac)

    # up to two words on screen, like the references
    shown = active[-2:]
    txt = " ".join(x["word"] for x in shown).upper()

    sc = pop_scale(t - shown[-1]["start"])
    size = int(font.size * max(0.2, sc))

    from PIL import ImageFont
    try:
        fnt = ImageFont.truetype(font.path, size)
    except Exception:
        fnt = font

    bb = d.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    tw = bb[2] - bb[0]
    while tw > max_w and size > 24:
        size -= 4
        try:
            fnt = ImageFont.truetype(font.path, size)
        except Exception:
            break
        bb = d.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
        tw = bb[2] - bb[0]

    x = (w - tw) / 2 - bb[0]
    y = h * y_frac - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((x, y), txt, font=fnt, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)
    return f.convert("RGB")
