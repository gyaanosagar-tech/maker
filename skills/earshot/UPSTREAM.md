# earshot

- Upstream: https://github.com/Leonxlnx/earshot
- Commit:  591fa3e028032e6dce56620a20e932e35667e8d8
- Pulled:  2026-11-01
- Licence: **MIT** (see LICENSE) — most permissive of the three sources here
- Files:   282 (whole repo, nothing dropped)

## Why this matters for us

Every video we made had a weak point: **sound**. Voice plus a sub-bass hit and
room tone is not a sound design. We could not tell whether a hit landed on the
cut, whether a whoosh peaked before or after it, or whether an effect sounded
premium or cheap — because nothing in the pipeline could hear.

earshot gives an agent ears:

| Command | What it answers |
|---|---|
| `earshot describe file.ogg` | What does this sound like, in words? (with z-scores, attack/decay, brightness) |
| `earshot match file.ogg "a deep thocky key press"` | How well does it fit a description? Ranked against alternatives. |
| `earshot find keys.ogg "a single key press"` | Where in a long recording is the best instance? (timestamped) |
| `earshot real` / `forge` | Is this a real recording or code-synthesized? |
| `earshot timeline film.mp4` | Second-by-second listening transcript of a whole film |
| `earshot forge` | **Make sound effects in code**, then improve them by listening |
| `earshot fit recording.ogg` | Translate a recording into code that can be varied |
| `earshot kit film.mp4` | Render a whole film's effects with **measured sync points** |

The `fit` and `kit` paths are the ones that fix our actual problem: hits
measured against cuts, effects mixed against a music bed instead of at a fixed
level, and a rule for how close a run may go.

Runs locally on CPU. CLI + Python API + MCP server.

## Licence

MIT — do what you want. No copyleft obligation, unlike
`skills/openmontage` (AGPLv3).
