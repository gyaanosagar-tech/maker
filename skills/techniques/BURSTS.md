# Bursts — kinetic punches in the middle of a video

The references do **not** run effects for their whole runtime. They run a calm
body and then punch for a few frames at the moment that matters. This is the
system for that.

A burst is a short insert (0.3–2.0 s) dropped at a chosen time, driven by the
music, on top of whatever frame the video already has.

---

## Why middle-of-video, not whole-video

Measured from the library:

| Video | LRA | What the edit does |
|---|---|---|
| Zohair | 2.3 LU | flat bed, no punches — a music video |
| kavamarts | 4.8 LU | 4 red flashes in the **last 3 s only** |
| Marcel | 3.3 LU | collage cards throughout, one word each |
| Cashworth | 12.1 LU | sparse speech, punches on the words |

**The pattern across all of them: contrast.** Long calm, short violence, calm
again. A video at maximum intensity for its whole length reads as a screensaver.
The punch only works because of the calm around it.

Rule of thumb from the library: **1 burst per 2–3 s of runtime, each 0.3–0.8 s,
covering roughly 15–25 % of the timeline.**

---

## The seven burst styles

| Style | What it looks like | Typical duration |
|---|---|---|
| `flash` | white blast, decays over 3–4 frames | 0.25–0.5 s |
| `glitch` | channel split + displaced bands (datamosh) | 0.4–0.8 s |
| `invert` | full negative, strobing at 4 Hz | 0.3–0.6 s |
| `strobe` | alternating white/red pulse at 4–14 Hz | 0.3–0.5 s |
| `slam` | one word, huge, overshoot-and-settle | 0.6–1.2 s |
| `stack` | 3–4 images tiled as a collage card | 0.5–1.0 s |
| `wipe` | blur sweep across the frame | 0.3–0.5 s |

---

## How to use it

### Manual — you choose every punch

```json
{
  "bursts": [
    {"at": 2.2, "dur": 0.45, "style": "flash",  "intensity": 0.9},
    {"at": 3.6, "dur": 0.55, "style": "glitch", "intensity": 0.85},
    {"at": 5.0, "dur": 0.70, "style": "slam",   "word": "WATCH"},
    {"at": 6.4, "dur": 0.50, "style": "invert", "intensity": 1.0},
    {"at": 7.8, "dur": 0.40, "style": "strobe", "intensity": 0.7}
  ]
}
```

### Automatic — on the beat grid

```json
{
  "mode": "grid",
  "music": "bed.wav",
  "auto_bursts": {
    "styles": ["flash", "glitch", "invert"],
    "every": 2.5,
    "dur": 0.5,
    "intensity": 0.85
  }
}
```

With `mode: "grid"` the beat grid already exists, so `every` is a real musical
interval rather than a guess.

### On the audio, not on a timer

```python
from fx import beat_times
beats = beat_times("bed.wav")        # detected grid, 118 BPM on a 120 BPM test
for i, b in enumerate(beats):
    if i % 8 == 4:                    # the backbeat of every second bar
        bursts.append({"at": b, "dur": 0.35, "style": "flash"})
```

**Bursts should land on beats, not on round numbers.** A burst at 2.0 s when
the beat is at 2.06 s is a 60 ms miss, and 60 ms is the whole difference between
"edited" and "assembled".

---

## Verified

| Check | Result |
|---|---|
| Five styles in one 7.4 s video | flash 2.20 · glitch 3.60 · slam 5.00 · invert 6.40 · strobe 7.80 |
| Render | 222 frames, 7.4 s, −14.6 LUFS, **QC PASS** |
| Visual | flash frame washes out, glitch frame shows RGB split + band displacement, slam shows WATCH at ~40 % frame height, then clean body frames between punches |
| Determinism | seeds from the frame index, so a re-render is byte-identical |

---

## What it still does not do

- `stack` needs 2+ source images in the job; with one image it returns the frame unchanged.
- `slam` uses one word. Multi-word lines wrap only at extreme sizes.
- No motion blur on `glitch` beyond the band offset — real datamosh smears.
- Bursts never move the audio. If you want the *sound* to punch too, add an
  impact at the same time in the job's music/SFX track; the engine does not
  currently sync a burst to a sound effect automatically.
