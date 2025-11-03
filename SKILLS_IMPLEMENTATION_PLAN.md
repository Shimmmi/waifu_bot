# 🎯 Skills System Implementation Plan

## Overview
✅ **IMPLEMENTED**: Core skills system infrastructure and most gameplay-affecting skills are now functional.

- ✅ Skill effects helper module created
- ✅ Summon discount (bargain_hunter)
- ✅ Rarity bonuses (lucky_novice, summon_mage, legend_seeker)
- ✅ Chat bonuses (gold_mine, experienced_player)
- ✅ Daily bonuses (investor, wise_mentor)
- ✅ Power bonuses (all training and passive skills)

Remaining skills require new systems (energy, mood, loyalty restoration) or are passive income features.

## Skills Analysis

### 📊 ACCOUNT SKILLS

#### 1. `gold_mine` - Золотая жила ✅ IMPLEMENTED
- **Effect**: `gold_bonus` (0.1 to 0.3)
- **Location**: Chat message rewards in `src/bot/services/global_xp.py`
- **Status**: ✅ Implemented in `award_global_xp()` - applies bonus to gold rewards

#### 2. `investor` - Инвестор ✅ IMPLEMENTED
- **Effect**: `daily_gold_bonus` (0.05 to 0.15)
- **Location**: Daily bonus claim in `src/bot/api_server.py` (`claim_daily_bonus` endpoint)
- **Status**: ✅ Implemented - applies bonus to daily gold (100 base)

#### 3. `bargain_hunter` - Скупщик ✅ IMPLEMENTED
- **Effect**: `summon_discount` (0.05 to 0.1)
- **Location**: `src/bot/api_server.py` (`summon_waifus` endpoint) - **Line 521**
- **Status**: ✅ Implemented - applies 5-10% discount to summon costs

#### 4. `banker` - Банкир ✅ IMPLEMENTED
- **Effect**: `collection_gold_bonus` (0.01 per waifu, max 0.5 total)
- **Location**: `src/bot/services/global_xp.py`
- **Status**: ✅ Implemented - applies gold bonus based on collection size to chat rewards

#### 5. `experienced_player` - Опытный игрок ✅ IMPLEMENTED
- **Effect**: `xp_bonus` (0.2 to 1.0)
- **Location**: Chat message rewards in `src/bot/services/global_xp.py`
- **Status**: ✅ Implemented - applies bonus to XP rewards from chat

#### 6. `wise_mentor` - Мудрец ✅ IMPLEMENTED
- **Effect**: `daily_xp_bonus` (0.1 to 0.3)
- **Location**: Daily bonus claim in `src/bot/api_server.py`
- **Status**: ✅ Implemented - applies bonus to XP from daily bonus

#### 7. `teacher` - Наставник ✅ IMPLEMENTED
- **Effect**: `high_level_xp_bonus` (0.05 per waifu >20 lvl, max 1.0)
- **Location**: `src/bot/services/global_xp.py`
- **Status**: ✅ Implemented - counts high-level waifus and applies XP bonus to chat rewards

#### 8. `lucky_novice` - Удача новичка ✅ IMPLEMENTED
- **Effect**: `rare_chance` (0.02 to 0.1)
- **Location**: `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - increases rare waifu chances on summon

#### 9. `summon_mage` - Маг призыва ✅ IMPLEMENTED
- **Effect**: `epic_chance` (0.01 to 0.03)
- **Location**: `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - increases epic waifu chances on summon

