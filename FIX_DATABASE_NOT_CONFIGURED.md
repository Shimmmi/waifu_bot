# 🔧 Fix: "Database not configured" Error

## 🐛 The Problem

WebApp was showing:
```
❌ Ошибка
Произошла ошибка при загрузке данных вайфу: HTTP error! status: 500, 
body: {"detail":"Database not configured"}
```

Logs showed:
```
INFO: GET /api/waifu/wf_aa7cdf45 HTTP/1.1 500 Internal Server Error
```

## 🔍 Root Cause

In `src/bot/api_server.py`, the imports were using relative paths:
```python
from db import SessionLocal  # ❌ Wrong!
from models import Waifu     # ❌ Wrong!
```

But when uvicorn loads the FastAPI app via `from bot.api_server import app`, the module context is the `bot` package. The relative imports failed silently, setting `SessionLocal = None`, which triggered the "Database not configured" error.

## ✅ The Fix

Changed to absolute imports:
```python
from bot.db import SessionLocal        # ✅ Correct!
from bot.models import Waifu          # ✅ Correct!
from bot.services.waifu_generator import calculate_waifu_power  # ✅ Correct!
```

Also added:
- ✅ Better logging to show import success/failure
- ✅ Path debugging information
- ✅ Full exception stack traces for import errors

## 🚀 Deploy

```bash
git add src/bot/api_server.py
git commit -m "Fix: Database imports in API server"
git push origin main
```

Render will auto-deploy (1-2 minutes).

## ✅ Test

After deployment:

1. Open bot in Telegram
2. Select a waifu
3. Click "Подробно" button
4. **Expected:** WebApp shows real waifu data (name, XP, energy, etc.)
5. **Not expected:** Error message or test data

## 📊 What to Look For in Logs

**Good signs (after fix):**
```
🌐 Starting Waifu Bot API Server...
   Current directory: /path/to/src/bot/
   Python path: ['/path/to/src', ...]
✅ Database modules imported successfully
   SessionLocal: <function SessionLocal at 0x...>
   Waifu model: <class 'bot.models.Waifu'>
```

**Then when WebApp is opened:**
```
📡 API REQUEST: GET /api/waifu/wf_aa7cdf45
🔍 Querying database for waifu_id: wf_aa7cdf45
✅ FETCHED FROM DB: Waifu wf_aa7cdf45 (Hye-jin)
   XP: 19
   Dynamic: {'energy': 95, 'mood': 100, 'loyalty': 57}
📤 SENDING TO CLIENT:
   XP: 19
   Dynamic: {'energy': 95, 'mood': 100, 'loyalty': 57}
INFO: GET /api/waifu/wf_aa7cdf45 HTTP/1.1 200 OK  ← Success!
```

**Bad signs (if still broken):**
```
❌ Failed to import database modules: <error details>
```
If you see this, check the full error message in logs.

---

**This should be the final fix needed for the WebApp!** 🎉

