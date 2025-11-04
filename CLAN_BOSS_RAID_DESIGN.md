# 🐉 Дизайн-документ: Клановые рейды на боссов

## 📋 Обзор

Система клановых рейдов на боссов, где здоровье босса уменьшается на основе активности игроков в групповых чатах Telegram. Каждое действие игрока (сообщение, стикер, видео и т.д.) наносит урон боссу, а награды распределяются пропорционально вкладу каждого участника.

---

## 🎯 Основные принципы

### 1. **Здоровье босса = Активность клана**
- Босс имеет большое количество HP (например, 100,000 - 1,000,000+)
- Каждое действие игрока в групповых чатах уменьшает HP босса
- Рейд длится определенное время (например, 24-72 часа) или до победы

### 2. **Урон от действий**
Разные типы действий наносят разный урон:
- **Текстовое сообщение** (≥5 символов) = **-1 HP**
- **Стикер/GIF** = **-2 HP**
- **Изображение** = **-3 HP**
- **Видео** = **-5 HP**
- **Голосовое сообщение** = **-4 HP**
- **Ссылка в сообщении** = **-5 HP**
- **Документ** = **-2 HP**

### 3. **Награды по вкладу**
- Распределение наград основано на общем уроне, нанесенном каждым игроком
- Топ-игроки получают бонусные награды
- Все участники получают базовые награды пропорционально вкладу

---

## 🏗️ Архитектура системы

### 1. **База данных**

#### 1.1. Расширение таблицы `clan_events`
Добавить в `data` JSONB поле для хранения информации о боссе:
```sql
-- data структура для raid:
{
  "boss_name": "Дракон Клана",
  "boss_max_hp": 500000,
  "boss_current_hp": 375000,
  "damage_dealt": 125000,
  "participant_count": 23,
  "activity_tracking": true  // Флаг для отслеживания активности
}
```

#### 1.2. Новая таблица `clan_raid_activity`
Для отслеживания активности каждого участника:
```sql
CREATE TABLE IF NOT EXISTS clan_raid_activity (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES clan_events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_id BIGINT NOT NULL,  -- Telegram chat ID
    message_type VARCHAR(20) NOT NULL,  -- 'text', 'sticker', 'photo', 'video', 'voice', 'link'
    damage_dealt INTEGER NOT NULL DEFAULT 0,  -- Урон от этого действия
    message_id BIGINT,  -- Telegram message ID (для отслеживания)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, user_id, message_id)  -- Одно сообщение = один урон
);

CREATE INDEX IF NOT EXISTS idx_raid_activity_event_id ON clan_raid_activity(event_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_user_id ON clan_raid_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_chat_id ON clan_raid_activity(chat_id);
CREATE INDEX IF NOT EXISTS idx_raid_activity_created_at ON clan_raid_activity(created_at);
```

#### 1.3. Обновление `clan_event_participations`
Добавить дополнительные поля для отслеживания:
```sql
-- contribution структура для raid:
{
  "total_damage": 5000,  // Общий урон
  "message_count": 2500,  // Количество сообщений
  "damage_by_type": {
    "text": 1500,
    "sticker": 800,
    "photo": 600,
    "video": 200,
    "voice": 400
  },
  "participation_rate": 0.85  // Процент активности от общего урона клана
}
```

---

## 🔧 Техническая реализация

### 2. **Обработка сообщений в групповых чатах**

#### 2.1. Модификация `message_handler.py`
Добавить логику проверки активных рейдов и нанесения урона:

```python
# src/bot/handlers/message_handler.py

from bot.models import ClanMember, ClanEvent, ClanRaidActivity
from bot.services.clan_raid import ClanRaidService

@router.message()
async def handle_group_message(message: Message) -> None:
    """Handle messages in groups for global XP awarding and clan raid damage."""
    
    # ... существующая логика для XP ...
    
    # Проверяем активные рейды клана
    if user:
        raid_service = ClanRaidService()
        await raid_service.process_message_for_raid(
            session=session,
            user_id=user.id,
            chat_id=message.chat.id,
            message=message
        )
```

#### 2.2. Новый сервис `ClanRaidService`
Создать файл `src/bot/services/clan_raid.py`:

```python
"""
Clan Raid Service

Обрабатывает активность игроков в групповых чатах для нанесения урона боссу.
"""

class ClanRaidService:
    # Таблица урона по типам сообщений
    DAMAGE_BY_MESSAGE_TYPE = {
        "text": 1,
        "sticker": 2,
        "photo": 3,
        "video": 5,
        "voice": 4,
        "link": 5,
        "document": 2,
        "animation": 2,  # GIF
    }
    
    async def process_message_for_raid(
        self,
        session: Session,
        user_id: int,
        chat_id: int,
        message: Message
    ) -> Optional[Dict]:
        """
        Обрабатывает сообщение для активного рейда клана.
        
        Returns:
            Dict с информацией об уроне или None, если рейдов нет
        """
        # 1. Проверяем, состоит ли пользователь в клане
        member = session.query(ClanMember).filter(
            ClanMember.user_id == user_id
        ).first()
        
        if not member:
            return None
        
        # 2. Ищем активный рейд для клана
        raid_event = session.query(ClanEvent).filter(
            and_(
                ClanEvent.clan_id == member.clan_id,
                ClanEvent.event_type == 'raid',
                ClanEvent.status == 'active'
            )
        ).first()
        
        if not raid_event:
            return None
        
        # 3. Проверяем, что рейд отслеживает активность
        event_data = raid_event.data or {}
        if not event_data.get('activity_tracking', False):
            return None
        
        # 4. Определяем тип сообщения и урон
        message_type, damage = self._get_message_damage(message)
        
        if damage == 0:
            return None  # Нет урона (например, текст < 5 символов)
        
        # 5. Проверяем, не обработано ли уже это сообщение
        existing_activity = session.query(ClanRaidActivity).filter(
            and_(
                ClanRaidActivity.event_id == raid_event.id,
                ClanRaidActivity.user_id == user_id,
                ClanRaidActivity.message_id == message.message_id
            )
        ).first()
        
        if existing_activity:
            return None  # Уже обработано
        
        # 6. Сохраняем активность
        activity = ClanRaidActivity(
            event_id=raid_event.id,
            user_id=user_id,
            chat_id=chat_id,
            message_type=message_type,
            damage_dealt=damage,
            message_id=message.message_id
        )
        session.add(activity)
        
        # 7. Обновляем HP босса
        current_hp = event_data.get('boss_current_hp', 0)
        new_hp = max(0, current_hp - damage)
        event_data['boss_current_hp'] = new_hp
        event_data['damage_dealt'] = event_data.get('damage_dealt', 0) + damage
        
        # 8. Обновляем участие пользователя
        participation = session.query(ClanEventParticipation).filter(
            and_(
                ClanEventParticipation.event_id == raid_event.id,
                ClanEventParticipation.user_id == user_id
            )
        ).first()
        
        if not participation:
            participation = ClanEventParticipation(
                event_id=raid_event.id,
                user_id=user_id,
                score=damage,
                contribution={
                    'total_damage': damage,
                    'message_count': 1,
                    'damage_by_type': {message_type: damage}
                }
            )
            session.add(participation)
        else:
            # Обновляем существующее участие
            participation.score += damage
            contribution = participation.contribution or {}
            contribution['total_damage'] = contribution.get('total_damage', 0) + damage
            contribution['message_count'] = contribution.get('message_count', 0) + 1
            
            damage_by_type = contribution.get('damage_by_type', {})
            damage_by_type[message_type] = damage_by_type.get(message_type, 0) + damage
            contribution['damage_by_type'] = damage_by_type
            
            participation.contribution = contribution
            flag_modified(participation, 'contribution')
        
        # 9. Проверяем, побежден ли босс
        if new_hp <= 0:
            await self._finalize_raid(session, raid_event)
        
        # 10. Обновляем событие
        raid_event.data = event_data
        flag_modified(raid_event, 'data')
        
        session.commit()
        
        return {
            'damage': damage,
            'boss_hp': new_hp,
            'boss_max_hp': event_data.get('boss_max_hp', 0),
            'boss_defeated': new_hp <= 0
        }
    
    def _get_message_damage(self, message: Message) -> Tuple[str, int]:
        """
        Определяет тип сообщения и соответствующий урон.
        
        Returns:
            (message_type, damage)
        """
        # Проверка текстового сообщения
        if message.text:
            text_length = len(message.text.strip())
            if text_length >= 5:
                # Проверка на ссылки
                if message.entities:
                    for entity in message.entities:
                        if entity.type in ["url", "text_link"]:
                            return ("link", self.DAMAGE_BY_MESSAGE_TYPE["link"])
                return ("text", self.DAMAGE_BY_MESSAGE_TYPE["text"])
            return ("text", 0)  # Слишком короткое сообщение
        
        # Проверка других типов
        if message.sticker:
            return ("sticker", self.DAMAGE_BY_MESSAGE_TYPE["sticker"])
        if message.photo:
            return ("photo", self.DAMAGE_BY_MESSAGE_TYPE["photo"])
        if message.video or message.video_note:
            return ("video", self.DAMAGE_BY_MESSAGE_TYPE["video"])
        if message.voice:
            return ("voice", self.DAMAGE_BY_MESSAGE_TYPE["voice"])
        if message.document:
            return ("document", self.DAMAGE_BY_MESSAGE_TYPE["document"])
        if message.animation:
            return ("animation", self.DAMAGE_BY_MESSAGE_TYPE["animation"])
        
        return ("unknown", 0)
    
    async def _finalize_raid(
        self,
        session: Session,
        raid_event: ClanEvent
    ) -> None:
        """
        Завершает рейд, распределяет награды и отправляет уведомления.
        """
        # 1. Обновляем статус рейда
        raid_event.status = 'completed'
        raid_event.ends_at = datetime.utcnow()
        
        # 2. Получаем всех участников с их уроном
        participations = session.query(ClanEventParticipation).filter(
            ClanEventParticipation.event_id == raid_event.id
        ).order_by(ClanEventParticipation.score.desc()).all()
        
        if not participations:
            session.commit()
            return
        
        # 3. Вычисляем общий урон для расчета процентов
        total_damage = sum(p.score for p in participations)
        
        # 4. Распределяем награды
        base_rewards = {
            'gold': 5000,  # Базовое золото за победу
            'gems': 100,   # Базовые гемы
            'skill_points': 50  # Базовые очки навыков
        }
        
        # 5. Награждаем каждого участника
        for idx, participation in enumerate(participations):
            user = session.query(User).filter(User.id == participation.user_id).first()
            if not user:
                continue
            
            # Базовые награды пропорционально вкладу
            contribution_rate = participation.score / total_damage if total_damage > 0 else 0
            
            gold_reward = int(base_rewards['gold'] * contribution_rate)
            gems_reward = int(base_rewards['gems'] * contribution_rate)
            skill_points_reward = int(base_rewards['skill_points'] * contribution_rate)
            
            # Бонусы за место в топе
            if idx == 0:  # 1 место
                gold_reward += 5000
                gems_reward += 200
                skill_points_reward += 100
            elif idx == 1:  # 2 место
                gold_reward += 3000
                gems_reward += 150
                skill_points_reward += 75
            elif idx == 2:  # 3 место
                gold_reward += 2000
                gems_reward += 100
                skill_points_reward += 50
            elif idx < 10:  # Топ-10
                gold_reward += 1000
                gems_reward += 50
                skill_points_reward += 25
            
            # Выдаем награды
            user.coins += gold_reward
            user.gems += gems_reward
            
            # Обновляем очки навыков
            try:
                from bot.models import UserSkills
                user_skills = session.query(UserSkills).filter(
                    UserSkills.user_id == user.id
                ).first()
                if user_skills:
                    user_skills.skill_points += skill_points_reward
            except:
                pass
            
            # Сохраняем награды в participation
            participation.contribution['rewards'] = {
                'gold': gold_reward,
                'gems': gems_reward,
                'skill_points': skill_points_reward
            }
            flag_modified(participation, 'contribution')
        
        # 6. Обновляем опыт клана
        clan = session.query(Clan).filter(Clan.id == raid_event.clan_id).first()
        if clan:
            clan.experience += 500  # Бонус опыта за победу в рейде
        
        # 7. Сохраняем награды в событии
        raid_event.rewards = {
            'distributed': True,
            'total_participants': len(participations),
            'total_damage': total_damage
        }
        
        session.commit()
        
        # 8. Отправляем уведомления (асинхронно)
        # TODO: Реализовать отправку уведомлений в клановый чат
        
        logger.info(f"✅ Raid {raid_event.id} completed! Total damage: {total_damage}")
```

