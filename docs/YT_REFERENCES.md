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

### CORRECTION — I was wrong about this, and the user caught it

I first wrote "there is no commentary". I had only looked at **frames**. The
user said the videos have narration. I transcribed the audio and **he is right,
I was wrong.**

DogedogRanks, word-level transcript of a 58 s Short:

```
[ 0.00]  Bro, the hoop is bigger than you.
[ 1.96]  I got this!
[ 8.74]  Guess who the star player is?
[10.98]  Let's go!
[21.20]  Bro's aura just went to zero.
[27.80]  I got this!
[33.16]  Bro's footwork is actually illegal.
[41.58]  Bro really pressed every emote button.
[43.92]  Let's go!
[50.12]  I got this!
```

RankCola, 30 s Short — 137 characters of speech:

```
"I got this / bro thinks it's a trampoline / such an organized shovel factory
 / subscribe now / got this / he's doing this with incredible precision"
```

### So what is the actual structure?

**Not a voiceover. A spoken judgment line setting up each clip.**

| Before the clip | During the clip |
|---|---|
| **one spoken line**, narration style, sets up what you are about to see | the clip plays with its own original audio |

- RankCola: `bro thinks it's a trampoline` → the clip plays.
- Dogedog: `Bro's aura just went to zero.` → the clip plays.
  `Bro really pressed every emote button.` → the clip plays.

The line sits **inside the clip's window**, 1.5–2.5 s, one sentence, present
tense, and it is a **judgment**, not a description.

### The recurring phrases — and one already in your repo

| Phrase | Where | Count |
|---|---|---|
| **"I got this!"** | Dogedog **and** RankCola | 5× in 58 s, 3× in 30 s |
| "Let's go!" | both | 2× |
| "Bro's aura just went to zero" | Dogedog | 1 |

**`I got this` is shared between two different channels** — a meme phrase in
this niche, used as the fake-out before a fail: he says it, then fails.

**It is already in your workspace.** `studio/FORMAT_MEMORY.md`:
> *"use the recurring 'I got this' phrase at transitions"*

You were already doing this. **The EP33/34 one-off builder dropped it.** That is
the regression.

### Is it a pasted sample?

No. Cross-correlating the three "I got this" takes in the Dogedog video:

```
1.90s vs 27.75s: -0.013
1.90s vs 50.05s:  0.026
27.75s vs 50.05s: 0.008
```

Correlation ≈ 0 — **three separate recordings, same voice.** That is why it does
not sound mechanical.

### What is on screen

- persistent 1–5 list on the left edge, filling in as clips play
  (`failed?` `WTF` `Ref?` `Celebration 🎉` `Mythic weapon ⚔️` `level 80`)
- two-line title bar top-centre, white on black, colour change on line 2
- thin progress bar at the bottom
- handle watermark bottom-centre, every frame
- country flag (RankCola)
- clips cropped to 9:16, **no source credit**

### Measurements

- **−10.4 LUFS** (RankCola), −13.3 (Dogedog). YouTube normalises playback to
  about −14, so a −10.4 master plays louder than its neighbours.
- **cut rate 0.15–0.23/sec** — slow. They hold the clip; the line and chrome
  carry the attention.
- **360×640** — a re-encode of a re-encode.
- The clip's own audio is **not muted**.

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
| Commentary | **one spoken line per clip** | none | recipe has it, build dropped it |
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

**Category A already does the thing I said was missing.** One spoken judgment
line per clip, over the clip's own audio, plus a persistent list, a two-line
title bar and a loud master.

Your Type-2 recipe already contains the same idea (`"I got this"` at
transitions). The gap is not the idea — it is that **it was implemented as a
pasted sample and then dropped.**

The rebuild is: **record one line per clip**, keep the list, keep the loudness,
keep the bursts. That is category A done right.
