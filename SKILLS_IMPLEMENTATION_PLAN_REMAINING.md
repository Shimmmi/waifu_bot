# 📋 План реализации оставшихся 3 навыков

## Обзор

Этот документ содержит подробный план реализации трех навыков, которые требуют дополнительных систем в игре:

1. **`endurance`** (Неутомимость) - Уменьшает расход энергии на действия
2. **`golden_hand`** (Золотая рука) - Увеличивает золото от вайфу за действия
3. **`stamina`** (Выносливость) - Увеличивает максимальное здоровье всех вайфу

---

## 📊 Детальный анализ навыков

### 1. `endurance` - Неутомимость 💪

#### Определение навыка:
- **ID**: `endurance`
- **Название**: Неутомимость
- **Описание**: Уменьшает расход энергии на действия
- **Категория**: `passive` (Waifu Passive Skills)
- **Максимальный уровень**: 3
- **Требования разблокировки**: 9 очков в категории "passive"
- **Стоимость**: 3, 4, 5 очков навыков (для уровней 1, 2, 3)

#### Эффекты по уровням:
```json
{
  "1": {"energy_cost_reduction": 0.2},  // -20% расход энергии
  "2": {"energy_cost_reduction": 0.4},  // -40% расход энергии
  "3": {"energy_cost_reduction": 0.6}   // -60% расход энергии
}
```

#### Текущее состояние:
- ✅ Навык определен в БД (`sql/010_create_skills_system.sql`)
- ✅ Эффект извлекается через `get_user_skill_effects()` в `src/bot/services/skill_effects.py`
- ❌ **НЕ ПРИМЕНЯЕТСЯ** - требуется система действий вайфу

#### Где применяется энергия:
1. **События (Events)**:
   - Файл: `src/bot/services/event_system.py` → `can_participate_in_event()`
   - Файл: `src/bot/handlers/waifu.py` → `handle_random_event()` (строка 414)
   - Файл: `src/bot/handlers/menu.py` → `handle_event_waifu_select_callback()` (строка 1053)
   - Файл: `src/bot/services/group_event_system.py` → `finalize_event()`
   - **Текущий расход**: 20 энергии (hardcoded)

2. **Групповые события**:
   - Файл: `src/bot/services/group_event_system.py`
   - **Текущий расход**: 20 энергии (hardcoded)

#### План реализации:

**Шаг 1: Создать утилиту для расчета расхода энергии**
- Файл: `src/bot/services/energy_cost.py` (NEW)
- Функция: `calculate_energy_cost(base_cost: int, user_id: int, session: Session) -> int`
- Логика:
  ```python
  def calculate_energy_cost(base_cost: int, user_id: int, session: Session) -> int:
      """Рассчитывает стоимость энергии с учетом навыка 'endurance'"""
      from bot.services.skill_effects import get_user_skill_effects
      
      skill_effects = get_user_skill_effects(session, user_id)
      energy_cost_reduction = skill_effects.get('energy_cost_reduction', 0.0)
      
      # Применяем скидку (0.2 = -20%, 0.4 = -40%, 0.6 = -60%)
      reduced_cost = int(base_cost * (1.0 - energy_cost_reduction))
      
      return max(1, reduced_cost)  # Минимум 1 энергия
  ```

**Шаг 2: Заменить hardcoded значения расхода энергии**

**2.1. События (Events)**:
- Файл: `src/bot/handlers/waifu.py`
  - В функции `handle_random_event()`:
    ```python
    # БЫЛО:
    waifu.dynamic["energy"] = max(0, waifu.dynamic["energy"] - 20)
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.energy_cost import calculate_energy_cost
    energy_cost = calculate_energy_cost(20, user.id, session)
    waifu.dynamic["energy"] = max(0, waifu.dynamic["energy"] - energy_cost)
    ```

- Файл: `src/bot/handlers/menu.py`
  - В функции `handle_event_waifu_select_callback()`:
    ```python
    # БЫЛО:
    "energy": max(0, current_energy - 20),
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.energy_cost import calculate_energy_cost
    energy_cost = calculate_energy_cost(20, user.id, session)
    "energy": max(0, current_energy - energy_cost),
    ```

