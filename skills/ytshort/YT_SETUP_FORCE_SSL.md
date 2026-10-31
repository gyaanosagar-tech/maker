# YOUTUBE CONNECT — poora guide (force-ssl scope)

**Ye file purani `TOKEN_STEPS.md` ki jagah use karo.** (Wo `auth/youtube` wali thi.)

- Time: **15-20 min** (aapke ~18 click)
- Paisa: **0**
- Scope: **`youtube.force-ssl` + `yt-analytics.readonly`**
- Aakhir me: YouTube connected → channel naam, subscribers, saari playlists, aur `.env` ready

---

## 0. End me kya milega

| Cheez | Kaun dega |
|---|---|
| `YT_CLIENT_ID` | JSON se |
| `YT_CLIENT_SECRET` | JSON se |
| `YT_REFRESH_TOKEN` | **main** (main token exchange karunga) |
| `YT_CHANNEL_ID` | **main** (token se channel lookup) |
| `PLAYLIST_IDS` | **main** (aapki playlists nikaal ke) |
| `.env` file | **main** bana dunga |
| Channel ka verify | **main** — naam, subscribers, video count |
| Insights scope test | **main** — Analytics chal raha hai ya nahi |

Aap sirf: console me click + Allow + ek URL paste.

---

## 0.1 Shuru karne se pehle — 3 cheezein

1. **Usi Chrome profile / Gmail se karo jispe YouTube channel hai.** Doosre Gmail se karoge to bot ko channel hi nahi milega.
2. **Chrome ke alawa kuch mat kholo** jo same Google account use kare — Allow ke waqt galat account select ho jaata hai.
3. **3 tab** khol lo:
   - Tab 1: `console.cloud.google.com`
   - Tab 2: `studio.youtube.com` (channel ka naam + playlist dekhne ke liye)
   - Tab 3: `youtube.com` (channel confirm karne ke liye)

---

## A. Project banao (2 min)

**A1.** 👉 **https://console.cloud.google.com/projectcreate**

| Field | Kya daalo |
|---|---|
| **Project name** | `Ytshort` |
| **Location** | `No organization` (jaisa hai waise chhod do) |
| Organization field na dikhe to koi baat nahi | |

**A2.** **CREATE** dabao → 15-20 second wait (page band mat karo)

**A3.** Upar right me notification aayega → **SELECT PROJECT** dabao
(na aaye to top bar ke project dropdown → `Ytshort` chuno)

✅ **Check:** page ke top-left me, project dropdown me **`Ytshort`** likha dikhe.

> Project ID Google khud banayega (jaise `ytshort-473921`) — usse koi farak nahi padta,
> code usko use nahi karta.

---

## B. Do APIs enable karo (2 min)

API enable nahi ki to token ban jaayega par **har call `accessNotConfigured`** dega.

### B1. YouTube Data API v3
👉 **https://console.cloud.google.com/apis/library/youtube.googleapis.com**

1. Page khulega "YouTube Data API v3" ka
2. Blue button **ENABLE** dabao
3. 5-10 sec → "API enabled" dikhega

### B2. YouTube Analytics API
👉 **https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com**

1. **ENABLE** dabao

✅ **Check:** 👉 **https://console.cloud.google.com/apis/dashboard**
List me dono dikhni chahiye:
- YouTube Data API v3
- YouTube Analytics API

> Analytics API kyun: `bot.py insights` isi se views/retention laata hai.
> Na enable karo to upload chalega, par insights khaali rahega.

---

## C. OAuth consent screen (3 min)

> Google ne isko rename kar diya hai — ab **"Google Auth Platform"** kehta hai.
> Kuch accounts pe purana sidebar (`APIs & Services → OAuth consent screen`) hi dikhta hai.
> **Dono ka result ek hi hai**, labels alag.

**C1.** 👉 **https://console.cloud.google.com/auth/overview**

