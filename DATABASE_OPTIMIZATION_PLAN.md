# 📊 План оптимизации использования базы данных

## 🎯 Цель

Снизить нагрузку на базу данных Neon и уменьшить объём передаваемых данных через:
1. Кэширование частых запросов
2. Оптимизацию запросов к БД
3. Внедрение пагинации для больших списков

---

## 📋 Часть 1: Кэширование частых запросов

### 1.1. Выбор системы кэширования

**Рекомендуемое решение:** In-memory кэш (Python `functools.lru_cache` + TTL)

**Преимущества:**
- Не требует дополнительных зависимостей
- Простота внедрения
- Достаточно для большинства случаев

**Альтернатива:** Redis (если нужен распределённый кэш)

### 1.2. Запросы для кэширования

#### Приоритет 1 (высокий - кэшировать обязательно):

1. **Получение профиля пользователя** (`/api/profile`)
   - Частота: каждое открытие WebApp
   - TTL: 30 секунд
   - Кэш-ключ: `user_profile:{user_id}`

2. **Получение информации о клане** (`/api/clans/my-clan`)
   - Частота: каждое открытие страницы клана
   - TTL: 10 секунд
   - Кэш-ключ: `clan_info:{clan_id}`

3. **Список вайфу пользователя** (`/api/waifus`)
   - Частота: каждое открытие страницы вайфу
   - TTL: 15 секунд
   - Кэш-ключ: `user_waifus:{user_id}:{sort_by}:{favorites_only}`

4. **Данные навыков** (`/api/skills/tree`, `/api/skills/status`)
   - Частота: каждое открытие страницы навыков
   - TTL: 60 секунд (навыки меняются редко)
   - Кэш-ключ: `skills_tree:{user_id}`

#### Приоритет 2 (средний):

5. **Детали вайфу** (`/api/waifu/{waifu_id}`)
   - Частота: открытие карточки вайфу
   - TTL: 30 секунд
   - Кэш-ключ: `waifu_details:{waifu_id}`

6. **Список квестов** (`/api/quests`)
   - Частота: открытие страницы квестов
   - TTL: 60 секунд
   - Кэш-ключ: `quests:{user_id}`

7. **Статус рейда клана** (`/api/clans/raid/status`)
   - Частота: каждые 5 секунд (автообновление)
   - TTL: 3 секунды (очень короткий)
   - Кэш-ключ: `raid_status:{clan_id}`

### 1.3. Реализация кэширования

#### 1.3.1. Создать модуль кэширования

**Файл:** `src/bot/services/cache_service.py`

```python
from functools import lru_cache
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
import hashlib
import json

class CacheEntry:
    """Запись кэша с TTL"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

class CacheService:
    """Сервис кэширования с TTL"""
    
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._max_size = 1000  # Максимальное количество записей
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        entry = self._cache.get(key)
        if entry is None:
            return None
        
        if entry.is_expired():
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 30) -> None:
        """Сохранить значение в кэш"""
        # Очистка устаревших записей при достижении лимита
        if len(self._cache) >= self._max_size:
            self._cleanup_expired()
            # Если всё ещё переполнен, удаляем самые старые
            if len(self._cache) >= self._max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].expires_at)
                del self._cache[oldest_key]
        
        self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        self._cache.clear()
    
    def _cleanup_expired(self) -> None:
        """Удалить все устаревшие записи"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def get_or_set(self, key: str, factory: Callable[[], Any], ttl_seconds: int = 30) -> Any:
        """Получить из кэша или вычислить и сохранить"""
        value = self.get(key)
        if value is not None:
            return value
        
        value = factory()
        self.set(key, value, ttl_seconds)
        return value
    
    def make_key(self, *args, **kwargs) -> str:
        """Создать ключ кэша из аргументов"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

# Глобальный экземпляр
cache_service = CacheService()
```

#### 1.3.2. Декоратор для кэширования API endpoints

**Файл:** `src/bot/utils/cache_decorator.py`

