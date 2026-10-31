# Adding a source repo

Every source gets its own folder. No mixing.

```
skills/
  <source-name>/
    LICENSE or LICENSE.md     <- upstream licence, verbatim
    UPSTREAM.md               <- url, commit sha, date pulled, what it does
    ...the files you actually use
```

## Rules

1. **Pin it.** Record the upstream commit SHA in `UPSTREAM.md`. "latest" means
   the repo breaks silently the next time it changes shape.
2. **Keep the licence.** Copy it verbatim. Never paraphrase a licence.
3. **Copy only what you use.** Vendoring an entire 160 MB repo when you need
   1.5 MB of docs is how a repo turns into a maintenance problem.
4. **Text only unless there is a reason.** Binary assets bloat the clone and
   conflict forever. If an asset is essential, say why in `UPSTREAM.md`.
5. **No credentials, no live data.** Scrub identifiers from docs and config
   samples. A public repo is public forever — git history included.
6. **Update the README table.** A source nobody can find is not a source.

## UPSTREAM.md template

```markdown
# <source-name>

- Upstream: https://github.com/owner/repo
- Commit:  <sha>
- Pulled:  <YYYY-MM-DD>
- Licence: <SPDX id> (see LICENSE)
- Why:     <one line — what this actually helps with>
- Kept:    <what was copied, what was dropped and why>
```