- Agar likha ho **"Google Auth platform not configured yet"** → niche right me **GET STARTED** dabao
- Agar form seedha khula ho → C2 ke values bhar do

**C2.** Wizard ke 4 page (ek-ek karke):

**Page 1 — App Information**
| Field | Kya daalo |
|---|---|
| **App name** | `Ytshort` |
| **User support email** | dropdown se **apna Gmail** |

→ **NEXT**

**Page 2 — Audience** ⭐ yahan galti hoti hai
- **External** chuno
  (Internal grey ho sakta hai — personal Gmail pe Internal option nahi milta)
→ **NEXT**

**Page 3 — Contact Information**
- **Email address**: apna Gmail dobara
→ **NEXT**

**Page 4 — Finish**
- Google ki user-data policy ka **checkbox ✅ tick** karo
→ **CREATE** dabao

✅ **Check:** Overview page khulega, **Publishing status: Testing** dikhega. Ye theek hai.

> **Purana UI wala raasta** (agar classic sidebar dikhe):
> `APIs & Services → OAuth consent screen → External → CREATE → App name + Email →
> Save and Continue → (Scopes) Save and Continue → (Test users) → Save and Continue →
> Back to Dashboard`

---

## D. Test user add karo — ⚠️ yahi step sabse zyada miss hota hai

Ye chhoot gaya to Allow dabane pe **`Error 403: access_denied`** aayega aur token banega hi nahi.

**D1.** 👉 **https://console.cloud.google.com/auth/audience**
(purane UI me: OAuth consent screen → **Test users** section)

**D2.** **Test users** ke neeche **+ ADD USERS** dabao

**D3.** Apna Gmail address type karo (poora, `something@gmail.com`) → **SAVE**

✅ **Check:** list me aapka email dikhe.
(Max 100 users allowed — ek hi kaafi hai.)

---

## E. Scopes add karo — `youtube.force-ssl` (2 min)

### E1. Scopes page kholo

👉 **https://console.cloud.google.com/auth/scopes**
(purane UI me: OAuth consent screen → **Scopes** / "Data access")

### E2. Do scopes add karo

**ADD OR REMOVE SCOPES** dabao → search box me ek-ek karke ye do daalo aur tick karo:

```
https://www.googleapis.com/auth/youtube.force-ssl
https://www.googleapis.com/auth/yt-analytics.readonly
```

> Search me `youtube.force-ssl` type karo → "YouTube Data API v3" ke andar milega.
> Na mile to **"Manually add scopes"** wale box me poori URL paste kar do.

**E3.** Neeche **UPDATE** dabao → phir **SAVE**

✅ **Check:** dono scopes list me dikhein, **status: Testing** ke saath.

### E4. In scopes me kya hota hai

| Scope | Kya deta hai | Kyun chahiye |
|---|---|---|
| `youtube.force-ssl` | upload, playlist me add, video update, comments/captions/ratings | **Upload + playlist + backfill — teeno isi se** |
| `yt-analytics.readonly` | channel ki analytics padhna | `bot.py insights` |

### E5. Allow page pe kya likha aayega

```
Ytshort wants to:
  ✔ Manage your YouTube account
  ✔ See, edit, and permanently delete your YouTube videos, ratings, comments and captions
  ✔ View YouTube Analytics reports for your YouTube content
```

**"permanently delete" padh ke ghabrana nahi.** Ye `youtube.force-ssl` ka official Google
label hai — jo bhi tool playlist me video add karta hai ya comments padhta hai, usko yehi
scope chahiye, isliye ye wording aati hai. Scope ke andar se "delete hata do" aisa option
Google deta hi nahi — poora scope milta hai ya nahi milta.

### E6. Is code me delete hota hai kya? — nahi

Maine code grep se verify kiya:

| Endpoint | Kaam | Use hota hai? |
|---|---|---|
| `videos.insert` | video upload | ✅ |
| `playlistItems.insert` | playlist me add | ✅ |
| `videos.update` | title/description update (backfill) | ✅ |
| `channels.list`, `playlists.list`, `videos.list` | padhna | ✅ |
| `videos.delete` | video delete | ❌ **code me nahi hai** |
| `playlistItems.delete` | playlist se hatana | ❌ **code me nahi hai** |

Matlab: **delete ka koi endpoint hi nahi likha gaya.**

### E7. Access kabhi bhi band kar sakte ho

👉 **https://myaccount.google.com/permissions** → `Ytshort` → **Remove access**

Turant refresh token mar jaayega. Channel ko kuch nahi hoga, koi video delete nahi hogi.

### E8. ⚠️ Ye 3 scope **mat** add karna

`youtube.force-ssl` ke saath ye maangna **overlapping scopes** hai — Google reject kar sakta hai
aur verification me dikkat aati hai:

```
❌ https://www.googleapis.com/auth/youtube
❌ https://www.googleapis.com/auth/youtube.upload
❌ https://www.googleapis.com/auth/youtube.readonly
```

`force-ssl` in sab ko already cover karta hai. **Bas do scopes rakho** (E2 wale).

---

## F. Playlist — channel pe (2 min)

**Kyun:** aapka rule hai "random playlist nahi, exact playlist". Bot ko playlist **ID** chahiye.

### Raasta 1 — Studio se banao (recommended)

1. 👉 **https://studio.youtube.com** kholo
2. Left menu → **Playlists**
3. Upar right → **+ New playlist**
4. **Title**: `Bihar Vlogs` (ya jo naam aap chahte ho)
5. **Visibility**: **Public**
6. **CREATE**
7. Playlist kholo → address bar dekho:

```
https://studio.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxx
                                        ↑ yahi playlist ID hai
```

**PL se shuru hone wala part copy kar lo** — mujhe baad me bas naam batana hai, ID main khud
nikaal lunga. Par rakh lo, kaam aayegi.

### Raasta 2 — bot hi bana de

Playlist banane ka mann nahi? Koi dikkat nahi:
- Token milne ke baad main `playlists.insert` se **aapke diye naam se** playlist bana dunga
- ID khud `.env` me daal dunga
- Bas naam batao — jaise `Bihar Vlogs`

### Raasta 3 — ek hi playlist hai

to kuch nahi karna, main wahi default set kar dunga.

> ⚠️ Playlist **Public** rakho. Private playlist me add ho sakti hai, par viewers ko dikhegi nahi.

---

## G. Desktop OAuth client + JSON (2 min)

**G1.** 👉 **https://console.cloud.google.com/auth/clients**
(purane UI me: **APIs & Services → Credentials → + CREATE CREDENTIALS → OAuth client ID**)

**G2.** Upar **+ CREATE CLIENT** dabao (purane UI me **+ CREATE CREDENTIALS**)

**G3.** Form bharo:

| Field | Kya chuno |
|---|---|
| **Application type** | **Desktop app** ⭐ |
| **Name** | `Ytshort Desktop` |

→ **CREATE**

> ⚠️ **Web application NAHI** chunna. Web application me redirect URI daalna padta hai aur
> hamara flow (localhost) fail ho jaata hai → `redirect_uri_mismatch`.

**G4.** Popup aayega: "OAuth client created" → **DOWNLOAD JSON** dabao

Na dikhe to:
- **Clients** list me `Ytshort Desktop` pe click karo
- Upar right me **Download JSON** icon

**G5.** File ka naam badal do → **`client_secret.json`**

> ⚠️ Client secret **sirf ek baar** dikhta hai (naye console me hashed hai). Turant download
> kar lo. Kho gaya to naya client banana padega.

✅ **Check:** file kholo (Notepad me), andar aisa dikhna chahiye:

```json
{
  "installed": {
    "client_id": "1234567890-abc.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxxxxxxxxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

**`"installed"`** likha ho — agar `"web"` likha hai to galat client hai (Web application bana diya).

---

## H. JSON mujhe do (chat me upload)

**H1.** `client_secret.json` yahan chat me **upload kar do**.

**H2.** Main andar se nikaal lunga:
- `client_id`
- `client_secret`

**H3.** File kahan rakhni hai (aapke computer pe): `sulbot/client_secret.json`

### 🔒 Security — saaf baat

- JSON chat me upload karne ka matlab: `client_secret` yahan visible hoga
- Refresh token bhi main yahan dikhaunga (`.env` me)
- **Kaam hone ke baad revoke kar sakte ho:** https://myaccount.google.com/permissions → `Ytshort` → Remove access
- Ya console me client delete karke naya bana lo — bot phir bhi chalega, bas naya token lena padega
- **`.env` kabhi GitHub pe commit mat karna** — `.gitignore` me already hai

Agar chat me share nahi karna, to H ke bajaye ye chalao (secret aapke computer pe rahega):

```bash
cd sulbot
python connect_yt.py link
# link khulega -> Allow -> address bar ka URL copy
python connect_yt.py code "http://localhost:8080/?code=4/0A..."
python doctor.py --yt
```

---

## I. Consent — aapke 5 click (2 min)

Main aapko ek link dunga (aapke client_id se bana hua). Wo kholo:

| Step | Screen pe kya | Aap kya karo |
|---|---|---|
| **I1** | Gmail account chooser | **jis account pe channel hai** wahi chuno |
| **I2** | "Google hasn't verified this app" | **Advanced** dabao → **Go to Ytshort (unsafe)** |
| **I3** | Permissions list (Manage YouTube + Analytics) | **Select all** / saare checkbox ✅ tick |
| **I4** | **Continue / Allow** | dabao |
| **I5** | Browser me error: **"localhost refused to connect"** ya blank page | **ye NORMAL hai.** Daro mat, tab band mat karo |
| **I6** | Address bar me URL | **POORA URL copy karo** |

URL aisa dikhega:

```
http://localhost:8080/?state=xxxxxxxx&code=4/0AX4XfWh...&scope=https://www.googleapis.com/auth/youtube.force-ssl+...
```

**I7.** Wahi URL yahan paste kar do.
(Bas `code=4/0A...` wala part bhi chalega, par poora URL safest hai — usse redirect URI bhi
auto-detect ho jaata hai.)

### I2 pe "unsafe" kyun likha hai

Kyunki app **Testing** mode me hai (Google-verified nahi). Ye aapka khud ka app hai, isliye
verification ki zaroorat nahi. "unsafe" ka matlab sirf itna hai ki Google ne is app ko review
nahi kiya — code aapke saamne hai, aap dekh sakte ho.

---

## J. Mera kaam (aapko kuch nahi karna)

Aap URL bhejte ho, main ye karta hoon:

1. **Token exchange** — `code` → `refresh_token`, Google ke token endpoint se
2. **Channel lookup** — naam, channel ID, subscribers, video count
3. **Saari playlists** — naam + ID ki list (`playlists.list`)
4. **Playlist decide** — jo aapne bola, ya jo ek hi hai, ya naya banata hoon (`playlists.insert`)
5. **Insights test** — `yt-analytics` call chala ke dekhta hoon scope chal raha hai
6. **`.env` likhta hoon**:

```env
YT_CLIENT_ID=1234567890-abc.apps.googleusercontent.com
YT_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxx
YT_REFRESH_TOKEN=1//0g...
YT_CHANNEL_ID=UCxxxxxxxxxxxxxxxx
PLAYLIST_IDS=PLxxxxxxxxxxxxxxxx
NOTIFY_SUBSCRIBERS=false
```

7. **Aapko report deta hoon:**

```
✔ Channel: <naam> (UCxxxx) — 87 subscribers, 12 videos
✔ Playlists: 2 mili
     PLxxxx  Bihar Vlogs   <-- default set
     PLyyyy  Shorts
