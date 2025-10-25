# 🔄 Stat Restoration & Database Update Guide

## 📋 Overview

This guide explains the automatic stat restoration system and how database changes are properly saved and reflected in the WebApp.

## 🎯 What Was Fixed

### ✅ **1. Database Updates Are Now Saved Correctly**

Previously, changes to waifu stats (energy, mood, loyalty, XP) weren't being saved to the database properly. Now:

- **XP changes** are immediately saved to the database
- **Dynamic stats** (energy, mood, loyalty) are properly tracked with `flag_modified()`
- **Database commits** are explicitly flushed to ensure data persistence
- **Session refresh** pulls the latest data after commit

### ✅ **2. Automatic Energy Restoration**

A background service now runs **every minute** to restore energy for all waifus:

- **+1 Energy per minute** (up to max 100)
- **Runs automatically** in the background
- **Timestamps tracked** to calculate restoration accurately
- **Graceful shutdown** when bot stops

### ✅ **3. WebApp Always Shows Current Data**

When you open a waifu card in WebApp:
- **Fresh data** is pulled from database
- **All stats** reflect latest changes
- **Energy restoration** is calculated and displayed
- **XP progress** shows correct values

## 🔧 Technical Implementation

### **Database Schema**

```sql
-- Waifu table has a dynamic JSONB field that stores:
{
  "energy": 80,           -- Current energy (0-100)
  "mood": 55,             -- Current mood (0-100)
  "loyalty": 52,          -- Current loyalty (0-100)
  "last_restore": "2025-10-25T12:34:56"  -- Last restoration timestamp
}
```

### **Stat Restoration Service**

Located in: `src/bot/services/stat_restoration.py`

**Key Features:**
- Runs every 60 seconds
- Calculates minutes passed since last restore
- Restores energy: `min(minutes_passed * 1, MAX_ENERGY - current_energy)`
- Updates `last_restore` timestamp
- Uses `flag_modified()` to ensure SQLAlchemy tracks changes

### **Event Participation Updates**

When a waifu participates in an event:

```python
# Update XP
waifu.xp += rewards["xp"]

# Update dynamic stats (creates new dict to trigger change detection)
waifu.dynamic = {
    **waifu.dynamic,
    "energy": max(0, current_energy - 20),
    "mood": min(100, current_mood + 5),
    "loyalty": min(100, current_loyalty + 2),
    "last_restore": datetime.now().isoformat()
}

# Mark field as modified for SQLAlchemy
flag_modified(waifu, "dynamic")

# Save to database
session.commit()
session.flush()
session.refresh(waifu)
```

## 🚀 Setup Instructions

### **Step 1: Run Migration**

Initialize dynamic stats for all existing waifus:

```bash
python run_migration.py
```

This will:
- ✅ Set default energy (100), mood (50), loyalty (50) for all waifus
- ✅ Initialize `last_restore` timestamp
- ✅ Create database indexes for better performance

### **Step 2: Start the Bot**

```bash
python run_bot.py
```

The bot will:
- ✅ Start the stat restoration service automatically
- ✅ Restore energy every minute
- ✅ Save all changes to database properly

### **Step 3: Verify Everything Works**

1. **Check Current Stats:**
   - Open bot → "🎭 Вайфу" → "📋 Мои вайфу"
   - Click "ℹ️ Детальная информация"
   - Select your waifu (e.g., Chloe)
   - Note the current XP, energy, mood, loyalty

2. **Participate in Event:**
   - Go to "🎭 Вайфу" → "🎲 События" → "🎲 Случайное событие"
   - Click "✅ Да, участвовать!"
   - Select Chloe
   - See results: +XP, +coins, -20 energy, +5 mood, +2 loyalty

3. **Check Updated Stats:**
   - Go back to "📋 Мои вайфу" → "ℹ️ Детальная информация"
   - Select Chloe again
   - **XP should be increased** (e.g., 0 → 30)
   - **Energy should be decreased** by 20
   - **Mood should be increased** by 5
   - **Loyalty should be increased** by 2

