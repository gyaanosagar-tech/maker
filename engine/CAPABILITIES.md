# Everything we own, and where it plugs in

One table. If a capability is not here, we cannot do it — and the engine says
so instead of pretending.

## The three source repos

| Repo | Licence | What it contributes |
|---|---|---|
| `skills/openmontage` | **AGPLv3** ⚠️ | The *thinking*: research → script → asset plan → compose → self-review, 13 pipelines, 736 skill docs |
| `skills/hyperframes` | Apache-2.0 | The *motion*: HTML+GSAP render, 210 registry blocks, captions, transitions, `media-use` |
| `skills/earshot` | MIT | The *ears*: describe/match/find sound, audit a film's audio timeline, forge SFX in code |

## The tools we already had (from `studio/`)

| Tool | Was | Now lives as | Status |
|---|---|---|---|
| FFmpeg / ffprobe chain | ad-hoc per script | `core/audio.py`, `core/render.py`, `core/qc.py` | ✅ working |
| `textkit.py` — measured text, auto-fit | 801 lines, one file | `core/text.py` | ✅ ported, cleaner |
| `templates.py` — frame layouts | 779 lines | `core/compose.py` + `core/grid.py` | ✅ rebuilt on a grid |
| `render.py` — timeline render | 412 lines | `core/render.py` + `core/timeline.py` | ⚠️ replaced — frames-first, see below |
| Ken Burns | inline in renderers | `core/kburns.py` | ✅ 6 moves, no repeats |
| Per-image grade | inline | `core/grade.py` | ✅ exposure + vignette + scrim |
| Whip pan / flash / fades | inline | `core/transition.py` | ✅ |
| `musicgen*.py` (9 versions) | local MusicGen | dropped — replaced by Openverse bed or earshot forge | ⓘ see below |
| `mix_v4.py` — mix + LUFS | 111 lines | `core/audio.py:master()` | ✅ −14 LUFS target |
| `transcribe.py` — word times | 112 lines | unchanged need → **not ported** | ⚠️ see below |

### Why `musicgen*.py` was not ported

Nine versions exist, all local MusicGen. That is the single most likely thing to
blow the 6 h job timeout and the 2 GB box, and the output quality was never
good enough to ship. Replaced by two cheaper paths that are both better:
Openverse bed (real music, CC BY, credited) or `earshot forge` (SFX in code).
If you want MusicGen back, say so — it goes behind a flag, not the default path.

### Why `transcribe.py` was not ported

It produces word timings for word-by-word captions. The engine currently
captions **per beat**, not per word. Porting it without a word-level caption
layout would add a dependency that changes nothing on screen. Add both
together, or neither.

## The integration itself

| What | File | Job |
|---|---|---|
| Media — Wikimedia first | `core/tools.py:search_images/search_audio` | Openverse, licence-filtered, credit captured at download |
| Voice | `core/tools.py:tts` | Piper → espeak fallback. Local, offline, no key |
| Ears | `core/tools.py:Earshot` | `describe`, `timeline`, `kit`, `forge` |
| Motion | `core/tools.py:HyperFrames` | `npx hyperframes media-use resolve` |
| Truth table | `core/tools.py:status()` | what is installed *right now* |
| Pipeline | `core/build.py` | resolves → voices → frames → mixes → encodes → QCs → writes evidence |

## The rules baked into the code

0. **The truth table is honest.** `status.py` probes with a real request. This
   sandbox blocks `api.openverse.org` (github.com and google resolve, openverse
   times out) — so `network: unreachable` here is the sandbox, not the code.
   On the GitHub runner it resolves. Verify there, not here.
1. **Frames first, seconds derived.** `core/timeline.py`. This is the fix for every sync drift.
2. **Every image measured and corrected.** `core/grade.py:auto_expose`. One fixed filter across mixed sources is what makes a montage look cheap.
3. **Text measured before drawn.** `core/text.py:fit/wrap`. Nothing ships clipped.
4. **Only CC0 / PD / CC BY / CC BY-SA.** `core/tools.py:LICENSES`. Hard-coded filter, no override flag.
5. **Attribution written at download time**, not reconstructed later.
6. **QC refuses to lie.** `core/qc.py` probes the actual file; `ok:false` is a real failure.
7. **Missing tool = stated, not simulated.** Every adapter reports absence.

## What is NOT integrated, and why

| Not integrated | Reason |
|---|---|
| MusicGen (9 scripts) | Slow, fragile, superseded. Flag it if you want it back. |
| Word-level captions | Needs `transcribe.py` **and** a caption layout. Half now = no visible change. |
| Remotion path | HyperFrames covers it; running both means two Node toolchains on a 14 GB runner. |
| Publishing | Out of scope by your instruction. `ytshort` stays private. |


---

## Bugs found while integrating — and what fixed them

Recorded because each one would have shipped silently.

| Symptom | Cause | Fix |
|---|---|---|
| Black bars at frame edges | PIL `crop()` pads out-of-bounds with black instead of raising; the Ken Burns zoom cropped past the source | `kburns.oversize()` guarantees the source is ≥ max-zoom, and every crop is clamped |
| Pepper frame blown out | Exposure corrected on **mean** luma only. A bright subject on a dark background has a low mean and already-clipped highlights, so the correction pushed them further | `auto_expose()` now measures the **95th percentile** too and takes the stricter of the two limits |
| `credits.json` came out empty | `fetch_assets` wrote credits into the assets dir; `build` never read them back and rebuilt an empty list | `build` reads `assets/credits.json` at start; the on-frame credit is derived from it |
| Fine print never appeared on frame | credit was passed but the draw call had nothing to draw | wired to `core.grid.Y.credit` |
| `"hot"` alone on a line | greedy wrap | `text._balance()` moves words so the short line is ≥ ~55% of the long one |
| `status.py` said skills absent on CI | path resolved inside `engine/`, skills live at the repo root | `repo_root()` |
| `network: no` on a healthy runner | probe did a bare GET on a base URL | probes a real query against a real endpoint |
| Openverse unreachable from CI | it genuinely is blocked from GitHub runners (25 s timeout, http 000) | Wikimedia promoted to primary provider |

## Verified, not assumed

| Check | Result |
|---|---|
| Local render, demo job | 93 frames, 3.10 s, −16.3 LUFS, QC **PASS** |
| GitHub Actions render | run **#2 success**, artifact 2.12 MB, 1080×1920 h264 + aac, 93 frames |
| Live Wikimedia search | `capsicum annuum fruit` → CC BY-SA 3.0, 1600×1278, creator captured |
| Full chain: search → download → render → mp4 | 81 frames, QC **PASS**, credits present on frame and in JSON |
| Probe/QC refusing bad output | `qc.py` fails on wrong size, wrong frame count, missing audio, loudness outside range |
