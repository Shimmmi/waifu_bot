# 🔧 Решение проблемы с WebApp окнами

## 🎯 Проблема

При открытии WebApp окна для одной вайфу и последующем нажатии на кнопку другой вайфу, Telegram делает активным старое окно вместо открытия нового.

## ❌ Ограничения Telegram

К сожалению, Telegram Bot API не позволяет:
- ❌ Программно закрывать WebApp окна
- ❌ Открывать новые WebApp окна поверх существующих
- ❌ Заставлять WebApp окна обновляться при изменении параметров

## ✅ Решения

### Решение 1: Добавить уведомление пользователю (Текущее)

Добавлено логирование в WebApp для отслеживания смены вайфу. Пользователь должен:
1. Закрыть текущее WebApp окно
2. Нажать на кнопку новой вайфу
3. WebApp откроется с новыми данными

### Решение 2: Показывать информацию в боте (Рекомендуется)

Вместо WebApp для просмотра, показывать базовую информацию о вайфу прямо в боте:

```python
# В src/bot/handlers/menu.py
async def handle_waifu_quick_view_callback(callback: CallbackQuery) -> None:
    """Быстрый просмотр информации о вайфу в боте"""
    # Парсим callback data: waifu_quick_view_{waifu_id}
    parts = callback.data.split("_")
    if len(parts) >= 4:
        waifu_id = parts[3]
        
        # Получаем данные вайфу
        session = SessionLocal()
        try:
            waifu = session.query(Waifu).filter(Waifu.id == waifu_id).first()
            
            if not waifu:
                await callback.answer("Вайфу не найдена!")
                return
            
            # Формируем текст с информацией
            power = calculate_waifu_power({
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "level": waifu.level
            })
            
            text = (
                f"🎭 <b>{waifu.name}</b>\n\n"
                f"⭐ Уровень: {waifu.level}\n"
                f"💪 Сила: {power}\n"
                f"🏷️ Редкость: {waifu.rarity}\n"
                f"👤 Раса: {waifu.race}\n"
                f"💼 Профессия: {waifu.profession}\n\n"
                f"📊 <b>Статы:</b>\n"
                f"⚔️ Сила: {waifu.stats['power']}\n"
                f"💖 Обаяние: {waifu.stats['charm']}\n"
                f"🍀 Удача: {waifu.stats['luck']}\n"
                f"💕 Привязанность: {waifu.stats['affection']}\n"
                f"🧠 Интеллект: {waifu.stats['intellect']}\n"
                f"⚡ Скорость: {waifu.stats['speed']}\n\n"
                f"🔄 <b>Динамика:</b>\n"
                f"😊 Настроение: {waifu.dynamic['mood']}\n"
                f"❤️ Лояльность: {waifu.dynamic['loyalty']}\n"
                f"⚡ Энергия: {waifu.dynamic['energy']}"
            )
            
            # Кнопки
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🖼️ Открыть карточку в WebApp",
                    web_app=WebAppInfo(url=f"https://waifu-bot-webapp.onrender.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
                )],
                [InlineKeyboardButton(text="🔙 Назад к списку", callback_data=f"waifu_list_page_0_created_at")]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
            
        finally:
            session.close()
```

### Решение 3: Использовать URL кнопки вместо WebApp

Изменить кнопки в детальной информации с WebApp на обычные URL кнопки:

```python
# Вместо WebApp кнопки
InlineKeyboardButton(
    text=f"🖼️ {waifu.name}",
    web_app=WebAppInfo(url=f"https://waifu-bot-webapp.onrender.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
)

# Использовать URL кнопку
InlineKeyboardButton(
    text=f"🖼️ {waifu.name}",
    url=f"https://waifu-bot-webapp.onrender.com/waifu-card/{waifu.id}?waifu_id={waifu.id}"
)
```

URL кнопки открываются в браузере, что позволяет открывать несколько окон одновременно.

## 🎯 Рекомендация

**Лучший подход - комбинированный:**

1. **Быстрый просмотр в боте** - показывает основную информацию
2. **WebApp для детального просмотра** - открывается по желанию

Это обеспечивает:
- ✅ Быстрый доступ к информации без открытия WebApp
- ✅ Возможность просмотреть несколько вайфу подряд
- ✅ Расширенный просмотр в WebApp при необходимости

## 🚀 Реализация

Хотите ли вы:
1. **Оставить как есть** - пользователь закрывает WebApp вручную
2. **Добавить быстрый просмотр** - информация показывается в боте
3. **Использовать URL кнопки** - открывается в браузере

Я могу реализовать любой из этих вариантов! 🎭✨
