"""Grid — the single source of truth for composition.

Everything is laid out on a 1080x1920 design grid. Render at any scale:
all coordinates are fractions of the grid, never pixels.

This kills the class of bug where a text overlay is drawn in one
coordinate space and composited in another.
"""
from dataclasses import dataclass

W, H = 1080, 1920
FPS = 30

@dataclass(frozen=True)
class Safe:
    """Platform-safe margins. Keep text inside these."""
    top: int = 220        # below the status bar / above the hook
    bottom: int = 320     # above captions / UI chrome
    left: int = 72
    right: int = 72

SAFE = Safe()

def px(frac: float) -> int:
    """Fraction of width -> pixels. Use for horizontal measures."""
    return int(round(W * frac))

def fy(frac: float) -> int:
    """Fraction of height -> pixels."""
    return int(round(H * frac))

# Vertical anchors, as fractions of H. These are the only places text goes.
class Y:
    tag       = 0.165     # yellow chip
    kicker    = 0.115
    headline  = 0.300     # 1-2 line statement
    body      = 0.640     # supporting line
    caption   = 0.780     # spoken-text caption
    credit    = 0.965     # attribution, always bottom
    pips      = 0.905     # progress indicators
