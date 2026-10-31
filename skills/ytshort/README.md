# sulbot — "jo mai bolu, wahi 3 jagah"

Drive se file → YouTube + Instagram + Facebook. Time aapka, text main likhta hoon.
Sab **IST**. Subscriber notification **OFF**. Playlist **aapki exact**.

```
aap: "ye file, kal 6 baje, teeno jagah"
  ↓
text (title/description/tags/caption) — main likhta hoon
  ↓
bot.py → Drive se file → YT (private+publishAt, notify=false, playlist) → FB (scheduled) → IG (cron)
  ↓
Master_Log.csv + performance.csv
```

## Setup — 6 steps

### 1. YouTube OAuth (ek baar)

> 📘 **Poora click-by-click guide: `YT_SETUP_FORCE_SSL.md`** (force-ssl scope, 18 steps, checklist ke saath)
1. Google Cloud Console → New Project
2. APIs enable: **YouTube Data API v3** + **YouTube Analytics API** (insights ke liye)
3. OAuth consent screen → External → apna Gmail **Test users** me add
4. Credentials → OAuth client ID → **Desktop app** → JSON download → `client_secret.json`
5. ```bash
   pip install -r requirements.txt
   python will_provide.py --analytics --env     # upload + insights scope
   ```
   Browser me tick sab allow kar do (insights ke liye zaroori hai).

> ⚠️ Testing app me refresh token **7 din** me expire hota hai → `invalid_grant`.
> Tab `will_provide.py` dobara chalao. Permanent fix: app ko **Published** kar do.

### 2. Playlist (aapke rule ke liye)
Channel pe playlist banao → URL se ID copy karo (`list=PLxxxx`).

```bash
# ek hi playlist sab ke liye
PLAYLIST_IDS=PLxxxxxxxx

# ya category-wise (job file me "playlist": "bihar" likhoge)
PLAYLIST_MAP=bihar=PLaaa,teaser=PLbbb,default=PLccc
```
Job file me naam bhi de sakte ho (`"playlist": "Bihar Vlogs"`) — bot channel se naam se
dhoond lega. **Naam galat hua to playlist me nahi daalega (random kabhi nahi)** aur log me warning dega.

### 3. Instagram + FB Page
1. Business Settings → Instagram Accounts → Connect (page se link)
2. System Users → Create → Assign Assets →
   Pages pe **pages_manage_posts** + **pages_read_engagement**, IG pe
   **instagram_content_publish** + **instagram_insights**
3. Generate Token → `IG_ACCESS_TOKEN`, `IG_USER_IDS`, `FB_PAGE_IDS`

> `pages_manage_posts` miss = `#100 No permission`. Token dobara generate karna padta hai.

### 4. Drive
Service account banao → JSON download → **uske email** ko video file/folder pe
**Viewer** share karo (agar Drive use karna ho).

`FOLDER_REENCODED` = **ab zaroorat nahi.** Instagram resumable upload
(`rupload.facebook.com`) se file seedha Meta ke server pe jaati hai —
koi public URL, koi Drive folder nahi.

### 5. GitHub
```bash
git init && git add . && git commit -m "init"
git remote add origin https://github.com/USER/REPO.git && git push -u origin main
gh auth login

gh secret set YT_CLIENT_ID --body "xxx"
gh secret set YT_CLIENT_SECRET --body "xxx"
gh secret set YT_REFRESH_TOKEN --body "1//xxx"
gh secret set IG_ACCESS_TOKEN --body "EAAX..."
gh secret set IG_USER_IDS --body "1784..."
gh secret set FB_PAGE_IDS --body "..."
gh secret set GOOGLE_SERVICE_ACCOUNT_JSON_B64 --body "$(base64 -w0 sa.json)"

gh variable set PLAYLIST_IDS --body "PLxxxxxxxx"
gh variable set FOLDER_REENCODED --body "<public folder id>"
```
> **Repo public rakho** — private me hourly cron free minutes (2000/mahina) kha jaata hai.
> Secrets GitHub me hote hain, code me kuch nahi.

### 6. Pehla test
```bash
python bot.py upload "<drive-link>" --job jobs/example_single.json --offline   # preview
python bot.py upload "<drive-link>" --job jobs/example_single.json --publish   # asli (turant)
python bot.py list                                                           # queue
```