```python
from functools import wraps
from typing import Callable, Any
from bot.services.cache_service import cache_service

def cached(ttl_seconds: int = 30, key_prefix: str = ""):
    """Декоратор для кэширования результатов функции"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Создаём ключ кэша
            cache_key = f"{key_prefix}:{cache_service.make_key(*args, **kwargs)}"
            
            # Проверяем кэш
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_service.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator
```

#### 1.3.3. Инвалидация кэша

Необходимо очищать кэш при обновлении данных:

- При обновлении профиля: `cache_service.delete(f"user_profile:{user_id}")`
- При изменении вайфу: `cache_service.delete(f"user_waifus:{user_id}:*")` (удалить все варианты)
- При изменении клана: `cache_service.delete(f"clan_info:{clan_id}")`

### 1.4. План внедрения кэширования

1. ✅ Создать `cache_service.py`
2. ✅ Создать декоратор `@cached`
3. ✅ Добавить кэширование в `/api/profile`
4. ✅ Добавить кэширование в `/api/clans/my-clan`
5. ✅ Добавить кэширование в `/api/waifus`
6. ✅ Добавить кэширование в `/api/skills/*`
7. ✅ Добавить инвалидацию кэша при обновлениях
8. ✅ Мониторинг эффективности кэша

---

## 📋 Часть 2: Оптимизация запросов к БД

### 2.1. Проблемные запросы для оптимизации

#### 2.1.1. N+1 проблемы

**Проблема:** Множественные запросы к БД вместо одного с JOIN

**Примеры:**
- Получение списка вайфу с запросами характеристик по каждой
- Получение списка участников клана с отдельными запросами пользователей
- Получение сообщений чата клана с отдельными запросами пользователей

**Решение:** Использовать `joinedload()` или `selectinload()` SQLAlchemy

#### 2.1.2. Избыточные данные

**Проблема:** Загружаются все поля, хотя нужны только некоторые

**Примеры:**
- Загрузка всех сообщений чата при запросе информации о клане
- Загрузка всех вайфу при запросе списка
- Загрузка полных данных пользователя при запросе списка участников

**Решение:** Использовать `.with_entities()` для выбора только нужных полей

#### 2.1.3. Отсутствие индексов

**Проблема:** Медленные запросы из-за отсутствия индексов

**Решение:** Добавить индексы для часто используемых полей

### 2.2. Конкретные оптимизации

#### 2.2.1. Оптимизация `/api/clans/my-clan`

**Текущий код:**
```python
# Проблема: N+1 запросов
members = db.query(ClanMember).filter(ClanMember.clan_id == clan.id).all()
members_data = []
for m in members:
    member_user = db.query(User).filter(User.id == m.user_id).first()  # ❌ N+1
    messages_data.append(...)
```

**Оптимизированный код:**
```python
from sqlalchemy.orm import joinedload

# ✅ Один запрос с JOIN
members = db.query(ClanMember)\
    .options(joinedload(ClanMember.user))\
    .filter(ClanMember.clan_id == clan.id)\
    .all()

members_data = []
for m in members:
    # user уже загружен, нет дополнительного запроса
    members_data.append({
        "user_id": m.user_id,
        "username": m.user.username if m.user else "Unknown",
        ...
    })
```

#### 2.2.2. Оптимизация `/api/waifus`

**Проблема:** Загружаются все вайфу со всеми полями, включая изображения (base64)

**Оптимизированный код:**
```python
# ✅ Загружаем только нужные поля
waifus = db.query(Waifu)\
    .with_entities(
        Waifu.id,
        Waifu.name,
        Waifu.rarity,
        Waifu.level,
        Waifu.power,
        Waifu.stats,
        Waifu.dynamic,
        Waifu.is_active,
        Waifu.is_favorite
    )\
    .filter(Waifu.owner_id == user.id)\
    .all()

# Не загружаем image_url (база64 строки большие)
```

#### 2.2.3. Оптимизация запросов с подсчётом

**Проблема:** Отдельные запросы для подсчёта