**2.2. Групповые события**:
- Файл: `src/bot/services/group_event_system.py`
  - В функции `finalize_event()`:
    ```python
    # БЫЛО:
    current_energy = int(waifu.dynamic.get("energy", 100))
    waifu.dynamic["energy"] = max(0, current_energy - 20)
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.energy_cost import calculate_energy_cost
    energy_cost = calculate_energy_cost(20, user.id, session)
    current_energy = int(waifu.dynamic.get("energy", 100))
    waifu.dynamic["energy"] = max(0, current_energy - energy_cost)
    ```

**2.3. Проверка возможности участия**:
- Файл: `src/bot/services/event_system.py`
  - В функции `can_participate_in_event()`:
    ```python
    # БЫЛО:
    if energy < 20:
        return False, "Недостаточно энергии для участия"
    
    # ДОЛЖНО БЫТЬ:
    # Требуется передавать user_id в функцию
    # Или создавать отдельную функцию для проверки минимальной энергии
    ```

**Шаг 3: Обновить проверку минимальной энергии**
- Файл: `src/bot/services/event_system.py`
- Добавить функцию: `get_min_energy_required(user_id: int, session: Session) -> int`
- Логика:
  ```python
  def get_min_energy_required(user_id: int, session: Session) -> int:
      """Возвращает минимальную энергию для участия в событии с учетом навыка 'endurance'"""
      from bot.services.energy_cost import calculate_energy_cost
      base_cost = 20
      return calculate_energy_cost(base_cost, user_id, session)
  ```

**Шаг 4: Обновить логирование**
- Добавить логирование применения навыка `endurance`:
  ```python
  logger.info(f"💪 Endurance skill applied: {energy_cost_reduction*100}% reduction, "
              f"energy cost: {base_cost} → {reduced_cost}")
  ```

---

### 2. `golden_hand` - Золотая рука 🤲

#### Определение навыка:
- **ID**: `golden_hand`
- **Название**: Золотая рука
- **Описание**: Увеличивает золото от вайфу за действия
- **Категория**: `passive` (Waifu Passive Skills)
- **Максимальный уровень**: 3
- **Требования разблокировки**: 7 очков в категории "passive"
- **Стоимость**: 2, 3, 4 очков навыков (для уровней 1, 2, 3)

#### Эффекты по уровням:
```json
{
  "1": {"waifu_gold_bonus": 0.1},  // +10% золота
  "2": {"waifu_gold_bonus": 0.2},  // +20% золота
  "3": {"waifu_gold_bonus": 0.3}   // +30% золота
}
```

#### Текущее состояние:
- ✅ Навык определен в БД (`sql/010_create_skills_system.sql`)
- ✅ Эффект извлекается через `get_user_skill_effects()` в `src/bot/services/skill_effects.py`
- ❌ **НЕ ПРИМЕНЯЕТСЯ** - требуется система действий вайфу

#### Где вайфу получают золото:
1. **События (Events)**:
   - Файл: `src/bot/services/event_system.py` → `get_event_rewards()` (строка 41)
   - Файл: `src/bot/handlers/waifu.py` → `handle_random_event()` (строка 420)
   - Файл: `src/bot/handlers/menu.py` → `handle_event_waifu_select_callback()` (строка 1082)
   - **Текущее начисление**: Зависит от очков события, преобразуется в золото

2. **Групповые события**:
   - Файл: `src/bot/services/group_event_system.py` → `finalize_event()`
   - **Текущее начисление**: Зависит от места в рейтинге

#### План реализации:

**Шаг 1: Создать утилиту для расчета золота от действий вайфу**
- Файл: `src/bot/services/waifu_action_rewards.py` (NEW)
- Функция: `apply_waifu_gold_bonus(base_gold: int, user_id: int, session: Session) -> int`
- Логика:
  ```python
  def apply_waifu_gold_bonus(base_gold: int, user_id: int, session: Session) -> int:
      """Применяет бонус 'golden_hand' к золоту от действий вайфу"""
      from bot.services.skill_effects import get_user_skill_effects
      
      skill_effects = get_user_skill_effects(session, user_id)
      waifu_gold_bonus = skill_effects.get('waifu_gold_bonus', 0.0)
      
      if waifu_gold_bonus > 0:
          bonus_gold = int(base_gold * waifu_gold_bonus)
          return base_gold + bonus_gold
      
      return base_gold
  ```

