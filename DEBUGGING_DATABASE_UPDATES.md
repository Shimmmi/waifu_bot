# 🐛 Debugging Database Updates - Complete Guide

## 🎯 Problem

Stats (XP, energy, mood, loyalty) aren't updating after events, even after redeploying to Render.

## 📊 What We Added

### **Comprehensive Logging System** 🔍

We added detailed logs at **every critical point** in the data flow:

#### **1. Event Participation (menu.py)** 📝
- **BEFORE changes:** Current XP and dynamic stats
- **AFTER changes:** New values before database commit
- **AFTER commit:** Values after database refresh

#### **2. Waifu List Display (menu.py)** 📋
- XP and dynamic stats when displaying waifu list
- Shows what data is currently in database

#### **3. API Endpoint (api_server.py)** 📡
- Request received
- Database query
- Data fetched from database
- Data sent to client

---

## 🔍 How to Debug

### **Step 1: Deploy with Logging**

```bash
# Commit changes
git add .
git commit -m "Add comprehensive logging for database operations"
git push origin main
```

Render will automatically redeploy.

### **Step 2: Watch Render Logs**

1. Go to https://dashboard.render.com
2. Select your Web Service
3. Click "Logs" tab
4. Keep this window open

### **Step 3: Test Event Participation**

1. Open your bot in Telegram
2. Go to: 🎭 Вайфу → 🎲 События → 🎲 Случайное событие
3. Click "✅ Да, участвовать!"
4. Select a waifu

### **Step 4: Check Logs**

You should see in Render logs:

```
🔍 EVENT PARTICIPATION - BEFORE: Waifu wf_xxx (Chloe)
   XP: 0
   Dynamic: {'energy': 100, 'mood': 50, 'loyalty': 50, ...}

🔄 EVENT PARTICIPATION - AFTER CHANGES: Waifu wf_xxx
   XP: 0 → 30
   Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
   flag_modified: dynamic field marked as modified

💾 Committing to database...

✅ COMMITTED TO DB: Waifu wf_xxx
   XP after refresh: 30
   Dynamic after refresh: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
```

### **Step 5: View Waifu List**

1. Go to: 🎭 Вайфу → 📋 Мои вайфу → ℹ️ Детальная информация

Check logs:

```
📋 DISPLAYING WAIFU IN LIST: wf_xxx (Chloe)
   XP: 30
   Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
```

### **Step 6: Open WebApp**

1. Click on waifu button to open WebApp

Check logs:

```
📡 API REQUEST: GET /api/waifu/wf_xxx
🔍 Querying database for waifu_id: wf_xxx
✅ FETCHED FROM DB: Waifu wf_xxx (Chloe)
   XP: 30
   Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
📤 SENDING TO CLIENT:
   XP: 30
   Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
```

---

## 🔍 Diagnosis Guide

### **Scenario 1: Changes Not Saved to DB**

**Symptoms:**
- ✅ BEFORE shows old values
- ✅ AFTER CHANGES shows new values
- ❌ COMMITTED TO DB shows old values again

**Cause:** Database commit failing

**Solutions:**
1. Check PostgreSQL connection
2. Verify DATABASE_URL in Render
3. Check for database permissions issues
4. Look for error messages in logs

### **Scenario 2: Changes Saved But Not Fetched**

**Symptoms:**
- ✅ COMMITTED TO DB shows new values
- ❌ DISPLAYING WAIFU shows old values
- ❌ API FETCHED FROM DB shows old values

**Cause:** Database caching or connection pool issues

**Solutions:**
1. Check if using connection pooling
2. Verify session.refresh() is working
3. Check for stale database connections
4. Restart Render service

### **Scenario 3: Fetched But WebApp Shows Old**

**Symptoms:**
- ✅ COMMITTED TO DB shows new values
- ✅ API FETCHED FROM DB shows new values
- ❌ WebApp displays old values

**Cause:** Frontend caching

**Solutions:**
1. Close WebApp window completely
2. Reopen WebApp (forces fresh fetch)
3. Check browser console for errors
4. Clear Telegram app cache

### **Scenario 4: No Logs Appearing**

**Symptoms:**
- ❌ No logs showing up in Render

**Cause:** Logging not configured or old code still running

**Solutions:**
1. Verify deployment completed
2. Check git commit was pushed
3. Manually trigger redeploy in Render
4. Check Render is using correct branch

---

## 📊 Expected Log Flow

### **Complete Flow for Event Participation:**