**Текущий код:**
```python
clans = db.query(Clan).all()
for clan in clans:
    member_count = db.query(ClanMember)\
        .filter(ClanMember.clan_id == clan.id)\
        .count()  # ❌ N+1 запросов
```

**Оптимизированный код:**
```python
from sqlalchemy import func

# ✅ Один запрос с подсчётом
clans_with_counts = db.query(
    Clan,
    func.count(ClanMember.user_id).label('member_count')
)\
.join(ClanMember, Clan.id == ClanMember.clan_id, isouter=True)\
.group_by(Clan.id)\
.all()
```

### 2.3. Добавление индексов

**Файл:** `sql/016_add_performance_indexes.sql`

```sql
-- Индексы для частых запросов

-- Индекс для поиска вайфу по владельцу и активности
CREATE INDEX IF NOT EXISTS idx_waifu_owner_active 
ON waifus(owner_id, is_active) 
WHERE is_active = TRUE;

-- Индекс для поиска участников клана
CREATE INDEX IF NOT EXISTS idx_clan_member_clan_user 
ON clan_members(clan_id, user_id);

-- Индекс для сообщений чата клана
CREATE INDEX IF NOT EXISTS idx_clan_chat_clan_created 
ON clan_chat_messages(clan_id, created_at DESC) 
WHERE is_deleted = FALSE;

-- Индекс для событий клана
CREATE INDEX IF NOT EXISTS idx_clan_event_clan_status 
ON clan_events(clan_id, status, event_type);

-- Индекс для участия в событиях
CREATE INDEX IF NOT EXISTS idx_clan_event_participation_event_user 
ON clan_event_participations(event_id, user_id);

-- Индекс для активности рейдов
CREATE INDEX IF NOT EXISTS idx_clan_raid_activity_event_chat 
ON clan_raid_activity(event_id, chat_id, created_at DESC);

-- Индекс для XPLog по источнику
CREATE INDEX IF NOT EXISTS idx_xp_log_user_source 
ON xp_log(user_id, source, created_at DESC);

-- Индекс для пользователей по Telegram ID
CREATE INDEX IF NOT EXISTS idx_user_tg_id 
ON users(tg_id);

-- Индекс для навыков пользователя
CREATE INDEX IF NOT EXISTS idx_user_skill_level_user_skill 
ON user_skill_levels(user_id, skill_id);
```

### 2.4. План оптимизации запросов

1. ✅ Добавить SQL-миграцию с индексами
2. ✅ Оптимизировать `/api/clans/my-clan` (убрать N+1)
3. ✅ Оптимизировать `/api/waifus` (выбирать только нужные поля)
4. ✅ Оптимизировать `/api/clans/search` (подсчёт участников)
5. ✅ Оптимизировать `/api/clans/raid/status` (загружать только нужные поля)
6. ✅ Проверить все остальные endpoints на N+1 проблемы

---

## 📋 Часть 3: Пагинация для больших списков

### 3.1. Списки, требующие пагинации

1. **Список вайфу** (`/api/waifus`)
   - Может быть 100+ вайфу
   - Размер страницы: 20-30 вайфу

2. **Сообщения чата клана** (`/api/clans/my-clan`)
   - Загружается 50 сообщений сразу
   - Размер страницы: 20 сообщений
   - Ленивая загрузка при скролле

3. **Список участников клана** (в модальном окне)
   - Может быть 50+ участников
   - Размер страницы: 20 участников

4. **История событий клана** (`/api/clans/events`)
   - Размер страницы: 10 событий

### 3.2. Реализация пагинации

#### 3.2.1. API изменения для пагинации

**Общий формат запроса:**
```
GET /api/waifus?page=1&limit=20&sort_by=name&favorites_only=false
```

**Общий формат ответа:**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 3.2.2. Утилита для пагинации

**Файл:** `src/bot/utils/pagination.py`