**Шаг 2: Применить бонус к наградам за события**

**2.1. Одиночные события**:
- Файл: `src/bot/handlers/waifu.py`
  - В функции `handle_random_event()`:
    ```python
    # БЫЛО:
    rewards = get_event_rewards(score, event_type)
    user.coins += rewards["coins"]
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.waifu_action_rewards import apply_waifu_gold_bonus
    rewards = get_event_rewards(score, event_type)
    base_coins = rewards["coins"]
    final_coins = apply_waifu_gold_bonus(base_coins, user.id, session)
    user.coins += final_coins
    ```

- Файл: `src/bot/handlers/menu.py`
  - В функции `handle_event_waifu_select_callback()`:
    ```python
    # БЫЛО:
    rewards = get_event_rewards(score, event_type)
    user.coins += rewards["coins"]
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.waifu_action_rewards import apply_waifu_gold_bonus
    rewards = get_event_rewards(score, event_type)
    base_coins = rewards["coins"]
    final_coins = apply_waifu_gold_bonus(base_coins, user.id, session)
    user.coins += final_coins
    ```

**2.2. Групповые события**:
- Файл: `src/bot/services/group_event_system.py`
  - В функции `finalize_event()`:
    ```python
    # БЫЛО:
    coins = base_rewards["coins"]
    user.coins += coins
    
    # ДОЛЖНО БЫТЬ:
    from bot.services.waifu_action_rewards import apply_waifu_gold_bonus
    base_coins = base_rewards["coins"]
    final_coins = apply_waifu_gold_bonus(base_coins, user.id, session)
    user.coins += final_coins
    ```

**Шаг 3: Обновить логирование**
- Добавить логирование применения навыка `golden_hand`:
  ```python
  logger.info(f"🤲 Golden Hand skill applied: +{waifu_gold_bonus*100}%, "
              f"gold: {base_coins} → {final_coins}")
  ```

---

### 3. `stamina` - Выносливость ❤️‍🩹

#### Определение навыка:
- **ID**: `stamina`
- **Название**: Выносливость
- **Описание**: Увеличивает максимальное здоровье всех вайфу
- **Категория**: `training` (Waifu Training)
- **Максимальный уровень**: 3
- **Требования разблокировки**: 18 очков в категории "training"
- **Стоимость**: 3, 4, 5 очков навыков (для уровней 1, 2, 3)

#### Эффекты по уровням:
```json
{
  "1": {"health_bonus": 0.2},  // +20% максимального здоровья
  "2": {"health_bonus": 0.4},  // +40% максимального здоровья
  "3": {"health_bonus": 0.6}   // +60% максимального здоровья
}
```

#### Текущее состояние:
- ✅ Навык определен в БД (`sql/010_create_skills_system.sql`)
- ✅ Эффект извлекается через `get_user_skill_effects()` в `src/bot/services/skill_effects.py`
- ❌ **НЕ ПРИМЕНЯЕТСЯ** - требуется система здоровья/боя

#### Текущая система здоровья:
- ❌ **ОТСУТСТВУЕТ** - в базе данных нет поля `health` или `hp` у вайфу
- ❌ **ОТСУТСТВУЕТ** - нет боевой системы
- ❌ **ОТСУТСТВУЕТ** - нет системы урона

#### План реализации:

**Шаг 1: Добавить поле здоровья в модель Waifu**
- Файл: `src/bot/models.py`
- Добавить поле в модель `Waifu`:
  ```python
  health = Column(Integer, default=100)  # Текущее здоровье
  max_health = Column(Integer, default=100)  # Максимальное здоровье
  ```
- Или использовать JSONB поле `dynamic`:
  ```python
  # В dynamic добавить:
  {
      "health": 100,
      "max_health": 100
  }
  ```

