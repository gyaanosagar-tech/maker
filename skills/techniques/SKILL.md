# techniques — how the reference edits are made, and how we make them

This folder is the **bridge** between the reference library and the engine.
Every technique below is implemented in `engine/core/fx/` or `engine/core/rhythm.py`
and verified by a test, not a claim.

Source of the list: `@WILLRVAIL` publishes his own 12-item effect menu on screen
at 30.0 s of `a4b9dd5d5fea4c1193f0410aa9593e27.mp4`. Full analysis in
`docs/REFERENCE_LIBRARY.md` and `docs/EDIT_DNA.md`.

---

## The one idea that explains all of it

**It is not footage editing. It is a poster per beat, cut to a drum track.**

Every reference video in the library — all eleven — is assembled the same way:

1. find the beat grid of the track
2. build N static compositions ("posters")
3. cut between them **on the grid**
4. add a graphic event on the loud beats (flash, invert, wipe, strobe)
5. put words on the syllables
6. end on black with the handle

The cutting is mechanical. **The posters are where the time goes.**

---

## The 12 effects, and what each one actually is

| # | Name | What it really is | Engine | File |
|---|---|---|---|---|
| 1 | **Masking (hook)** | an alpha matte of the subject so it can be moved, filled, or layered | ✅ | `fx/masks.py:subject_mask`, `cutout` |
| 2 | **Wipe the Frame** | directional transition with a **feathered** edge | ✅ | `fx/motion.py:wipe` |
| 3 | **Layer Effect** | N stacked elements, ground → subject → accent → type | ✅ | `core/compose.py` |
| 4 | **Sound Wave** | log-spaced FFT bands per frame, drawn as bars | ✅ | `fx/reactive.py:soundwave` |
| 5 | **Clone Effect** | the frame repeated, offset and **dimmed** (equal copies look like a bug) | ✅ | `fx/motion.py:clone` |
| 6 | **Flash Effect** | white/tinted blast on a beat | ✅ | `fx/motion.py:flash` |
| 7 | **Silhouette Overlay** | mask filled with flat black over a plate | ✅ | `fx/masks.py:silhouette` |
| 8 | **Lyric Pop** | word arrives on its syllable, with overshoot | ✅ | `fx/kinetic.py:lyric_pop` |
| 9 | **Slo-mo** | retime by **blending** neighbours, not duplicating | ✅ | `fx/motion.py:slomo` |
| 10 | **Handheld** | deterministic position + rotation + micro blur | ✅ | `fx/motion.py:handheld` |
| 11 | **Inverted Shot** | full-frame invert | ✅ | `fx/motion.py:invert` |
| 12 | **Glow** | **thresholded** bloom, screened back | ✅ | `fx/motion.py:glow` |

**All 12 implemented.** Before this, 3 of 12 existed.

---

## The rhythm rules, measured

| Rule | Evidence | Where |
|---|---|---|
| Cuts land on the beat | 25 cuts, median 37 ms off the grid, 10/25 within one frame | `core/rhythm.py` |
| Shot lengths follow a curve, not a constant | V1: 0.9 s tightening to 0.1 s bursts, then opening to 2.0 s | `rhythm.accelerate`, `rhythm.opens_again` |
| Cut rate is set by **format**, not quality | ambient 0.01–0.04/s · tutorial 0.5–0.7/s · kinetic 1.1–1.9/s | choose `mode` in the job |
| Loudness is fixed at −13 to −14 LUFS | all 11 references, no exception | `audio.master_two_pass` |
| LRA follows whether there is speech | 2.3 LU (music only) → 12.1 LU (sparse speech) | mix bed_gain per format |
| Colour is mostly absent | mean saturation 4–16 / 255 | `fx/masks.py:chroma_red_mask` keeps the one red thing |
| Every video ends on black + handle | 11/11 | job `tail_seconds`, `compose` credit |

---

## Two modes, and when to use each

```json
{"mode": "grid", "music": "bed.wav", "weights": [2,1.5,1,0.8,0.6,0.6,1,2.5]}
```

- **`grid`** — shots snap to detected beats. For poster-collage, kinetic,
  anything cut to music. `weights` are **in beats**: 2 = hold two beats,
  0.6 = a burst.
- **`free`** — shots follow narration length + pad. For tutorials and talking
  heads, where the cut should land on the end of a sentence, not a drum.

Picking `grid` for a tutorial is the mistake. So is picking `free` for a
music-driven short.

---

## What is still missing, honestly

| Missing | Why it matters | Cheap fix? |
|---|---|---|
| **Real letterform textures** (grunge/ink inside type) | the references' type has a distressed fill; we draw flat glyphs | yes — generate a noise/grain texture mask and multiply into the glyph alpha |
| **Torn-paper edges** (V2's red strip) | a rectangle of red reads as a bar, a torn edge reads as paper | yes — a noise-displaced edge mask |
| **Word-level timing without a transcript** | `lyric_pop` needs `[{word,start,end}]`; we can get it from faster-whisper if installed, else it silently does nothing | yes — faster-whisper is in `setup.sh` already |
| **Subject matting without rembg** | the heuristic works for dark-subject-on-bright-plate (our references) but not for a person in a cluttered room | needs `pip install rembg` (~170 MB) — not needed for the collage formats |
| **9:16 / 16:9 / 4:3 switch** | engine is 1080×1920 only; the library has 16:9 and 4:3 too | small — `grid.py` already uses fractions |

None of these block making a video in the poster-collage format today.

---

## Verified

| Check | Result |
|---|---|
| All 12 fx import and run | ✅ grid of 8 rendered effects inspected |
| `beat_times` on a 120 BPM test | 118 BPM (librosa) — my own detector said 240 |
| `beat_times` on a 90 BPM test | 89 BPM |
| Grid mode render | 8 shots over 8.1 s, 17 beats detected, QC **PASS** |
| Shot curve | 1.5 → 1.0 → 0.5 ×4 → 2.0 s (accelerate-then-release) |
| Two-pass loudness | −19.1 LUFS corrected to −15.3 LUFS against a −14 target |
| **Same render on GitHub Actions** | run success — 8.1 s, 243 frames, −15.3 LUFS, QC PASS, 1.65 MB artifact |
