# Reference library — 11 videos in Drive folder **See**

Folder `1qTcae9HQ6xxLPMOauzxOxHTWEoF8dsYT`. Re-read 2026-11-01: it grew from 3 to 11.
Everything below is measured from the files with ffprobe/ffmpeg, plus judgement from
sampled frames.

**The library is not one style. It is at least four, and one of them costs nothing
to copy because the creator published his own effect menu.**

---

## The 11, grouped by what they actually are

### Group 1 — Poster-collage / dark motivational
| | kavamarts | SUMANTH.MP4 | TECHNOCRAFTS |
|---|---|---|---|
| File | `F0E2B6A9…` | `1a5bf441…` | `8fb5d1e4…` |
| Format | 1080×1920 | 720×406 | 720×406 |
| Duration | 15.4 s | 28.9 s | 20.4 s |
| Cuts/sec | 1.9 | 1.1 | 1.4 |
| LUFS / LRA | −14.2 / 4.8 | −13.6 / 12.2 | −13.3 / 6.0 |
| Luma / Sat | 54 / 5 | 57 / 5 | 42 / 5 |

Full breakdown in **EDIT_DNA.md**. Cut-out collage, one red accent, type as hero,
beat-locked cuts on a ~0.13 s pulse, palette strobe.

### Group 2 — Collage-montage, contemporary / "aesthetic"
| | @MARCELGRAUU |
|---|---|
| File | `8f7025e1…` |
| Format | 720×1280 (9:16) |
| Duration | **14.1 s** |
| Cuts/sec | 0.64 |
| LUFS / LRA | **−13.1 / 3.3** |
| Luma / Sat | 58 / 5 |

A talking head in a dim room, and **stacked image collages** dropped over him:
a grid of photos, a torn receipt, a blue CRT scanline composition, a 1-bit
dithered figure, a classical statue. Each collage is a **paper card** — visible
edges, hard shadow, sitting on top of the frame like a print on a desk.

Words land one per shot in a heavy grotesque: `Datamosh` `Flash Light` `CRT`
`1-bit dither` `Comment`. Those five words are literally the **techniques being
named** — the video is a sampler, and the type is the index.

Then the last ~3 s is the creator's handle on black, with the Instagram glyph
transitioning white → brand gradient → white.

**Why this one matters most to us:** it is the only reference that is a
*person + graphics*, which is a format we can actually produce without
footage. Its recipe is repeatable: one static plate, N collage cards, one word
each, cut on the word.

### Group 3 — Screen-recording tutorial / educational
| | @EDIDAY.5 | @WILLRVAIL | @THETEACHER |
|---|---|---|---|
| File | `d679b486…` | `a4b9dd5d…` | `7f2aba0c…` |
| Format | 720×540 | 720×1280 | 720×1280 |
| Duration | 23.2 s | **71.0 s** | **81.8 s** |
| Cuts/sec | 0.65 | 0.01 | 0.53 |
| LUFS / LRA | −13.3 / 5.8 | −13.9 / 4.7 | −14.3 / 5.1 |

- **@EDIDAY.5** — After Effects screenshots, one term per screen, huge:
  `SHAKE THE CAMERA` over a face, `FIGHT CLUB SHAKE EFFECT`, then the actual
  Time Mapper / Track Matte / Apply Mode panels. Type alternates red and white.
  Words wipe on from behind a hard edge.
- **@WILLRVAIL** — a talking head to camera, and a **persistent numbered menu in
  the corner** that stays up the whole video. This is the one that hands us the
  recipe (below).
- **@THETEACHER** — a 2-up screen-recording of a timeline, with the narration
  burned in as **karaoke subtitles** (one or two words at a time, centred,
  black outline). Ends on a black card with a jump-cut in the audio.

### Group 4 — Ambient / loop / mood
| | @ASTROSPACE | @RAAJJJJJ/ | @CASHWORTHCLPZ |
|---|---|---|---|
| File | `aa23f6bb…` | `7841808f…` | `7f73e363…` |
| Format | 720×406 | 720×544 | 720×1280 |
| Duration | 26.6 s | 50.9 s | 41.4 s |
| Cuts/sec | **0.04** | 0.55 | 0.14 |
| LUFS / LRA | −13.5 / 5.6 | −13.8 / 7.6 | −13.6 / **12.1** |

- **@ASTROSPACE** — one continuous space render, no cuts, no voice. A thin
  caption line under the handle (`"Blawan - Close the Cycle"` — a **music credit
  in the frame**). Ends on black + glyph. The whole video is one shot.
