> ⚠️ **Purana guide.** Naya, poora, force-ssl wala: **`YT_SETUP_FORCE_SSL.md`** — wahi use karo.

# Code → refresh_token (2 command, koi library nahi)

## Kyun seedha curl

`code` ko token me badalne ke liye **client_secret chahiye**. Wo file mere paas nahi hai
(aapne upload nahi ki, aur achha hi kiya). Isliye ye command **aapke terminal me** chalegi —
secret aapke computer se bahar nahi jaata.

---

## Windows (PowerShell) — copy-paste

```powershell
curl.exe -X POST https://oauth2.googleapis.com/token `
  -d "code=PASTE_CODE_HERE" `
  -d "client_id=PASTE_CLIENT_ID" `
  -d "client_secret=PASTE_CLIENT_SECRET" `
  -d "redirect_uri=http://localhost:8080/" `
  -d "grant_type=authorization_code"
```

## Mac / Linux (bash)

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -d "code=PASTE_CODE_HERE" \
  -d "client_id=PASTE_CLIENT_ID" \
  -d "client_secret=PASTE_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/" \
  -d "grant_type=authorization_code"
```

**Kahan se kya:**

| Cheez | Kahan milegi |
|---|---|
| `code` | address bar ka URL — `code=` ke baad, `&` se pehle (poora copy karo, `4/0A...`) |
| `client_id` | `client_secret.json` me `"client_id"` ki value |
| `client_secret` | `client_secret.json` me `"client_secret"` ki value (GOCSPX-...) |
| `redirect_uri` | **8080** — jo aapke browser me dikha. Kabhi 8085 ho to wahi daalo |

---

## Response me kya dikhega

```json
{
  "access_token": "ya29.a0Af...",
  "expires_in": 3599,
  "refresh_token": "1//0g...",        <-- YE CHAHIYE
  "scope": "https://www.googleapis.com/auth/youtube.force-ssl ...",
  "token_type": "Bearer"
}
```

**`refresh_token` wali line yahan bhej do** (poora JSON bhi chalega).
`access_token` ki zaroorat nahi — wo 1 ghante me mar jaata hai.

⚠️ Ye line ek hi baar aati hai. Agar `refresh_token` **nahi** aaya → matlab app ko pehle bhi
allow kar chuke ho. Fix: https://myaccount.google.com/permissions → app remove →
naya consent link → naya code → dobara curl.

---

## Agar `redirect_uri_mismatch` aaye

Aapka browser 8080 pe gaya tha, par command me kuch aur likha hai. Dono match karne chahiye:
- browser ka URL: `http://localhost:8080/?code=...` → `redirect_uri=http://localhost:8080/`
- browser ka URL: `http://localhost:8085/?code=...` → `redirect_uri=http://localhost:8085/`

`http://localhost` (bina port) bhi Desktop client me registered hota hai, par jo browser me
dikha wahi safest hai.

---

## Local script se karna ho (secret hidden rehta hai)

```bash
python connect_yt.py code "http://localhost:8080/?code=4/0Ab..." 
```
Ye redirect apne aap detect kar leta hai, token laata hai, aur `.env` me likh deta hai.

---

## Uske baad

```bash
python doctor.py --yt
```
Channel naam + playlist IDs dikhenge. Wahi mujhe bhej do — main playlist config,
text style aur pehla job file bana dunga.