**Шаг 2: Создать SQL миграцию**
- Файл: `sql/014_add_waifu_health.sql` (NEW)
- Содержимое:
  ```sql
  -- Добавляем поля здоровья в таблицу waifu
  ALTER TABLE waifu 
  ADD COLUMN IF NOT EXISTS health INTEGER DEFAULT 100,
  ADD COLUMN IF NOT EXISTS max_health INTEGER DEFAULT 100;

  -- Или обновить JSONB поле dynamic для существующих вайфу
  UPDATE waifu
  SET dynamic = jsonb_set(
      COALESCE(dynamic, '{}'::jsonb),
      '{health}',
      '100'::jsonb,
      true
  )
  WHERE dynamic->>'health' IS NULL;

  UPDATE waifu
  SET dynamic = jsonb_set(
      dynamic,
      '{max_health}',
      '100'::jsonb,
      true
  )
  WHERE dynamic->>'max_health' IS NULL;
  ```

**Шаг 3: Создать утилиту для расчета максимального здоровья**
- Файл: `src/bot/services/waifu_health.py` (NEW)
- Функция: `calculate_max_health(base_health: int, user_id: int, session: Session) -> int`
- Логика:
  ```python
  def calculate_max_health(base_health: int, user_id: int, session: Session) -> int:
      """Рассчитывает максимальное здоровье вайфу с учетом навыка 'stamina'"""
      from bot.services.skill_effects import get_user_skill_effects
      
      skill_effects = get_user_skill_effects(session, user_id)
      health_bonus = skill_effects.get('health_bonus', 0.0)
      
      if health_bonus > 0:
          bonus_health = int(base_health * health_bonus)
          return base_health + bonus_health
      
      return base_health
  ```

**Шаг 4: Применить бонус при создании вайфу**
- Файл: `src/bot/services/waifu_generator.py`
- В функции `generate_waifu()`:
  ```python
  # Добавить после генерации базовых характеристик:
  from bot.services.waifu_health import calculate_max_health
  
  base_max_health = 100
  max_health = calculate_max_health(base_max_health, user_id, session)
  
  waifu_data["dynamic"]["health"] = max_health
  waifu_data["dynamic"]["max_health"] = max_health
  ```

**Шаг 5: Обновить восстановление здоровья (если будет система восстановления)**
- Файл: `src/bot/services/stat_restoration.py` (если будет добавлено восстановление здоровья)
- Применить `calculate_max_health()` при восстановлении здоровья до максимума

**Шаг 6: Применить бонус к существующим вайфу (опционально)**
- Создать утилиту для пересчета максимального здоровья всех вайфу:
  ```python
  def recalculate_all_waifu_max_health(session: Session):
      """Пересчитывает максимальное здоровье всех вайфу с учетом навыка 'stamina'"""
      from bot.models import Waifu, User
      
      waifus = session.query(Waifu).all()
      
      for waifu in waifus:
          user = session.query(User).filter(User.id == waifu.owner_id).first()
          if user:
              base_max_health = 100
              new_max_health = calculate_max_health(base_max_health, user.id, session)
              
              # Обновляем max_health, но не увеличиваем текущее здоровье выше текущего значения
              current_health = waifu.dynamic.get("health", 100)
              waifu.dynamic["max_health"] = new_max_health
              waifu.dynamic["health"] = min(current_health, new_max_health)
              
              flag_modified(waifu, "dynamic")
      
      session.commit()
  ```

**Примечание**: Реализация навыка `stamina` требует предварительной реализации системы здоровья/боя. Если такой системы нет, навык будет готов к применению, но не будет использоваться до тех пор, пока не будет реализована система здоровья.

---

## 📝 Приоритеты реализации

### Высокий приоритет:
1. **`endurance`** (Неутомимость) - ✅ Можно реализовать сразу, система событий уже существует
2. **`golden_hand`** (Золотая рука) - ✅ Можно реализовать сразу, система событий уже существует

### Низкий приоритет:
3. **`stamina`** (Выносливость) - ⏳ Требует реализации системы здоровья/боя

---

## 🧪 Тестирование