---

### 3. **API Endpoints**

#### 3.1. Обновление существующих endpoints

**`POST /api/clans/raid/start`**
- Добавить параметр `activity_tracking: bool = True`
- Установить `activity_tracking` в `data` рейда

**`GET /api/clans/raid/status`** (новый)
```python
@router.get("/api/clans/raid/status")
async def get_raid_status(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получить статус активного рейда"""
    user = get_user_from_request(request, db)
    member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Вы не состоите в клане")
    
    raid_event = db.query(ClanEvent).filter(
        and_(
            ClanEvent.clan_id == member.clan_id,
            ClanEvent.event_type == 'raid',
            ClanEvent.status == 'active'
        )
    ).first()
    
    if not raid_event:
        return {"active": False}
    
    event_data = raid_event.data or {}
    
    # Получаем статистику участников
    participations = db.query(ClanEventParticipation).filter(
        ClanEventParticipation.event_id == raid_event.id
    ).order_by(ClanEventParticipation.score.desc()).limit(10).all()
    
    leaderboard = []
    for p in participations:
        participant_user = db.query(User).filter(User.id == p.user_id).first()
        if participant_user:
            leaderboard.append({
                'username': participant_user.display_name or participant_user.username,
                'damage': p.score,
                'contribution': p.contribution
            })
    
    return {
        "active": True,
        "boss_name": event_data.get('boss_name', 'Дракон Клана'),
        "boss_max_hp": event_data.get('boss_max_hp', 0),
        "boss_current_hp": event_data.get('boss_current_hp', 0),
        "damage_dealt": event_data.get('damage_dealt', 0),
        "hp_percentage": (event_data.get('boss_current_hp', 0) / event_data.get('boss_max_hp', 1)) * 100,
        "leaderboard": leaderboard,
        "ends_at": raid_event.ends_at.isoformat() if raid_event.ends_at else None
    }
```

