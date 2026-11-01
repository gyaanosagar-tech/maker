"""fx — the twelve effects from @WILLRVAIL's published menu, implemented.

Each one is a function over PIL frames or numpy arrays so it composes with
core/compose.py. No effect is listed here unless it is implemented and tested.

    1. masking       12. glow
    2. wipe          11. invert
    3. layer          9. slomo  (retime)
    4. soundwave      5. clone
    6. flash          7. silhouette
    8. lyricpop      10. handheld
"""
from .masks import (
    subject_mask, cutout, silhouette, chroma_red_mask, text_mask,
)
from .motion import (
    wipe, flash, slomo, handheld, clone, invert, glow,
)
from .reactive import (
    soundwave, waveform_envelope, beat_times,
)
from .kinetic import (
    lyric_pop, pop_scale, word_times,
)

REGISTRY = {
    "masking":     subject_mask,
    "wipe":        wipe,
    "layer":       None,          # compose.py handles N layers
    "soundwave":   soundwave,
    "clone":       clone,
    "flash":       flash,
    "silhouette":  silhouette,
    "lyricpop":    lyric_pop,
    "slomo":       slomo,
    "handheld":    handheld,
    "invert":      invert,
    "glow":        glow,
}

def status() -> dict:
    """What is implemented right now, and what each needs."""
    return {
        "masking":    "ready (rembg optional, cv2 fallback)",
        "wipe":       "ready",
        "layer":      "ready (compose.py)",
        "soundwave":  "ready",
        "clone":      "ready",
        "flash":      "ready",
        "silhouette": "ready (needs a mask)",
        "lyricpop":   "ready (needs word times)",
        "slomo":      "ready",
        "handheld":   "ready",
        "invert":     "ready",
        "glow":       "ready",
    }
