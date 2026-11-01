# The 9 YouTube references — what they actually are

Downloaded and watched (8 of 9; the boxing one 403'd and is the same channel
and format as #2). Analysed with ffprobe/ffmpeg plus frame sampling.

---

## The three real categories

| # | Video | Channel | Form | Dur | Cuts/sec | LUFS | Luma | Sat |
|---|---|---|---|---|---|---|---|---|
| 1 | Ranking Coolest Skilled Moments | RankCola | ranking | 29.9 s | 0.23 | **−10.4** | 113 | 20 |
| 2 | Ranking Worst Basketball Moments | DogedogRanks | ranking | 58.4 s | 0.15 | −13.3 | 110 | 11 |
| 3 | Ranking Funniest Boxing Moments | DogedogRanks | ranking | — | *403* | — | — | — |
| 4 | iShowSpeed flipflops | deagzzzshorts | clip + subs | 41.6 s | 0.50 | −11.5 | 98 | 15 |
| 5 | Cathy edit / HIMYM | Aetheron | TV edit | 44.5 s | **0.02** | −13.7 | 51 | 14 |
| 6 | A Shop for Killers | Flicky ae | film edit | 58.7 s | 0.27 | −10.7 | 64 | 22 |
| 7 | Iron Man / Avengers | Editclips | film edit | 59.0 s | **0.86** | −12.9 | 95 | 14 |
| 8 | War / Mare | Prox Editz | film edit | 59.7 s | 0.47 | −10.4 | 124 | 15 |
| 9 | Hulk remembers Peter | 4kmovie_io | film edit | 13.5 s | 0.74 | **−23.2** | 89 | 12 |

---

## Category A — ranking compilations (RankCola, DogedogRanks)

**This is exactly your `ytshort` format, and mine confirms what I suspected.**

What is on screen, from the frames:

- A **persistent 1–5 list on the left edge** for the whole video, with labels
  filled in as each clip plays. Labels are 1–2 words: `failed?` `WTF` `Ref?`
  `Celebration 🎉` `Mythic weapon ⚔️` `level 80` `level 60`
- A **title bar top-centre**, two lines, white on black:
  `Ranking Worst` / `Basketball Moments` — colour change on the second line
- A **thin progress bar at the very bottom**, colour-changing
- A **handle watermark, bottom-centre**, semi-transparent, on every frame
- A **country flag** in RankCola's version (🇺🇸)
- Clips from TikTok/IG/other YouTube, cropped to 9:16, **no source credit ever**
- **kbps is low, resolution 360×640** — these are re-encodes of re-encodes

**There is no commentary.** No voice, no face, no opinion. Frame after frame is
the clip plus chrome. The "ranking" is a **number next to a clip**.

### The measurement that proves the point

Loudness: **−10.4 LUFS** (RankCola) and −13.3 (Dogedog). YouTube normalises
playback to about −14, so a −10.4 master is **pushed up to be louder than
everything around it** in the feed. That is a distribution trick, not an
editing choice. It is also the single most common thing these channels do.

Cut rate is **low** — 0.15–0.23/sec. They do not cut fast. They hold the clip
and let the chrome carry the attention.

### What the channel says about itself

DogedogRanks' own description, verbatim:

> "This channel creates ranking-style compilation videos using carefully selected
> clips that are trimmed, edited, and enhanced with original on-screen text,
> captions, music, sound effects, and creative transitions... All clips belong to
> their rightful owners... This content falls under Fair Use (Section 107 of the
> U.S. Copyright Act)..."

That is a **legal shield written by the channel**, not a permission from
YouTube. And YouTube's 1 October 2026 Shorts update says the reach of exactly
this — re-uploads "without adding anything of your own" — will be reduced, with
"the same template applied to hundreds of clips" named explicitly.

**So the format works. It just is not safe, and it is not yours.**

---

## Category B — the movie/TV edits (this is the part I have to be blunt about)

Five of the nine. All 1080x1920-ish film/TV footage, slowed song, subtitle lines.

What the editor actually did, from the frames:

| What | Evidence |
|---|---|
| **Picked a scene** | the film already shot, lit and graded it |
| **Cut it to 45–60 s** | HIMYM: **1 scene change in 44 s** — it is a single continuous scene |
| **Added subtitle-style text** | HIMYM: dialogue in coloured caps, `Excuse me` `Hi there SEXY` `Aunt Cathy's got an ITCH` — coloured per speaker |
| **Slowed the song** | every title carries "(Slowed)" — `DIA DE FIESTA (Slowed)`, `NO BATIDÃO (slowed)` |
| **A watermark** | `AETHERON`, `Flicky`, `EDITCLIPS`, `PROXEDITZ`, `4kmovies_io` |

**That is the entire edit.** The HIMYM one has *one cut in 44 seconds* — the
"editing" is subtitles and a slowed track on top of a scene someone else shot.

### The honest summary

**90 % of what makes these look good is the film.** The cinematography, the
actors, the colour grade, the production design — none of it is the editor's.
The editor added a caption and a song.

That is why there are thousands of these channels and why none of them can be
scaled, sold, or protected. The moment the rights holder files, they are gone.
And it is straightforwardly copyright infringement: a whole scene, unmodified,
with a slowed song. Fair use does not cover "I slowed it down".

**I will not build a pipeline for this.** Not because it is hard — it is
trivially easy — but because the tool would exist only to infringe.

---

## Category C — the iShowSpeed clip (deagzzzshorts)

One 41.6 s video, 0.50 cuts/sec, coloured word-by-word subtitles
(`🔴 YOU WANT A PICTURE?` / `WE DORM` / `NO ONE'S HOME` / `HE KICKING OUT`),
handle watermark. It is a stolen stream clip with karaoke captions.

Same problem as B, one level down.

---

## What this comparison actually tells you

| | Ranking (A) | Film edits (B) | Your `ytshort` |
|---|---|---|---|
| Source footage | stolen | stolen | stolen |
| Commentary | **none** | none | none |
| Text | list labels | subtitles | rank labels |
| Safe? | no | **no** | no |
| Scalable? | no | no | no |
| Can maker help? | **yes** | no | **yes** |

**Your format is category A.** Same chrome, same labels, same absence of
commentary. RankCola and DogedogRanks are not doing anything you are not doing —
they just have more episodes.

And that means: **the same thing that is hurting them is hurting you**, and
neither of you has a defence that survives October 2026.

---

## What I noticed that you could copy today, legally

Three things in these frames are pure technique, owned by nobody:

1. **The persistent list.** The 1–5 list is on screen from the first frame and
   fills in as clips play. The viewer stays to see #1. Our engine has `pips`;
   this is a labelled version of the same idea. **Cheap to build, works.**
2. **Loudness above the field.** −10.4 LUFS. Ours targets −14. This is a real
   distribution lever, and it is not a rights issue — though going loud on a
   quiet-content channel is also just… loud.
3. **The two-line title bar with a colour change on line 2.** RankCola:
   `Ranking the Best` white / `Coolest Skilled Moments` yellow-green gradient.
   Simple, strong, ours is close already.

None of these fix the underlying problem. They make your current format look
better while it is still the format that is at risk.

---

## The recommendation, in one line

Copy category A's **craft** — list, title bar, loudness, watermark discipline.
Do not copy its **source model**. Add the one thing the October update asks
for and nobody in these eight videos has: **a line of your own judgment per
clip.**
