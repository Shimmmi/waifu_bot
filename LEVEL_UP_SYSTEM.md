# 🎉 Level-Up System Documentation

## 📋 Overview

The level-up system has been fully implemented! Waifus now gain levels as they earn XP, with stat increases and proper XP tracking.

## ✨ Features

### 1. XP Formula
**Progressive XP Requirements:**
- Level 1 → 2: 100 XP
- Level 2 → 3: 200 XP  
- Level 3 → 4: 300 XP
- Level 4 → 5: 400 XP
- And so on...

**Total XP Formula:**
```
Total XP for level N = 50 * N * (N - 1)
```

Examples:
- Level 1: 0 XP
- Level 2: 100 XP (0 + 100)
- Level 3: 300 XP (0 + 100 + 200)
- Level 4: 600 XP (0 + 100 + 200 + 300)
- Level 5: 1000 XP (0 + 100 + 200 + 300 + 400)

### 2. Level-Up Process

When a waifu gains enough XP:

1. **Level increases** to the appropriate level
2. **One random stat increases by 1**:
   - 💪 Сила (Power)
   - 💖 Очарование (Charm)
   - 🍀 Удача (Luck)
   - ❤️ Привязанность (Affection)
   - 🧠 Интеллект (Intellect)
   - ⚡ Скорость (Speed)

3. **User receives notification** with:
   - New level reached
   - Which stat increased
   - Old → New stat value
   - Total power (sum of all stats)

4. **Changes saved to database** immediately

### 3. Multiple Level-Ups

If a waifu gains enough XP to level up multiple times in one event:
- All levels are applied at once
- Multiple stats increase (one per level gained)
- User is notified of total levels gained

Example: If waifu has 50 XP (Level 1) and gains 400 XP:
- New total: 450 XP
- Should be Level 3 (300 XP needed)
- **Result:** Gains 2 levels, 2 random stats increase

### 4. XP Display

**In Bot Messages:**
```
✨ Опыт: 50/200 (25%)
```
Shows: Current progress in level / XP needed for next level / Percentage

**In WebApp:**
```
✨ Опыт: 50 / 200 (25%)
[████░░░░░░░░░░░░]
```
Visual progress bar showing XP progress within current level

### 5. XP Never Exceeds Properly

✅ **OLD PROBLEM (Fixed):**
- Waifu could have 114/100 XP
- Level stayed at 1

✅ **NEW BEHAVIOR:**
- Waifu gains XP: 0 + 114 = 114 XP
- System checks: 114 >= 100 (Level 2 threshold)
- **Waifu levels up to Level 2**
- Display shows: **14/200 XP**
  - 14 XP remaining towards Level 3
  - 200 XP needed for Level 3 (from Level 2)

## 🔧 Technical Implementation

### Files Created/Modified

1. **`src/bot/services/level_up.py`** (NEW)
   - `LevelUpService` class
   - XP calculation formulas
   - Level-up logic
   - Stat increase system
   - Message formatting

2. **`src/bot/handlers/menu.py`** (MODIFIED)
   - Integrated level-up checks after XP gain
   - Added level-up notifications
   - Updates both level and stats in database

3. **`src/bot/services/waifu_generator.py`** (MODIFIED)
   - Updated `format_waifu_card()` to show correct XP progress
   - Uses level-up service for XP calculations

4. **`webapp/waifu-card.html`** (MODIFIED)
   - Updated XP calculation formulas
   - Shows XP progress within current level
   - Displays proper progress bar

## 📊 Example Scenarios

### Scenario 1: Normal Level-Up
```
Initial State:
- Level: 1
- XP: 80/100

Event Reward: +25 XP

Result:
- Level: 1 → 2 ✅
- XP: 105 total → Display as 5/200
- Random stat (e.g., Intellect): 7 → 8
- Notification: "🎉 Hye-jin достигла 2 уровня! Интеллект увеличился на 1"
```

