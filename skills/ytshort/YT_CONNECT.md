> ⚠️ **Purana guide.** Naya, poora, force-ssl wala: **`YT_SETUP_FORCE_SSL.md`** — wahi use karo.

# YOUTUBE CONNECT — click by click (2026 console)

Ye guide sirf YouTube ke liye hai. Aakhir me aapke paas 3 cheezein hongi:
1. Ek **project** (jisme APIs on hain)
2. Ek **client_secret.json** (aapko download karna hai)
3. Ek **refresh token** (`will_provide.py` banayega)

⏱️ Time: 10-12 minute. Paisa: **0** (credit card nahi chahiye).

> ⚠️ Sabse pehle: **jis Gmail se aapka YouTube channel bana hai, usi se login karo.**
> Warna bot ko channel milega hi nahi.

---

## STEP 1 — Project banao (2 min)

1. Browser me kholo: **https://console.cloud.google.com/projectcreate**
   (ya console.cloud.google.com → top-left me project dropdown → **New Project**)
2. Fields:
   - **Project name**: `sulbot`
   - **Location**: `No organization` (jaisa hai waise chhod do)
3. **Create** dabao → 10-20 second wait → notification me **Select project** dabao

✅ **Check:** top bar me project ka naam `sulbot` dikhna chahiye.

---

## STEP 2 — 2 APIs enable karo (2 min)

Ye zaroori hai — API enable nahi hogi to token hone ke baad bhi "accessNotConfigured" error aayega.

**2a. YouTube Data API v3** (upload ke liye)
1. Kholo: **https://console.cloud.google.com/apis/library/youtube.googleapis.com**
2. Blue button **ENABLE** dabao
3. Wait → "API enabled" dikhega

**2b. YouTube Analytics API** (insights ke liye)
1. Kholo: **https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com**
2. **ENABLE** dabao

✅ **Check:** **https://console.cloud.google.com/apis/dashboard** pe dono APIs list me dikhni chahiye.

---

## STEP 3 — Google Auth Platform setup (3 min)

Purane guides "OAuth consent screen" bolte hain — **wo ab exist nahi karta**. Naya raasta:

1. Kholo: **https://console.cloud.google.com/auth/overview**
2. Agar likha ho **"Google Auth platform not configured yet"** → niche right me **GET STARTED** dabao
3. 4-step wizard aayega:

   **Step 1 — App Information**
   - **App name**: `sulbot`
   - **User support email**: dropdown se **apna Gmail** chuno
   - **Next**

   **Step 2 — Audience** ⭐ (yahan galti hoti hai)
   - **External** chuno (Internal grey ho sakta hai — personal Gmail pe Internal nahi milta)
   - **Next**

   **Step 3 — Contact Information**
   - **Email address**: apna Gmail dobara
   - **Next**

   **Step 4 — Finish**
   - Google ki policy ka checkbox ✅ tick karo
   - **CREATE** dabao

✅ **Check:** Overview page khulega, status me **Testing** likha hoga. Ye theek hai.

---

## STEP 4 — Apna Gmail "Test user" me add karo (30 sec)

Ye step chhoda to login pe **403 access_denied** aayega.

1. Kholo: **https://console.cloud.google.com/auth/audience**
2. **Test users** section → **ADD USERS** dabao
3. Apna Gmail address type karo → **SAVE**

✅ **Check:** list me aapka email dikhe. Max 100 allowed.

---

## STEP 5 — Desktop client banao + JSON download (2 min)

1. Kholo: **https://console.cloud.google.com/auth/clients**
2. **+ CREATE CLIENT** dabao
3. **Application type**: dropdown me → **Desktop app** ⭐ (Web application **NAHI**)
4. **Name**: `sulbot-desktop`
5. **CREATE**
6. Popup aayega — **DOWNLOAD JSON** dabao
   (agar download button na dikhe: Clients list me `sulbot-desktop` pe click → upar **Download JSON** icon)
   > Naye console me client secret sirf ek baar dikhta hai — turant download kar lo.
