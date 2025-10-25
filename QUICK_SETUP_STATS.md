# ⚡ Quick Setup: Stats & Auto-Restoration

## 🎯 Problem Solved

Your waifus' stats (XP, energy, mood, loyalty) weren't being saved to the database after events. Now they are! Plus, energy automatically restores every minute.

## 🚀 Quick Start (3 Steps)

### **Step 1: Run Migration**

This initializes stat tracking for all your waifus:

```bash
python run_migration.py
```

**Expected output:**
```
🔄 Running migration: Initialize dynamic stats...
✅ Migration completed successfully!
✅ All waifus now have initialized dynamic stats (energy, mood, loyalty)
```

### **Step 2: Test the System**

Verify everything works:

```bash
python test_stat_system.py
```

**Expected output:**
```
🔍 Testing Stat System...

📋 Testing with: Chloe (ID: wf_00123)
   Rarity: uncommon

✅ Test 1: Updating XP...
   XP: 0 → 30
   ✅ XP update works!

✅ Test 2: Updating dynamic stats...
   Energy: 100 → 80
   Mood: 50 → 55
   Loyalty: 50 → 52
   ✅ Dynamic stats update works!

✅ Test 3: Verifying persistence...
   Reloaded XP: 30
   Reloaded Dynamic: {'energy': 80, 'mood': 55, 'loyalty': 52, ...}
   ✅ Data persists correctly!

🎉 All tests passed! Stat system is working correctly!
```

### **Step 3: Start the Bot**

```bash
python run_bot.py
```

**Expected output:**
```
INFO - Bot starting...
✅ Stat restoration service started
INFO - Start polling...
```

## ✅ What Now Works

### **1. Stats Save to Database** 💾

When your waifu participates in an event:
- ✅ **XP increases** and is saved immediately
- ✅ **Energy decreases** by 20 (event cost)
- ✅ **Mood increases** by 5 (happiness from participating)
- ✅ **Loyalty increases** by 2 (bond strengthens)

**All changes persist to the database!**

### **2. Energy Auto-Restores** ⚡

Every minute, automatically:
- ✅ **+1 Energy** for all waifus (up to max 100)
- ✅ Works even when you're not using the bot
- ✅ Calculated accurately based on time passed

### **3. WebApp Shows Current Data** 🖼️

When you open a waifu card:
- ✅ **Fresh data** pulled from database
- ✅ **All stats** reflect latest changes
- ✅ **XP progress bar** shows correct value
- ✅ **Energy level** is current

## 📊 Restoration Rates

| What | Rate | Maximum |
|------|------|---------|
| Energy | +1/min | 100 |
| Mood | Events only | 100 |
| Loyalty | Events only | 100 |

## 🧪 How to Test

1. **Check current stats:**
   ```
   Bot → 🎭 Вайфу → 📋 Мои вайфу → ℹ️ Детальная информация
   Select Chloe → Note: XP=0, Energy=100
   ```

2. **Participate in event:**
   ```
   Bot → 🎭 Вайфу → 🎲 События → 🎲 Случайное событие
   ✅ Да, участвовать! → Select Chloe
   See results: +30 XP, +40 coins, -20 energy, +5 mood, +2 loyalty
   ```

3. **Verify stats updated:**
   ```
   Bot → 🎭 Вайфу → 📋 Мои вайфу → ℹ️ Детальная информация
   Select Chloe → Should show: XP=30, Energy=80
   ```

4. **Check WebApp:**
   ```
   Click 🖼️ Открыть карточку в WebApp
   Should show: XP bar at 30/100, Energy at 80
   ```

5. **Wait 5 minutes, check again:**
   ```
   Energy should now be 85 (restored 5 points)
   ```

## 🔧 Technical Details

### Files Changed:
- ✅ `src/bot/handlers/menu.py` - Proper database saves
- ✅ `src/bot/services/stat_restoration.py` - NEW: Auto restoration
- ✅ `src/bot/main.py` - Starts restoration service
- ✅ `sql/002_add_dynamic_stats.sql` - NEW: Migration
- ✅ `run_migration.py` - NEW: Run migration script
- ✅ `test_stat_system.py` - NEW: Test script

### How It Works:

**Event Participation:**
```python
# Update stats
waifu.xp += 30
waifu.dynamic = {
    **waifu.dynamic,
    "energy": 80,
    "mood": 55,
    "loyalty": 52,
    "last_restore": "2025-10-25T12:34:56"
}

# Mark as modified
flag_modified(waifu, "dynamic")

# Save to database
session.commit()
session.flush()
session.refresh(waifu)
```

**Auto Restoration (every 60 seconds):**
```python
# Calculate time passed
now = datetime.now()
last_restore = datetime.fromisoformat(waifu.dynamic["last_restore"])
minutes_passed = (now - last_restore).total_seconds() / 60

# Restore energy
energy_to_restore = min(minutes_passed * 1, 100 - current_energy)
waifu.dynamic["energy"] += energy_to_restore

# Save to database
session.commit()
```

## 🐛 Troubleshooting

### Stats not updating?
```bash
# 1. Check migration ran
python run_migration.py

# 2. Test the system
python test_stat_system.py

# 3. Check database connection
echo $DATABASE_URL
```

### Energy not restoring?
```bash
# Check logs for restoration service
# Should see: "✅ Restored stats for X waifus" every minute
```

### WebApp shows old data?
```
# Close WebApp window completely
# Open it again (forces fresh fetch)
```

## 📚 More Info

For detailed technical documentation, see:
- `STAT_RESTORATION_GUIDE.md` - Full technical guide

## 🎉 You're Done!

Everything should now work perfectly:
- ✅ Stats save to database
- ✅ Energy restores automatically
- ✅ WebApp shows current data

Enjoy your waifu bot! 🎭✨

