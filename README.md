# maker

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

## Sources

| Folder | Licence | What it gives you |
|---|---|---|
| `skills/openmontage` | **AGPLv3** | Research → script → assets → compose → self-review. The pipeline thinking. |
| `skills/hyperframes` | **Apache-2.0** | HTML+GSAP render runtime. Motion, captions, transitions, 210 ready blocks. |

Licences differ and it matters: **AGPLv3 is copyleft** — build a product on that
material and you must publish your source. **Apache-2.0 is permissive** — no such
obligation. Full texts sit next to each source.

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