**`GET /api/clans/raid/my-contribution`** (новый)
```python
@router.get("/api/clans/raid/my-contribution")
async def get_my_contribution(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получить свой вклад в активный рейд"""
    user = get_user_from_request(request, db)
    member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
    
    if not member:
        raise HTTPException(status_code=403, detail="Вы не состоите в клане")
    
    raid_event = db.query(ClanEvent).filter(
        and_(
            ClanEvent.clan_id == member.clan_id,
            ClanEvent.event_type == 'raid',
            ClanEvent.status == 'active'
        )
    ).first()
    
    if not raid_event:
        return {"participating": False}
    
    participation = db.query(ClanEventParticipation).filter(
        and_(
            ClanEventParticipation.event_id == raid_event.id,
            ClanEventParticipation.user_id == user.id
        )
    ).first()
    
    if not participation:
        return {"participating": False, "damage": 0}
    
    # Получаем общий урон клана
    total_damage = db.query(
        func.sum(ClanEventParticipation.score)
    ).filter(
        ClanEventParticipation.event_id == raid_event.id
    ).scalar() or 0
    
    contribution_rate = (participation.score / total_damage * 100) if total_damage > 0 else 0
    
    return {
        "participating": True,
        "damage": participation.score,
        "contribution_percentage": round(contribution_rate, 2),
        "message_count": participation.contribution.get('message_count', 0),
        "damage_by_type": participation.contribution.get('damage_by_type', {})
    }
```

---

### 4. **Расчет HP босса**

