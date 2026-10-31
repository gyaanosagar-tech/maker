# Edit DNA — measured from the three reference videos

Source folder: **See** (`1qTcae9HQ6xxLPMOauzxOxHTWEoF8dsYT`), 3 files, analysed 2026-11-01.
Everything below is measured from the files, not guessed from the thumbnails.

| | V1 | V2 | V3 |
|---|---|---|---|
| File | `F0E2B6A9…A769.mov` | `1a5bf441…bebf.mp4` | `8fb5d1e4…942b.mp4` |
| Handle | kavamarts | @SUMANTH.MP4 | @TECHNOCRAFTSS |
| Title | GOD'S WISDOM | KILL… SHRINE | PAPER… ROCKET |
| Format | **1080×1920** 9:16 | 720×406 16:9 | 720×406 16:9 |
| Duration | 15.37 s | 28.90 s | 20.37 s |
| fps | 30 | 30 | 25 |
| Cuts | ~29 | ~31 | ~28 |
| **Cuts/sec** | **1.9** | **1.1** | **1.4** |
| Loudness | −14.2 LUFS | −13.6 LUFS | −13.3 LUFS |
| Loudness range | **4.8 LU** | 12.2 LU | 6.0 LU |
| True peak | −0.1 dBFS | +0.2 dBFS | +0.1 dBFS |
| Mean luma | 54.4 | 56.6 | **42.1** |
| Mean saturation | 5.4 | 5.3 | 4.8 |

Mean saturation of ~5/255 on all three is the whole story: these are **near-monochrome
images with a single red element**. V1 even spikes to sat 20.7 only on the red title card.

---

## The seven rules that make these edits feel expensive

### 1. Paletted, not graded
Black, white, one red. Saturation is switched *off* almost everywhere and switched
*on* for one object per frame. That object is the only colour in the shot.

> Our engine currently calls `ImageEnhance.Color(1.18)` on everything. **Wrong for this
> look.** It needs a desaturate-then-selectively-recolour path.

### 2. Type is the loudest element, and it is treated like an object
- **V1** — `GOD'S` small, stacked above `WISDOM` at roughly **90 % of frame width**,
  condensed heavy sans, **red with a grunge/ink texture** knocked through the fill.
  Corner chips: handle top-left, `0:15` top-right — a *running counter*, not a duration.
- **V2** — `KILL` / `SHRINE` / `MALEVOLENT` in **crimson red**, thin-to-fat contrast,
  sometimes as a **textured alpha mask over a figure** (MALEVOLENT sits *inside* the
  silhouette). Words appear in sync with the audio, not on a schedule.
- **V3** — `PAPER`, `I`, `ROCKET`, `SEE`, `JARVIS`, `DROP MY NEEDLE` in **white, heavy,
  wide-tracked**, sitting directly on the image with no plate or scrim.

**This is the single biggest gap between our output and theirs.** We draw a yellow chip,
a headline at 116 px and a white credit — clean but generic. They treat type as the
hero: 90 % width, textured, red, and animated on syllable.

### 3. Black cards are punctuation, not filler
- V1: opens on a 1.2 s black card. The title lands *after* the black, not on it.
- V2: a **7.8 s near-black stretch** (0–7.8 s) with only thin red letters fading in,
  then the first image at 7.8 s. The video withholds the picture for a quarter of its
  runtime.
- V3: 0.52 s and 1.44 s black flashes early, then a **5.4 s black end card** at 15.8 s.

The pattern: **black → title → image**, and **black end card** with the handle.

### 4. Speed is not constant — it accelerates
V1 cut gaps, first half vs second half:

```
2.3 → 3.4 → 3.6 → 3.7 → 4.2 → 4.6 → 5.1 … (0.9, 0.2, 0.1, 0.5, 0.4, 0.5)
8.0 → 8.4 → 8.5 → 8.6 → 8.7 → 9.6 → 9.8 … (0.4, 0.1, 0.1, 0.1, 0.9, 0.2)
```

It starts around **0.9 s per shot**, tightens to **0.1–0.2 s bursts**, then opens up
again. V3 does the same in miniature: 0.52 / 0.96 / 1.44 / 1.88 — a rhythm of
0.44 s then a run at 0.15–0.25 s.

A constant 3–4 s shot length — what our engine does today — is the tell.

### 5. Cuts are **not** on the music grid
V1's audio has onsets at a clean **1.0 s** interval (14 onsets, 8 gaps of exactly 1.0 s).
The cuts sit an average of **280 ms off that grid**, drifting up to 470 ms.

So the editing is **not** beat-matching. It is **narrated**: a cut happens when the line
or the idea changes. Beat-syncing this material would make it worse.

### 6. Audio is loud, dense and flat
−13.3 to −14.2 LUFS with true peak at 0 dBFS. V1's LRA of **4.8 LU** means it is
compressed hard — the quiet parts are pushed up near the loud ones. It is a wall.

Our engine targets −14 LUFS with room tone at 0.30 and impacts at 0.42. That is
*quieter and more dynamic* than these. For this look the mix needs to be denser.

### 7. The handle is institutionalised chrome
Every frame carries the handle + Instagram glyph, **top or bottom corner**, ~30 px,
white, 90 % opacity. It is not a watermark added later — it is part of the layout,
present on the black cards too, and it survives every cut.

---

## Structure, all three

| | V1 | V2 | V3 |
|---|---|---|---|
| Opening | 1.2 s black | 7.8 s black + red type | 4 quick black flashes |
| Body | image, 29 cuts, text overlay | silhouette figure, red bands, type | Iron Man stills, white type |
| Peak | sat spikes to 20.7 at the red title | MALEVOLENT mask over the body | ROCKET / JARVIS / DROP MY NEEDLE |
| Ending | keeps cutting to the last frame | black card + handle | **5.4 s black end card** + handle |
| Handle chip | top-left + counter top-right | bottom-left | top-right |

---

## What our engine does now vs what it needs

| Element | Engine today | These videos | Verdict |
|---|---|---|---|
| Saturation | +18 % everywhere | ~none, one red object | ❌ needs selective colour |
| Type size | headline 116 px (~11 % width) | up to **90 % width** | ❌ far too small |
| Type fill | flat white + shadow | textured red / grunge alpha | ❌ needs texture |
| Type animation | fade in with the beat | on syllable, sometimes per-word | ❌ needs word timing |
| Crop fill | 9:16 cover | 9:16 for V1, **16:9 letterbox** for V2/V3 | ⚠️ both formats needed |
| Shot length | uniform per beat | 0.1–0.9 s, accelerating | ❌ needs a rhythm curve |
| Black cards | none | open, mid, and 5.4 s end card | ❌ missing entirely |
| Handle chrome | credit line at 0.965 | handle + glyph, corner, always on | ⚠️ close, wrong shape |
| Loudness | −14 LUFS, gentle | −13 to −14 LUFS, hard-compressed | ⚠️ needs more compression |
| Beat sync | impacts on cuts | cuts deliberately off-grid | ⚠️ keep, but for the other formats |

---

## Honest limits of this analysis

- Measured from the files with ffprobe/ffmpeg: cut points, loudness, luma, saturation,
  audio onsets. **Visual judgement of type and colour is mine from 20 sampled frames**,
  not a pixel measurement of font or recipe.
- I could not identify the exact fonts. They are condensed heavy sans — close to
  Anton / Barlow Condensed ExtraBold (we already have both) — but the grunge treatment
  is a texture over the glyph, not a font.
- These are 720×406 16:9 for V2/V3, i.e. already-compressed reposts. The real masters
  were surely sharper; I measured what was in the folder.
- I did not attempt to identify the music or the source footage.
