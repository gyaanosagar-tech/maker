"""Rhythm — the thing the reference edits do that our engine did not.

Our old timeline derived every shot from (narration length + pad). That can
never land on a beat, because `pad` is arbitrary. Every reference video in the
library is cut on a detected grid. This module makes the grid the authority.

Two modes:

    timeline.mode = "grid"   -> shots snap to beats (kinetic, poster-collage)
    timeline.mode = "free"   -> shots follow narration (tutorial, talking head)

The measured evidence:
    poster-collage references  1.1-1.9 cuts/sec, cuts on the grid
    tutorials                  0.5-0.7 cuts/sec, cuts on the sentence
    ambient                    0.01-0.04 cuts/sec, almost no cuts at all
"""
import numpy as np


def shot_lengths_from_grid(beats: list, n_shots: int, duration: float,
                           weights: list = None) -> list:
    """Distribute n_shots across a beat grid.

    weights: relative length of each shot, e.g. [1,1,1,1,2,0.5].
    A weight of 2 means the shot holds for two beats. This is how the
    accelerate-then-open pattern in the references is produced.
    """
    if not beats:
        step = duration / max(1, n_shots)
        return [(i * step, step) for i in range(n_shots)]

    g = sorted(beats)
    if weights is None:
        weights = [1.0] * n_shots
    w = np.asarray(weights, dtype=np.float64)
    w = w / w.sum()

    # how many grid steps does each shot get
    total_steps = max(n_shots, len(g) - 1)
    raw = w * total_steps
    steps = np.maximum(1, np.floor(raw).astype(int))
    while steps.sum() > total_steps:
        steps[np.argmax(steps)] -= 1

    out, k = [], 0
    for s in steps:
        if k >= len(g) - 1:
            break
        k2 = min(len(g) - 1, k + int(s))
        start = g[k]
        end = g[k2]
        if end - start < 0.02:
            end = start + 0.02
        out.append((round(start, 3), round(end - start, 3)))
        k = k2
    return out


def accelerate(n: int, start_hold: float = 2.0, end_hold: float = 0.5) -> list:
    """Weights that start slow and tighten — the build every reference uses.

    V1 of the library: 0.9s shots tightening to 0.1s bursts, then opening again.
    """
    if n <= 1:
        return [1.0]
    x = np.linspace(0, 1, n)
    curve = start_hold + (end_hold - start_hold) * (x ** 0.7)
    return [float(v) for v in curve]


def opens_again(n: int, hold: float = 2.5) -> list:
    """Same as accelerate but the last shot holds — the release."""
    w = accelerate(n - 1)
    return w + [hold]


def cut_points(shots: list) -> list:
    """Start times of every shot after the first, i.e. where impacts go."""
    return [round(s[0], 3) for s in shots[1:]]


def describe(shots: list) -> str:
    lens = [s[1] for s in shots]
    if not lens:
        return "no shots"
    r = len(lens) / max(1e-6, sum(lens))
    return (f"{len(lens)} shots, {sum(lens):.2f}s, "
            f"mean {sum(lens)/len(lens):.2f}s, {r:.2f} cuts/sec, "
            f"min {min(lens):.2f}s max {max(lens):.2f}s")
