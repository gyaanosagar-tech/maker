# EP_RANK_01 — the first episode built only from reusable footage

16.8 s · 1080×1920 · 30 fps · −11.1 LUFS · 3 ranked clips · 4 spoken judgment lines.

## Sources (every one reusable, attribution on screen and in the closing card)

| clip | source | licence | author |
|---|---|---|---|
| The jump (rank 1) | `youtube-eFa3zdRX58I` on archive.org | CC BY 4.0 | ACC Digital Network |
| The kickflip (rank 3) | `Skateboarding at Mexico City - Flip - 040.webm` | CC BY 4.0 | Jarek Tuszyński |
| The penalty save (rank 2) | `Keller saves PK attempt by Henry.ogv` | CC BY 2.0 | Ted Kerwin |
| Music bed | `jobs/burst/assets/bed.wav` | generated | maker |

No YouTube rip. No Dailymotion rip. Nothing taken from another creator without a licence.

## What it does, in the order the format needs it

1. **Two-line title** in the top 13 % — white line, red line. Same as every reference.
2. **A numbered list on the left from frame one.** It fills in as the clips play. The
   viewer stays to find out what #1 is; that is the retention mechanism, not the clips.
3. **One spoken judgment line per clip**, 1.7–4.2 s, placed before the action resolves.
   This is the thing YouTube's October 2026 update calls commentary. It is also the
   thing the reference channels actually do — measured, not guessed.
4. **Mid-video bursts** at the three seams only: flash, glitch, flash. 0.26–0.30 s each,
   under 2 s total on a 14.8 s timeline.
5. **−11 LUFS master**, matching the reference loudness range (−10.4 to −13.3 measured).

## Rebuild

```
bash jobs/realclips/build.sh     # downloads sources, cuts shots, composes, mixes
```

`assets/`, `shots/` and `build/` are gitignored — 800 MB of intermediates do not belong
in a repo. The script re-derives them.

## Honest limits

- The voice is TTS, not a recorded human. It reads as a narrator, which is what the
  references do, but it is not a person.
- Three clips is thin for a ranking. The archive has very little clean sport footage with
  a commercial-use licence; this is what exists, not what I would pick from a full library.
- No end-card CTA and no title animation. Those are format, not craft, and they were not
  part of the question.
