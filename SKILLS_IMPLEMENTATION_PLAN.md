# 🎯 Skills System Implementation Plan

## Overview
The skills system is defined in the database but **NOT IMPLEMENTED** in the game logic. Skills are purely cosmetic at the moment - they can be upgraded but their effects are never applied.

## Skills Analysis

### 📊 ACCOUNT SKILLS

#### 1. `gold_mine` - Золотая жила
- **Effect**: `gold_bonus` (0.1 to 0.3)
- **Location**: Chat message rewards in `src/bot/services/global_xp.py`
- **Implementation**: Modify `award_global_xp()` to fetch skill effects and multiply `gold_amount` by `(1 + gold_bonus)`

#### 2. `investor` - Инвестор
- **Effect**: `daily_gold_bonus` (0.05 to 0.15)
- **Location**: Daily bonus claim in `src/bot/api_server.py` (`claim_daily_bonus` endpoint)
- **Implementation**: Fetch skill effects, apply bonus to the 100 gold reward

#### 3. `bargain_hunter` - Скупщик ⚠️ USER'S ISSUE
- **Effect**: `summon_discount` (0.05 to 0.1)
- **Location**: `src/bot/api_server.py` (`summon_waifus` endpoint) - **Line 521**
- **Current**: `cost = 100 if count == 1 else 1000` (hardcoded)
- **Implementation**: Fetch skill effects, apply discount: `cost = base_cost * (1 - summon_discount)`

#### 4. `banker` - Банкир
- **Effect**: `collection_gold_bonus` (0.01 per waifu, max 0.5 total)
- **Location**: Passive income system (not implemented yet)
- **Implementation**: Create new endpoint for passive gold collection

#### 5. `experienced_player` - Опытный игрок
- **Effect**: `xp_bonus` (0.2 to 1.0)
- **Location**: Chat message rewards in `src/bot/services/global_xp.py`
- **Implementation**: Modify `award_global_xp()` to multiply `xp_amount` by `(1 + xp_bonus)`

#### 6. `wise_mentor` - Мудрец
- **Effect**: `daily_xp_bonus` (0.1 to 0.3)
- **Location**: Daily bonus claim in `src/bot/api_server.py`
- **Implementation**: Fetch skill effects, apply bonus to XP reward

#### 7. `teacher` - Наставник
- **Effect**: `high_level_xp_bonus` (0.05 per waifu >20 lvl, max 1.0)
- **Location**: XP calculation system
- **Implementation**: Modify XP calculation to count high-level waifus and apply bonus

#### 8. `lucky_novice` - Удача новичка
- **Effect**: `rare_chance` (0.02 to 0.1)
- **Location**: `src/bot/services/waifu_generator.py`
- **Implementation**: Modify rarity generation logic to increase rare+ chances

#### 9. `summon_mage` - Маг призыва
- **Effect**: `epic_chance` (0.01 to 0.03)
- **Location**: `src/bot/services/waifu_generator.py`
- **Implementation**: Modify rarity generation logic

#### 10. `legend_seeker` - Легенда
- **Effect**: `legendary_chance` (0.005 to 0.01)
- **Location**: `src/bot/services/waifu_generator.py`
- **Implementation**: Modify rarity generation logic

### 🎭 PASSIVE WAIFU SKILLS

#### 11. `loyalty` - Верность
- **Effect**: `loyalty_power_bonus` (0.2 to 1.0)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Implementation**: Modify `calculate_waifu_power()` to fetch user skills and apply bonus

#### 12. `joy` - Радость
- **Effect**: `mood_power_bonus` (0.15 to 0.75)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Implementation**: Modify `calculate_waifu_power()` 

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

#### 18. `mentor` - Ментор
- **Effect**: `upgrade_xp_bonus` (0.25 to 1.25)
- **Location**: Waifu upgrade in `src/bot/api_server.py` (`perform_upgrade` endpoint)
- **Implementation**: Modify XP calculation to fetch and apply skill effects

#### 19. `golden_hand` - Золотая рука
- **Effect**: `waifu_gold_bonus` (0.1 to 0.3)
- **Location**: Gold rewards from waifu actions (not implemented)
- **Implementation**: Create gold reward system