7. File ka naam badal ke **`client_secret.json`** rakho aur `sulbot/` folder me daal do

✅ **Check:** `sulbot/client_secret.json` file ka size ~400 bytes, andar `"installed"` key hogi.

---

## STEP 6 — Token banao (2 min) ← **yahan aapko 3 click karne hain**

Terminal me:
```bash
cd sulbot
python will_provide.py --analytics --env   # scope: youtube.force-ssl
```

Jo hoga step by step:
1. Terminal me link print hoga, **browser khulega**
2. Gmail list → **jis account pe channel hai wahi chuno**
3. Warning: **"Google hasn't verified this app"** → **Advanced** dabao → **Go to sulbot (unsafe)** dabao
   *(Ye normal hai — app aapka khud ka hai, verify karane ki zaroorat nahi)*
4. Permissions screen: **saare checkbox tick** rahne do ("Select all") — warna insights band rahega
5. **Continue / Allow** dabao
6. Browser: "The authentication flow has completed" → tab band kar do
7. Terminal me 3 lines aayengi aur `.env` me khud likh jayengi:
   ```
   YT_CLIENT_ID=xxx.apps.googleusercontent.com
   YT_CLIENT_SECRET=GOCSPX-xxx
   YT_REFRESH_TOKEN=1//xxx
   ```

> ⚠️ **7-din rule:** app Testing me hai, isliye refresh token **7 din me expire** hota hai.
> Har hafte (ya jab `invalid_grant` aaye) yehi command dobara chalao — 30 second ka kaam.
> Permanent chahiye to app ko "Publish" karna padta hai (verification chahiye), abhi zaroorat nahi.

---

## STEP 7 — Verify (30 sec)

```bash
python doctor.py --yt
```

Aisa dikhna chahiye:
```
[2] YouTube
  ✔ channel — <aapke channel ka naam> (UCxxxxxxxx)
  ✔ subscribers — 87
  ✔ videos — 12
  ✔ notifySubscribers — False (rule: False)
  ✔ playlists — 2 mili:
       PLxxxxxxxx  Bihar Vlogs
  ✔ insights scope — YouTube Analytics chal raha hai
```

Playlist ke saamne wali **ID** copy karo → `.env` me:
```
PLAYLIST_IDS=PLxxxxxxxx
```

---

## STEP 8 — Playlist (agar nahi hai)

1. **https://studio.youtube.com** kholo
2. Left menu → **Playlists** → **New playlist**
3. Naam: `Bihar Vlogs` → **Create**
4. Playlist kholo → URL dekho:
   `https://studio.youtube.com/playlist?list=PLxxxxxxxxxxxxx`
   → `PL...` wala part hi **playlist ID** hai

---

## Errors — kya matlab hai

| Screen pe kya dikha | Matlab | Fix |
|---|---|---|
| `Error 403: access_denied` | aapka Gmail Test users me nahi hai | STEP 4 dobara |
| `Google hasn't verified this app` | normal (Testing app) | **Advanced → Go to sulbot (unsafe)** |
| `invalid_grant` (terminal me) | 7 din ho gaye, token expire | `python will_provide.py --analytics --env   # scope: youtube.force-ssl` dobara |
| `redirect_uri_mismatch` | Desktop app ki jagah **Web application** client ban gaya | STEP 5 dobara, **Desktop app** chuno |
| `accessNotConfigured` | API enable nahi hui | STEP 2 dobara |
| `insufficientPermissions` / insights khaali | scope kam | `will_provide.py --analytics` se token dobara, saare checkbox tick |
| "This app is blocked" | project galat / test user nahi | STEP 1 ka project select hai? STEP 4? |

---

## Ho gaya?

`python doctor.py --yt` ka output mujhe paste kar do. Usme channel ka naam + playlist IDs
aa jayenge, phir main:
1. aapki playlist config kar dunga
2. channel ke hisaab se title/caption style bana dunga
3. pehla job file ready kar dunga — ek video chadha ke test karenge

Uske baad Instagram (Step 3 of CONNECT.md) aur Drive.
