> ⚠️ **Purana guide.** Naya, poora, force-ssl wala: **`YT_SETUP_FORCE_SSL.md`** — wahi use karo.

# CONNECT — step by step (aapko click karna hai, main guide kar raha hoon)

Har step ke baad bolo "done" — main next step dunga. Kuch atke to screenshot/error paste karo.

---

## Step 0 — Local setup (2 min)

```bash
cd sulbot
pip install -r requirements.txt
# ffmpeg:
#   Windows: winget install ffmpeg
#   Mac:     brew install ffmpeg
#   Linux:   sudo apt install ffmpeg
python doctor.py          # abhi sab RED hoga — theek hai, aage bharenge
```

---

## Step 1 — Google Cloud project (YouTube)

1. https://console.cloud.google.com → **New Project** → naam: `sulbot`
2. **APIs & Services → Library** → ye 3 enable karo:
   - ✅ YouTube Data API v3
   - ✅ YouTube Analytics API  *(insights ke liye)*
   - ✅ Google Drive API *(agar service account Drive use karega)*
3. **OAuth consent screen** → **External** → App name `sulbot` → apna Gmail **Test users** me add
   - ⚠️ **Publishing status: Testing** rakho abhi (7-din token issue), baad me Publish kar dena
4. **Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Naam: `sulbot-desktop`
   - **Download JSON** → file ka naam `client_secret.json` → `sulbot/` folder me rakho

**Verify:** `ls sulbot/client_secret.json` dikhna chahiye.

---

## Step 2 — YouTube token (main nahi kar sakta, aap 3 click karoge)

```bash
cd sulbot
python will_provide.py --analytics --env
```

Jo hoga:
- Browser khulega → Gmail chuno
- "sulbot wants access" → **Allow** (sab tick rehne do, warna insights band)
- Terminal me `YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN` `.env` me likh jayenge

**Verify:**
```bash
python doctor.py --yt
```
Dikhna chahiye:
```
✔ channel — <aapke channel ka naam>
✔ playlists — N mili:
     PLxxxx  Bihar Vlogs
✔ insights scope — YouTube Analytics chal raha hai
```
Aur **playlist IDs** copy karo → `.env` me:
```
PLAYLIST_IDS=PLxxxxxxxx
```

> Channel pe playlist nahi hai? YouTube Studio → Playlists → New playlist → naam do
> (jaise `Bihar Vlogs`) → us page ka URL: `.../playlist?list=PLxxxx` → wahi ID.

---

## Step 3 — Instagram + FB Page

1. **Business Settings → Instagram Accounts → Connect** (page se link)
2. **Business Settings → System Users → Add** → naam `sulbot-bot` → role Employee
3. **Assign Assets**:
   - **Pages** → apna page → Full control ya Content → `pages_manage_posts` ✅, `pages_read_engagement` ✅
   - **Instagram accounts** → apna IG → `instagram_content_publish` ✅, `instagram_insights` ✅, `instagram_basic` ✅
4. **Generate new token** → wo token `.env` me:
   ```
   IG_ACCESS_TOKEN=EAAX...
   IG_USER_IDS=<IG user id>
   FB_PAGE_IDS=<page id>
   ```

ID kahan se:
- **Page ID**: Page → About → Page transparency, ya Graph Explorer `me/accounts`
- **IG user ID**: `GET /{page-id}?fields=instagram_business_account` → `id`

**Verify:**
```bash
python doctor.py --ig
```
Dikhna chahiye:
```
✔ IG @yourhandle — 87 followers, 12 posts
! trial reels — 87 followers hain (trial ke liye 200+) — sab normal reels
✔ FB Page Patna Vlogs — 1234567890
```
(200 se kam hone pe `!` aayega — sahi hai, bot normal reels daalega.)

---

## Step 4 — Drive

1. Google Cloud → **IAM & Admin → Service Accounts → Create**
   - Naam: `sulbot-drive` → **Keys → Add key → JSON** → download → `sulbot/sa.json`
2. Us service account ka email copy karo (`sulbot-drive@....iam.gserviceaccount.com`)
3. Drive me:
   - Videos ka **folder** banao → folder ko us email pe **Viewer** share karo
   - Ek aur folder banao `IG_Reencoded` → us email pe **Editor** share karo
4. `.env`:
   ```
   GOOGLE_SERVICE_ACCOUNT_JSON=./sa.json
   FOLDER_REENCODED=<IG_Reencoded folder id>
   ```

**Verify:**
```bash
python doctor.py --drive
```

---

## Step 5 — Sab green?

```bash
python doctor.py
```
Agar `Sab connected` aaya → pehla test:
```bash
python bot.py upload "<kisi bhi video ka drive link>" --job jobs/example_single.json --offline   # preview
python bot.py upload "<drive link>" --job jobs/example_single.json --publish                     # asli upload
```

---

## Step 6 — GitHub (cron ke liye)

```bash
git init && git add . && git commit -m "init"
gh auth login
gh repo create sulbot --private --source . --push
# ya manual: git remote add origin ... && git push -u origin main

gh secret set YT_CLIENT_ID --body "..."
gh secret set YT_CLIENT_SECRET --body "..."
gh secret set YT_REFRESH_TOKEN --body "1//..."
gh secret set IG_ACCESS_TOKEN --body "EAAX..."
gh secret set IG_USER_IDS --body "..."
gh secret set FB_PAGE_IDS --body "..."
gh secret set GOOGLE_SERVICE_ACCOUNT_JSON_B64 --body "$(base64 -w0 sa.json)"

gh variable set PLAYLIST_IDS --body "PLxxxxxxxx"
gh variable set FOLDER_REENCODED --body "<folder id>"
```

Phir GitHub → Actions → **sulbot** → **Run workflow** → `dry_run: true` → dekho chal raha hai.

---

## Kya main kar sakta hoon / nahi

| Kaam | Main | Aap |
|---|---|---|
| Code, job files, text (title/caption/tags) | ✅ | |
| Analysis (insights se brief) | ✅ | |
| OAuth "Allow" dabana | ❌ | ✅ |
| Cloud console me APIs enable | ❌ | ✅ |
| System User token banana | ❌ | ✅ |
| Error debug (error paste karo) | ✅ | |

**Sabse zaroori:** Step 1-2 karke `python doctor.py --yt` ka output paste kar do —
usme aapke channel ka naam aur playlist IDs dikh jayenge, phir main text/job files
aapke channel ke hisaab se bana dunga.

---

## Naya tareeka — bina local script (jab main file le lunga)

Agar aap `client_secret.json` **yahan chat me upload** kar dete ho, to main token
ka poora kaam chat me hi karwa dunga:

1. Main aapko ek **consent URL** dunga → aap browser me kholo → Allow
2. Page "localhost refused to connect" dikhega (normal) → **address bar ka URL copy** karke
   yahan paste kar do
3. Main usko token me badal ke `.env` de dunga — aapko kuch chalana nahi padega

CLI se hi karna ho to:
```bash
python connect_yt.py link
python connect_yt.py code "<paste kiya hua URL>"
python doctor.py --yt
```

⚠️ Chat me **refresh token / client secret** paste karna mat bhoolna ki wo
permanent credential hai — us session ke baad revoke kar sakte ho:
https://myaccount.google.com/permissions