#### 10. `legend_seeker` - Легенда ✅ IMPLEMENTED
- **Effect**: `legendary_chance` (0.005 to 0.01)
- **Location**: `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - increases legendary waifu chances on summon

### 🎭 PASSIVE WAIFU SKILLS

#### 11. `loyalty` - Верность ✅ IMPLEMENTED
- **Effect**: `loyalty_power_bonus` (0.2 to 1.0)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies loyalty bonus in power calculation

#### 12. `joy` - Радость ✅ IMPLEMENTED
- **Effect**: `mood_power_bonus` (0.15 to 0.75)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies mood bonus in power calculation 

#### 13. `trust` - Доверие ✅ IMPLEMENTED
- **Effect**: `loyalty_growth` (0.1 to 0.3)
- **Location**: `src/bot/services/stat_restoration.py`
- **Status**: ✅ Implemented - multiplies loyalty restoration rate

#### 14. `optimism` - Оптимизм ✅ IMPLEMENTED
- **Effect**: `mood_recovery` (0.05 to 0.15)
- **Location**: `src/bot/services/stat_restoration.py`
- **Status**: ✅ Implemented - multiplies mood restoration rate

#### 15. `battery` - Батарейка ✅ IMPLEMENTED
- **Effect**: `max_energy` (+20 to +100)
- **Location**: `src/bot/services/waifu_generator.py` and `stat_restoration.py`
- **Status**: ✅ Implemented - increases max energy on generation and restoration

#### 16. `regeneration` - Регенерация ✅ IMPLEMENTED
- **Effect**: `energy_recovery` (0.1 to 0.3)
- **Location**: `src/bot/services/stat_restoration.py`
- **Status**: ✅ Implemented - multiplies energy restoration rate

#### 17. `endurance` - Неутомимость ⏳ PENDING
- **Effect**: `energy_cost_reduction` (0.2 to 0.6)
- **Location**: Energy consumption system (not implemented)
- **Status**: ⏳ Requires energy consumption mechanics

#### 18. `mentor` - Ментор ✅ IMPLEMENTED
- **Effect**: `upgrade_xp_bonus` (0.25 to 1.25)
- **Location**: Waifu upgrade in `src/bot/api_server.py` (`perform_upgrade` endpoint)
- **Status**: ✅ Implemented - applies bonus to XP from sacrificed waifus

#### 19. `golden_hand` - Золотая рука ⏳ PENDING
- **Effect**: `waifu_gold_bonus` (0.1 to 0.3)
- **Location**: Gold rewards from waifu actions (not implemented)
- **Status**: ⏳ Requires waifu action system

#### 20. `synergy` - Синергия ✅ IMPLEMENTED
- **Effect**: `favorite_power_bonus` (0.05 per favorite, max 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - counts favorite waifus and applies bonus

### 🏋️ TRAINING WAIFU SKILLS

#### 21. `spiritual_strength` - Сила духа ✅ IMPLEMENTED
- **Effect**: `power_bonus` (0.1 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies power stat in calculation

#### 22. `mental_acuity` - Острота ума ✅ IMPLEMENTED
- **Effect**: `intellect_bonus` (0.1 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies intellect stat in calculation

#### 23. `magnetism` - Магнетизм ✅ IMPLEMENTED
- **Effect**: `charm_bonus` (0.1 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies charm stat in calculation

#### 24. `agility` - Ловкость ✅ IMPLEMENTED
- **Effect**: `dexterity_bonus` (0.1 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies speed stat (dexterity stored as bond)

#### 25. `fortune` - Фортуна ✅ IMPLEMENTED
- **Effect**: `luck_bonus` (0.15 to 0.45)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies luck stat in calculation

#### 26. `speed` - Скорость ✅ IMPLEMENTED
- **Effect**: `speed_bonus` (0.15 to 0.45)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies speed stat in calculation

#### 27. `stamina` - Выносливость ⏳ PENDING
- **Effect**: `health_bonus` (0.2 to 0.6)
- **Location**: Combat/health system (not implemented)
- **Status**: ⏳ Requires combat/health system

#### 28. `elite` - Элита ✅ IMPLEMENTED
- **Effect**: `rare_power_bonus` (0.25 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies power for rare waifus

#### 29. `legend` - Легенда ✅ IMPLEMENTED
- **Effect**: `epic_power_bonus` (0.5 to 1.0)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies power for epic/legendary waifus

#### 30. `harmony` - Гармония ✅ IMPLEMENTED
- **Effect**: `rarity_bonus` (0.05 per rarity type, max 0.25)
- **Location**: Power calculation
- **Status**: ✅ Implemented - counts unique rarities and applies bonus

## 🔧 Implementation Summary

### ✅ Step 1: Skill Effects Helper - COMPLETE
Created `src/bot/services/skill_effects.py`:
- `get_user_skill_effects()` - Fetches all active skill effects for a user
- `get_skill_effect_value()` - Gets specific effect value
- `apply_skill_multiplier()` - Applies additive multipliers (e.g., +20%)
- `apply_skill_discount()` - Applies discounts (e.g., -5%)
- `apply_max_cap()` - Applies maximum caps

### ✅ Step 2: Core Systems Updated
Modified files to fetch and apply skill effects:

1. **`src/bot/services/global_xp.py`** ✅
   - Applied `gold_bonus` and `xp_bonus` in `award_global_xp()`

2. **`src/bot/api_server.py`** ✅
   - `summon_waifus()` - Applied `summon_discount` (5-10%)
   - `claim_daily_bonus()` - Applied `daily_gold_bonus` and `daily_xp_bonus`
   - `get_profile()` - Applied power bonuses to active waifu
   - `get_waifus()` - Applied power bonuses to all waifus

3. **`src/bot/services/waifu_generator.py`** ✅
   - `generate_waifu()` - Applied rarity bonuses in summon
   - `calculate_waifu_power()` - Applied all power bonuses

### ✅ Implementation Complete
1. **✅ IMMEDIATE**: `bargain_hunter` - summon discount (5-10% off)
2. **✅ HIGH**: Gold/XP bonuses for chat messages (+10-30%)
3. **✅ MEDIUM**: Power bonuses for waifus (all stats + rare/epic bonuses)
4. **⏳ DEFERRED**: Energy/mood/loyalty systems (require new systems)

## 📋 Detailed Implementation Table

| Skill ID | Name | Effect Key | Base Value | File | Status |
|----------|------|------------|------------|------|--------|
| `bargain_hunter` | Скупщик | `summon_discount` | 0.05-0.1 | `api_server.py` | ✅ IMPLEMENTED |
| `gold_mine` | Золотая жила | `gold_bonus` | 0.1-0.3 | `global_xp.py` | ✅ IMPLEMENTED |
| `experienced_player` | Опытный игрок | `xp_bonus` | 0.2-1.0 | `global_xp.py` | ✅ IMPLEMENTED |
| `investor` | Инвестор | `daily_gold_bonus` | 0.05-0.15 | `api_server.py` | ✅ IMPLEMENTED |
| `wise_mentor` | Мудрец | `daily_xp_bonus` | 0.1-0.3 | `api_server.py` | ✅ IMPLEMENTED |
| `teacher` | Наставник | `high_level_xp_bonus` | 0.05 per >20lvl | `global_xp.py` | ✅ IMPLEMENTED |
| `banker` | Банкир | `collection_gold_bonus` | 0.01 per waifu | `global_xp.py` | ✅ IMPLEMENTED |
| `lucky_novice` | Удача новичка | `rare_chance` | 0.02-0.1 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `summon_mage` | Маг призыва | `epic_chance` | 0.01-0.03 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `legend_seeker` | Легенда | `legendary_chance` | 0.005-0.01 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `mentor` | Ментор | `upgrade_xp_bonus` | 0.25-1.25 | `api_server.py` | ✅ IMPLEMENTED |
| `loyalty` | Верность | `loyalty_power_bonus` | 0.2-1.0 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `joy` | Радость | `mood_power_bonus` | 0.15-0.75 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `trust` | Доверие | `loyalty_growth` | 0.1-0.3 | `stat_restoration.py` | ✅ IMPLEMENTED |
| `optimism` | Оптимизм | `mood_recovery` | 0.05-0.15 | `stat_restoration.py` | ✅ IMPLEMENTED |
| `battery` | Батарейка | `max_energy` | +20 to +100 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `regeneration` | Регенерация | `energy_recovery` | 0.1-0.3 | `stat_restoration.py` | ✅ IMPLEMENTED |
| `spiritual_strength` | Сила духа | `power_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `mental_acuity` | Острота ума | `intellect_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `magnetism` | Магнетизм | `charm_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `agility` | Ловкость | `dexterity_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `fortune` | Фортуна | `luck_bonus` | 0.15-0.45 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `speed` | Скорость | `speed_bonus` | 0.15-0.45 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `elite` | Элита | `rare_power_bonus` | 0.25-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `legend` | Легенда | `epic_power_bonus` | 0.5-1.0 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `synergy` | Синергия | `favorite_power_bonus` | 0.05-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `harmony` | Гармония | `rarity_bonus` | 0.05-0.25 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `stamina` | Выносливость | `health_bonus` | 0.2-0.6 | - | ⏳ PENDING |
| `endurance` | Неутомимость | `energy_cost_reduction` | 0.2-0.6 | - | ⏳ PENDING |
| `golden_hand` | Золотая рука | `waifu_gold_bonus` | 0.1-0.3 | - | ⏳ PENDING |

## ✅ Completed Implementation

**27 out of 30 skills successfully implemented!** The comprehensive skills system is now fully functional across all gameplay mechanics:

### 🎰 **Summon System**
- **Summon Discount** (bargain_hunter): 5-10% cost reduction
- **Rarity Bonuses** (lucky_novice, summon_mage, legend_seeker): Increased rare/epic/legendary chances

### 💰 **Gold System**
- **Chat Bonuses** (gold_mine): +10-30% gold from messages
- **Daily Bonuses** (investor): +5-15% daily gold
- **Collection Bonuses** (banker): +0.01% per waifu, capped at +50%

### ⚡ **XP System**
- **Chat Bonuses** (experienced_player): +20-100% XP from messages
- **Daily Bonuses** (wise_mentor): +10-30% daily XP
- **High-Level Bonuses** (teacher): +0.05% per waifu above level 20, capped at +100%
- **Upgrade Bonuses** (mentor): +25-125% XP from sacrificed waifus

### 💪 **Power System**
- **Stat Training** (spiritual_strength, mental_acuity, magnetism, agility, fortune, speed): +10-50% to each stat
- **Rarity Bonuses** (elite, legend): +25-100% for rare/epic waifus
- **Collection Synergies** (synergy, harmony): Bonuses from favorites and unique rarities
- **Dynamic Bonuses** (loyalty, joy): Multipliers for mood/loyalty contributions

### 🔋 **Restoration System**
- **Energy Recovery** (regeneration, battery): Faster recovery and increased max energy
- **Mood Recovery** (optimism): Faster mood restoration
- **Loyalty Growth** (trust): Faster loyalty increase

## ⏳ Future Enhancements (3 skills remaining)

Skills requiring new game systems:
- **`stamina`** - Requires health/combat system
- **`endurance`** - Requires energy consumption mechanics
- **`golden_hand`** - Requires waifu action system

These will be implemented when their respective game systems are developed.

## ⚠️ Notes

- Skills are stored in JSONB format: `{"1": {"effect": value}, "2": {"effect": value}}`
- Need to aggregate effects across all skill levels
- Some effects are multiplicative, others are additive
- Max caps exist for some effects (`max_collection_bonus`, etc.)

