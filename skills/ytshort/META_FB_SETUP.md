# FACEBOOK PAGE SETUP

**App:** `Ytshort` · **App ID:** `1485334480129972`
**Kya chahiye:** ek naya token (`EAAG...`) — Instagram wala token Page pe kaam nahi karta

---

## Kyun naya token

```
IG token (IGAA...)  →  graph.instagram.com  →  sirf Instagram
FB token (EAAG...)  →  graph.facebook.com  →  Facebook Page + Instagram
```

Aapka IG token Page access **nahi** kar sakta. Maine test kiya:
```
me/accounts  →  "Tried accessing nonexisting field (accounts)"
```

---

## Aapke paas already kya hai (screenshot se)

Sidebar me jo dikhta hai:
```
dashboard
Required actions
Methods of use
Facebook Login for Bu...
Testing
Publish      [Unpublished]
App settings
App roles
Alert inbox
```

Dashboard pe 2 use cases:
```
Customize the Manage messaging & content on Instagram use case    ✅ ho gaya
Customize the Manage everything on your Page use case             ⬜ abhi karna hai
```

---

## ⚠️ Pehle ye samajh lo

**"Manage Pages" wale page pe `Generate token` button hota hi NAHI.**

| Screen | Kya karta hai |
|---|---|
| `Use cases > Customize` → `Permissions and features` | **permissions add** karta hai |
| `Graph API Explorer` (alag website) | **token deta hai** |

Instagram me `Generate token` button tha kyunki wahan Instagram ka apna login flow hai.
**Facebook Page ka token sirf Graph API Explorer se milta hai.**

---

## Step 1 — Permissions add karo (jo screen abhi khuli hai)

Screen: **`Use cases > Customize`** → dropdown me **`Manage Pages`** →
tab **`Permissions and features`**

Yahan permissions ki list hai, har ek ke saamne **`+ Add`** button.

**Ye 3 dhoondh ke `+ Add` dabao:**

| Permission | Kaam | Dhoondhne ka tareeka |
|---|---|---|
| **`pages_manage_posts`** | **video post karna** | upar search box me type karo |
| `pages_show_list` | Page list | search |
| `pages_read_engagement` | Page padhna | search |

Optional (chaho to):
```
pages_manage_engagement
pages_read_user_content
```

**Add hone ka proof:** Status column me **`Ready for testing`** dikhega
(jaise `business_management` me pehle se dikh raha hai).

> Upar **search box** hai. 3 permission dhoondhne ke liye scroll nahi karna —
> naam type karo, turant aayega.

**Iske baad ye page band kar do.** Yahan token nahi milega.

---

## Step 2 — Page wala account check

Agar use case page pe **"Add account"** button dikhe to dabao aur apna
**Facebook Page** select karo.
Na dikhe to koi baat nahi — Graph API Explorer me Page chunne ka option aayega.

---

## Step 3 — Token nikaalo (Graph API Explorer)

👉 **https://developers.facebook.com/tools/explorer**

**Ye app dashboard se alag website hai.** Yahan token milta hai.

1. Upar daayein **`Meta App`** dropdown → **`Ytshort`**
2. **`User or Page`** dropdown → **`Get Page Access Token`**
3. **`Permissions`** me tick karo:
```
pages_show_list
pages_read_engagement
pages_manage_posts
pages_manage_engagement      (optional)
```
4. **`Generate Access Token`** dabao
5. Facebook login → **Continue**
6. Aapke Pages ki list → **Page select karo** → **Continue**

Token box me `EAAG...` se shuru hone wala lamba token. **Copy karo.**

> **`Get Page Access Token` nahi dikha?**
> Pehle `Add a Permission` me `pages_manage_posts` add karo,
> phir dropdown dobara dekho.

---

## Step 4 — 60 din ka banao

👉 **https://developers.facebook.com/tools/debug/accesstoken**

1. Token paste karo → **`Debug`**
2. Neeche scroll → **`Extend Access Token`**
3. **Naya token** milega — 60 din
4. **Wahi naya token copy karo** ← ye mujhe dena hai

> Button na dikhe to token already long-lived hai. Seedha wahi bhejo.

---

## Step 5 — Mujhe bhejo

```
FB Token:  EAAG...   (Step 4 ka)
```

Bas ek cheez. App Secret ki zaroorat **nahi** (Instagram wala kaam kar gaya bina uske).

---

## Step 6 — Main kya karunga

```
python meta_fb_check.py --token EAAG...
```

Ye check karega:
- Page mila? kaunsa? admin ho?
- Permissions asli me kaunse hain
- token kitne din ka
- video post ho sakta hai?
- schedule ho sakta hai?

Phir `.env` + GitHub Secrets update karunga.

---

## Facebook me kya-kya milega

| Cheez | Status |
|---|---|
| Video post | ✅ |
| **Native schedule** | ✅ **10 min se 6 mahine tak** (cron nahi chahiye!) |
| Delete | ✅ `DELETE /{video-id}` |
| Page insights | ✅ |
| Reels | 🔸 post hoga, par **schedule support iffy** — test karenge |

**Sabse achhi baat:** Facebook pe **cron ki zaroorat nahi.**
`published=false` + `scheduled_publish_time` bhej do — FB khud us time live kar dega.
Aap so rahe ho, main bhi nahi hoon — post ho jaayegi.

---

## Jo NAHI chahiye

| | Zaroorat |
|---|---|
| App Review | ❌ nahi |
| Business Verification | ❌ nahi |
| App publish karna | ❌ nahi (`Unpublished` rehne do) |
| Webhooks | ❌ nahi |
| Naya app banana | ❌ nahi — wahi `Ytshort` |
| App Secret | ❌ nahi |

---

## Dikkat aaye to

| Dikha | Fix |
|---|---|
| `Get Page Access Token` dropdown me nahi | Step 2 pehle karo |
| "koi Page nahi" | aap us Page ke admin ho? |
| `(#10) permission` | `pages_manage_posts` add nahi hui |
| IG token se try kiya | `IGAA...` Page pe kaam nahi karega — `EAAG...` chahiye |
