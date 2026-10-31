# DRIVE CONNECT — click by click (service account)

**Kyun service account (aur YouTube wala token nahi):**
- YouTube token me Drive ka access nahi hai (aur usko Drive dene ka matlab pura Drive kholna)
- Service account ko **sirf wahi folder dikhta hai** jo aap share karte ho — baaki Drive bilkul
  invisible
- Aap kabhi bhi sharing hata sakte ho → bot ka Drive access turant khatam

**Time:** 12-15 min · **Paisa:** 0

**End me:** bot aapke diye Drive link se video download kar sakta hai + IG ke liye chhoti copy
upload kar sakta hai.

---

## A. Google Drive API enable karo (1 min)

Isi project me (jo `Ytshort` hai):

👉 **https://console.cloud.google.com/apis/library/drive.googleapis.com**

→ Blue button **ENABLE** dabao → wait

✅ **Check:** 👉 https://console.cloud.google.com/apis/dashboard — list me
**Google Drive API** dikhni chahiye (YouTube wali 2 ke saath).

---

## B. Service account banao (2 min)

**B1.** 👉 **https://console.cloud.google.com/iam-admin/serviceaccounts**

**B2.** Upar **+ CREATE SERVICE ACCOUNT** dabao

**B3.** Page 1 — Service account details:

| Field | Kya daalo |
|---|---|
| **Service account name** | `sulbot-drive` |
| **Service account ID** | auto bhar jayega (`sulbot-drive`) |
| Description | `Drive access for upload bot` |

→ **CREATE AND CONTINUE**

**B4.** Page 2 — "Grant this service account access to project"

→ **kuch mat chuno** (role khaali chhod do). Hamare kaam me project-level role ki zaroorat nahi —
Drive access folder sharing se milta hai, role se nahi.

→ **CONTINUE**

**B5.** Page 3 — "Grant users access"

→ **kuch mat bharna** → **DONE**

✅ **Check:** list me `sulbot-drive@<GCP_PROJECT>.iam.gserviceaccount.com` dikhe.

**B6.** Us email ko **copy** kar lo — aage chahiye.

---

## C. Key (JSON) download karo (1 min)

**C1.** List me `sulbot-drive` pe **click** karo

**C2.** Upar tab **KEYS** dabao

**C3.** **ADD KEY** → **Create new key**

**C4.** **JSON** chuno → **CREATE**

**C5.** File khud download ho jaayegi (`<GCP_PROJECT>-xxxxxxxx.json`)

**C6.** Uska naam badal do → **`sa.json`**

> ⚠️ Ye key **dobara download nahi hoti**. Kho gayi to nayi banani padegi (ADD KEY se).

**C7.** File kholo (Notepad) — aisa dikhna chahiye:

```json
{
  "type": "service_account",
  "project_id": "<GCP_PROJECT>",
  "client_email": "sulbot-drive@<GCP_PROJECT>.iam.gserviceaccount.com",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  ...
}
```

✅ `"type": "service_account"` hona chahiye (OAuth client nahi).

---

## D. Drive me 2 folder banao + share karo (5 min)

### D1. Folder 1 — `Videos` (yahan aapke videos rahenge)

1. 👉 **https://drive.google.com** kholo
2. **+ New** → **Folder** → naam: `Videos` → **Create**
3. Folder kholo → **Share** dabao (ya right-click → Share)
4. **People** box me wo email paste karo jo B6 me copy kiya:
   `sulbot-drive@<GCP_PROJECT>.iam.gserviceaccount.com`
5. Permission: **Viewer** ⭐ (padh/download kar sakta hai, delete/modify nahi)
6. **"Notify people"** ka tick **hata do** (wo service account hai, email padhta nahi)
7. **Share** / **Send** dabao
8. Ab folder ka **link copy** karo: `https://drive.google.com/drive/folders/XXXXXXXX`

### D2. Folder 2 — `IG_Reencoded` (IG ke chhoti copies yahan banengi)

1. **+ New** → **Folder** → naam: `IG_Reencoded` → **Create**
2. **Share** → wahi SA email paste karo
3. Permission: **Editor** ⭐ (upload karne ke liye Editor chahiye)
4. "Notify people" tick hatao → **Share**
5. Link copy karo

> **Kyun Editor:** Instagram ko public `video_url` chahiye. Bot re-encode karke (5-6 MB)
> yahan upload karta hai, public link banata hai, IG ko deta hai — aur publish ke baad file
> delete kar deta hai (quota saaf rahe).

✅ **Check:** dono folder ki sharing me `sulbot-drive@...` dikhe —
`Videos` me **Viewer**, `IG_Reencoded` me **Editor**.

---

## E. Mujhe ye 3 cheezein do

Chat me bhejo:

1. **`sa.json`** file (upload)
2. **`Videos`** folder ka link — `https://drive.google.com/drive/folders/...`
3. **`IG_Reencoded`** folder ka link

Main:
- `sa.json` → `sulbot/sa.json` me rakhta hoon
- folder links se **folder ID** nikalta hoon → `.env` me daalta hoon
- ek chhoti test file upload karke **Editor** permission verify karta hoon
- `Videos` folder me jo files hain wo list karta hoon (agar koi hain)

---

## F. Verification (main karunga)

```bash
python doctor.py --drive
```

Iska output aisa aana chahiye:

```
[4] Drive
  ✔ service account — sulbot-drive@<GCP_PROJECT>.iam.gserviceaccount.com
  ✔ FOLDER_REENCODED — IG_Reencoded
  ✔ Videos folder — 3 files
```

---

## G. Errors

| Dikhe | Matlab | Fix |
|---|---|---|
| `File not found` / `403` | folder SA ko share nahi hua | **Step D** dobara |
| `The user does not have sufficient permissions` | Viewer diya, Editor chahiye | `IG_Reencoded` pe **Editor** |
| `storage quota exceeded` | SA ki apni storage bhar gayi | purane copies delete karo (bot khud karta hai) |
| `Drive API has not been used...` | API enable nahi | **Step A** |
| `Invalid grant: account not found` | SA email galat copy hua | **B6** se dobara copy |
| `invalid_client` / `"type": "authorized_user"` | galat JSON (OAuth ka hai) | **Step C** dobara — service account key |

---

## H. Ye kyun behtar hai (aapke sawaal ka jawab)

| Tarika | Aapko kya karna padta | Bot ko kitna dikhta | Risk |
|---|---|---|---|
| **Service account** (ye guide) | 2 folder share | sirf wo 2 folder | kam — baaki Drive invisible |
| YouTube token me Drive scope | Allow pe sab tick | **pura Drive** | zyada — token leak = pura Drive |

Aur: Drive ka access **kabhi bhi band** kar sakte ho —
`Videos` folder → Share → SA email → **Remove**, ya Drive me `sulbot-drive` ke saare shares hata do.
Bot ka Drive access turant khatam, YouTube wala kaam chalta rahega.