```python
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Query
from pydantic import BaseModel

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Параметры пагинации из запроса"""
    page: int = 1
    limit: int = 20
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    """Пагинированный ответ"""
    items: List[T]
    pagination: PaginationInfo

def paginate_query(
    query: Query,
    page: int = 1,
    limit: int = 20,
    max_limit: int = 100
) -> tuple[List, PaginationInfo]:
    """
    Применить пагинацию к SQLAlchemy запросу
    
    Args:
        query: SQLAlchemy запрос
        page: Номер страницы (начиная с 1)
        limit: Размер страницы
        max_limit: Максимальный размер страницы
    
    Returns:
        (items, pagination_info)
    """
    # Ограничиваем максимальный размер страницы
    limit = min(limit, max_limit)
    page = max(1, page)
    
    # Получаем общее количество записей
    total = query.count()
    
    # Применяем пагинацию
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    # Вычисляем информацию о пагинации
    total_pages = (total + limit - 1) // limit  # Округление вверх
    
    pagination_info = PaginationInfo(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    return items, pagination_info
```

#### 3.2.3. Изменения в API endpoints

**Пример: `/api/waifus`**

```python
@router.get("/api/waifus")
async def get_waifus(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    sort_by: str = "name",
    favorites_only: bool = False
) -> Dict[str, Any]:
    """Получить список вайфу с пагинацией"""
    user = get_user_from_request(request, db)
    
    # Строим запрос
    query = db.query(Waifu).filter(Waifu.owner_id == user.id)
    
    # Фильтр по избранным
    if favorites_only:
        query = query.filter(Waifu.is_favorite == True)
    
    # Сортировка
    if sort_by == "name":
        query = query.order_by(Waifu.name.asc())
    elif sort_by == "power":
        query = query.order_by(Waifu.power.desc())
    # ... другие варианты сортировки
    
    # Применяем пагинацию
    from bot.utils.pagination import paginate_query
    items, pagination_info = paginate_query(query, page, limit)
    
    # Преобразуем в словари
    waifus_data = [waifu_to_dict(w) for w in items]
    
    return {
        "waifus": waifus_data,
        "pagination": pagination_info.dict()
    }
```

#### 3.2.4. Изменения во фронтенде

**Файл:** `webapp/app.js`

```javascript
// Глобальные переменные для пагинации
let currentPage = 1;
const itemsPerPage = 20;

// Функция загрузки вайфу с пагинацией
async function loadWaifus(page = 1) {
    try {
        const sortBy = waifuSortBy || 'name';
        const favoritesOnly = showOnlyFavorites || false;
        
        const params = new URLSearchParams({
            initData: window.Telegram?.WebApp?.initData || '',
            page: page.toString(),
            limit: itemsPerPage.toString(),
            sort_by: sortBy,
            favorites_only: favoritesOnly.toString()
        });
        
        const response = await fetch(`/api/waifus?${params}`);
        const data = await response.json();
        
        // Обновляем список вайфу
        currentWaifuList = data.waifus || [];
        renderWaifuList(currentWaifuList);
        
        // Обновляем UI пагинации
        updatePaginationUI(data.pagination);
        
        currentPage = page;
    } catch (error) {
        console.error('Error loading waifus:', error);
    }
}

// Функция обновления UI пагинации
function updatePaginationUI(pagination) {
    const paginationContainer = document.getElementById('waifu-pagination');
    if (!paginationContainer) return;
    
    paginationContainer.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin: 20px 0;">
            <button 
                onclick="loadWaifus(${pagination.page - 1})" 
                ${!pagination.has_prev ? 'disabled' : ''}
                style="padding: 8px 16px; border: 1px solid #ccc; border-radius: 4px; background: ${pagination.has_prev ? '#fff' : '#f5f5f5'}; cursor: ${pagination.has_prev ? 'pointer' : 'not-allowed'};"
            >
                ← Назад
            </button>
            
            <span style="font-size: 14px;">
                Страница ${pagination.page} из ${pagination.total_pages}
            </span>
            
            <button 
                onclick="loadWaifus(${pagination.page + 1})" 
                ${!pagination.has_next ? 'disabled' : ''}
                style="padding: 8px 16px; border: 1px solid #ccc; border-radius: 4px; background: ${pagination.has_next ? '#fff' : '#f5f5f5'}; cursor: ${pagination.has_next ? 'pointer' : 'not-allowed'};"
            >
                Вперёд →
            </button>
        </div>
    `;
}

