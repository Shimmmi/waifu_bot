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

#### 4. `banker` - Банкир
- **Effect**: `collection_gold_bonus` (0.01 per waifu, max 0.5 total)
- **Location**: Passive income system (not implemented yet)
- **Implementation**: Create new endpoint for passive gold collection

#### 5. `experienced_player` - Опытный игрок ✅ IMPLEMENTED
- **Effect**: `xp_bonus` (0.2 to 1.0)
- **Location**: Chat message rewards in `src/bot/services/global_xp.py`
- **Status**: ✅ Implemented - applies bonus to XP rewards from chat

#### 6. `wise_mentor` - Мудрец ✅ IMPLEMENTED
- **Effect**: `daily_xp_bonus` (0.1 to 0.3)
- **Location**: Daily bonus claim in `src/bot/api_server.py`
- **Status**: ✅ Implemented - applies bonus to XP from daily bonus

#### 7. `teacher` - Наставник
- **Effect**: `high_level_xp_bonus` (0.05 per waifu >20 lvl, max 1.0)
- **Location**: XP calculation system
- **Implementation**: Modify XP calculation to count high-level waifus and apply bonus

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

#### 13. `trust` - Доверие
- **Effect**: `loyalty_growth` (0.1 to 0.3)
- **Location**: Loyalty restoration system (not implemented)
- **Implementation**: Create loyalty restoration system

#### 14. `optimism` - Оптимизм
- **Effect**: `mood_recovery` (0.05 to 0.15)
- **Location**: Mood restoration system (not implemented)
- **Implementation**: Create mood restoration system

#### 15. `battery` - Батарейка
- **Effect**: `max_energy` (+20 to +100)
- **Location**: Waifu generation in `src/bot/services/waifu_generator.py`
- **Implementation**: Modify initial `max_energy` based on skills

#### 16. `regeneration` - Регенерация
- **Effect**: `energy_recovery` (0.1 to 0.3)
- **Location**: Energy restoration system (not implemented)
- **Implementation**: Create energy restoration system

#### 17. `endurance` - Неутомимость
- **Effect**: `energy_cost_reduction` (0.2 to 0.6)
- **Location**: Energy consumption system (not implemented)
- **Implementation**: Create energy consumption system

#### 18. `mentor` - Ментор ⏳ PENDING
- **Effect**: `upgrade_xp_bonus` (0.25 to 1.25)
- **Location**: Waifu upgrade in `src/bot/api_server.py` (`perform_upgrade` endpoint)
- **Status**: ⏳ Requires implementation in upgrade XP calculation

#### 19. `golden_hand` - Золотая рука
- **Effect**: `waifu_gold_bonus` (0.1 to 0.3)
- **Location**: Gold rewards from waifu actions (not implemented)
- **Implementation**: Create gold reward system

#### 20. `synergy` - Синергия ⏳ PENDING
- **Effect**: `favorite_power_bonus` (0.05 per favorite, max 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ⏳ Requires counting favorite waifus in collection

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
- **Location**: Combat system (not implemented)
- **Status**: ⏳ Requires combat system implementation

#### 28. `elite` - Элита ✅ IMPLEMENTED
- **Effect**: `rare_power_bonus` (0.25 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies power for rare waifus

#### 29. `legend` - Легенда ✅ IMPLEMENTED
- **Effect**: `epic_power_bonus` (0.5 to 1.0)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Status**: ✅ Implemented - multiplies power for epic/legendary waifus

#### 30. `harmony` - Гармония ⏳ PENDING
- **Effect**: `rarity_bonus` (0.05 per rarity type, max 0.25)
- **Location**: Power calculation
- **Status**: ⏳ Requires counting unique rarities in collection

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
| `lucky_novice` | Удача новичка | `rare_chance` | 0.02-0.1 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `summon_mage` | Маг призыва | `epic_chance` | 0.01-0.03 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `legend_seeker` | Легенда | `legendary_chance` | 0.005-0.01 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `mentor` | Ментор | `upgrade_xp_bonus` | 0.25-1.25 | `api_server.py` | ⏳ PENDING |
| `loyalty` | Верность | `loyalty_power_bonus` | 0.2-1.0 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `joy` | Радость | `mood_power_bonus` | 0.15-0.75 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `spiritual_strength` | Сила духа | `power_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `mental_acuity` | Острота ума | `intellect_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `magnetism` | Магнетизм | `charm_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `agility` | Ловкость | `dexterity_bonus` | 0.1-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `fortune` | Фортуна | `luck_bonus` | 0.15-0.45 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `speed` | Скорость | `speed_bonus` | 0.15-0.45 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `elite` | Элита | `rare_power_bonus` | 0.25-0.5 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `legend` | Легенда | `epic_power_bonus` | 0.5-1.0 | `waifu_generator.py` | ✅ IMPLEMENTED |
| `synergy` | Синергия | `favorite_power_bonus` | 0.05-0.5 | `waifu_generator.py` | ⏳ PENDING |
| `harmony` | Гармония | `rarity_bonus` | 0.05-0.25 | `waifu_generator.py` | ⏳ PENDING |

## ✅ Completed Implementation

All core gameplay skills have been successfully implemented. The skills system is now fully functional for:
- Summon cost reduction
- Rarity improvements
- Gold/XP bonuses
- Waifu power scaling
- Daily bonus enhancements

## ⏳ Future Enhancements

Skills requiring new systems:
- Energy management (battery, regeneration, endurance)
- Mood/loyalty restoration (optimism, trust)
- Passive income (banker, golden_hand)
- Collection synergies (synergy, harmony, teacher, banker)

These will be implemented as their respective game systems are developed.

## ⚠️ Notes

- Skills are stored in JSONB format: `{"1": {"effect": value}, "2": {"effect": value}}`
- Need to aggregate effects across all skill levels
- Some effects are multiplicative, others are additive
- Max caps exist for some effects (`max_collection_bonus`, etc.)

