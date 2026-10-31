# maker

Video production skills, workflows and notes — for building short-form video
end to end: research → script → assets → edit → render → publish.

Built to run on **GitHub Actions** (public repo = 16 GB RAM / 4 vCPU runners,
unlimited minutes), not on a laptop.

---

## What's in here

```
skills/
  openmontage/        # agentic video production knowledge (see LICENSE note below)
    skills/           # core, meta, creative, pipeline stage skills
    agent-skills/     # 90+ focused provider/technique skills
    pipeline_defs/    # 13 pipeline definitions (yaml)
    *.md              # agent guide, project context
  ytshort/            # cross-posting bot: Drive -> YouTube + Instagram + Facebook
    bot.py            # main entrypoint
    youtube_uploader.py
    instagram_uploader.py
    meta_*.py         # Meta Graph helpers
    state_store.py    # run state / logs
    *.md              # setup guides
workflows/            # GitHub Actions
scripts/              # helpers
docs/                 # notes
```

---

## Two things that live here

### 1. `skills/openmontage` — agentic video production

The knowledge layer behind an AI-driven video pipeline: how to research a topic,
pick a pipeline, generate or retrieve assets, compose a timeline, render, and
self-review the result before delivery.

Highlights worth knowing:

| Skill | What it teaches |
|---|---|
| `meta/video-reference-analyst.md` | Given a reference video URL, break down its pacing/structure/style |
| `core/ffmpeg.md` | Composition, encoding, delivery |
| `core/subtitle-sync.md` | Word-level caption timing |
| `core/color-grading.md` | Grade consistency across mixed sources |
| `creative/broll-planning.md` | When to cut, what to put on screen |
| `pipelines/*/` | 13 end-to-end pipeline playbooks |
| `agent-skills/hyperframes-animation/` | Motion rules, transitions, blueprints |
| `agent-skills/ffmpeg/` | Low-level filter graph patterns |

**Licence:** the OpenMontage material in `skills/openmontage/` is derived from
[calesthio/OpenMontage](https://github.com/calesthio/OpenMontage), which is
**AGPLv3**. The original LICENSE is kept at
`skills/openmontage/LICENSE`. Anything you build by reusing that material
inherits AGPLv3 — read it before you publish a product on top of it.

### 2. `skills/ytshort` — publish layer

A bot that takes a finished file from Drive and posts it to YouTube, Instagram
and Facebook on a schedule.

- YouTube: resumable upload, `publishAt` scheduling, playlist insert,
  `notifySubscribers=false`
- Instagram: container + poll + publish, 720x1280 re-encode
- Facebook: page video upload
- State in CSV so you can see what went where

All credentials come from environment variables. **Nothing is committed.**
Copy `.env.example` → `.env` and fill it locally or as GitHub Secrets.

---

## Why GitHub Actions

| | Local laptop | Public repo runner |
|---|---|---|
| RAM | 2 GB (typical small box) | **16 GB** |
| vCPU | 2 | **4** |
| Minutes | your time | **unlimited (public repo)** |
| Disk | varies | 14 GB |

Rendering 1500+ frames at 1080p with Pillow blows past 2 GB. It does not come
close to 16 GB.

**Caveats that actually bite:**

- **6-hour job limit.** A render that long is a bug, not a job.
- **Artifacts expire after 90 days.** Never leave a final video as a build
  artifact only — push it to Drive/YouTube, or attach it to a release.
- **Standard runners only are free.** Bigger machines are billed even on public
  repos.
- **Don't put credentials in a public repo** — not even in Actions logs. Use
  repository secrets and mask them.

---

## Setup

```bash
pip install -r skills/ytshort/requirements.txt
cp skills/ytshort/.env.example .env    # then fill it
```

For the render side you also need:

- Python 3.10+
- FFmpeg
- Node.js 18+ (only if you use the Remotion/HyperFrames composition path)

---

## House rules learned the hard way

1. **Frame-exact timing beats everything.** Build the shot list in frames, not
   seconds. Audio trimmed to the exact frame count. Sync drifts silently
   otherwise.
2. **Never trust a search result's subject.** A query for "chili pepper" once
   returned a rock band. Always eyeball before you ship.
3. **Licence is not a credit line.** CC BY / CC BY-SA / Public Domain are usable.
   A credit on an unlicensed image is still unlicensed. Check
   `skills/openmontage/agent-skills/` and the source's own metadata.
4. **Bake static work once.** Per-frame overlays that re-render fonts and
   gradients every frame are what make renders slow. Pre-compute the base
   image, composite per frame.
5. **Don't hold big images in memory.** Caching scaled copies of every source
   image is how you get OOM-killed on a small box.

---

## Status

- `skills/openmontage` — reference material, not a running pipeline
- `skills/ytshort` — working bot, used in production
- `workflows/` — being built

---

## Credits

- OpenMontage — https://github.com/calesthio/OpenMontage (AGPLv3)
- Everything else here is original work.
