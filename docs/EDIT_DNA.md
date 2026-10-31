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

### 5. Every cut is locked to the audio grid — and I got this wrong the first time

**Correction.** My first pass fitted a 1.0 s grid, found a 280 ms drift, and wrote
"cuts are not beat-matched". That was wrong. The 1.0 s "onsets" were the *loud*
accents; the actual pulse is much faster.

Measured properly (10 ms resolution onsets vs 96×170 frame-difference cuts):

```
pulse: 0.13 s   (25 gaps of 0.13, 14 of 0.14, 11 of 0.12)  -> ~462 BPM feel
cuts:  25
offset mean 56 ms | median 37 ms | 10/25 within one frame (33 ms)
       -> 92 % land within 150 ms
```

Concrete hits: cut 3.37 → onset 3.37 (3 ms). Cut 5.27 → 5.26 (7 ms).
Cut 6.07 → 6.06 (7 ms). Cut 11.03 → 11.02 (13 ms). Cut 12.47 → 12.48 (13 ms).

**So: cuts are beat-matched, hard.** The editing is a drum edit. The apparent
"narrative" cuts are narrative *and* on the grid, because the track was written
or cut to support them.

The red flashes and black stutters land on the grid too — 10 ms, 50 ms, 70 ms,
120 ms — with one deliberate 390 ms anticipation.

**Rule for the engine:** cut on the beat, not on the beat plus an arbitrary pad.
`timeline.py` currently derives shot length from narration duration + `pad`, which
can never land on a grid. For this format the beat grid has to drive it.

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

## How it is actually built — the technique underneath

All three are the same method wearing different clothes. It is not "editing
footage". **It is a poster per beat, cut to a drum track.**

### The unit: one collage, four layers

Every shot is assembled from the same four slots, in this order:

| Layer | What it is | V1 | V2 | V3 |
|---|---|---|---|---|
| 1. Ground | black or a photographic plate | black | cloud/sky plate | black |
| 2. Subject | one cut-out photographic element | Dark God artwork | silhouette figure, hand, samurai | Iron Man still |
| 3. Accent | **one** saturated red object | red title texture | torn red paper strip behind the figure | (none — white type instead) |
| 4. Type | the loudest layer | WISDOM | KILL / SHRINE / MALEVOLENT | PAPER / ROCKET / JARVIS |

Colour discipline: layers 1 and 2 are desaturated to near-grey, layer 3 is the
**only** thing with saturation, layer 4 is either that same red or pure white.
That is why the average saturation is 5/255 — red is scarce, so it reads as loud.

### The four moves, repeated

1. **Cut-out collage.** Subjects are silhouetted or knocked out of their
   background and stacked. In V2 the figure is pure black in front of a grey sky
   plate with a **torn red paper strip** wedged between them — the tear edge is
   visible, so it reads as paper, not as a colour grade.
2. **Type as a window (knockout).** `MALEVOLENT` in V2 is not red text — the
   letters are a **mask**, and the photograph shows through them. `WISDOM` in V1
   is the inverse: the letters are solid, with a **grunge/ink texture inside the
   fill**, and the countdown chip burns through them.
3. **Palette strobe.** V1 holds one still frame and strobes its *treatment*, not
   its position:

   ```
   0.00  BLACK
   2.33  RED      <- title lands, letters + red wash
   3.50  grey/art <- back to normal
   8.17  BLACK    (17 frames)
   8.67  BLACK    (second stutter)
   9.67  RED      (flash)
   10.33 RED      (flash)
   11.33 RED      (flash)
   12.50 RED      (flash)
   ```

   Four red flashes in the last 3 s, each on the grid. A 0.13 s pulse with a
   0.1–0.2 s red flash on the accent is the cheapest way to make a static image
   feel like it is exploding.
4. **Withhold.** V2 shows nothing but faint red letters for 7.8 s of its 28.9 s.
   V1 opens on 1.2 s of black. V3 opens on four black flashes. **None of them
   open on the image.** The picture is the reward, and it arrives late.

### The assembly pipeline they most likely used

```
1. pick the track, find the grid            -> 0.13 s pulse here
2. lay the grid on the timeline             -> every cut and effect snaps to it
3. build N posters (one still each)         -> collage + type + one accent
4. cut the posters on the grid              -> 1–2 cuts/sec, bursts at accents
5. add the strobe events                    -> red flash / black stutter / invert
6. type on syllables                        -> word appears when the line hits
7. handle chrome last                       -> corner, always on, on black cards too
8. master loud and flat                     -> -13 to -14 LUFS, true peak 0 dBFS
```

Step 3 is where the time goes. The cutting is mechanical once the grid exists.

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
| Beat sync | impacts on **cut frames**, no grid | every cut on a 0.13 s pulse | ❌ needs a real grid, not narration+pad |

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
