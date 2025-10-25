# 🚀 Final Deployment Steps

## ✅ **Your Setup is Perfect!**

You have **ONE service** (`waifu-bot-webapp.onrender.com`) that will run:
- ✅ Telegram Bot (polling)
- ✅ FastAPI Server (WebApp + API endpoints)
- ✅ Static files (WebApp HTML/JS/CSS)
- ✅ All connected to one Neon database

---

## 📋 **Pre-Deployment Checklist**

### **1. Render Environment Variables**

Make sure these are set in `waifu-bot-webapp` service:

| Variable | Value | Status |
|----------|-------|--------|
| `BOT_TOKEN` | Your Telegram bot token | ✅ You have |
| `DATABASE_URL` | Your Neon PostgreSQL URL | ✅ You have |
| `REDIS_URL` | `redis://...` | ✅ You have |
| `WEBAPP_URL` | `https://waifu-bot-webapp.onrender.com` | ✅ You have |

### **2. Database Tables**

Make sure you've created the tables in Neon (see `SETUP_NEON_DATABASE.md`):

Run these SQL scripts in Neon SQL Editor:
- ✅ Script 1: Basic tables (users, waifus, etc.)
- ✅ Script 2: Waifu table + events

Verify with:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should show: `users`, `waifu`, `waifus`, `events`, etc.

---

## 🚀 **Deployment Steps**

### **Step 1: Commit Changes**

```bash
git add run_bot.py
git commit -m "Add FastAPI server to run alongside bot"
git push origin main
```

### **Step 2: Wait for Deployment**

Render will automatically deploy (2-3 minutes).

Watch in: Dashboard → `waifu-bot-webapp` → Logs tab

### **Step 3: Check Logs**

After deployment, you should see:

```
✅ Starting FastAPI server on port 10000
   WebApp will be available at: http://0.0.0.0:10000/
   API endpoints at: http://0.0.0.0:10000/api/waifu/{id}

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000

🚀 Starting Waifu Bot...
✅ All routers included
🔄 Starting stat restoration service...
✅ Stat restoration service started
✅ Waifu Bot is ready!
📡 Polling for updates...
```

**If you see all these ✅ - SUCCESS!**

---

## 🧪 **Testing**

### **Test 1: Bot Responds**

1. Open Telegram bot
2. Send `/start`
3. Bot should respond with menu

✅ **Works?** → Bot is running!

### **Test 2: WebApp Loads**

1. In bot, go to: 🎭 Вайфу → 📋 Мои вайфу
2. If you have no waifus, summon one first
3. Click: ℹ️ Детальная информация
4. Click on a waifu button

**WebApp should open showing:**
- Waifu name
- Stats (HP, ATK, etc.)
- XP progress bar
- Energy, Mood, Loyalty

✅ **Shows YOUR waifu?** → WebApp working!  
❌ **Shows test waifu?** → API not connecting (see troubleshooting)

### **Test 3: API Endpoint**

Open in browser:
```
https://waifu-bot-webapp.onrender.com/health
```

Should show: `{"status":"ok","message":"Waifu Bot API is running"}`

✅ **Shows this?** → API is running!

### **Test 4: Stats Update**

1. Participate in an event
2. Check waifu stats before
3. Complete event
4. Check waifu stats after

**XP, Energy, Mood should change!**

Check Render logs - should show:
```
🔍 EVENT PARTICIPATION - BEFORE: Waifu wf_xxx
   XP: 0
🔄 EVENT PARTICIPATION - AFTER CHANGES: 
   XP: 0 → 30
✅ COMMITTED TO DB:
   XP after refresh: 30
```

---

## 🔍 **Troubleshooting**

### **Issue: Port Timeout**

**Logs show:**
```
No open ports detected
```

**Solution:**
- The new code opens port 10000 via FastAPI server
- Make sure deployment completed successfully
- Check `PORT` environment variable in Render (should be auto-set)

---

### **Issue: WebApp Shows Test Data**

**Symptoms:**
- WebApp opens but shows wrong waifu
- Always shows same test waifu

**Check:**

1. **Database Connection:**
   ```
   Open: https://waifu-bot-webapp.onrender.com/api/waifu/wf_xxx
   Replace wf_xxx with a real waifu ID from your bot
   ```
   
   Should return JSON with your waifu data.
   
   If shows error or wrong data → DATABASE_URL issue

2. **Check Logs:**
   Look for:
   ```
   📡 API REQUEST: GET /api/waifu/wf_xxx
   ✅ FETCHED FROM DB: Waifu wf_xxx (Name)
   ```
   
   If not seeing these → API server not running

---

### **Issue: "Relation waifu does not exist"**

**Logs show:**
```
Error: relation "waifu" does not exist
```

**Solution:**
Run the SQL scripts in Neon! See `SETUP_NEON_DATABASE.md`

---

### **Issue: FastAPI Not Starting**

**Logs show bot starting but no FastAPI logs:**

**Check:**
1. Is `uvicorn` in requirements.txt? ✅ (already there)
2. Does `bot.api_server` import correctly?
3. Any import errors in logs?

**Fix:**
Check for import errors:
```python
# Test locally:
python -c "from bot.api_server import app; print('OK')"
```

---

## 📊 **Expected Architecture**

After deployment:

```
waifu-bot-webapp.onrender.com (Single Service)
├── Port 10000
│   ├── FastAPI Server
│   │   ├── GET / → WebApp HTML
│   │   ├── GET /waifu-card/{id} → WebApp HTML
│   │   ├── GET /api/waifu/{id} → JSON data
│   │   └── GET /health → Health check
│   │
│   └── Telegram Bot (polling)
│       ├── Handlers (menu, events, etc.)
│       └── Stat restoration service
│
└── Database: Neon PostgreSQL
    ├── users table
    ├── waifu table
    ├── events table
    └── All other tables
```

---

## ✅ **Success Criteria**

After deployment, verify:

- [ ] Render logs show: "✅ Starting FastAPI server on port 10000"
- [ ] Render logs show: "✅ Waifu Bot is ready!"
- [ ] No "port timeout" errors
- [ ] No "relation waifu does not exist" errors
- [ ] Bot responds to `/start` in Telegram
- [ ] WebApp opens when clicking waifu buttons
- [ ] WebApp shows YOUR waifus (not test data)
- [ ] Stats update after events
- [ ] Logs show database operations

---

## 🎯 **Deploy Now!**

```bash
# 1. Commit the changes
git add run_bot.py
git commit -m "Add FastAPI server alongside bot"
git push origin main

# 2. Watch Render logs
# Go to: https://dashboard.render.com
# Click: waifu-bot-webapp
# Click: Logs tab

# 3. Wait for deployment (2-3 min)

# 4. Test in Telegram!
```

---

## 📞 **If Issues Persist**

Share:
1. **Full Render logs** (from deployment)
2. **Test results** (which tests passed/failed)
3. **Browser console** (F12) when opening WebApp

This will help diagnose the exact issue!

---

**Deploy now and everything should work!** 🎉

