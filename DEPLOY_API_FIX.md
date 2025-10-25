# 🔧 API & WebApp Fix - Deployment Guide

## 📋 Summary of Issues Found

### Issue 1: Stats ARE Updating ✅
**GOOD NEWS:** The logs confirm that stats are updating correctly in the database!

```
2025-10-25 10:34:55 - bot.handlers.menu - INFO - 🔄 EVENT PARTICIPATION - AFTER CHANGES
   XP: 0 → 19 ✅
   Dynamic: {'energy': 78, 'mood': 100, 'loyalty': 57} ✅
2025-10-25 10:34:55 - sqlalchemy.engine.Engine - INFO - UPDATE waifu SET xp=19, dynamic=... ✅
2025-10-25 10:34:55 - sqlalchemy.engine.Engine - INFO - COMMIT ✅
```

**Stat restoration is also working** - energy is being restored every minute!

### Issue 2: WebApp API Error ❌
The WebApp was throwing `500 Internal Server Error` when trying to fetch waifu data.

**Root Cause:**
1. **Hardcoded wrong URL** - The WebApp HTML had this line:
   ```javascript
   const apiUrl = `https://waifu-bot-webapp.onrender.com/api/waifu/${waifuId}`;
   ```
   But your actual service URL is `https://shimmirpgbot.ru`!

2. **Fallback to test data** - When the API failed, the WebApp silently fell back to showing test data instead of the real error.

3. **Missing error logging** - The API server wasn't logging the full exception details with stack traces.

## 🛠️ Changes Made

### 1. Fixed API Server (`src/bot/api_server.py`)
- ✅ Added `exc_info=True` to log full exception stack traces
- ✅ Fixed `created_at` serialization (added null check)
- ✅ Better error handling for HTTP exceptions

### 2. Fixed WebApp HTML (`webapp/waifu-card.html`)
- ✅ Changed from hardcoded URL to **relative URL** `/api/waifu/${waifuId}`
  - This means the API call will automatically use the same domain as the WebApp (your service URL)
- ✅ Removed fallback to test data
- ✅ Added better error logging (shows actual API response)
- ✅ Shows proper error messages to the user instead of silently failing

## 📦 Deployment Steps

### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix: API URL in WebApp and improve error logging"
git push origin main
```

### Step 2: Render Will Auto-Deploy
Your Render service (`waifu-bot-webapp`) should automatically redeploy when it detects the new commit.

### Step 3: Monitor Logs
After deployment, watch the logs:
```
https://dashboard.render.com/web/YOUR_SERVICE_ID/logs
```

You should now see:
- ✅ Proper API requests with waifu IDs
- ✅ Data fetched from database
- ✅ If any errors occur, you'll see **full stack traces** instead of just "500 Internal Server Error"

### Step 4: Test the WebApp
1. Open the bot in Telegram
2. Summon a waifu
3. Participate in an event
4. Click "Подробно" to open the WebApp card

**Expected behavior:**
- WebApp should show the correct waifu data (name, XP, energy, etc.)
- XP and stats should match what you see in the bot
- No more "Тестовая вайфу" (test waifu)

## 🔍 Debugging New Errors

If you still see errors after deploying, the logs will now show much more detail:

```
❌ API ERROR: <ErrorType>: <Detailed error message>
Traceback (most recent call last):
  ... full stack trace ...
```

Common issues to check:
1. **Database connection** - Is `DATABASE_URL` set correctly in Render environment variables?
2. **Waifu not found** - Does the waifu ID exist in the database?
3. **JSON serialization** - Are all fields in the `Waifu` model serializable?

## 📊 How to Verify Everything is Working

### Test 1: Stats Update
```
1. Open bot → /start
2. Click "🎁 Ежедневная награда" (daily reward)
3. Click "🃏 Мои вайфу" (my waifus)
4. Select a waifu → "🎯 События" (events)
5. Participate in an event
6. Check the bot message - should show:
   - ⚡ Энергия: -20
   - 😊 Настроение: +5
   - 💝 Лояльность: +2
   - 🏆 Получен опыт: +X
7. Click "Подробно" to open the waifu card
8. Verify XP and stats match!
```

### Test 2: Stat Restoration
```
1. Wait 1-2 minutes
2. Open waifu card again
3. Energy should have increased by 1-2 points
```

### Test 3: WebApp Loading
```
1. Open waifu card
2. Check browser console (if on desktop):
   - Should see "Fetching from: /api/waifu/wf_XXXXX"
   - Should see successful data fetch
   - NO "test waifu" or "тестовая вайфу"
```

## ✅ Success Criteria

You'll know everything is working when:
- ✅ Stats (XP, energy, mood, loyalty) update after events
- ✅ Stats persist between bot sessions
- ✅ WebApp shows actual waifu data (not test data)
- ✅ WebApp updates when you refresh after events
- ✅ Energy restores automatically every minute
- ✅ All data matches between bot messages and WebApp

## 🚨 If You Still See "Test Waifu"

If the WebApp still shows test data after deploying:
1. **Hard refresh the WebApp** - The browser might be caching the old HTML
   - On desktop: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - On mobile: Close and reopen Telegram
2. **Check Render deployment status** - Make sure the new commit was deployed
3. **Check the logs** - Look for the detailed error messages we added

## 📝 Next Steps

After confirming everything works:
1. ✅ Test all event types
2. ✅ Test with multiple waifus
3. ✅ Verify stat restoration over time
4. ✅ Test WebApp on both mobile and desktop
5. ✅ Clean up any test data in the database if needed

---

## 🎉 Summary

The core functionality was already working! The database updates were happening correctly. The only issue was the WebApp couldn't display the data because:
- It was calling the wrong API URL
- It was silently falling back to test data

These issues are now fixed. Your bot should work perfectly after deploying these changes! 🚀