4. **Verify WebApp:**
   - Click "🖼️ Открыть карточку в WebApp"
   - **All stats should match** what you saw in the bot
   - **XP progress bar** should show correct value (e.g., 30/100)

5. **Wait and Check Energy Restoration:**
   - Wait 5 minutes
   - Open Chloe's card again
   - **Energy should have increased** by 5 (1 per minute)

## 📊 Restoration Rates

| Stat | Restoration Rate | Maximum | Notes |
|------|-----------------|---------|-------|
| **Energy** | +1 per minute | 100 | Restores automatically |
| **Mood** | Manual | 100 | Changed by events/interactions |
| **Loyalty** | Manual | 100 | Changed by events/interactions |
| **XP** | Manual | ∞ | Gained from events/activities |

## 🔍 How to Check Database Directly

If you want to verify data is saved in database:

```python
from src.bot.database import get_session
from src.bot.models import Waifu
from sqlalchemy import select

session = get_session()
waifu = session.execute(
    select(Waifu).where(Waifu.name == "Chloe")
).scalar_one()

print(f"XP: {waifu.xp}")
print(f"Dynamic: {waifu.dynamic}")
session.close()
```

## 🐛 Troubleshooting

### **Stats Not Updating?**

1. **Check if bot is running:**
   ```bash
   # Should show python process
   ps aux | grep python
   ```

2. **Check logs for errors:**
   - Look for "Error in stat restoration" messages
   - Check database connection errors

3. **Verify migration was run:**
   ```bash
   python run_migration.py
   ```

### **WebApp Shows Old Data?**

1. **Close and reopen WebApp window**
   - Telegram WebApp caches data
   - Closing forces fresh fetch

2. **Check database connection:**
   - Verify `DATABASE_URL` in environment
   - Test database connectivity

3. **Force refresh:**
   - Click back to bot
   - Open WebApp again

### **Energy Not Restoring?**

1. **Check restoration service is running:**
   - Look for "✅ Stat restoration service started" in logs
   - Should run every 60 seconds

2. **Verify last_restore timestamp:**
   ```python
   print(waifu.dynamic.get("last_restore"))
   # Should show recent timestamp
   ```

3. **Check for errors in logs:**
   - Look for "Error in stat restoration"
   - Check database write permissions

## 📝 File Structure

```
Waifu_bot/
├── src/bot/
│   ├── main.py                          # ✅ Starts restoration service
│   ├── services/
│   │   └── stat_restoration.py          # ✅ NEW: Auto restoration
│   ├── handlers/
│   │   └── menu.py                      # ✅ UPDATED: Proper DB saves
│   └── models.py                        # Waifu model with dynamic field
├── sql/
│   └── 002_add_dynamic_stats.sql        # ✅ NEW: Migration script
├── run_migration.py                     # ✅ NEW: Run migration
└── STAT_RESTORATION_GUIDE.md            # ✅ This file
```

## 🎉 Summary

### **What Happens Now:**

1. **When waifu participates in event:**
   - XP increases ✅
   - Energy decreases ✅
   - Mood increases ✅
   - Loyalty increases ✅
   - **All saved to database immediately** ✅

2. **Every minute (automatic):**
   - Bot checks all waifus
   - Calculates time since last restore
   - Restores +1 energy per minute
   - Updates `last_restore` timestamp
   - **Saves to database** ✅

3. **When opening WebApp:**
   - Bot fetches latest data from database
   - Sends to WebApp with current timestamp
   - WebApp displays up-to-date information
   - **User sees correct stats** ✅

### **Benefits:**

- ✅ **No data loss** - All changes persisted to database
- ✅ **Automatic restoration** - Energy recovers over time
- ✅ **Real-time updates** - WebApp always shows current data
- ✅ **Scalable** - Works for any number of waifus
- ✅ **Efficient** - Only updates waifus that need restoration

## 🚀 Next Steps

1. **Run the migration:** `python run_migration.py`
2. **Start the bot:** `python run_bot.py`
3. **Test everything** as described above
4. **Monitor logs** for any errors

**Everything should now work perfectly!** 🎭✨

