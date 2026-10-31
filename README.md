# maker

**One repo that makes videos.** Three source repos for knowledge, one engine
that actually renders, and a truth table that says what is available before
anything is attempted.

A public home for the tools we use to **make** short-form video.

One repo, many sources. Each source lives in its own folder under `skills/`,
credited and licensed where it comes from. Rendering runs on **GitHub Actions**
(public repo → 16 GB / 4 vCPU runners, unlimited minutes), not on a small box.

---

## Layout

```
skills/
  openmontage/        agentic video production knowledge  (AGPLv3)
    skills/           736 skill docs — core, meta, creative, pipeline stages
    agent-skills/     90+ focused provider / technique skills
    pipeline_defs/    13 pipeline definitions (yaml)
    *.md              agent guide, project context
  hyperframes/        HTML + GSAP motion-graphics runtime  (Apache-2.0)
    skills/           9 skill folders — core, cli, registry, media, slideshow, figma
    agent-skills/     7 agent skills — captions, motion doctrine, seam craft
    registry-blocks/  210 blocks with templates + markup
  earshot/            ears for coding agents — sound analysis + synthesis  (MIT)
    earshot/          CLI, Python API, MCP server, 252-sound code bank
    skills/           agent skill docs
    eval/             benchmark suites (semantics, timeline, realness, forge)
.github/workflows/
  selftest.yml        runner shape + ffmpeg + Pillow fps probe
  render.yml          job file -> render -> ffprobe verify -> artifact
scripts/render.py     render entrypoint (replace the body with the real pipeline)
jobs/example.json     the shape of a render request
docs/WORKFLOWS.md     runner limits, secrets, what bites
```

**Publishing is deliberately not here.** The upload bot lives in its own
**private** repo and is invoked from outside. This repo only *makes* things.

---

---

## The engine

`engine/` is the part that renders. Everything else in this repo is reference
material it reads from.

```
engine/
  core/
    grid.py        1080x1920 design grid — every coordinate is a fraction, never a pixel
    timeline.py    shots in FRAMES; seconds derived. The fix for every sync drift.
    grade.py       per-image auto-exposure + vignette + scrim
    kburns.py      6 moves, rotating, clamped so a crop can never pad black
    text.py        measured type — fitted and wrapped before it is drawn
    compose.py     one frame: image -> grade -> move -> scrim -> type
    transition.py  whip pan, impact flash, fades
    audio.py       voice at frame offsets, impact on every cut, room, bed, -14 LUFS
    render.py      frames -> mp4
    qc.py          probe the real file; refuse to report success on a bad one
    tools.py       every capability we own, and whether it is actually installed
    build.py       the pipeline that ties it together
  scripts/
    render.py      render a job
    fetch_assets.py  CC0/PD/CC BY only, credit written at download time
    status.py      what can this machine do, right now
```

### Render a video

```bash
python3 engine/scripts/render.py jobs/demo.json
```

Output lands in `out/<job>/`: the mp4, plus `timeline.json`, `credits.json`,
`qc.json`, `summary.json`, `report.txt`. Evidence, every time.

On GitHub: **Actions → engine → Run workflow** (that runner has 4 vCPU / 16 GB;
the local box does not).

### A job file

```json
{
  "name": "my_video",
  "music_query": "tense cinematic percussion",
  "beats": [
    {"id": "b1", "query": "capsicum annuum macro", "tag": "STEP 1",
     "line": "Capsaicin binds TRPV1", "narration": "vo/b1.wav"},
    {"id": "b2", "image": "local_file.jpg", "line": "Not heat. A trick.",
     "narration": "vo/b2.wav"}
  ]
}
```

`query` fetches a licensed image. `image` uses one you already have. Either way
the credit is recorded.

### What the engine refuses to do

- Use an image whose licence is unknown, NC, or ND.
- Report success when the file fails probe.
- Pretend a tool is installed when it is not — run `status.py` and it says.
- Ship text that overflows its safe area.

