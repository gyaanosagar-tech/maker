# PLAN v3 — idea final (code isse banega)

v2 + aapke naye 3 points (insights/analysis, YT notification OFF + playlist rule, IG trial/normal).
Code abhi nahi bana raha — ye padh ke "ok" bolo, phir banata hoon.

---

## 0. Pehle ek sach — "tumhare paas sara access hoga"

Aisa nahi hai, aur isse design badalta hai:

| Kya | Main kar sakta hoon? |
|---|---|
| Aapke channel ka private analytics khud dekhna | ❌ nahi. Mujhe aapke YT/IG ka login/insights access nahi hai |
| Bot se aapka analytics nikalna (token se) | ✅ haan — par **bot nikaalega**, main nahi. Bot CSV banayega, main usko chat me padh ke analyse karunga |
| Dusre channels ka public data (views, titles, thumbnails, upload time) | ✅ research se, par andaza + public info tak seemit |
| Dusre channels ka private data (retention, CTR, watch time) | ❌ kabhi nahi, kisi ke paas nahi hota |

Isliye sach wala flow ye hai: **bot data laata hai → main analyse karta hoon → brief banata hoon →
bot us brief se upload karta hai.** Ye loop hi reach badhata hai, "copy paste title" nahi.

---

## 1. Analysis engine (naya hissa)

### Level 1 — Competitor research (main karta hoon, chat me)
Aap bolenge: "Bihar/Patna ke top 10 shorts channels" ya link doge. Main dekhunga:
- Top videos ke **title patterns** (numbers, curiosity gap, emoji, length)
- **Hook** — pehle 3 second me kya hota hai
- **Length** (15-25s vs 40-60s), upload **time** aur **cadence**
- **Hashtag** pattern, description ka pehla line
Output: `analysis/brief_<niche>.md` — "ise karo, ye mat karo" wali concrete list.

### Level 2 — Aapka apna data (bot laayega)
Bot token se ye nikaal sakta hai:
- YT: views, likes, comments, average view duration, CTR, impressions (Analytics API — alag scope)
- IG: reach, plays, likes, saves, shares, follows (insights permission)
Ye `analysis/performance.csv` me aayega. Aap wahi file mujhe dikha doge → main batata hoon
**kaunsa video kyun chala**, aur agle 10 video ka plan bana dunga.

### Level 3 — A/B test (jo actually kaam karta hai)
Ek hi video ke 2 title/caption variants — 3-4 video pe test. Data se pata chalega
aapke audience ko kya kheenchta hai. Guess nahi, measurement.

> Sach: YouTube Shorts me **title/tags ka asar kam** hai. Reach marta hai hook + retention +
> repeat views se. Tags lagbhag bekaar hain (chhota ranking signal). Isliye main text pe
> zyada nahi, **hook + first frame + length** pe focus karunga — wahan asli fayda hai.

---

## 2. YouTube — aapke 2 rules

### (a) Subscriber notification OFF ✅ ho sakta hai
`notifySubscribers=false` — upload karte waqt query param me jaata hai.
⚠️ 2 baatein:
- Default `true` hota hai, isliye code me **hamesha** `false` bhejna padega.
- Upload ke baad API se **badla nahi ja sakta** (sirf Studio se, aur wo bhi public karne se pehle).
  Matlab galti se true chala gaya to wapas nahi hoga — isliye ye param har upload pe lock rahega
  aur log me dikhega.

### (b) Playlist rule — aapko ek cheez deni hogi
Aapka rule: "random playlist nahi, exact playlist".
Mujhe chahiye: **playlist ka naam ya ID** (YT Studio → Playlist → URL me `list=PLxxxx`).
- Ek hi fixed playlist me har video → `PLAYLIST_ID` config me
- Ya har niche/format ki alag playlist (aap bologe kaunsi kis me jaaye)
- Playlist na ho to bot `playlists.insert` se bana sakta hai (naam aapka diya hua)
- ⚠️ Quota: video upload 1600 units + playlist me daalna 50 units = **1650 units/video**.
  10,000/day limit me **~6 video/day** (wahi jo pehle bola tha).

---

## 3. Instagram / Facebook — trial + normal

Aapka sawaal: "5 video me 3 normal 2 trial, fir Insta khud normal kar deti hai n?"

**Aadha sahi, aadha galat:**

| Aapka assumption | Sach |
|---|---|
| 3 normal + 2 trial ka mix rakh sakte hain | ✅ haan — **par ratio hum tay karte hain**, Insta nahi |
| Insta khud decide karti hai kaunsa trial hoga | ❌ nahi. Hum har reel pe trial flag lagate hain (`trial_params`) |
| Trial reel baad me "normal" ho jaati hai | ✅ haan — `graduation_strategy` se: `SS_PERFORMANCE` = perform kare to Insta **khud followers ko dikha deti hai**; `MANUAL` = aap app me karke graduate karoge |

Yaani 5 video = 3 normal + 2 trial **hum** rakhenge (config me ratio), aur un 2 trial me se
jo achha chalega use Insta khud graduate kar degi (agar `SS_PERFORMANCE` chuna).

⚠️ 3 practical baatein:
- Trial reel sirf **200+ followers** (kuch jagah 1000+) wale professional account pe chalta hai —
  naye account pe fail hoga. Aapka count batao.
- Trial reel **sirf non-followers** ko jaati hai, followers ko nahi.
- Trial ki daily cap Meta ne officially nahi batayi (reports: ~20/24h, kuch kehte hain ~5).
  Cap cross hua to trial block ho jaata hai (normal reels chalte rehte hain).

**Default jo main rakhunga (badal sakte ho):** 60/40 — 3 normal, 2 trial (5 me se).
Ratio `config` me ek number hai, aap "aaj se 50/50" bologe to badal dunga.

> Facebook pe trial ka concept hi nahi hai — wahan sab normal page video.

---

## 4. Baaki sab v2 jaisa (final)

- **Trigger:** aap bologe — ek file ya bulk ("5 file schedule me laga do")
- **Time:** IST. Aap doge → wahi. Na do → turant. (Koi 30-min gap, koi fixed hour list nahi)
- **IG timing:** bot cron se, sahi slot pe (minute-exact nahi — ±10-15 min, jaisa pehle bataya)
- **Text:** main likhunga (title, description, tags, caption, hashtags) — Gemini/Whisper nahi
- **Composite:** `Master_Log.csv` + `analysis/performance.csv`

## 5. sul.md se nahi banega

`MIN_GAP_MINUTES` · `BEST_HOURS_IST` · `02_Guidelines_PDF` · Whisper · Gemini ·
"YT 100/day" (galat — asli ~6) · Drive auto-scan (default OFF)

## 6. Ab bas ye 4 jawab chahiye

1. **Playlist:** naam/ID do — ya bot ko banana hai? Ek hi sab ke liye ya format-wise?
2. **Trial ratio:** 60/40 (3 normal + 2 trial) theek hai? Graduation `SS_PERFORMANCE` ya `MANUAL`?
3. **IG followers:** kitne hain? (trial chalu hoga ya nahi)
4. **Analysis:** pehle Level-1 (competitor brief) karun, phir code? Ya dono saath?

`ok` + ye jawab → main code likhna shuru karta hoon (bot.py, playlist, notify=false,
trial split, cron, logs, setup README).
