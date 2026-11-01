# THE IDEA

## One line

**Ranking shorts where the ranking is the content and the footage is only the evidence.**

Three to five clips, ordered worst to best, each one introduced by a judgment spoken in
one sentence before the action resolves. The list is on screen from frame zero and fills
in. The viewer stays for #1.

---

## Why this and not a clip compilation

The reference channels we measured (DogedogRanks, RankCola, Aetheron, ProxEditz) all do
the same thing mechanically: trim a clip, stack a rank list, drop "I got this" on the
seam. It works — 15.4 M views on one Short from a channel with 684 subscribers.

It also sits directly in front of YouTube's 1 October 2026 update, which says systems will

> *"further prioritize original content and reduce the reach of content re-uploaded from
> other creators without adding anything of your own."*

The list of things that update calls **not original** is a checklist of the reference
format: crops, flips, zooms, speed changes, a music swap, transcript captions, and
*"the same template applied to hundreds of clips."*

The list of things it calls **original** has three entries that matter here:

1. **your own commentary, analysis or critique**
2. **a clip used as evidence inside your own story**
3. **your own footage**

The judgment line is (1). The ranking is (2). That is the whole design. We keep the craft
that makes the format retain — the list, the title bar, the loud master, the bursts — and
we add the one thing the reference channels only half-add: a line that says something.

**What we do not do:** we do not take the clips from YouTube or Dailymotion. Not because
it is impossible, but because it converts the channel into exactly the thing the policy
targets, and one strike is enough to end it.

---

## The format, locked

Every number here was measured off the references, not invented.

| element | spec | source |
|---|---|---|
| length | 15–30 s | references run 13.5–59.7 s; short ones retain |
| frame | 1080×1920, 30 fps | — |
| title | two lines, top 13 %, white + red | measured on all 8 |
| rank list | left edge, 20 % down, fills in per clip | measured on all 8 |
| judgment line | 1.5–2.5 s, one sentence, present tense, **before** the action resolves | transcribed from both channels |
| audio | **−11 LUFS** integrated | references measured −10.4 to −13.3 |
| bursts | 1 per 2–3 s, 0.3–0.8 s each, **mid-video only** | 15–25 % of runtime |
| attribution | on frame, plus a 2 s end card | licence obligation |

### The judgment line is the product

It is the only part that is *ours*. It has to do three things at once:

- name what is about to happen without spoiling it
- be true — the clip has to actually contain the thing the line promises
- sound like a person, not a caption

Good: `Keeper reads it. Striker doesn't.`
Bad: `This is a penalty save.` (describes; adds nothing)
Bad: `The most insane save ever.` (a claim, not a judgment)

---

## Where the footage comes from

Only sources that permit commercial reuse. Two that actually work:

**archive.org** — `advancedsearch.php` with `licenseurl:*by/4.0*`, filter out `nc`
(no commercial) and `nd` (no derivative). Yields sport, news, and stock collections.
The Jordan clip in EP_RANK_01 came from here.

**Wikimedia Commons** — `action=query&generator=search&filetype:video`. Better coverage of
real sport than archive.org, and licences are machine-readable per file (`CC BY 4.0`,
`CC BY-SA 4.0`, `CC BY 2.0`, `CC0`). Both clips in EP_RANK_01 came from here.

Attribution is not optional and is not a caption in the description — it is burned into
the frame, because the frame gets screenshotted and the description does not.

### The honest constraint

There is **not much** good commercial-use sport footage in the world. Finding three clips
for EP_RANK_01 took a full search pass across both APIs and one dead end (a demolition
derby that was unusable at night). This is the real bottleneck of the format, and it is a
content problem, not a code problem.

Two ways out, both legitimate:

- **Widen the subject.** Sport is thin; festival footage, city life, machinery, animals,
  historical archive, and public-domain film are deep. A ranking of "things that went
  wrong in 1920s silent film" is the same format with an infinite supply.
- **Shoot it.** A phone and a park. Then the footage is fully ours and the ranking can be
  anything.

---

## Ten episodes that this format can carry

Each line is a title plus the ranking logic. None of them needs a YouTube rip.

1. **3 jumps that broke physics** — Jordan rim, kickflip, pole vault. (sport, thin supply)
2. **3 saves that should not have happened** — keeper, goalkeeper, defender. (sport)
3. **Ranking every crash in a demolition derby** — one night of footage, many clips.
4. **1920s silent film stunts, ranked** — public domain, effectively unlimited.
5. **4 factory machines that move faster than a human** — archive.org industry reels.
6. **Ranking the worst weather I could find in free footage** — storms, floods, hail.
7. **3 animals that clearly know what a camera is** — Commons has thousands.
8. **Ranking the best 5 seconds of every city I have footage of** — travel cutdowns.
9. **One-take shots, ranked by how impossible they look** — public domain cinema.
10. **3 things that broke exactly where they were supposed to hold** — engineering fails.

The rule that keeps supply alive: **pick a subject that public-domain and CC libraries are
already full of**, rather than the subject everyone wants to watch on YouTube.

---

## What EP_RANK_01 proves and what it does not

**Proven.** The pipeline runs end to end from licence-checked sources to a −11 LUFS
1080×1920 master. The rank list fills correctly, the title bar holds, the judgment lines
land before the action, the bursts sit only at the seams. `jobs/realclips/build.sh`
reproduces it from scratch.

**Not proven.** That it retains. One episode in a Drive folder is a build, not a signal.
Retention is decided by the first 2 seconds and by how good the judgment lines are, and
neither is measurable without an uploaded Short and 48 hours of data.

**Known weaknesses.**

- The voice is TTS. It reads as narration, which is what the references do, but it is not
  a person. Four lines, so it is cheap to re-record.
- Three clips is thin. Five is the real format.
- No end-card CTA, no title animation, no hook variant testing.

---

## What to decide next

1. **Keep the three-clip structure or go to five?** Five needs a deeper source pass.
2. **Widen the subject or keep chasing sport?** Sport is the audience, the thin library.
3. **TTS or your mic?** This is the only decision that changes the legal character of the
   channel, because a human reading the judgment is unambiguously "your own commentary."
4. **Upload one and read the retention graph?** Nothing below this line matters until
   that number exists.