✔ Insights: YouTube Analytics chal raha hai
✔ .env ready
```

Bas — **YouTube connected.** 🎉

---

## K. Pehla test upload (5 min)

Ab pipeline test karenge — sirf YouTube, ek local clip se.

### K1. Ek chhota clip ready rakho
Koi bhi `.mp4` — 5-10 second ka bhi chalega. Path note kar lo.

### K2. Preview (kuch upload nahi hoga)

```bash
cd sulbot
python bot.py upload "/path/clip.mp4" --job jobs/example_single.json --platforms youtube --offline
```

Output me dikhega: title, description, tags, playlist, `yt_notify_subscribers: false`.
Kuch galat lage to job file badal lo.

### K3. Asli upload (scheduled — safe)

```bash
python bot.py upload "/path/clip.mp4" --job jobs/example_single.json \
  --platforms youtube --at "in 2h" --publish
```

Kya hoga:
- Video upload hogi → **private** rahegi
- `publishAt` = 2 ghante baad → YouTube khud public karega
- Playlist me add hogi
- Subscribers ko notification **nahi** jaayega (`notifySubscribers=false`)
- Log: `state/Master_Log.csv`

### K4. Verify — YouTube Studio

👉 **https://studio.youtube.com** → **Content** → video dikhegi, status **Scheduled**

Check karo:
- ✅ Playlist me hai?
- ✅ Scheduled time sahi hai?
- ✅ Notification gaya nahi?

### K5. Agar kuch galat ho

| Problem | Wajah | Fix |
|---|---|---|
| `403 insufficientPermissions` playlist pe | scope kam | Step E dobara + naya token |
| Playlist me nahi daali, par upload ho gayi | playlist naam/ID nahi mili | log me `playlist lookup fail` dekho, `PLAYLIST_IDS` check karo |
| Video public maanga, private rahi | project audit pending | scheduled flow use karo (safe hai) |
| `invalid_grant` | 7 din / code reuse | J section dekho (naya token) |

---

## L. Uske baad — baaki phases

| Phase | Kya | Time | Guide |
|---|---|---|---|
| **3** | **Drive connect** — service account + folder share | 15 min | bolna, bana dunga |
| **4** | **Instagram + FB** — System User token | 20 min | bolna, bana dunga |
| **5** | **GitHub** — repo + secrets + hourly cron | 10 min | `python setup_github.py` |

GitHub wala aapke haath se hi hoga (connector is session me nahi hai), par script saara kaam
kar deti hai — `.env` se secrets khud utha ke daalti hai.

---

## M. 7 din baad — token expiry (ye normal hai)

App **Testing** me hai, isliye refresh token **7 din** me expire hota hai.
Pehchan: error `invalid_grant` ya "Token has been expired or revoked".

**Fix (2 min, har 6-7 din):**
1. Mujhe bolo "token refresh karo" — main naya consent link dunga
2. Aap Allow → URL copy → paste
3. Main naya refresh token `.env` + GitHub secret me update kar dunga

**Permanent chahiye?** Consent screen ko **Publish** karna padta hai (Google verification
maangta hai, 2-6 hafte). Aapke case me zaroorat nahi — 7-din wala loop chal jaayega.

---

## N. Limits jo code khud sambhalta hai

| Limit | Value | Code kya karta hai |
|---|---|---|
| Upload quota | `videos.insert` ka apna bucket **100 uploads/day** (June 2026 se) | 100 pe saaf error |
| Baaki API | 10,000 units/day (playlist add = 50 units) | ~200 playlist add/day |
| `publishAt` | kam se kam ~15 min future, UTC | 20 min lead rakhta hai; late ho to turant public |
| `publishAt` rule | sirf `privacyStatus: private` ke saath chalta hai | code hamesha private bhejta hai |
| Video size | max 256 GB, `video/*` | — |
| Title | 100 char | auto-truncate |
| Description | 5000 char | auto-truncate |
| Tags | ~500 char total, 15 tags | auto-limit |
| Shorts | ≤ 3 min (ab 3 min tak) | aapki file pe depend |
| Notification | default **true** | code **false** bhejta hai, har upload pe |

---

## O. Error → seedha matlab

| Screen / terminal pe | Matlab | Fix |
|---|---|---|
| `Error 403: access_denied` | Gmail Test users me nahi | **Step D** |
| `Error 400: redirect_uri_mismatch` | **Web application** client bana diya | **Step G** dobara — Desktop app |
| `invalid_client` | JSON galat / purana / delete ho gaya | naya client + naya JSON (G) |
| `invalid_grant` | code ek baar chala, ya 7 din ho gaye | naya consent link (M) |
| `invalid_request: Missing required parameter: code` | URL galat copy hua | URL dobara copy karo (I6) |
| Allow page pe YouTube scope hi nahi | scopes add nahi hue | **Step E** |
| `accessNotConfigured` | API enable nahi | **Step B** |
| `insufficientPermissions` (403) playlist pe | `youtube` scope nahi mila | **Step E** + Allow pe Select all → naya token |
| `quotaExceeded` | 100 upload ya 10k units khatam | kal tak wait (midnight PT reset) |
| Upload hui par private | project audit pending | scheduled flow use karo |
| `playlistNotFound` | playlist ID galat / private hai | Step F dobara |

---

## P. Final checklist (tick karte jao)

- [ ] **A** — Project `Ytshort` bana, SELECT PROJECT kiya
- [ ] **B1** — YouTube Data API v3 → ENABLE
- [ ] **B2** — YouTube Analytics API → ENABLE
- [ ] **C** — Consent: App name `Ytshort`, **External**, email, policy tick → CREATE
- [ ] **D** — Test users me apna Gmail **ADD** + SAVE
- [ ] **E2-E3** — Scopes me `youtube.force-ssl` + `yt-analytics.readonly` → UPDATE → SAVE
- [ ] **E8** — `youtube` / `youtube.upload` / `youtube.readonly` **add nahi kiye**
- [ ] **F** — Playlist bana li (ya bot ko banana hai — naam bataya)
- [ ] **G3** — Client: **Desktop app**, naam `Ytshort Desktop`
- [ ] **G4-G5** — JSON download, naam `client_secret.json`, andar `"installed"` hai
- [ ] **H** — JSON chat me upload kar diya
- [ ] **I** — Allow kiya, address bar ka URL copy kiya, paste kar diya
- [ ] **J** — Main `.env` + channel + playlists de chuka
- [ ] **K** — Pehla test upload, Studio me verify
- [ ] **L** — Aage: Drive → IG/FB → GitHub

---

## Q. FAQ

**Delete ho sakti hai kya meri videos?**
Scope me technically delete ka option hai (label me "permanently delete" likha hai). Par **code me
delete ka endpoint hi nahi hai** — maine grep se verify kiya. Aur access kabhi bhi revoke kar
sakte ho (E7).

**Kya koi aur access kar sakta hai mere channel ko?**
Nahi. Ye token **aapke Google account** me bana hai, sirf is app ke liye. Kisi ke saath share
nahi hota. `.env` kisi ko na do.

**Kitna time lagta hai?**
Setup 15-20 min. Uske baad har video ka kaam: aap bologe → main text + job file → ek command.

**Paisa lagta hai?**
Nahi. YouTube Data API free hai (quota ke andar). Google Cloud me billing card nahi chahiye.

**Ek hi baar sab karna hai?**
Setup ek baar. Token har 7 din me renew (2 min). Upload baar baar.

**Purani `TOKEN_STEPS.md` ka kya karun?**
Is file (`YT_SETUP_FORCE_SSL.md`) se replace kar do — ye poora aur updated hai.