#### 20. `synergy` - Синергия
- **Effect**: `favorite_power_bonus` (0.05 per favorite, max 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Implementation**: Count favorite waifus and apply bonus

### 🏋️ TRAINING WAIFU SKILLS

#### 21. `spiritual_strength` - Сила духа
- **Effect**: `power_bonus` (0.1 to 0.5)
- **Location**: Power calculation in `src/bot/services/waifu_generator.py`
- **Implementation**: Modify `calculate_waifu_power()` to apply stat bonus

#### 22. `mental_acuity` - Острота ума
- **Effect**: `intellect_bonus` (0.1 to 0.5)
- **Location**: Power calculation (intellect affects power)
- **Implementation**: Modify stat calculation

#### 23. `magnetism` - Магнетизм
- **Effect**: `charm_bonus` (0.1 to 0.5)
- **Location**: Power calculation
- **Implementation**: Modify stat calculation

#### 24. `agility` - Ловкость
- **Effect**: `dexterity_bonus` (0.1 to 0.5)
- **Location**: Power calculation
- **Implementation**: Modify stat calculation

#### 25. `fortune` - Фортуна
- **Effect**: `luck_bonus` (0.15 to 0.45)
- **Location**: Power calculation
- **Implementation**: Modify stat calculation

#### 26. `speed` - Скорость
- **Effect**: `speed_bonus` (0.15 to 0.45)
- **Location**: Combat system (not implemented)
- **Implementation**: Create combat system

#### 27. `stamina` - Выносливость
- **Effect**: `health_bonus` (0.2 to 0.6)
- **Location**: Combat system (not implemented)
- **Implementation**: Create combat system

#### 28. `elite` - Элита
- **Effect**: `rare_power_bonus` (0.25 to 0.5)
- **Location**: Power calculation
- **Implementation**: Modify `calculate_waifu_power()` to check rarity

#### 29. `legend` - Легенда
- **Effect**: `epic_power_bonus` (0.5 to 1.0)
- **Location**: Power calculation
- **Implementation**: Modify `calculate_waifu_power()` to check rarity

#### 30. `harmony` - Гармония
- **Effect**: `rarity_bonus` (0.05 per rarity type, max 0.25)
- **Location**: Power calculation
- **Implementation**: Count unique rarities in collection and apply bonus

## 🔧 Implementation Strategy

### Step 1: Create Skill Effects Helper
Create `src/bot/services/skill_effects.py`:

```python
def get_user_skill_effects(db: Session, user_id: int) -> Dict[str, float]:
    """Fetch all active skill effects for a user"""
    # Query UserSkillLevel, join with Skill, aggregate effects
    pass

def get_skill_effect_sum(effects: Dict[str, float], effect_name: str, default: float = 0.0) -> float:
    """Get sum of a specific effect across all skills"""
    pass
```

### Step 2: Update Core Systems
Modify these files to fetch and apply skill effects:

1. **`src/bot/services/global_xp.py`** (Line ~152-282)
   - Import skill effects helper
   - Apply `gold_bonus` and `xp_bonus` in `award_global_xp()`

2. **`src/bot/api_server.py`**:
   - `summon_waifus()` (Line 496-580) - Apply `summon_discount`
   - `claim_daily_bonus()` - Apply `daily_gold_bonus` and `daily_xp_bonus`
   - `perform_upgrade()` - Apply `upgrade_xp_bonus`

3. **`src/bot/services/waifu_generator.py`**:
   - `generate_waifu()` - Apply rarity bonuses
   - `calculate_waifu_power()` - Apply all power bonuses

### Step 3: Priority Order
1. **IMMEDIATE** (User's reported issue): `bargain_hunter` - summon discount
2. **HIGH**: Gold/XP bonuses for chat messages
3. **MEDIUM**: Power bonuses for waifus
4. **LOW**: Energy/mood/loyalty systems (not implemented yet)

## 📋 Detailed Implementation Table

| Skill ID | Name | Effect Key | Base Value | File | Line | Status |
|----------|------|------------|------------|------|------|--------|
| `bargain_hunter` | Скупщик | `summon_discount` | 0.05-0.1 | `api_server.py` | 521 | ❌ Not Implemented |
| `gold_mine` | Золотая жила | `gold_bonus` | 0.1-0.3 | `global_xp.py` | 152 | ❌ Not Implemented |
| `experienced_player` | Опытный игрок | `xp_bonus` | 0.2-1.0 | `global_xp.py` | 152 | ❌ Not Implemented |
| `investor` | Инвестор | `daily_gold_bonus` | 0.05-0.15 | `api_server.py` | TBD | ❌ Not Implemented |
| `wise_mentor` | Мудрец | `daily_xp_bonus` | 0.1-0.3 | `api_server.py` | TBD | ❌ Not Implemented |
| `lucky_novice` | Удача новичка | `rare_chance` | 0.02-0.1 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `summon_mage` | Маг призыва | `epic_chance` | 0.01-0.03 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `legend_seeker` | Легенда | `legendary_chance` | 0.005-0.01 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `mentor` | Ментор | `upgrade_xp_bonus` | 0.25-1.25 | `api_server.py` | TBD | ❌ Not Implemented |
| `loyalty` | Верность | `loyalty_power_bonus` | 0.2-1.0 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `joy` | Радость | `mood_power_bonus` | 0.15-0.75 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `spiritual_strength` | Сила духа | `power_bonus` | 0.1-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `mental_acuity` | Острота ума | `intellect_bonus` | 0.1-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `magnetism` | Магнетизм | `charm_bonus` | 0.1-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `agility` | Ловкость | `dexterity_bonus` | 0.1-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `fortune` | Фортуна | `luck_bonus` | 0.15-0.45 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `elite` | Элита | `rare_power_bonus` | 0.25-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `legend` | Легенда | `epic_power_bonus` | 0.5-1.0 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `synergy` | Синергия | `favorite_power_bonus` | 0.05-0.5 | `waifu_generator.py` | TBD | ❌ Not Implemented |
| `harmony` | Гармония | `rarity_bonus` | 0.05-0.25 | `waifu_generator.py` | TBD | ❌ Not Implemented |

## 🚀 Next Steps

1. Create `skill_effects.py` helper
2. Implement `bargain_hunter` first (user's reported issue)
3. Implement chat gold/XP bonuses
4. Implement waifu power bonuses
5. Test thoroughly with debug menu

## ⚠️ Notes

- Skills are stored in JSONB format: `{"1": {"effect": value}, "2": {"effect": value}}`
- Need to aggregate effects across all skill levels
- Some effects are multiplicative, others are additive
- Max caps exist for some effects (`max_collection_bonus`, etc.)

