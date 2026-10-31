# META SETUP — Instagram + Facebook

**App:** `Ytshort` · **App ID:** `1485334480129972`
**Aakhri update:** 25 Oct 2026

---

## 🟢 AB SIRF 2 KAAM BACHE HAIN

Aapne bahut kuch kar liya hai. Ab bas ye:

### Kaam 1 — `Generate token` dabao
Jis page pe **"2. Generate access tokens"** hai, wahan **`Generate token`** button
dabao. Instagram account already connect hai. Dabane pe token milega — copy karo.

### Kaam 2 — Mujhe 2 cheezein bhejo
```
App Secret:  App settings → Basic → Show
Token:       (Kaam 1 ka token)
```

**Bas. Uske baad main sab karta hoon.**

Aur koi screenshot nahi chahiye. Koi permission nahi chahiye. Kuch nahi.

---

## Aapki asli halat (jo ho chuka)

| Cheez | Status |
|---|---|
| App `Ytshort` | ✅ |
| Business portfolio `failtadka` | ✅ |
| Permissions | ✅ aapne add kar diye |
| Instagram account use case se juda | ✅ |
| `Facebook Login for Bu...` product | ✅ sidebar me hai |
| **Token** | ⬜ **bas yahi baaki** |

---

## Jo "nahi mila" — uski chinta chhodo

Aapne likha: *"wo app settings ke niche wala nahi mila"*.

**Koi baat nahi. Uske bina bhi kaam chal jaayega.**

Wo `Facebook Login for Business` ki alag configuration thi — wo sirf **resumable upload**
(hosting-free) aur **delete** ke liye chahiye thi. Pehle token lo, kaam shuru karo.
Baad me zaroorat padi to wo add kar lenge — product aapke paas already hai.

---

## Token milne ke baad kya hoga

Main ye chalaunga:
```
python meta_check.py --token <aapka token>
```

Aur aapko **exact** bataunga:

| Main kya check karunga | Kyun |
|---|---|
| Token valid hai? | warna sab bekaar |
| Login type (IGAA / EAAG) | isse pata chalega kaunsa raasta |
| **Asli me kaunsi permission mili** | jo add kiya, wo actually mila ya nahi |
| IG account + followers | trial gate (200) |
| Publish limit | aaj kitne post ho sakte hain |
| Delete possible? | permission ke hisaab se |

**Phir main aapko batata hoon:** kya kaam karega, kya nahi, aur kya karna padega.

---

## Screenshot kab chahiye

**Abhi nahi.** Aap token bhejo, main check karunga.

Agar check me kuch aisa aaya jo mujhe dekhna padega — tab **tabhi** maangunga,
aur bata dunga exactly kaunsi screen.

---

## Part A — Instagram token (aap yahan ho)

Page: **"Ytshort · Use cases · Manage messaging & content on Instagram"**

```
1. Add required messaging permissions     ✅ ho gaya (aapne kaha)
2. Generate access tokens                 ← YAHAN
3. Configure webhooks                     ⏭️ skip
```

**"2. Generate access tokens"** ke neeche **`Generate token`** / **`Generate access token`**
button hai. **Dabao.**

Popup me:
- Instagram account already juda hua hai — wahi rahega
- Permissions listed hongi — sab tick rehne do
- **Generate**

Token milega — `IGAA...` se shuru hoga. **Copy karo.**

> Ye token **1 ghante** me expire hota hai. Part D me 60 din ka banayenge.

---

## Part B — Permissions (jo add karne hain)

Aapne kaha "sara permission add kar diya" ✅

Confirm karne ke liye — ye 8 hone chahiye:
```
business_management
instagram_basic
instagram_content_publish        ← reel post
instagram_manage_contents        ← reel delete
instagram_manage_insights        ← insights
pages_show_list
pages_read_engagement
pages_manage_posts               ← FB post
```

Aur **do jo Instagram Login raaste me alag naam se hote hain:**
```
instagram_business_basic
instagram_business_content_publish
```

Aapke paas kaunsa set hai — wo **token check karne pe pata chal jaayega.**
Main `meta_check.py` chala ke batata hoon asli me kya mila.

**Abhi kuch add nahi karna. Bas token bhejo.**

---

## Part C — Facebook Page wala use case (baad me)

Ye **abhi nahi** karna. Pehle Instagram chale, phir ye.

Dashboard → `Customize the Manage everything on your Page use case` → `>`

Andar: permissions add → Page add → webhooks skip.

---

## Part D — Token 60 din ka banao (zaroori)

👉 **https://developers.facebook.com/tools/debug/accesstoken**

1. Part A ka token paste karo → **`Debug`**
2. Neeche scroll → **`Extend Access Token`**
3. **Naya token** — 60 din chalega
4. **Wahi naya token copy karo** ← ye mujhe dena hai

> Button na dikhe to — token already long-lived hai. Seedha wahi bhejo.

---

## Part E — Mujhe ye 2 cheezein bhejo

```
1. Token:       Part D ka token (IGAA... ya EAAG...)
2. App Secret:  App settings → Basic → Show
```

Bas. Uske baad main:
- `meta_check.py` chala ke asli permissions check karunga
- IG account, followers, publish limit batata hoon
- Delete possible hai ya nahi batata hoon
- `.env` + GitHub Secrets bharunga
- `meta_token.py` auto-refresh set karunga
- **Test reel tabhi** jab aap bologe

---

## Jo bilkul NAHI chahiye

| Cheez | Zaroorat |
|---|---|
| Instagram Tester role | ❌ nahi |
| App Review | ❌ nahi |
| Business Verification | ❌ nahi |
| App publish karna | ❌ nahi — `Unpublished` rehne do |
| Webhooks / Callback URL / Verify token | ❌ nahi |
| Drive / hosting | ❌ nahi |
| Ad-related use cases | ❌ nahi |

---

## Dikkat aaye to

| Dikha | Fix |
|---|---|
| `Generate token` button nahi | "Add account" pehle karo |
| `Invalid OAuth access token` | token copy adhoora hua |
| `(#10) permission` | permission add nahi hui — batao |
| Token turant expire | Part D karo |
| `Extend Access Token` nahi dikha | token already 60 din ka hai, chhod do |