### Scenario 2: Multiple Level-Ups
```
Initial State:
- Level: 1
- XP: 50/100

Event Reward: +350 XP

Result:
- Level: 1 → 3 ✅ (+2 levels!)
- XP: 400 total → Display as 100/300
- Two random stats increase by 1 each
- Notification: "🎉 Hye-jin достигла 3 уровня! (+2 уровней)"
```

### Scenario 3: High XP Gain
```
Initial State:
- Level: 2
- XP: 250/300

Event Reward: +200 XP

Result:
- Level: 2 → 4 ✅
- XP: 450 total → Display as 50/400
  - Level 3 threshold: 300 XP
  - Level 4 threshold: 600 XP
  - Progress: 450 - 600 = -150 → 50/400 within Level 4
```

## 🎮 How to Test

### Test 1: Single Level-Up
1. Summon a new waifu (Level 1, 0 XP)
2. Participate in events until you get 100+ XP
3. **Expected:** Level-up message appears
4. **Check:** Level = 2, One stat increased, XP shows as X/200

### Test 2: Multiple Level-Ups
1. Find a waifu with ~50 XP (Level 1)
2. Participate in multiple events to gain 300+ XP
3. **Expected:** "достигла X уровня (+Y уровней)" message
4. **Check:** Multiple stats increased

### Test 3: XP Display
1. After any event, click "Подробно" (Details)
2. **Check WebApp:**
   - XP shows as "X / Y (Z%)"
   - X + Y never exceeds next level threshold
   - Progress bar matches percentage

### Test 4: Database Persistence
1. Level up a waifu
2. Close bot completely
3. Reopen bot and check waifu
4. **Expected:** Level, stats, and XP are saved correctly

## 🎯 Level Progression Table

| Level | Total XP Needed | XP for This Level |
|-------|-----------------|-------------------|
| 1     | 0               | -                 |
| 2     | 100             | 100               |
| 3     | 300             | 200               |
| 4     | 600             | 300               |
| 5     | 1,000           | 400               |
| 6     | 1,500           | 500               |
| 7     | 2,100           | 600               |
| 8     | 2,800           | 700               |
| 9     | 3,600           | 800               |
| 10    | 4,500           | 900               |

## 📝 Sample Messages

### Level-Up Notification (Single Level)
```
🎉 ПОВЫШЕНИЕ УРОВНЯ! 🎉

🌟 Hye-jin достигла 2 уровня!

📈 Интеллект увеличилась на 1
     7 → 8

💪 Общая сила: 50

✨ Продолжай в том же духе!
```

### Level-Up Notification (Multiple Levels)
```
🎉 ПОВЫШЕНИЕ УРОВНЯ! 🎉

🌟 So-young достигла 5 уровня! (+3 уровней)

📈 Сила: 8 → 11 (+3)
💪 Общая сила: 58

✨ Поздравляем с прогрессом!
```

### Event Result with Level-Up
```
🎭 Результат события: Культурный фестиваль

⭐ Оценка: 85/100

🎁 Награды:
💰 Монеты: +28
🏆 Получен опыт: +19

⚡ Энергия: -20
😊 Настроение: +5
💝 Лояльность: +2

🎉 ПОВЫШЕНИЕ УРОВНЯ! 🎉

🌟 Hye-jin достигла 2 уровня!

📈 Обаяние увеличилась на 1
     10 → 11

💪 Общая сила: 51

✨ Продолжай в том же духе!
```

## ✅ Deployment Checklist

- [x] Level-up service created
- [x] Event handler updated with level-up checks
- [x] Stat increase logic implemented
- [x] Level-up notifications added
- [x] XP display updated in bot
- [x] XP display updated in WebApp
- [x] Database changes saved correctly
- [x] Multiple level-ups supported
- [ ] Tested with real bot deployment

## 🚀 Ready to Deploy!

All code is complete and ready. Just deploy to Render:

```bash
git add .
git commit -m "Feature: Implement level-up system with stat increases"
git push origin main
```

Then test using the scenarios above!

---

**The level-up system is fully implemented and ready to use!** 🎉

