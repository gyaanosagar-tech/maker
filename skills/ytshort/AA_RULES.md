# RULES — jo user ne bola, wahi hoga

## 1. Upload + privacy — dono user ka faisla (25 Oct 2026)
> "Aage se mere command pr krna"
> "agar mai bolu to public, private ya schedule — khud se nhi,
>  aur khud se bhi tb jb mai direction dun"

**Fail-closed:** job me `"privacy"` likhi na ho to **upload hi nahi hota.**

| Job me likho | Kya hota hai |
|---|---|
| `"privacy": "public"` | public |
| `"privacy": "private"` | private |
| `"privacy": "unlisted"` | unlisted |
| `"privacy": "scheduled"` + `"when": "2026-10-26 18:00"` | private + publishAt |
| `"privacy": "scheduled"` par `when` nahi | **BLOCKED** |
| kuch bhi nahi | **BLOCKED** |
| galat spelling | **BLOCKED** |

- Main khud se video, title, privacy, ya timing **nahi** chunta.
- Direction mile bina kuch upload nahi.

Pehla video (`-VqzsUqT_gA`) mere galti se public gaya — user ne rehne diya.
Aage aisa nahi hoga.

## 1b. GitHub bhi poochh ke (25 Oct 2026)
> "jab GitHub ki zarurt padegi tum pata kar lena aur phir mujhse zarur puchhna"

- GitHub ka use **sirf tab** jab main pehle se bata doon ki kyun zaroori hai.
- **Aur user se poochh ke hi** — chup-chaap trigger nahi.
- YouTube ke liye GitHub ki zaroorat nahi (YT ka apna scheduler hai).
- IG/FB ke liye zaroori ho sakta hai — tab poochhna.

## 2. File kaunsi, text kya — user bolega
Main sirf likhta hoon jab bolo. Frame dekh ke text likhna **suggest** kar sakta
hoon, par upload tabhi jab "haan" mile.

## 3. YouTube
- `notifySubscribers = false` — har upload pe
- Playlist: user ka diya exact ID, random nahi
- Title ≤50 chars, title me hashtag nahi (data se: 107% view wala video)

## 4. Music
Koi background music nahi. `music` key job file me nahi daalni.

## 5. Time
IST only. `when` field: `"2026-10-26 18:00"`. Grace 90 min. `when` khaali = turant.

## Rule kaise enforce hota hai
| Layer | File | Kya |
|---|---|---|
| Code default | `youtube_uploader.py` `build_body()` | privacy = private unless allow_public |
| Job gate | `bot.py` | `allow_public` sirf `confirm_public: true` se |
| Test | `tests/test_bot.py` | 3 tests — default private, explicit public, scheduled private |

Tests: **29 passed**
