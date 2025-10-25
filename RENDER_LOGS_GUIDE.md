# 📊 Render Logs - What to Look For

## ✅ **Logging is Now Configured!**

I've added comprehensive logging to track database operations. Here's what you should see in Render logs after deploying.

---

## 🚀 After Deployment

### **On Bot Startup**

You should see:
```
🚀 Starting Waifu Bot...
✅ All routers included
🔄 Starting stat restoration service...
✅ Stat restoration service started
✅ Waifu Bot is ready!
📡 Polling for updates...
```

### **On API Server Startup**

You should see:
```
🌐 Starting Waifu Bot API Server...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🔍 Testing Scenarios

### **Scenario 1: Event Participation**

**What to do:**
1. Open bot in Telegram
2. Go to: 🎭 Вайфу → 🎲 События → 🎲 Случайное событие
3. Click "✅ Да, участвовать!"
4. Select a waifu

**What you should see in Render logs:**

```
2025-10-25 14:23:45 - bot.handlers.menu - INFO - 🔍 EVENT PARTICIPATION - BEFORE: Waifu wf_cfe1d04d (Chloe)
2025-10-25 14:23:45 - bot.handlers.menu - INFO -    XP: 0
2025-10-25 14:23:45 - bot.handlers.menu - INFO -    Dynamic: {'energy': 100, 'mood': 50, 'loyalty': 50, ...}

2025-10-25 14:23:45 - bot.handlers.menu - INFO - 🔄 EVENT PARTICIPATION - AFTER CHANGES: Waifu wf_cfe1d04d
2025-10-25 14:23:45 - bot.handlers.menu - INFO -    XP: 0 → 30
2025-10-25 14:23:45 - bot.handlers.menu - INFO -    Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
2025-10-25 14:23:45 - bot.handlers.menu - INFO -    flag_modified: dynamic field marked as modified

2025-10-25 14:23:45 - bot.handlers.menu - INFO - 💾 Committing to database...

2025-10-25 14:23:46 - bot.handlers.menu - INFO - ✅ COMMITTED TO DB: Waifu wf_cfe1d04d
2025-10-25 14:23:46 - bot.handlers.menu - INFO -    XP after refresh: 30
2025-10-25 14:23:46 - bot.handlers.menu - INFO -    Dynamic after refresh: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
```

**❗ If you DON'T see these logs:**
- Bot might not be using `run_bot.py`
- Check Render "Start Command" setting
- It should be: `python run_bot.py`

---

### **Scenario 2: Viewing Waifu List**

**What to do:**
1. Go to: 🎭 Вайфу → 📋 Мои вайфу → ℹ️ Детальная информация

**What you should see:**

```
2025-10-25 14:24:10 - bot.handlers.menu - INFO - 📋 DISPLAYING WAIFU IN LIST: wf_cfe1d04d (Chloe)
2025-10-25 14:24:10 - bot.handlers.menu - INFO -    XP: 30
2025-10-25 14:24:10 - bot.handlers.menu - INFO -    Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
```

---

### **Scenario 3: Opening WebApp**

**What to do:**
1. Click on any waifu button to open WebApp

**What you should see:**

```
INFO:     94.73.196.153:0 - "GET /waifu-card/wf_cfe1d04d?waifu_id=wf_cfe1d04d HTTP/1.1" 200 OK

2025-10-25 14:24:30 - __main__ - INFO - 📡 API REQUEST: GET /api/waifu/wf_cfe1d04d
2025-10-25 14:24:30 - __main__ - INFO - 🔍 Querying database for waifu_id: wf_cfe1d04d
2025-10-25 14:24:30 - __main__ - INFO - ✅ FETCHED FROM DB: Waifu wf_cfe1d04d (Chloe)
2025-10-25 14:24:30 - __main__ - INFO -    XP: 30
2025-10-25 14:24:30 - __main__ - INFO -    Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
2025-10-25 14:24:30 - __main__ - INFO - 📤 SENDING TO CLIENT:
2025-10-25 14:24:30 - __main__ - INFO -    XP: 30
2025-10-25 14:24:30 - __main__ - INFO -    Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}