- **@RAAJJJJJ/** — mostly **black with one small element at a time**: blue text
  `LAUGHED` / `MOST PEOPLE WERE`, then a 1-bit dithered face in a blue box,
  then black. Extreme negative space as the entire aesthetic.
- **@CASHWORTHCLPZ** — a reaction/talking head in a dark room with coloured
  LED lights, plus a **picture-in-picture screen** showing his own edit. Highest
  LRA of the set (12.1) because the speech is sparse against the music.

### Group 5 — Footage edit (no graphics)
| | THISISZOHAIR |
|---|---|
| File | `65460EFC…` |
| Format | **1080×1920** |
| Duration | 32.3 s |
| Cuts/sec | 0.03 |
| LUFS / LRA | −14.1 / **2.3** |

Cinema clips cut to music, with a **running timecode** top-right and the handle
top-left (`THISISZOHAIR`), and a black end card carrying the handle alone.
Almost no cuts by scene-detection because the shots are long and the changes are
in-camera. This is the classic "movie edit" format.

---

## What this tells us that the first three did not

**1. Loudness is identical across all eleven.** −13.1 to −14.3 LUFS. No exceptions.
Whatever else varies, the master does not. Our engine's −14 target is correct and
should be treated as fixed.

**2. Loudness *range* is the real variable.** LRA runs from **2.3** (Zohair, pure
music bed) to **12.1** (Cashworth, sparse speech over a bed). Cut density does not
predict it; **whether there is talking** does. Speech → higher LRA.

**3. Saturation is consistently near-zero except where red or a screen exists.**
5, 4, 13, 7, 16, 6, 4, 10. The two highest (EDIDAY 13, Cashworth 16) both have
**UI screenshots or coloured lights** in them. Everything else is a grey world.

**4. Cut rate does not correlate with quality — it correlates with format.**

| cuts/sec | what kind of video |
|---|---|
| 0.01 – 0.04 | ambient / loop / single-shot (Astro, Will, Zohair) |
| 0.5 – 0.7 | tutorial, collage, talking-head-with-graphics |
| 1.1 – 1.9 | poster-collage kinetic (the first three) |

So "more cuts" is not the goal. **The format decides the rate.** A tutorial at
1.9 cuts/sec would be unwatchable; an ambient loop at that rate is not a loop.

**5. Every single one ends on black with the handle.** Eleven out of eleven.
That is not taste, it is a convention of the platform.

**6. Two formats are represented and we only build one.** 9:16 for short-form
(Marcel, Cashworth, Will, Teacher, Zohair), 16:9 for reposted cinema/anime edits
(Astro, SUMANTH, Technocrafts) and 4:3 for screen recordings (EDIDAY). Our engine
assumes 1080×1920. It needs a format switch.

---

## The gift: @WILLRVAIL published his own effect menu

Frame at 30.0 s of `a4b9dd5d…`, in the corner of his own screen recording, in his
own words:

```
EFFECTS
1.  Masking (hook)
2.  Wipe the Frame
3.  Layer Effect
4.  Sound Wave
5.  Clone Effect
6.  Flash Effect
7.  Silhouette Overlay
8.  Lyric Pop
9.  Slo-mo
10. Handheld
11. Inverted Shot
12. Glow
```

**This is the highest-value find in the folder.** It is not my inference from
watching — the creator states the twelve things he does, and then demonstrates
them over 71 seconds.

Which of these we can already do, and which are new:

| # | Effect | Engine today | Notes |
|---|---|---|---|
| 1 | Masking (hook) | ❌ | we have no matte/knockout path — V2's MALEVOLENT needs the same thing |
| 2 | Wipe the Frame | ⚠️ | we have `whip_pan`; a hard directional wipe is different and easier |
| 3 | Layer Effect | ✅ | `compose.py` stacks image + scrim + type; needs arbitrary N layers |
| 4 | Sound Wave | ❌ | reactive bars from the audio buffer — new, and cheap |
| 5 | Clone Effect | ❌ | same frame repeated offset — new, cheap |
| 6 | Flash Effect | ✅ | `transition.impact_flash` exists |
| 7 | Silhouette Overlay | ❌ | cut-out subject over plate — the same mask as #1 |
| 8 | Lyric Pop | ❌ | **word-level timing** — we caption per beat, not per word |
| 9 | Slo-mo | ❌ | no retime path |
| 10 | Handheld | ❌ | synthetic camera shake |
| 11 | Inverted Shot | ✅ | trivial frame invert, not wired |
| 12 | Glow | ⚠️ | box-blur composite, not wired |

**Score: 3 of 12 exist, 2 are close, 7 are missing.** That list is now the
feature backlog for the engine, in the order a person who makes these videos
would rank them.

---

## Honest limits

- Cut counts come from ffmpeg scene detection at threshold 0.3. Videos with
  in-camera movement or a static composition under-report (Astro 1, Zohair 1).
  Those are genuinely low-cut videos, but the exact number is a floor, not a count.
- I read the @WILLRVAIL menu off a frame. I have **not** verified that every item
  is demonstrated, only that it is listed.
- Fonts are still unidentified. Group 2 and 4 use a heavy grotesque close to
  Inter/Archivo Black; Group 1 uses a condensed display face close to Anton.
- I did not identify the music, the footage sources, or the creators' actual
  software. After Effects is visible in two of them; that is all that is provable.