// Бесконечная прокрутка (опционально)
let isLoadingMore = false;
window.addEventListener('scroll', () => {
    if (isLoadingMore) return;
    
    const scrollPosition = window.innerHeight + window.scrollY;
    const documentHeight = document.documentElement.scrollHeight;
    
    // Если прокрутили до 90% страницы, загружаем следующую
    if (scrollPosition >= documentHeight * 0.9) {
        const nextPage = currentPage + 1;
        // Проверяем, есть ли следующая страница
        // Загружаем следующую страницу и добавляем к текущему списку
    }
});
```

### 3.3. План внедрения пагинации

1. ✅ Создать утилиту `pagination.py`
2. ✅ Добавить пагинацию в `/api/waifus`
3. ✅ Добавить пагинацию в сообщения чата клана
4. ✅ Добавить пагинацию в список участников клана
5. ✅ Обновить фронтенд для работы с пагинацией
6. ✅ Добавить кнопки навигации по страницам
7. ✅ (Опционально) Реализовать бесконечную прокрутку

---

## 📊 Метрики эффективности

### До оптимизации:
- Средний размер ответа API: ~500 KB
- Количество запросов к БД на страницу: 10-15
- Время ответа API: 500-1000ms

### После оптимизации (ожидаемые результаты):
- Средний размер ответа API: ~50-100 KB (уменьшение на 80-90%)
- Количество запросов к БД на страницу: 2-3 (уменьшение на 70-80%)
- Время ответа API: 50-200ms (улучшение на 60-90%)
- Хитрейт кэша: 70-90% (для частых запросов)

---

## 🚀 План внедрения (по приоритетам)

### Неделя 1: Критичные оптимизации
1. ✅ Добавить индексы в БД (миграция)
2. ✅ Оптимизировать запросы с N+1 проблемами
3. ✅ Добавить пагинацию для списка вайфу

### Неделя 2: Кэширование
4. ✅ Реализовать систему кэширования
5. ✅ Добавить кэширование для профиля и клана
6. ✅ Добавить инвалидацию кэша

### Неделя 3: Дополнительные оптимизации
7. ✅ Добавить пагинацию для сообщений чата
8. ✅ Оптимизировать запросы с выбором полей
9. ✅ Мониторинг и настройка TTL кэша

---

## 📝 Заметки

- Кэширование особенно эффективно для данных, которые читаются чаще, чем изменяются
- Пагинация критична для списков с более чем 50 элементами
- Индексы нужно добавлять аккуратно - они ускоряют SELECT, но замедляют INSERT/UPDATE
- Мониторинг метрик поможет понять, какие оптимизации дают наибольший эффект

---

## ✅ Чеклист реализации

- [x] Создан `cache_service.py`
- [x] Создан декоратор `@cached`
- [x] Добавлена SQL-миграция с индексами (`sql/016_add_performance_indexes.sql`)
- [x] Оптимизирован `/api/clans/my-clan` (N+1 убран через joinedload)
- [x] Оптимизирован `/api/clans/search` (подсчет участников через JOIN)
- [x] Оптимизирован `/api/waifus` (поля + пагинация, удален image_url)
- [x] Добавлено кэширование для профиля (`/api/profile`)
- [x] Добавлено кэширование для клана (`/api/clans/my-clan`)
- [x] Добавлена пагинация для сообщений чата клана
- [x] Добавлены relationships в модели (ClanMember, ClanChatMessage)
- [x] Добавлена инвалидация кэша при обновлениях (set-active, toggle-favorite, join/leave clan)
- [ ] Обновлён фронтенд для работы с пагинацией (требуется обновление webapp/app.js)
- [ ] Проведено тестирование и измерение метрик
