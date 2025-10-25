# ⚡ Quick Deployment Reference

## 🎯 What Was Fixed
- ✅ WebApp API URL (was hardcoded to wrong domain)
- ✅ Error handling (now shows real errors instead of test data)
- ✅ Logging (now shows full stack traces)

## 🚀 Deploy in 3 Steps

### 1. Commit & Push
```bash
git add .
git commit -m "Fix: WebApp API URL and error handling"
git push origin main
```

### 2. Render Auto-Deploys
Wait 1-2 minutes for Render to detect and deploy the new commit.
Monitor at: https://dashboard.render.com/

### 3. Test
1. Open bot in Telegram
2. Summon a waifu (or use existing)
3. Participate in an event
4. Click "Подробно" button
5. **Verify WebApp shows real data** (not "Тестовая вайфу")

## ✅ Success Checklist

- [ ] Bot shows event results (XP, energy changes)
- [ ] WebApp opens without errors
- [ ] WebApp shows correct waifu name
- [ ] WebApp shows correct XP value
- [ ] WebApp shows correct energy value
- [ ] No "Тестовая вайфу" or test data visible
- [ ] Refreshing WebApp shows updated stats

## 🔍 If Something Goes Wrong

### WebApp shows error message
✅ **This is GOOD!** It means it's trying to fetch real data now.

Check Render logs for:
```
❌ API ERROR: <error type>: <detailed message>
```

Common fixes:
- Verify `DATABASE_URL` is set in Render environment variables
- Check if the waifu ID exists in the database
- Look at the full stack trace in logs

### WebApp still shows "Тестовая вайфу"
- Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
- Clear browser cache
- Restart Telegram app
- Verify Render deployment completed successfully

### 500 errors in logs but no detailed error message
- Re-deploy to ensure latest code is running
- Check that `src/bot/api_server.py` has `exc_info=True` in the error handler

## 📊 Monitoring

### Render Logs to Watch For

**Good signs:**
```
📡 API REQUEST: GET /api/waifu/wf_xxxxx
🔍 Querying database for waifu_id: wf_xxxxx
✅ FETCHED FROM DB: Waifu wf_xxxxx (Name)
📤 SENDING TO CLIENT:
   XP: 19
   Dynamic: {'energy': 78, ...}
```

**Bad signs:**
```
❌ API ERROR: ...
```
If you see this, read the full error message - it will tell you exactly what's wrong.

## 🔧 Files Changed

- `src/bot/api_server.py` - Better error logging
- `webapp/waifu-card.html` - Fixed API URL, removed test data fallback

## 📞 Need Help?

1. Check `VISUAL_SUMMARY.md` for detailed explanation
2. Check `DEPLOY_API_FIX.md` for troubleshooting
3. Look at Render logs for specific error messages

---

**That's it! The fix is deployed and ready to test.** 🎉