```
1. User clicks event button
   ↓
2. 🔍 EVENT PARTICIPATION - BEFORE
   Shows current stats from database
   ↓
3. Calculate new stats in memory
   ↓
4. 🔄 EVENT PARTICIPATION - AFTER CHANGES
   Shows new stats before saving
   ↓
5. flag_modified(waifu, "dynamic")
   Mark field as changed
   ↓
6. 💾 Committing to database...
   session.commit() + flush()
   ↓
7. session.refresh(waifu)
   Reload from database
   ↓
8. ✅ COMMITTED TO DB
   Shows stats after database refresh
   Should match step 4!
   ↓
9. User opens waifu list
   ↓
10. 📋 DISPLAYING WAIFU IN LIST
    Shows stats from fresh database query
    Should match step 8!
    ↓
11. User opens WebApp
    ↓
12. 📡 API REQUEST
    ↓
13. 🔍 Querying database
    ↓
14. ✅ FETCHED FROM DB
    Shows stats from database
    Should match step 8!
    ↓
15. 📤 SENDING TO CLIENT
    Data sent to WebApp
    ↓
16. WebApp displays data
```

---

## 🛠️ Additional Debugging Tools

### **Check Database Directly (Neon Dashboard)**

1. Go to https://console.neon.tech
2. Select your project
3. Go to SQL Editor
4. Run query:

```sql
SELECT id, name, xp, dynamic 
FROM waifu 
WHERE name = 'Chloe'
ORDER BY created_at DESC 
LIMIT 1;
```

This shows **actual database values**.

### **Check Render Environment Variables**

1. Go to Render Dashboard → Your Service
2. Click "Environment" tab
3. Verify:
   - ✅ `DATABASE_URL` is set to Neon PostgreSQL URL
   - ✅ `BOT_TOKEN` is correct
   - ✅ No typos in variable names

### **Force Fresh Database Connection**

If you suspect stale connections, add this to `src/bot/db.py`:

```python
engine = create_engine()
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Add this
)
```

---

## 🚀 Deployment Checklist

Before testing, ensure:

- [ ] Code changes committed to git
- [ ] Changes pushed to GitHub: `git push origin main`
- [ ] Render shows "Deploy succeeded" (not just "Building")
- [ ] Render logs show bot starting: "Bot starting..."
- [ ] Render logs show: "✅ Stat restoration service started"
- [ ] No error messages in Render logs

---

## 📝 Common Issues & Solutions

### **Issue: "Database not configured" in logs**

**Solution:**
- Check `DATABASE_URL` in Render environment
- Verify it's a valid PostgreSQL URL (starts with `postgresql://`)
- Restart service after changing env vars

### **Issue: Import errors in logs**

**Solution:**
- Check all imports are correct
- Verify `requirements.txt` has all dependencies
- Redeploy after fixing

### **Issue: SQLAlchemy errors**

**Solution:**
- Check table exists: Run migration
- Verify database schema matches models
- Check PostgreSQL permissions

### **Issue: Changes save locally but not on Render**

**Solution:**
- Verify you pushed code to GitHub
- Check Render is deploying from correct branch
- Manually trigger redeploy

---

## 🎯 Success Criteria

When everything works, you should see:

1. ✅ Event participation logs show correct values
2. ✅ COMMITTED TO DB matches AFTER CHANGES
3. ✅ DISPLAYING WAIFU shows same as COMMITTED
4. ✅ API FETCHED shows same as COMMITTED
5. ✅ WebApp displays correct values
6. ✅ Stats persist after closing/reopening bot

---

## 📞 Next Steps

1. **Deploy code** to Render (git push)
2. **Watch logs** during testing
3. **Copy log output** for analysis
4. **Share logs** if issue persists

The logs will tell us **exactly** where the data is getting lost!

---

## 🔍 Example Working Logs

```
[Bot logs]
🔍 EVENT PARTICIPATION - BEFORE: Waifu wf_abc123 (Sakura)
   XP: 50
   Dynamic: {'energy': 100, 'mood': 60, 'loyalty': 55, ...}

🔄 EVENT PARTICIPATION - AFTER CHANGES: Waifu wf_abc123
   XP: 50 → 80
   Dynamic: {'energy': 80, 'mood': 65, 'loyalty': 57, ...}
   flag_modified: dynamic field marked as modified

💾 Committing to database...

✅ COMMITTED TO DB: Waifu wf_abc123
   XP after refresh: 80  ← Should match above!
   Dynamic after refresh: {'energy': 80, 'mood': 65, 'loyalty': 57, ...}

[API logs]
📡 API REQUEST: GET /api/waifu/wf_abc123
🔍 Querying database for waifu_id: wf_abc123
✅ FETCHED FROM DB: Waifu wf_abc123 (Sakura)
   XP: 80  ← Should match committed value!
   Dynamic: {'energy': 80, 'mood': 65, 'loyalty': 57, ...}
```

**If all these match → Everything works! 🎉**
**If they don't match → Logs show exactly where the problem is! 🔍**

---

**Deploy and check your logs!** They will reveal the issue! 🚀

