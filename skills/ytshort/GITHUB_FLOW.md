# GitHub + Drive — kaise chalta hai (bina service account)

**Status: LIVE.** Pehla video GitHub Actions se upload ho chuka hai.

## Sach jo pehle samajhna zaroori hai

| Kiske liye | Drive access | Kyun |
|---|---|---|
| **Main (chat me)** | ✅ connector | Aapne on kiya — is session me file utha sakta hoon |
| **GitHub Actions bot** | ❌ connector nahi | Headless runner. Uske paas koi connector/UI nahi hota |

Pehle maine kaha tha "isliye `sa.json` chahiye". **Wo zaroori nahi hai** — ek behtar
raasta hai: **GitHub Releases**.

## Kaam kaise hota hai

```
Aap: "ye file upload karo" (ya Drive link do)
      ↓
MAIN: Drive connector se file uthata hoon  ← mere paas access hai
      ↓
MAIN: GitHub Release me asset upload karta hoon (gh:v1/type2_ep1.mp4)
      ↓
MAIN: job file banata hoon + repo me commit
      ↓
CRON (har ghante): video Release se download → YouTube pe upload → playlist → log
```

Service account ki zaroorat **nahi**. Drive creds runner pe jaate hi nahi.

## File reference ke formats (job me `file` field)

| Format | Matlab |
|---|---|
| `gh:v1/type2_ep1.mp4` | release `v1` ka asset `type2_ep1.mp4` |
| `gh:type2_ep1.mp4` | latest release me naam se |
| `https://github.com/gyaanosagar-tech/ytshort/releases/download/v1/x.mp4` | seedha URL |
| `/path/local.mp4` | local file (sirf apne computer pe chalane ke liye) |
| `https://drive.google.com/file/d/<ID>/view` | Drive — **sirf** jab Drive creds hon (mere chat session me) |

## Pehla video (proof)

- **https://youtu.be/-VqzsUqT_gA** — "Ranking Best Fail Moments — Wait For #1"
- Privacy: **public** · Kids: No · notifySubscribers: **false** ✅
- Playlist: **Narration videos** (`<PLAYLIST_NARRATION>`) ✅
- Source: `gh:v1/type2_ep1.mp4` — Drive se GitHub tak, phir YouTube
- Log: `state/Master_Log.csv`

## Naya video add karne ka poora flow

```bash
# 1. Release banao (ek baar — v1 bana hua hai)
#    v2, v3 ... har batch ke liye nayi release

# 2. Asset upload — main karta hoon (Drive connector se)
#    ya aap khud: GitHub → Releases → v1 → Attach binaries

# 3. Job file: jobs/<naam>.json  (title/description/tags/caption)

# 4. Queue me daalo
python bot.py ...   # ya main job JSON commit kar deta hoon

# 5. Cron utha lega (xx:10 har ghante) — ya turant:
GitHub → Actions → sulbot → Run workflow
```

## Schedule (time dena ho to)

`when` field IST me: `"2026-10-26 18:00"` — bot us waqt tak wait karta hai
(private + publishAt), grace 90 min. `when` khaali = turant.

## Jo abhi baaki hai

1. **Instagram + Facebook** — token/IDs khaali hain (`IG_ACCESS_TOKEN`, `IG_USER_IDS`,
   `FB_PAGE_IDS`). Meta app banega tab.
2. ~~IG re-encode folder~~ — **zaroorat nahi.** IG resumable upload se file seedha
   Meta ke server pe jaati hai (rupload.facebook.com). Koi public link nahi chahiye.
3. Baaki 19 videos — bas bolo, main Drive se GitHub Release me daal dunga.

## Fixes jo is session me hue

- Workflow `vars` ki jagah `secrets` use kar raha tha → playlists khaali aa rahe the
- `FOLDER_VIDEOS` workflow me missing tha → add
- SA JSON: `_B64` ki jagah seedha `GOOGLE_SERVICE_ACCOUNT_JSON` — nahi chahiye ab
- **Bada bug:** `when` khaali hone pe job silently skip ho raha tha → on-demand
  upload kabhi nahi chalta. Fix + test.
- `state/.lock` repo me chala gaya tha → `.gitignore` me daala