#### 4.1. Формула расчета
```python
def calculate_boss_hp(clan: Clan, session: Session) -> int:
    """
    Рассчитывает максимальное HP босса на основе силы клана.
    
    Формула:
    - Базовая сила клана = sum(мощь активных вайфу всех участников)
    - HP босса = Базовая сила × коэффициент сложности × коэффициент уровня клана
    
    Коэффициенты:
    - Базовая сложность: 100 (босс должен быть достаточно сильным)
    - Множитель уровня клана: 1 + (уровень_клана * 0.1)
    
    Пример:
    - Клан с силой 50,000, уровень 10
    - HP = 50,000 × 100 × (1 + 10 × 0.1) = 50,000 × 100 × 2 = 10,000,000 HP
    """
    # Получаем всех участников
    members = session.query(ClanMember).filter(
        ClanMember.clan_id == clan.id
    ).all()
    
    total_power = 0
    for member in members:
        waifu = session.query(Waifu).filter(
            and_(
                Waifu.owner_id == member.user_id,
                Waifu.is_active == True
            )
        ).first()
        
        if waifu:
            from bot.services.waifu_generator import calculate_waifu_power
            from bot.services.skill_effects import get_user_skill_effects
            
            skill_effects = get_user_skill_effects(session, member.user_id)
            power = calculate_waifu_power({
                'stats': waifu.stats or {},
                'dynamic': waifu.dynamic or {},
                'level': waifu.level,
                'rarity': waifu.rarity
            }, skill_effects)
            
            total_power += power
    
    # Базовая сложность
    BASE_DIFFICULTY = 100
    
    # Множитель уровня клана
    level_multiplier = 1 + (clan.level * 0.1)
    
    # Рассчитываем HP
    boss_hp = int(total_power * BASE_DIFFICULTY * level_multiplier)
    
    # Минимальное HP (для маленьких кланов)
    min_hp = 100000
    boss_hp = max(boss_hp, min_hp)
    
    return boss_hp
```

---

## 🎮 UI/UX изменения

### 5. **Веб-интерфейс**

#### 5.1. Страница рейда в WebApp
Обновить `webapp/app.js` для отображения активного рейда:

```javascript
// Функция для загрузки статуса рейда
async function loadRaidStatus() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const response = await fetch(`/api/clans/raid/status?${new URLSearchParams({ initData })}`);
    
    if (!response.ok) {
        return null;
    }
    
    const data = await response.json();
    return data;
}

// Отображение рейда в UI клана
async function renderRaidSection(container) {
    const raidStatus = await loadRaidStatus();
    
    if (!raidStatus || !raidStatus.active) {
        // Нет активного рейда
        container.innerHTML = `
            <div style="padding: 16px; text-align: center; background: #f5f5f5; border-radius: 8px;">
                <h3 style="margin: 0 0 8px 0;">🐉 Клановый рейд</h3>
                <p style="margin: 0 0 16px 0; color: #666;">Активных рейдов нет</p>
                <button onclick="startRaid()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    Начать рейд
                </button>
            </div>
        `;
        return;
    }
    
    const hpPercent = raidStatus.hp_percentage.toFixed(1);
    const hpBarColor = hpPercent > 50 ? '#4ade80' : hpPercent > 25 ? '#fbbf24' : '#ef4444';
    
    container.innerHTML = `
        <div style="padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white;">
            <h3 style="margin: 0 0 12px 0; font-size: 20px;">🐉 ${raidStatus.boss_name}</h3>
            
            <!-- Прогресс HP -->
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 12px;">
                    <span>HP: ${raidStatus.boss_current_hp.toLocaleString()} / ${raidStatus.boss_max_hp.toLocaleString()}</span>
                    <span>${hpPercent}%</span>
                </div>
                <div style="background: rgba(255,255,255,0.2); border-radius: 4px; height: 20px; overflow: hidden;">
                    <div style="background: ${hpBarColor}; height: 100%; width: ${hpPercent}%; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <!-- Урон -->
            <div style="margin-bottom: 12px; font-size: 14px;">
                💥 Нанесено урона: <strong>${raidStatus.damage_dealt.toLocaleString()}</strong>
            </div>
            
            <!-- Мой вклад -->
            <div id="my-raid-contribution" style="margin-bottom: 16px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 4px; font-size: 14px;">
                Загрузка...
            </div>
            
            <!-- Лидерборд -->
            <div>
                <h4 style="margin: 0 0 8px 0; font-size: 16px;">🏆 Топ участников:</h4>
                <div style="max-height: 200px; overflow-y: auto;">
                    ${raidStatus.leaderboard.map((entry, idx) => `
                        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 13px;">
                            <span>${idx + 1}. ${entry.username}</span>
                            <span>💥 ${entry.damage.toLocaleString()}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    // Загружаем мой вклад
    loadMyContribution();
}

// Загрузка моего вклада
async function loadMyContribution() {
    const initData = window.Telegram?.WebApp?.initData || '';
    const response = await fetch(`/api/clans/raid/my-contribution?${new URLSearchParams({ initData })}`);
    
    if (!response.ok) {
        return;
    }
    
    const data = await response.json();
    const container = document.getElementById('my-raid-contribution');
    
    if (!container) return;
    
    if (!data.participating) {
        container.innerHTML = `
            <div style="text-align: center; color: rgba(255,255,255,0.8);">
                📝 Напишите что-нибудь в групповом чате, чтобы нанести урон боссу!
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div>
            <div style="font-weight: bold; margin-bottom: 6px;">Ваш вклад:</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>💥 Урон:</span>
                <span><strong>${data.damage.toLocaleString()}</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>📝 Сообщений:</span>
                <span><strong>${data.message_count}</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>📊 Вклад:</span>
                <span><strong>${data.contribution_percentage}%</strong></span>
            </div>
        </div>
    `;
}

// Автообновление статуса рейда (каждые 5 секунд)
let raidStatusInterval = null;

function startRaidStatusAutoRefresh() {
    if (raidStatusInterval) {
        clearInterval(raidStatusInterval);
    }
    
    raidStatusInterval = setInterval(async () => {
        const clanContainer = document.getElementById('clan-section');
        if (clanContainer && currentView === 'clan') {
            await renderRaidSection(clanContainer.querySelector('#raid-section'));
        }
    }, 5000);
}

function stopRaidStatusAutoRefresh() {
    if (raidStatusInterval) {
        clearInterval(raidStatusInterval);
        raidStatusInterval = null;
    }
}
```

---

## 📊 Примеры расчетов

### 6. **Примеры**

#### Пример 1: Маленький клан (10 участников)
- Средняя мощность вайфу: 5,000
- Общая сила клана: 50,000
- Уровень клана: 5
- **HP босса**: 50,000 × 100 × 1.5 = **7,500,000 HP**

#### Пример 2: Средний клан (25 участников)
- Средняя мощность вайфу: 10,000
- Общая сила клана: 250,000
- Уровень клана: 15
- **HP босса**: 250,000 × 100 × 2.5 = **62,500,000 HP**

#### Пример 3: Большой клан (50 участников)
- Средняя мощность вайфу: 15,000
- Общая сила клана: 750,000
- Уровень клана: 25
- **HP босса**: 750,000 × 100 × 3.5 = **262,500,000 HP**

---

## 🎯 Награды

### 7. **Система наград**

#### Базовые награды (пропорционально вкладу):
- **Золото**: 5,000 × (ваш_урон / общий_урон)
- **Гемы**: 100 × (ваш_урон / общий_урон)
- **Очки навыков**: 50 × (ваш_урон / общий_урон)

#### Бонусы за место:
- **1 место**: +5,000 золота, +200 гемов, +100 очков навыков
- **2 место**: +3,000 золота, +150 гемов, +75 очков навыков
- **3 место**: +2,000 золота, +100 гемов, +50 очков навыков
- **Топ-10**: +1,000 золота, +50 гемов, +25 очков навыков

#### Клановые награды:
- **Опыт клана**: +500 опыта за победу
- **Достижения**: Разблокировка достижений клана

---

## 🔄 Жизненный цикл рейда

### 8. **Этапы рейда**

1. **Запуск рейда** (лидер/офицер):
   - Выбирается босс
   - Рассчитывается HP на основе силы клана
   - Устанавливается время окончания (24-72 часа)
   - Включается отслеживание активности

2. **Активная фаза**:
   - Игроки пишут в групповые чаты
   - Каждое сообщение уменьшает HP босса
   - Реальный таймлайн обновляется каждые 5 секунд в WebApp
   - Лидерборд обновляется в реальном времени

3. **Победа**:
   - Когда HP босса достигает 0
   - Автоматически распределяются награды
   - Отправляются уведомления всем участникам
   - Обновляется опыт клана

4. **Таймаут** (если не победили):
   - Рейд завершается по времени
   - Частичные награды за прогресс
   - Босс остается непобежденным

---

## ⚙️ Настройки и балансировка

### 9. **Параметры для настройки**

```python
# Константы для балансировки
RAID_CONFIG = {
    'min_duration_hours': 24,      # Минимальная длительность
    'max_duration_hours': 72,       # Максимальная длительность
    'base_difficulty': 100,         # Базовая сложность (множитель HP)
    'level_multiplier': 0.1,        # Множитель уровня клана
    'min_boss_hp': 100000,          # Минимальное HP босса
    'damage_text': 1,               # Урон от текста
    'damage_sticker': 2,            # Урон от стикера
    'damage_photo': 3,              # Урон от фото
    'damage_video': 5,              # Урон от видео
    'damage_voice': 4,              # Урон от голосового
    'damage_link': 5,               # Урон от ссылки
    'base_reward_gold': 5000,       # Базовое золото
    'base_reward_gems': 100,        # Базовые гемы
    'base_reward_skill_points': 50, # Базовые очки навыков
    'clan_exp_reward': 500,         # Опыт клана за победу
}
```

---

## 📝 Чеклист реализации

### 10. **Этапы разработки**

#### Фаза 1: База данных и модели
- [ ] Создать таблицу `clan_raid_activity`
- [ ] Создать модель `ClanRaidActivity`
- [ ] Обновить модель `ClanEvent` для поддержки `activity_tracking`
- [ ] SQL миграция для новых таблиц

#### Фаза 2: Обработка сообщений
- [ ] Создать сервис `ClanRaidService`
- [ ] Интегрировать обработку рейдов в `message_handler.py`
- [ ] Реализовать определение типа сообщения и урона
- [ ] Реализовать предотвращение дублирования обработки

#### Фаза 3: API Endpoints
- [ ] Обновить `POST /api/clans/raid/start` для включения `activity_tracking`
- [ ] Создать `GET /api/clans/raid/status`
- [ ] Создать `GET /api/clans/raid/my-contribution`
- [ ] Реализовать автоматическое завершение рейда при HP = 0

#### Фаза 4: Распределение наград
- [ ] Реализовать функцию `_finalize_raid`
- [ ] Реализовать расчет наград по вкладу
- [ ] Реализовать бонусы за место в топе
- [ ] Добавить обновление опыта клана

#### Фаза 5: UI/UX
- [ ] Обновить WebApp для отображения активного рейда
- [ ] Добавить прогресс-бар HP босса
- [ ] Добавить лидерборд участников
- [ ] Добавить отображение личного вклада
- [ ] Реализовать автообновление статуса рейда

#### Фаза 6: Тестирование и балансировка
- [ ] Тестирование с маленьким кланом
- [ ] Тестирование со средним кланом
- [ ] Тестирование с большим кланом
- [ ] Балансировка HP босса и наград
- [ ] Оптимизация производительности

---

## 🚨 Важные замечания

### 11. **Рекомендации**

1. **Производительность**:
   - Использовать индексы для быстрого поиска активных рейдов
   - Кэшировать статус рейда в Redis для уменьшения нагрузки на БД
   - Батч-обработка обновлений HP босса (не на каждое сообщение)

2. **Безопасность**:
   - Проверять, что сообщение не обрабатывается дважды
   - Валидировать принадлежность пользователя к клану
   - Ограничить частоту обновлений API

3. **Масштабируемость**:
   - Рассмотреть использование очереди сообщений (Redis/RabbitMQ)
   - Асинхронная обработка завершения рейдов
   - Партиционирование таблицы `clan_raid_activity` по датам

4. **Мониторинг**:
   - Логирование всех действий в рейде
   - Метрики производительности
   - Алерты при ошибках

---

## 📚 Связанные файлы

- `src/bot/handlers/message_handler.py` - Обработка сообщений
- `src/bot/services/clan_raid.py` - Сервис рейдов (новый)
- `src/bot/api_clans_events.py` - API endpoints для рейдов
- `src/bot/models.py` - Модели данных
- `webapp/app.js` - UI рейдов
- `sql/013_add_clan_raid_activity.sql` - SQL миграция (новый)

---

## 🎉 Итог

Данная система позволяет создать динамичный и интерактивный геймплей, где активность игроков в групповых чатах напрямую влияет на прогресс кланового рейда. Это мотивирует игроков быть активными в чатах и работать вместе для достижения общей цели.
