# hyperframes

- Upstream: https://github.com/heygen-com/hyperframes
- Commit:  ee50cd2fc0d0fe4a4eac22683ed23b6066289ab3
- Pulled:  2026-11-01
- Licence: Apache-2.0 (see LICENSE in this folder)
- Version: ?

## Why

HTML + GSAP motion-graphics runtime. Where Remotion is React-shaped, HyperFrames
is for briefs that express naturally as **HTML + a GSAP timeline** — kinetic
type, data reveals, seamless loops, shader transitions, captions.

Relevant to us for: short-form motion graphics, beat-synced cuts, word-level
captions, and the "reverse any video" analysis path.

## Kept (12 MB)

| Folder | What |
|---|---|
| `skills/` | 9 skill folders: core `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `remotion-to-hyperframes`, `slideshow`, `figma`, `reverse-any-video` |
| `agent-skills/` | 7 agent-facing skills (captions-overlay, changelog-video, cut-the-curve, motion-doctrine, oversized-cursor, seam-craft) |
| `claude-skills/` | same set in Claude-plugin layout |
| `registry-blocks/` | 210 blocks — `registry-item.json` + `TEMPLATE.md` + `*.html` per block (the catalogue: what exists, and the markup) |

## Dropped (390 MB)

| Dropped | Size | Why |
|---|---|---|
| `registry/blocks/**/*.js` | 56 MB | bundler output, rebuildable |
| `docs/` | 125 MB | 588 md/mdx pages + assets — available upstream |
| `packages/` | 92 MB | TypeScript source for cli / sdk-playground / shader-transitions |
| `releases/`, `assets/`, 3D models (`*.glb`), sfx `*.wav`, avatar images | ~2.6 MB+ | binary media |

Rebuild or re-clone upstream if you need any of that:
```
git clone --depth 1 https://github.com/heygen-com/hyperframes.git
```

## Licence note

Apache-2.0 — permissive, unlike the AGPLv3 material under
`skills/openmontage`. Reuse here does **not** force your work open.
