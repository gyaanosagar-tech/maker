> ⚠️ **Purana guide.** Naya, poora, force-ssl wala: **`YT_SETUP_FORCE_SSL.md`** — wahi use karo.

# Screenshot wale process me kya missing hai

Aapke 2 screenshots (left = Steps 1-5, right = Steps 5-7) ke hisaab se.
**Process sahi hai** — bas 6 cheezein add karni hain, warna token banega par kaam nahi karega.

---

## ✅ Jo screenshots me sahi hai
- Project banana (Step 1)
- YouTube Data API v3 enable (Step 2)
- Consent screen External + app name (Step 3)
- Desktop app client + JSON download (Step 4-5)
- Code paste karke refresh_token (Step 6)

---

## ❌ 1. Test users add karna — PURA STEP MISSING

Screenshots me Step 3 kehta hai "3 baar Continue dabate jao". Us beech me **Test users** ka page
aata hai (kuch accounts pe scopes ke baad, kuch pe pehle).

**Kya karna:** OAuth consent screen me **Test users** section → **+ ADD USERS** →
apna Gmail → **SAVE**.

**Na karo to:** Allow dabane ke baad `Error 403: access_denied` — token banega hi nahi.

---

## ❌ 2. YouTube Analytics API — missing

Step 2 me sirf Data API hai. Insights ke liye Analytics API bhi chahiye.

👉 https://console.cloud.google.com/apis/library/youtubeanalytics.googleapis.com → **ENABLE**

---

## ❌ 3. Scope — `youtube` chahiye, sirf `youtube.upload` nahi

Ye **sabse important** hai, aur mere code me bhi galti thi (ab fix kar di).

`youtube.upload` scope se video upload hoti hai, par:
- **playlist me add nahi hoti** → `403 insufficientPermissions`
- **purane video update nahi hote** (backfill) → `403`

`playlistItems.insert` aur `videos.update` ke liye
**`https://www.googleapis.com/auth/youtube.force-ssl`** scope chahiye.

Ab code yehi maangta hai:
```python
SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",    # upload + playlist + update
    "https://www.googleapis.com/auth/yt-analytics.readonly", # insights
]
```

Consent screen pe Allow karte waqt **saare checkbox tick** kar dena — warna playlist silently
fail hogi.

---

## ⚠️ 4. Audit ka rule — uploads private ho sakti hain

28 July 2020 ke baad bane **unaudited project** ke uploads YouTube **private** lock kar sakta hai,
chahe aap `privacyStatus: public` bhejo. Video upload ho jaati hai, par studio me private rehti hai.

Abhi ke liye:
- **`private` + `publishAt` (scheduled) wala flow isse affect nahi hota** — wo waise bhi private hi
  rehta hai aur YouTube khud time pe public karta hai. Aapka main use-case yahi hai. ✅
- **Turant public** karna ho to audit chahiye: YouTube API Services compliance audit form.

Maine code me check lagaya hai — upload ke baad asli privacy padh ke warn karta hai:
```
[youtube] !! <id>: public maanga, YouTube ne PRIVATE rakha — project ka API audit pending ho sakta hai
```
To aapko pata chal jayega, chupchaap private me nahi rahegi.

---

## ❌ 5. Playlist — missing (aapne khud bola)

ITNI cheezein chahiye:
1. **Consent screen me `youtube.force-ssl` scope** (point 3) — warna add hi nahi hoga
2. **Playlist ID** — `PL` se shuru
3. `.env` me `PLAYLIST_IDS=PLxxxx`

Playlist ID kahan se: YouTube Studio → Playlists → playlist kholo → URL me `list=PLxxxx`.

**Naam galat/nahi mila to:** bot **random playlist me nahi daalega** (aapka rule) — skip karega
aur log me warning dega.

---

## ⚠️ 6. Quota — mera purana number galat tha

Maine pehle bola tha "6 uploads/day". **Ye ab galat hai.**

Oct 2026 docs ke hisaab se:
- `videos.insert` ka **apna bucket: 100 uploads/day** (June 2026 se)
- baaki sab (playlist add = 50 units) 10,000 units/day
- ek din me 100 upload + 100 playlist add = 5,000 units → theek hai

Code ab **100/day** guard rakhta hai. (Purana "100/day" maine galat bola tha — ab wo sach hai.)

---

## Ek aur chhoti cheez

**7. App "Testing" me = refresh token 7 din me expire.**
Har hafte `will_provide.py --analytics --env` dobara chalana padega (30 second).
Permanent nahi chahiye to consent screen publish karna padta hai (verification maangta hai) —
abhi zaroorat nahi.

---

## Final checklist — screenshot process + ye 6

| # | Kya | Kahan |
|---|---|---|
| 1 | Project | console.cloud.google.com |
| 2 | YouTube Data API v3 enable | APIs → Library |
| 3 | **YouTube Analytics API enable** | APIs → Library |
| 4 | Consent screen: External + app name | Auth Platform |
| 5 | **Test users → apna Gmail add** | Auth Platform → Audience |
| 6 | **Data access me `youtube.force-ssl` scope** (ya Allow pe sab tick) | Auth Platform → Data access |
| 7 | Desktop app client → JSON download | Auth Platform → Clients |
| 8 | Token banao (code paste) | terminal |
| 9 | **`.env` me `PLAYLIST_IDS=PLxxxx`** | local |
| 10 | `python doctor.py --yt` | terminal |

Baaki sab screenshot wale process me hai hi.
