# Consent link — ye kholo aur Allow karo

## 1. Ye link browser me kholo

(Us Chrome me jisme aapka YouTube channel wala Gmail login hai)

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=<CLIENT_ID_PREFIX>-h3af93rok8et3v2bprmcfdv6nqkccs7r.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.force-ssl%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyt-analytics.readonly&access_type=offline&prompt=consent&include_granted_scopes=true
```

## 2. Kya-kya dikhega

| # | Screen | Kya karo |
|---|---|---|
| 1 | Gmail chooser | **channel wala account** chuno |
| 2 | "Google hasn't verified this app" | **Advanced** → **Go to Ytshort (unsafe)** |
| 3 | Permissions: "Manage your YouTube account" + "See, edit, and permanently delete..." + "View YouTube Analytics" | **Select all** / saare tick → **Continue / Allow** |
| 4 | Page error: **"localhost refused to connect"** | ✅ **NORMAL hai** — ghabrana nahi, tab band mat karo |
| 5 | Address bar | **POORA URL copy karo** |

## 3. URL aisa dikhega

```
http://localhost:8080/?state=xxxxxxxx&code=4/0AX4XfWh...&scope=https://www.googleapis.com/auth/youtube.force-ssl+...
```

**Wahi URL yahan chat me paste kar do** — `code=4/0A...` wala part bhi chalega,
par poora URL safest hai.

## 4. Agar "localhost refused to connect" ke bajaye kuch aur dikhe

| Dikhe | Matlab |
|---|---|
| `Error 403: access_denied` | Test users me Gmail add nahi hai (Step D) |
| `Error 400: redirect_uri_mismatch` | client Desktop app nahi hai (par aapka hai ✅) |
| `invalid_client` | JSON galat (nahi hai ✅) |
| Blank page / "site can't be reached" | ✅ **yahi chahiye** — URL copy karo |