## Roz ka use

```bash
# turant
python bot.py upload "<drive-link>" --job jobs/patna_vlog.json --publish

# kal shaam 6 baje
python bot.py upload "<drive-link>" --job jobs/patna_vlog.json --at "2026-10-26 18:00" --publish

# 5 file, har ek ka apna time (bulk file me "when" likha hai)
python bot.py bulk jobs/weekly.json --publish

# 5 file, sab ek hi time
python bot.py bulk jobs/weekly.json --at "2026-10-26 18:00" --publish

python bot.py insights      # performance + analysis/report.md
```

Time formats: `now` · `in 2h` · `18:30` · `2026-10-26 18:00`

## Kaun kab chalta hai

| Platform | Scheduling | Timing ki galti |
|---|---|---|
| YouTube | native (`private` + `publishAt`) | **0** — exact minute |
| Facebook | native (`scheduled_publish_time`) | **0** |
| Instagram | API me scheduling nahi → **queue + cron** | ±10-15 min (cron xx:10 pe) |

Isliye: 6:00 bologe to YT/FB 6:00 pe, IG 6:10 ke aas-paas.
Minute-exact IG chahiye → slot ko `xx:10` pe rakho, ya cron `*/10` kar do (repo public ho tab).

## Trial reels (200+ followers ke baad khud ON)

- 5 video → **3 normal + 2 trial** (ratio `TRIAL_RATIO=0.4`)
- Trial flag **hum** lagate hain, Insta khud decide nahi karti
- `SS_PERFORMANCE` = perform kare to **Insta khud** followers ko dikha deti hai
- **200 se kam followers → sab normal reels** (aapka account abhi isi stage me hai)
- `bot.py run` har run pe followers check karta hai — 200 cross, agle bulk pe mix chalu

## Limits jo code khud sambhalta hai

| Limit | Value | Code kya karta hai |
|---|---|---|
| YT quota | 10,000 units/day, upload+playlist = 1650 | **6 video/day** guard, saaf error |
| YT publishAt | min ~15 min future | late slot → turant public (private me nahi atakta) |
| IG publish | 100 / 24h | quota check |
| IG trial | cap unofficial (~10 safe) | `TRIAL_DAILY_CAP` |
| IG file | bada file → `FINISHED` nahi | re-encode 720x1280 → 5-6 MB |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `invalid_grant` | refresh token expire (7 din) → `will_provide.py --analytics --env` |
| `#100 No permission` | System User: `pages_manage_posts` + `instagram_content_publish`, token dobara |
| playlist me nahi daala | naam galat / ID galat — log me `playlist lookup fail` dekho |
| IG `#9007` | `FOLDER_REENCODED` public hai? re-encode on hai? |
| IG `ERROR` status | video specs — 9:16, <100MB, H.264 AAC |
| "lock busy" | pichla run chal raha hai — normal |
| insights khaali | `will_provide.py --analytics` se token dobara (upload scope me insights nahi aata) |

## Files

| File | Kaam |
|---|---|
| `bot.py` | control panel — upload / bulk / run / list / cancel / insights |
| `textkit.py` | aapka text teeno platform ke liye fit karna + warnings |
| `youtube_uploader.py` | upload, **notify=false**, playlist rule, publishAt |
| `instagram_uploader.py` | trial/normal reels, re-encode, FB page video |
| `drive_helper.py` | link/ID se download, public copy, archive |
| `insights.py` | YT + IG performance → `analysis/performance.csv`, `report.md` |
| `state_store.py` | jobs.json, Master_Log.csv, lock, counters |
| `will_provide.py` | OAuth → refresh token |
| `.github/workflows/sulbot.yml` | hourly cron (jobs + IG slots + roz insights) |
| `tests/test_bot.py` | 24 offline tests (sab pass) |

## Analysis loop (kaise reach badhegi)

1. `bot.py insights` → data
2. Aap `analysis/report.md` / CSV mujhe dikhao → main level batata hoon (hook, length, timing, trial vs normal)
3. Main next 5-10 video ka **brief** likhta hoon (title pattern, hook, hashtags)
4. Wo brief job files me jaata hai → upload
5. Repeat — data se decide, andaze se nahi