See **[engine/CAPABILITIES.md](engine/CAPABILITIES.md)** for the full matrix:
what each source repo contributes, what was carried over from the old studio
tooling, and what was deliberately left out with the reason.

---

## Sources

| Folder | Licence | What it gives you |
|---|---|---|
| `skills/openmontage` | **AGPLv3** | Research → script → assets → compose → self-review. The pipeline thinking. |
| `skills/hyperframes` | **Apache-2.0** | HTML+GSAP render runtime. Motion, captions, transitions, 210 ready blocks. |
| `skills/earshot` | **MIT** | Hearing. Describe/match/find sound, audit a film's audio timeline, synthesize effects in code, fit existing recordings. |

Licences differ and it matters. **AGPLv3 is copyleft** — build a product on that
material and you must publish your source. **Apache-2.0 and MIT are permissive** —
no such obligation. Full texts sit next to each source.

---

## What's in `skills/openmontage`

Derived from [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage).

The useful parts, if you want a fast map:

| Skill | What it teaches |
|---|---|
| `meta/video-reference-analyst.md` | Given a reference video URL, break down pacing / structure / style |
| `meta/creative-intake.md` | Turning a vague idea into a producible brief |
| `meta/reviewer.md` | Multi-point self-review before delivery |
| `core/ffmpeg.md` | Composition, encoding, delivery |
| `core/subtitle-sync.md` | Word-level caption timing |
| `core/color-grading.md` | Grade consistency across mixed sources |
| `core/remotion.md` / `core/hyperframes.md` | Which render runtime for which brief |
| `creative/broll-planning.md` | When to cut, what goes on screen |
| `pipelines/*/` | 13 end-to-end playbooks |
| `agent-skills/hyperframes-animation/` | Motion rules, transitions, blueprints |
| `agent-skills/ffmpeg/` | Low-level filter graph patterns |

**Licence:** AGPLv3. Original text kept at `skills/openmontage/LICENSE`.
Anything you build on top of that material inherits AGPLv3 — read it before
you ship a product.

---

## Why GitHub Actions

| | Small box | Public repo runner |
|---|---|---|
| RAM | ~2 GB | **16 GB** |
| vCPU | 2 | **4** |
| Minutes | your time | **unlimited (public repo)** |
| Disk | varies | 14 GB |

Rendering ~1500 frames at 1080p with Pillow blows past 2 GB. It does not come
close to 16 GB.

**Limits that actually bite:**

- **6-hour job cap.** A render longer than that is a design bug, not a job.
- **Artifacts expire (90 days max, 14 set here).** Never let a finished video
  live only as a build artifact — push it somewhere durable.
- **Only standard runners are free.** Bigger machines are billed even on
  public repos.
- **Public repo = public logs.** Never inline a credential. Use secrets.

---

## Setup

```bash
pip install -r requirements.txt
# render side also needs: Python 3.10+, FFmpeg, Node 18+ (only for Remotion/HyperFrames)
```

Run the self test from the Actions tab first — it prints real CPU/RAM and how
long a 1544-frame render would take on the runner.

---

## House rules learned the hard way

1. **Frame-exact timing beats everything.** Build the shot list in frames, not
   seconds. Trim audio to the exact frame count. Sync drifts silently otherwise.
2. **Never trust a search result's subject.** A query for "chili pepper" once
   returned a rock band. Always eyeball the asset before shipping.
3. **Licence is not a credit line.** CC BY / CC BY-SA / Public Domain are usable.
   A credit on an unlicensed image is still unlicensed.
4. **Bake static work once.** Re-rendering fonts and gradients every frame is
   what makes renders slow. Pre-compute the base image, composite per frame.
5. **Don't hold big images in memory.** Caching scaled copies of every source
   image is how you get OOM-killed on a small box.
6. **Make and publish stay separate.** Different repos, different risk.

---

## Adding a source

New repos get their own folder under `skills/`. Each one needs:

- where it came from (upstream URL + commit if you pinned one)
- its licence
- one line on what it actually helps with

See `docs/ADDING_SOURCES.md`.