### Тест 1: `endurance`
1. Прокачать навык `endurance` до уровня 1 (требуется 9 очков в категории "passive")
2. Участвовать в событии
3. Проверить, что расходуется 16 энергии вместо 20 (20 * 0.8 = 16)
4. Прокачать навык до уровня 3 (требуется 3 + 4 + 5 = 12 очков навыков)
5. Проверить, что расходуется 8 энергии вместо 20 (20 * 0.4 = 8)

### Тест 2: `golden_hand`
1. Прокачать навык `golden_hand` до уровня 1 (требуется 7 очков в категории "passive")
2. Участвовать в событии и получить 100 золота
3. Проверить, что начисляется 110 золота (100 * 1.1 = 110)
4. Прокачать навык до уровня 3 (требуется 2 + 3 + 4 = 9 очков навыков)
5. Проверить, что начисляется 130 золота (100 * 1.3 = 130)

### Тест 3: `stamina`
1. Реализовать систему здоровья
2. Прокачать навык `stamina` до уровня 1 (требуется 18 очков в категории "training")
3. Призвать новую вайфу
4. Проверить, что максимальное здоровье = 120 (100 * 1.2 = 120)
5. Прокачать навык до уровня 3 (требуется 3 + 4 + 5 = 12 очков навыков)
6. Проверить, что максимальное здоровье = 160 (100 * 1.6 = 160)

---

## 📚 Связанные файлы

### Для `endurance`:
- `src/bot/services/energy_cost.py` (NEW)
- `src/bot/handlers/waifu.py`
- `src/bot/handlers/menu.py`
- `src/bot/services/group_event_system.py`
- `src/bot/services/event_system.py`

### Для `golden_hand`:
- `src/bot/services/waifu_action_rewards.py` (NEW)
- `src/bot/handlers/waifu.py`
- `src/bot/handlers/menu.py`
- `src/bot/services/group_event_system.py`
- `src/bot/services/event_system.py`

### Для `stamina`:
- `sql/014_add_waifu_health.sql` (NEW)
- `src/bot/services/waifu_health.py` (NEW)
- `src/bot/services/waifu_generator.py`
- `src/bot/models.py` (опционально, если добавляем отдельные поля)

---

## ✅ Чеклист реализации

### `endurance`:
- [ ] Создать `src/bot/services/energy_cost.py`
- [ ] Реализовать функцию `calculate_energy_cost()`
- [ ] Обновить `src/bot/handlers/waifu.py`
- [ ] Обновить `src/bot/handlers/menu.py`
- [ ] Обновить `src/bot/services/group_event_system.py`
- [ ] Обновить `src/bot/services/event_system.py`
- [ ] Добавить логирование
- [ ] Протестировать

### `golden_hand`:
- [ ] Создать `src/bot/services/waifu_action_rewards.py`
- [ ] Реализовать функцию `apply_waifu_gold_bonus()`
- [ ] Обновить `src/bot/handlers/waifu.py`
- [ ] Обновить `src/bot/handlers/menu.py`
- [ ] Обновить `src/bot/services/group_event_system.py`
- [ ] Добавить логирование
- [ ] Протестировать

### `stamina`:
- [ ] Реализовать систему здоровья/боя (если требуется)
- [ ] Создать `sql/014_add_waifu_health.sql`
- [ ] Создать `src/bot/services/waifu_health.py`
- [ ] Реализовать функцию `calculate_max_health()`
- [ ] Обновить `src/bot/services/waifu_generator.py`
- [ ] Добавить логирование
- [ ] Протестировать

---

## 🔍 Дополнительные заметки

1. **Совместимость с существующими системами**:
   - Все три навыка должны работать вместе с существующими системами событий
   - Не должны конфликтовать с другими навыками

2. **Производительность**:
   - `get_user_skill_effects()` вызывается для каждого действия вайфу
   - Рекомендуется кэширование эффектов навыков для пользователя на сессию

3. **Логирование**:
   - Все применения навыков должны логироваться для отладки
   - Использовать `logger.info()` для успешных применений
   - Использовать `logger.error()` для ошибок

4. **Обратная совместимость**:
   - Если навык не прокачан, система должна работать как раньше
   - Не должно быть ошибок, если навык не найден в БД
