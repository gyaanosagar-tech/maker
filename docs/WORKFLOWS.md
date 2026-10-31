# Running on GitHub Actions

## Why

This box has ~2 GB RAM. Rendering ~1500 frames at 1080p with Pillow needs
several times that. A **public** repo's standard runner gives 4 vCPU / 16 GB
for free with no minute cap.

Public repo, standard runner, unlimited minutes — that is the only free shape.
Bigger runners are billed even on public repos.

## Workflows

| File | Trigger | What it does |
|---|---|---|
| `selftest.yml` | push / manual | Prints CPU + RAM, checks ffmpeg, renders 60 dummy frames and reports fps |
| `render.yml` | manual | Full render from a job file, then `ffprobe` verification, then artifact upload |
| `publish.yml` | manual | Downloads a render artifact and posts it via the ytshort bot. **Dry-run by default** |

## First run

1. Push this repo, make it **public**.
2. Actions tab → `selftest` → Run workflow.
   Read the log: it prints real CPU/RAM and how long 1544 frames would take.
3. If that looks good, `render` with a real job file.

## Secrets

Only `publish.yml` needs them. Add under Settings → Secrets → Actions:

```
YT_CLIENT_ID
YT_CLIENT_SECRET
YT_REFRESH_TOKEN
IG_ACCESS_TOKEN
IG_USER_IDS
FB_PAGE_IDS
```

Never inline a token in a workflow file. Public repo = public logs.

## Limits to plan around

| Limit | Value | What it means |
|---|---|---|
| Job duration | 6 h | A render longer than this is a design bug |
| Artifact retention | 90 days (14 set here) | Never let a final video live only as an artifact |
| Disk | 14 GB | Long renders of uncompressed frames will fill it; encode incrementally |
| Storage billing | 500 MB free | Large artifacts count against it |