INFO:     94.73.196.153:0 - "GET /api/waifu/wf_cfe1d04d HTTP/1.1" 200 OK
```

---

## 🔍 Diagnosis

### **Problem 1: No Bot Logs at All**

**Symptoms:**
- Only see API logs like: `GET /waifu-card/... 200 OK`
- No emoji logs (🔍, 🔄, ✅, etc.)

**Causes:**
1. **Render Start Command is wrong**
2. **Bot not restarted after deployment**
3. **Using old code**

**Solutions:**

#### Check Render Start Command:
1. Go to Render Dashboard
2. Click your Web Service
3. Go to "Settings" tab
4. Find "Start Command"
5. It should be: `python run_bot.py` (NOT `python src/bot/main.py`)
6. If different, change it and click "Save Changes"
7. Service will automatically restart

#### Manually Restart:
1. Go to Render Dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

---

### **Problem 2: Logs Show Old Values**

**Symptoms:**
- ✅ See logs but values don't change
- "BEFORE" and "AFTER" are the same
- "COMMITTED" shows old values

**Possible causes:**
1. Code not deployed correctly
2. Old Python files cached
3. Need to clear Render build cache

**Solution:**
1. Go to Render Dashboard
2. Settings → "Clear Build Cache"
3. Manual Deploy → "Clear build cache & deploy"

---

### **Problem 3: Values Change But Don't Persist**

**Symptoms:**
- ✅ "AFTER CHANGES" shows new values
- ❌ "COMMITTED TO DB" shows old values
- OR
- ✅ "COMMITTED" shows new values
- ❌ "FETCHED FROM DB" (later) shows old values

**Cause:** Database connection or transaction issue

**Solutions:**
1. Check DATABASE_URL is correct
2. Check Neon database is accessible
3. Check no firewall blocking connections
4. Try restarting Neon database

---

## 🛠️ Render Dashboard Checklist

Before testing, verify in Render:

### **Environment Tab:**
- [ ] `DATABASE_URL` set to Neon PostgreSQL URL
- [ ] `BOT_TOKEN` set correctly
- [ ] `API_URL` set correctly (if needed)

### **Settings Tab:**
- [ ] Start Command: `python run_bot.py`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Python Version: 3.11 or higher

### **Logs Tab:**
- [ ] Shows "🚀 Starting Waifu Bot..."
- [ ] Shows "✅ Stat restoration service started"
- [ ] Shows "📡 Polling for updates..."
- [ ] No error messages

---

## 📋 Quick Test Checklist

After deployment:

1. **Check startup logs** ✅
   - Bot started
   - Restoration service started
   - No errors

2. **Test event** ✅
   - Participate in event
   - Check logs show BEFORE/AFTER/COMMITTED
   - All values should change

3. **View waifu list** ✅
   - Open waifu list
   - Check logs show DISPLAYING with updated values

4. **Open WebApp** ✅
   - Click waifu button
   - Check logs show API REQUEST and FETCHED FROM DB
   - Values should match COMMITTED values

5. **Check WebApp display** ✅
   - WebApp shows correct XP, energy, etc.
   - Matches values in logs

---

## 🆘 If Still No Logs

If you still don't see custom logs after deploying:

1. **Check you pushed to GitHub:**
   ```bash
   git status  # Should show "nothing to commit"
   git log -1  # Should show your latest commit
   ```

2. **Check Render deployed latest:**
   - Dashboard → "Events" tab
   - Should show recent "Deploy succeeded"
   - Click on it to see deployment details

3. **Check Render is running:**
   - Dashboard → Top right
   - Should show green "Running"
   - If not, click "Manual Deploy"

4. **Try forcing redeploy:**
   - Settings → "Clear Build Cache"
   - Manual Deploy → "Clear build cache & deploy"

---

## 📞 What to Share

If issues persist, share:

1. **Render Start Command** (from Settings)
2. **Render Environment Variables** (names only, not values)
3. **Full logs from "Events" tab** (when participating in event)
4. **Any error messages**

This will help diagnose exactly where the issue is!

---

**Deploy now and check your logs!** 🚀

