from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy import select, func
from datetime import datetime, timedelta

from bot.db import SessionLocal
from bot.models import User, Waifu, Transaction
from bot.services.waifu_generator import generate_waifu, format_waifu_card, calculate_waifu_power, get_rarity_color
from bot.services.event_system import (
    calculate_event_score, get_event_rewards, get_random_event, 
    get_event_description, format_event_result, get_available_events,
    can_participate_in_event
)
from bot.data_tables import EVENTS

router = Router()


def get_sort_display_name(sort_by: str) -> str:
    """Возвращает отображаемое название сортировки"""
    sort_names = {
        "power": "По силе",
        "name": "По имени", 
        "level": "По уровню",
        "rarity": "По редкости",
        "created_at": "По дате"
    }
    return sort_names.get(sort_by, "По дате")


@router.callback_query()
async def handle_menu_callback(callback: CallbackQuery) -> None:
    """Обработчик кнопок меню"""
    if callback.data == "profile":
        await handle_profile_callback(callback)
    elif callback.data == "daily":
        await handle_daily_callback(callback)
    elif callback.data == "waifu_menu":
        await handle_waifu_menu_callback(callback)
    elif callback.data == "waifu_pull":
        await handle_waifu_pull_callback(callback)
    elif callback.data == "waifu_list":
        await handle_waifu_list_callback(callback)
    elif callback.data == "waifu_events":
        await handle_waifu_events_callback(callback)
    elif callback.data == "random_event":
        await handle_random_event_callback(callback)
    elif callback.data.startswith("event_accept_"):
        await handle_event_accept_callback(callback)
    elif callback.data == "event_decline":
        await handle_event_decline_callback(callback)
    elif callback.data == "event_cannot_participate":
        await callback.answer("⛔ Эта вайфу не может участвовать в событии!")
    elif callback.data == "back_to_waifu_menu":
        await handle_waifu_menu_callback(callback)
    elif callback.data.startswith("waifu_list_page_"):
        await handle_waifu_list_page_callback(callback)
    elif callback.data.startswith("waifu_list_sort_"):
        await handle_waifu_list_sort_callback(callback)
    elif callback.data.startswith("waifu_list_sort_menu_"):
        await handle_waifu_list_sort_menu_callback(callback)
    elif callback.data.startswith("event_waifu_select_"):
        await handle_event_waifu_select_callback(callback)
    elif callback.data.startswith("waifu_details_menu_"):
        await handle_waifu_details_menu_callback(callback)
    elif callback.data == "admin_test_pull":
        await handle_admin_test_pull_callback(callback)
    elif callback.data == "admin_list_waifu":
        await handle_admin_list_waifu_callback(callback)
    elif callback.data == "admin_clear_waifu":
        await handle_admin_clear_waifu_callback(callback)
    elif callback.data == "admin_add_coins":
        await handle_admin_add_coins_callback(callback)
    elif callback.data == "debug_back":
        await handle_debug_back_callback(callback)
    elif callback.data == "stats":
        await handle_stats_callback(callback)
    elif callback.data == "back_to_menu":
        await handle_back_to_menu(callback)
    elif callback.data == "events_menu":
        await handle_waifu_events_callback(callback)
    elif callback.data == "debug_menu":
        from bot.handlers.debug import handle_debug_menu_callback
        await handle_debug_menu_callback(callback)
    elif callback.data.startswith("debug_"):
        from bot.handlers.debug import handle_debug_action_callback
        await handle_debug_action_callback(callback)
    elif callback.data == "teaching_menu":
        await handle_teaching_menu_callback(callback)
    elif callback.data.startswith("teaching_select_student_"):
        await handle_teaching_select_student_callback(callback)
    elif callback.data.startswith("teaching_select_teacher_"):
        await handle_teaching_select_teacher_callback(callback)
    elif callback.data.startswith("teaching_toggle_teacher_"):
        await handle_teaching_toggle_teacher_callback(callback)
    elif callback.data == "teaching_confirm":
        await handle_teaching_confirm_callback(callback)


async def handle_profile_callback(callback: CallbackQuery) -> None:
    """Обработка кнопки Профиль"""
    if callback.from_user is None:
        return

    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Пользователь не найден. Используйте /start")
            return

        text = (
            f"👤 <b>Профиль</b>\n\n"
            f"💰 Монеты: {user.coins}\n"
            f"💎 Гемы: {user.gems}\n"
            f"👤 Ник: @{user.username if user.username else '—'}\n"
            f"📅 Регистрация: {user.created_at.strftime('%d.%m.%Y')}\n"
            f"🔥 Серия дней: {user.daily_streak}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    finally:
        session.close()


async def handle_daily_callback(callback: CallbackQuery) -> None:
    """Обработка кнопки Ежедневный бонус"""
    if callback.from_user is None:
        return

    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Пользователь не найден. Используйте /start")
            return

        # Простая проверка ежедневного бонуса
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        last_daily = user.last_daily.replace(tzinfo=None) if user.last_daily else datetime(1970, 1, 1)
        
        if now - last_daily < timedelta(hours=24):
            time_left = timedelta(hours=24) - (now - last_daily)
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            
            text = (
                f"🎁 <b>Ежедневный бонус</b>\n\n"
                f"⏰ Бонус недоступен\n"
                f"⏳ Осталось: {hours}ч {minutes}м\n\n"
                f"💡 Приходите завтра за новым бонусом!"
            )
        else:
            # Выдаем бонус
            user.coins += 50
            user.daily_streak += 1
            user.last_daily = now
            session.commit()

            text = (
                f"🎁 <b>Ежедневный бонус получен!</b>\n\n"
                f"💰 +50 монет\n"
                f"🔥 Серия дней: {user.daily_streak}\n"
                f"💵 Баланс: {user.coins} монет"
            )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    finally:
        session.close()


async def handle_gacha_callback(callback: CallbackQuery) -> None:
    """Обработка кнопки Гача"""
    text = (
        "🎰 <b>Гача система</b>\n\n"
        "💰 <b>Обычный призыв:</b> 100 монет\n"
        "💎 <b>Премиум призыв:</b> 10 гемов\n"
        "🎁 <b>Ежедневный призыв:</b> Бесплатно\n\n"
        "📊 <b>Шансы:</b>\n"
        "• Обычный: 60%\n"
        "• Редкий: 25%\n"
        "• Эпический: 12%\n"
        "• Легендарный: 3%"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Обычный призыв (100 монет)", callback_data="gacha_normal")],
        [InlineKeyboardButton(text="💎 Премиум призыв (10 гемов)", callback_data="gacha_premium")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def handle_stats_callback(callback: CallbackQuery) -> None:
    """Обработка кнопки Статистика"""
    if callback.from_user is None:
        return
    
    session = SessionLocal()
    try:
        # Get current user
        tg_user_id = callback.from_user.id
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        current_user = result.scalar_one_or_none()
        
        # Get total users count
        total_users = session.execute(select(func.count(User.id))).scalar() or 0
        
        # Get total coins in system
        total_coins = session.execute(select(func.sum(User.coins))).scalar() or 0
        
        # Get top users by coins
        top_users = session.execute(
            select(User).order_by(User.coins.desc()).limit(5)
        ).scalars().all()
        
        # Build top players text
        top_players = ""
        for i, user in enumerate(top_users, 1):
            username = f"@{user.username}" if user.username else user.display_name or "Anonymous"
            coins = user.coins
            if user.id == current_user.id if current_user else False:
                top_players += f"<b>{i}. {username} - {coins} монет ⭐ (Вы)</b>\n"
            else:
                top_players += f"{i}. {username} - {coins} монет\n"
        
        # Get user stats
        user_waifus = session.execute(
            select(func.count(Waifu.id)).where(Waifu.owner_id == current_user.id if current_user else 0)
        ).scalar() or 0
        
        text = (
            f"📊 <b>Статистика</b>\n\n"
            f"🎯 <b>Общая статистика:</b>\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Всего монет в системе: {total_coins}\n\n"
            f"👤 <b>Ваша статистика:</b>\n"
            f"• Монеты: {current_user.coins if current_user else 0}\n"
            f"• Гемы: {current_user.gems if current_user else 0}\n"
            f"• Вайфу: {user_waifus}\n\n"
            f"🏆 <b>Топ игроки:</b>\n{top_players}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    finally:
        session.close()


async def handle_waifu_menu_callback(callback: CallbackQuery) -> None:
    """Обработка кнопки Вайфу"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Призвать вайфу", callback_data="waifu_pull")],
        [InlineKeyboardButton(text="📋 Мои вайфу", callback_data="waifu_list")],
        [InlineKeyboardButton(text="📚 Обучение", callback_data="teaching_menu")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])

    await callback.message.edit_text(
        "🎭 <b>Вайфу система</b>\n\n"
        "Добро пожаловать в мир вайфу! Здесь вы можете:\n"
        "• Призывать новых вайфу\n"
        "• Участвовать в событиях\n"
        "• Соревноваться в турнирах\n"
        "• Развивать своих вайфу\n"
        "• Обучать вайфу (жертвовать для XP)\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


async def handle_back_to_menu(callback: CallbackQuery) -> None:
    """Возврат в главное меню"""
    from aiogram.types import WebAppInfo
    import os
    
    webapp_url = os.getenv("WEBAPP_URL", "https://waifu-bot-webapp.onrender.com")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Профиль", web_app=WebAppInfo(url=f"{webapp_url}/webapp/profile.html"))],
        [InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data="daily")],
        [InlineKeyboardButton(text="🎭 Вайфу", callback_data="waifu_menu")],
        [InlineKeyboardButton(text="🎯 События", callback_data="events_menu")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🔧 Debug", callback_data="debug_menu")]
    ])

    await callback.message.edit_text(
        "🤖 <b>Waifu Bot</b>\n\nВыбери действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


async def handle_waifu_pull_callback(callback: CallbackQuery) -> None:
    """Обработка призыва вайфу"""
    if callback.from_user is None:
        return

    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        # Проверяем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Сначала используйте /start")
            return

        # Проверяем баланс
        if user.coins < 100:
            await callback.answer("Недостаточно монет! Нужно 100 монет для призыва.")
            return

        # Генерируем новую вайфу
        # Получаем следующий номер карты
        max_card = session.execute(select(func.max(Waifu.card_number))).scalar() or 0
        new_waifu_data = generate_waifu(max_card + 1, user.id)
        
        # Создаем вайфу в базе
        waifu = Waifu(**new_waifu_data)
        session.add(waifu)
        
        # Списываем монеты
        user.coins -= 100
        
        # Записываем транзакцию
        transaction = Transaction(
            user_id=user.id,
            kind="spend",
            amount=100,
            currency="coins",
            reason="waifu_pull",
            meta={"waifu_id": waifu.id}
        )
        session.add(transaction)
        
        session.commit()

        # Отправляем результат
        card_text = format_waifu_card(new_waifu_data)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к вайфу", callback_data="back_to_waifu_menu")]
        ])
        
        await callback.message.edit_text(
            f"🎰 <b>Призыв завершен!</b>\n\n{card_text}\n\n"
            f"💰 Осталось монет: {user.coins}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer("Вайфу успешно призвана!")

    except Exception as e:
        await callback.answer(f"Ошибка при призыве: {str(e)}")
    finally:
        session.close()


async def handle_waifu_list_callback(callback: CallbackQuery) -> None:
    """Список вайфу пользователя"""
    if callback.from_user is None:
        return

    # По умолчанию показываем первую страницу с сортировкой по дате создания
    await show_waifu_list_page(callback, page=0, sort_by="created_at")


async def show_waifu_list_page(callback: CallbackQuery, page: int = 0, sort_by: str = "created_at") -> None:
    """Показывает страницу списка вайфу"""
    if callback.from_user is None:
        return

    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Сначала используйте /start")
            return

        # Получаем все вайфу пользователя
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()
        
        # Применяем сортировку
        if sort_by == "power":
            # Сортировка по силе (сумма всех характеристик)
            waifus = sorted(waifus, key=lambda w: sum(w.stats.values()) if w.stats else 0, reverse=True)
        elif sort_by == "name":
            waifus = sorted(waifus, key=lambda w: w.name.lower())
        elif sort_by == "level":
            waifus = sorted(waifus, key=lambda w: w.level, reverse=True)
        elif sort_by == "rarity":
            rarity_order = {"Legendary": 5, "Epic": 4, "Rare": 3, "Uncommon": 2, "Common": 1}
            waifus = sorted(waifus, key=lambda w: rarity_order.get(w.rarity, 0), reverse=True)
        else:  # created_at or default
            waifus = sorted(waifus, key=lambda w: w.created_at, reverse=True)

        if not waifus:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к вайфу", callback_data="back_to_waifu_menu")]
            ])
            await callback.message.edit_text(
                "📋 <b>Мои вайфу</b>\n\n"
                "У вас пока нет вайфу.\n"
                "Используйте призыв, чтобы получить свою первую вайфу!",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # Пагинация
        WAIFUS_PER_PAGE = 5
        start_idx = page * WAIFUS_PER_PAGE
        end_idx = start_idx + WAIFUS_PER_PAGE
        current_waifus = waifus[start_idx:end_idx]
        
        # Формируем список
        text = f"📋 <b>Мои вайфу ({len(waifus)})</b>\n"
        text += f"📄 Страница {page + 1}/{(len(waifus) + WAIFUS_PER_PAGE - 1) // WAIFUS_PER_PAGE}\n"
        text += f"🔀 Сортировка: {get_sort_display_name(sort_by)}\n\n"
        
        for i, waifu in enumerate(current_waifus, start_idx + 1):
            power = calculate_waifu_power({
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "level": waifu.level
            })
            
            rarity_icon = get_rarity_color(waifu.rarity)
            # Показываем вайфу без ссылки
            text += f"{i}. {waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}\n"

        # Создаем кнопки
        keyboard_buttons = []
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"waifu_list_page_{page-1}_{sort_by}"))
        if end_idx < len(waifus):
            nav_buttons.append(InlineKeyboardButton(text="Далее ➡️", callback_data=f"waifu_list_page_{page+1}_{sort_by}"))
        
        if nav_buttons:
            keyboard_buttons.append(nav_buttons)
        
        # Кнопка детальной информации
        keyboard_buttons.append([InlineKeyboardButton(text="ℹ️ Детальная информация", callback_data=f"waifu_details_menu_{page}_{sort_by}")])
        
        # Кнопка сортировки
        keyboard_buttons.append([InlineKeyboardButton(text="🔀 Сортировка", callback_data=f"waifu_list_sort_menu_{page}_{sort_by}")])
        
        # Кнопка возврата
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к вайфу", callback_data="back_to_waifu_menu")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        try:
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception as edit_error:
            if "message is not modified" in str(edit_error):
                # Сообщение не изменилось, просто отвечаем
                await callback.answer()
                return
            else:
                raise edit_error
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_waifu_events_callback(callback: CallbackQuery) -> None:
    """События вайфу"""
    if callback.from_user is None:
        return

    events = get_available_events()
    
    text = "🎯 <b>События вайфу</b>\n\n"
    text += "Доступные события:\n\n"
    
    for event in events:
        text += f"🎪 <b>{event['name']}</b>\n"
        text += f"📝 {event['description']}\n"
        text += f"📊 Нужные характеристики: {', '.join(event['base_stats'])}\n"
        text += f"💼 Бонус профессии: {event['profession_bonus']}\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Случайное событие", callback_data="random_event")],
        [InlineKeyboardButton(text="🔙 Назад к вайфу", callback_data="back_to_waifu_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


async def handle_random_event_callback(callback: CallbackQuery) -> None:
    """Участие в случайном событии - предложение участия"""
    if callback.from_user is None:
        return

    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await callback.answer("Сначала используйте /start")
            return

        # Получаем все вайфу пользователя
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()

        if not waifus:
            await callback.answer("У вас нет вайфу для участия в событиях!")
            return

        # Выбираем случайное событие
        event_type = get_random_event()
        event = EVENTS.get(event_type, {})
        
        # Предлагаем участие с таймером 60 секунд
        text = (
            f"🎲 <b>Случайное событие!</b>\n\n"
            f"🎯 <b>{event.get('name', 'Событие')}</b>\n"
            f"📝 {event.get('description', 'Описание отсутствует')}\n\n"
            f"⏱️ У вас есть <b>60 секунд</b> чтобы принять решение!\n\n"
            f"Хотите участвовать?"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, участвовать!", callback_data=f"event_accept_{event_type}"),
                InlineKeyboardButton(text="❌ Нет, отказаться", callback_data="event_decline")
            ],
            [InlineKeyboardButton(text="🔙 Назад к событиям", callback_data="waifu_events")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_event_accept_callback(callback: CallbackQuery) -> None:
    """Обработка принятия участия в событии"""
    if callback.from_user is None:
        return
    
    # Парсим callback data: event_accept_{event_type}
    parts = callback.data.split("_")
    if len(parts) >= 3:
        event_type = parts[2]
        
        tg_user_id = callback.from_user.id
        session = SessionLocal()
        try:
            # Получаем пользователя
            result = session.execute(select(User).where(User.tg_id == tg_user_id))
            user = result.scalar_one_or_none()

            if user is None:
                await callback.answer("Сначала используйте /start")
                return

            # Получаем все вайфу пользователя
            waifus_result = session.execute(
                select(Waifu).where(Waifu.owner_id == user.id)
            )
            waifus = waifus_result.scalars().all()

            if not waifus:
                await callback.answer("У вас нет вайфу для участия в событиях!")
                return

            event = EVENTS.get(event_type, {})
            
            # Создаем кнопки для выбора вайфу
            keyboard_buttons = []
            for waifu in waifus:
                power = calculate_waifu_power({
                    "stats": waifu.stats,
                    "dynamic": waifu.dynamic,
                    "level": waifu.level
                })
                rarity_icon = get_rarity_color(waifu.rarity)
                
                # Проверяем возможность участия
                can_participate, reason = can_participate_in_event({
                    "dynamic": waifu.dynamic,
                    "profession": waifu.profession
                }, event_type)
                
                button_text = f"{waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}"
                if not can_participate:
                    button_text += f" ⛔ ({reason})"
                
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"event_waifu_select_{waifu.id}_{event_type}" if can_participate else "event_cannot_participate"
                    )
                ])
            
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к событиям", callback_data="waifu_events")])

            text = (
                f"🎯 <b>{event.get('name', 'Событие')}</b>\n\n"
                f"📝 {event.get('description', 'Описание отсутствует')}\n\n"
                f"Выберите вайфу для участия:"
            )

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()

        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}")
        finally:
            session.close()


async def handle_event_decline_callback(callback: CallbackQuery) -> None:
    """Обработка отказа от участия в событии"""
    text = (
        f"❌ <b>Вы отказались от участия в событии</b>\n\n"
        f"Возможно, в следующий раз повезет больше!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Новое событие", callback_data="random_event")],
        [InlineKeyboardButton(text="🔙 Назад к событиям", callback_data="waifu_events")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# Debug обработчики для администратора
ADMIN_ID = 305174198

async def handle_admin_test_pull_callback(callback: CallbackQuery) -> None:
    """Тестовый призыв для администратора"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Генерируем тестовую вайфу
        max_card = session.execute(select(func.max(Waifu.card_number))).scalar() or 0
        new_waifu_data = generate_waifu(max_card + 1, user.id)
        
        # Создаем вайфу в базе
        waifu = Waifu(**new_waifu_data)
        session.add(waifu)
        session.commit()
        
        # Формируем результат
        card_text = format_waifu_card(new_waifu_data)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к debug", callback_data="debug_back")]
        ])
        
        await callback.message.edit_text(
            f"🧪 <b>Тестовый призыв завершен!</b>\n\n{card_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer("Тестовая вайфу создана!")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_admin_list_waifu_callback(callback: CallbackQuery) -> None:
    """Список всех вайфу для администратора"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    session = SessionLocal()
    try:
        # Получаем все вайфу
        waifus_result = session.execute(
            select(Waifu).order_by(Waifu.created_at.desc()).limit(20)
        )
        waifus = waifus_result.scalars().all()
        
        if not waifus:
            text = "📋 <b>Список вайфу</b>\n\nВ системе пока нет вайфу."
        else:
            text = f"📋 <b>Последние {len(waifus)} вайфу:</b>\n\n"
            for i, waifu in enumerate(waifus, 1):
                power = calculate_waifu_power({
                    "stats": waifu.stats,
                    "dynamic": waifu.dynamic,
                    "level": waifu.level
                })
                text += f"{i}. {waifu.name} [{waifu.rarity}] - 💪{power}\n"
                text += f"   Владелец: {waifu.owner_id} | ID: {waifu.id}\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к debug", callback_data="debug_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_admin_clear_waifu_callback(callback: CallbackQuery) -> None:
    """Очистка всех вайфу для администратора"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    session = SessionLocal()
    try:
        # Удаляем все вайфу
        deleted_count = session.execute(select(func.count(Waifu.id))).scalar()
        session.execute(select(Waifu).delete())
        session.commit()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к debug", callback_data="debug_back")]
        ])
        
        await callback.message.edit_text(
            f"🗑️ <b>Очистка завершена</b>\n\nУдалено вайфу: {deleted_count}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer("Вайфу очищены!")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_admin_add_coins_callback(callback: CallbackQuery) -> None:
    """Добавление монет для администратора"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == callback.from_user.id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("❌ Пользователь не найден")
            return
        
        # Добавляем монеты
        user.coins += 1000
        session.commit()
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к debug", callback_data="debug_back")]
        ])
        
        await callback.message.edit_text(
            f"💰 <b>Монеты добавлены!</b>\n\nНовый баланс: {user.coins} монет",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer("Монеты добавлены!")
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_back_callback(callback: CallbackQuery) -> None:
    """Возврат к debug меню"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    # Возвращаемся к debug команде
    await callback.message.edit_text("🔍 <b>DEBUG MENU</b>\n\nИспользуйте /debug для просмотра информации")
    await callback.answer()


async def handle_waifu_list_page_callback(callback: CallbackQuery) -> None:
    """Обработка пагинации списка вайфу"""
    if callback.from_user is None:
        return
    
    # Парсим callback data: waifu_list_page_{page}_{sort_by}
    parts = callback.data.split("_")
    if len(parts) >= 5:
        page = int(parts[3])
        sort_by = parts[4]
        await show_waifu_list_page(callback, page=page, sort_by=sort_by)
    else:
        await callback.answer("Ошибка обработки запроса")


async def handle_waifu_list_sort_menu_callback(callback: CallbackQuery) -> None:
    """Обработка меню сортировки списка вайфу"""
    if callback.from_user is None:
        return
    
    # Парсим callback data: waifu_list_sort_menu_{page}_{sort_by}
    parts = callback.data.split("_")
    if len(parts) >= 5:
        page = int(parts[4])  # parts[4] = page
        # sort_by может содержать подчеркивания (например, "created_at")
        sort_by = "_".join(parts[5:]) if len(parts) > 5 else "created_at"
        
        # Создаем меню сортировки
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💪 По силе", callback_data=f"waifu_list_sort_power_{page}")],
            [InlineKeyboardButton(text="📝 По имени", callback_data=f"waifu_list_sort_name_{page}")],
            [InlineKeyboardButton(text="⭐ По уровню", callback_data=f"waifu_list_sort_level_{page}")],
            [InlineKeyboardButton(text="💎 По редкости", callback_data=f"waifu_list_sort_rarity_{page}")],
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data=f"waifu_list_page_{page}_{sort_by}")]
        ])
        
        await callback.message.edit_text(
            "🔀 <b>Выберите сортировку:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    else:
        await callback.answer("Ошибка обработки запроса")


async def handle_waifu_list_sort_callback(callback: CallbackQuery) -> None:
    """Обработка смены сортировки списка вайфу"""
    import logging
    logger = logging.getLogger(__name__)
    
    if callback.from_user is None:
        return
    
    logger.info(f"🔀 SORT CALLBACK: {callback.data}")
    
    # Парсим callback data: waifu_list_sort_{sort_by}_{page}
    parts = callback.data.split("_")
    logger.info(f"   Parts: {parts}")
    
    if len(parts) >= 5:
        # sort_by теперь без подчеркиваний (например, "createdat", "power", "name")
        # Для callback data: waifu_list_sort_power_0
        # parts = ['waifu', 'list', 'sort', 'power', '0']
        sort_by = parts[3]  # parts[3] = 'power'
        page = int(parts[4])  # parts[4] = '0' -> 0
        
        logger.info(f"   Parsed: sort_by={sort_by}, page={page}")
        
        # Преобразуем sort_by обратно в правильный формат (только для created_at)
        if sort_by == "createdat":
            sort_by = "created_at"
            logger.info(f"   Converted: sort_by={sort_by}")
        
        # Переходим к списку с новой сортировкой
        logger.info(f"   Calling show_waifu_list_page with sort_by={sort_by}")
        await show_waifu_list_page(callback, page=page, sort_by=sort_by)
    else:
        logger.error(f"   ERROR: Invalid parts length: {len(parts)}")
        await callback.answer("Ошибка обработки запроса")


async def handle_event_waifu_select_callback(callback: CallbackQuery) -> None:
    """Обработка выбора вайфу для участия в событии"""
    if callback.from_user is None:
        return
    
    # Парсим callback data: event_waifu_select_{waifu_id}_{event_type}
    # waifu_id может содержать подчеркивания (например, wf_ddd65e42)
    parts = callback.data.split("_")
    if len(parts) >= 5:
        # Собираем waifu_id обратно (все части кроме первых 3 и последней)
        # event_waifu_select_wf_ddd65e42_dance -> wf_ddd65e42
        waifu_id = "_".join(parts[3:-1])
        event_type = parts[-1]
        
        tg_user_id = callback.from_user.id
        session = SessionLocal()
        try:
            # Получаем пользователя
            result = session.execute(select(User).where(User.tg_id == tg_user_id))
            user = result.scalar_one_or_none()

            if user is None:
                await callback.answer("Сначала используйте /start")
                return

            # Получаем выбранную вайфу
            waifu_result = session.execute(
                select(Waifu).where(Waifu.id == waifu_id, Waifu.owner_id == user.id)
            )
            waifu = waifu_result.scalar_one_or_none()

            if not waifu:
                await callback.answer("Вайфу не найдена!")
                return

            # Проверяем возможность участия
            can_participate, reason = can_participate_in_event({
                "dynamic": waifu.dynamic,
                "profession": waifu.profession
            }, event_type)
            
            if not can_participate:
                await callback.answer(f"Нельзя участвовать: {reason}")
                return

            # Вычисляем результат
            score, event_name = calculate_event_score({
                "stats": waifu.stats,
                "profession": waifu.profession,
                "dynamic": waifu.dynamic
            }, event_type)
            
            rewards = get_event_rewards(score, event_type)
            
            # Обновляем вайфу
            from datetime import datetime
            from sqlalchemy.orm.attributes import flag_modified
            import logging
            from bot.services.level_up import level_up_service
            logger = logging.getLogger(__name__)
            
            # Log BEFORE changes
            old_xp = waifu.xp
            old_level = waifu.level
            old_dynamic = dict(waifu.dynamic) if waifu.dynamic else {}
            logger.info(f"🔍 EVENT PARTICIPATION - BEFORE: Waifu {waifu.id} ({waifu.name})")
            logger.info(f"   Level: {old_level}, XP: {old_xp}")
            logger.info(f"   Dynamic: {old_dynamic}")
            
            # Add XP
            waifu.xp += rewards["xp"]
            
            # Check for level up
            should_level_up, new_level = level_up_service.check_level_up(waifu.xp, waifu.level)
            level_up_info = None
            
            if should_level_up:
                logger.info(f"🎉 LEVEL UP DETECTED! {old_level} → {new_level}")
                
                # Apply level up changes
                waifu_data = {
                    "level": waifu.level,
                    "xp": waifu.xp,
                    "stats": dict(waifu.stats)
                }
                
                level_up_info = level_up_service.apply_level_up(waifu_data, new_level)
                
                # Update waifu with new level and stats
                waifu.level = new_level
                waifu.stats = level_up_info["updated_stats"]
                flag_modified(waifu, "stats")
                
                logger.info(f"   New level: {new_level}")
                logger.info(f"   Stat increased: {level_up_info['increased_stat']} "
                           f"({level_up_info['old_stat_value']} → {level_up_info['new_stat_value']})")
            
            # Преобразуем значения в int перед операциями
            current_energy = int(waifu.dynamic.get("energy", 100))
            current_mood = int(waifu.dynamic.get("mood", 50))
            current_loyalty = int(waifu.dynamic.get("loyalty", 50))
            
            # Обновляем dynamic - создаем новый словарь для корректного отслеживания изменений
            waifu.dynamic = {
                **waifu.dynamic,
                "energy": max(0, current_energy - 20),
                "mood": min(100, current_mood + 5),
                "loyalty": min(100, current_loyalty + 2),
                "last_restore": datetime.now().isoformat()  # Update restoration timestamp
            }
            
            # Помечаем поле как измененное для SQLAlchemy
            flag_modified(waifu, "dynamic")
            
            # Log AFTER changes (before commit)
            logger.info(f"🔄 EVENT PARTICIPATION - AFTER CHANGES: Waifu {waifu.id}")
            logger.info(f"   Level: {old_level} → {waifu.level}")
            logger.info(f"   XP: {old_xp} → {waifu.xp}")
            logger.info(f"   Dynamic: {waifu.dynamic}")
            logger.info(f"   flag_modified: dynamic and stats fields marked as modified")
            
            # Обновляем пользователя
            user.coins += rewards["coins"]
            
            # Commit and explicitly flush to database
            logger.info(f"💾 Committing to database...")
            session.commit()
            session.flush()
            session.refresh(waifu)  # Обновляем объект из базы данных
            
            # Log AFTER commit
            logger.info(f"✅ COMMITTED TO DB: Waifu {waifu.id}")
            logger.info(f"   Level after refresh: {waifu.level}")
            logger.info(f"   XP after refresh: {waifu.xp}")
            logger.info(f"   Dynamic after refresh: {waifu.dynamic}")

            # Формируем результат
            result_text = format_event_result({
                "name": waifu.name,
                "stats": waifu.stats,
                "dynamic": waifu.dynamic
            }, event_type, score, rewards)
            
            # Add level-up message if leveled up
            if level_up_info:
                level_up_message = level_up_service.format_level_up_message(
                    waifu.name,
                    level_up_info
                )
                result_text = f"{result_text}\n\n{level_up_message}"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад к событиям", callback_data="waifu_events")]
            ])

            await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()

        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}")
        finally:
            session.close()
    else:
        await callback.answer("Ошибка обработки запроса")


# ========== TEACHING SYSTEM HANDLERS ==========

async def handle_teaching_menu_callback(callback: CallbackQuery) -> None:
    """Show teaching menu where player selects which waifu will receive XP"""
    if callback.from_user is None:
        return
    
    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Сначала используйте /start")
            return
        
        # Get all waifus
        waifus = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id).order_by(Waifu.created_at.desc())
        ).scalars().all()
        
        if not waifus:
            await callback.answer("У вас нет вайфу для обучения!")
            return
        
        keyboard_buttons = []
        for waifu in waifus:
            rarity_icon = get_rarity_color(waifu.rarity)
            power = calculate_waifu_power({
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "level": waifu.level
            })
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}",
                    callback_data=f"teaching_select_student_{waifu.id}"
                )
            ])
        
        keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_waifu_menu")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            "📚 <b>Обучение</b>\n\n"
            "Выберите вайфу, которой хотите дать опыт (ученик):\n\n"
            "💡 Вы сможете пожертвовать других вайфу, чтобы передать им опыт.\n"
            "Количество опыта зависит от редкости пожертвованной вайфу.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    finally:
        session.close()


async def handle_teaching_select_student_callback(callback: CallbackQuery) -> None:
    """Player selected the student waifu, now show list of teachers to select"""
    if callback.from_user is None:
        return
    
    # Extract student waifu ID
    # Format: teaching_select_student_{waifu_id}
    # waifu_id can contain underscores (e.g., wf_5ddf4f29)
    import logging
    logger = logging.getLogger(__name__)
    
    parts = callback.data.split("_", 3)  # Split into max 4 parts
    logger.info(f"📚 Teaching select student callback data: {callback.data}")
    logger.info(f"   Parts: {parts}")
    
    if len(parts) < 4:
        logger.error(f"   ERROR: Invalid callback data format")
        await callback.answer("Ошибка обработки")
        return
    
    student_id = parts[3]  # Everything after "teaching_select_student_"
    logger.info(f"   Student ID: {student_id}")
    
    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Ошибка: пользователь не найден")
            return
        
        # Get student waifu
        student = session.execute(select(Waifu).where(
            Waifu.id == student_id,
            Waifu.owner_id == user.id
        )).scalar_one_or_none()
        
        if not student:
            await callback.answer("Вайфу не найдена!")
            return
        
        # Get all other waifus (teachers can't be the student)
        waifus = session.execute(
            select(Waifu).where(
                Waifu.owner_id == user.id,
                Waifu.id != student_id
            ).order_by(Waifu.created_at.desc())
        ).scalars().all()
        
        if not waifus:
            await callback.answer("У вас нет других вайфу для обучения!")
            return
        
        keyboard_buttons = []
        from bot.services.waifu_upgrade import calculate_teaching_xp, get_max_level
        
        for waifu in waifus:
            rarity_icon = get_rarity_color(waifu.rarity)
            xp_given = calculate_teaching_xp(student.level, waifu.rarity, waifu.level, waifu.xp)
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{waifu.name} - Ур.{waifu.level} {rarity_icon} → +{xp_given} XP",
                    callback_data=f"teaching_toggle_teacher_{waifu.id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="✅ Применить обучение", callback_data=f"teaching_confirm_{student_id}")
        ])
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="teaching_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        max_level = get_max_level(student.rarity)
        await callback.message.edit_text(
            f"📚 <b>Обучение: {student.name}</b>\n\n"
            f"👤 Ученик: {student.name} (Ур.{student.level}/{max_level})\n"
            f"📊 Текущий XP: {student.xp}\n\n"
            f"Выберите вайфу для жертвования (несколько можно выбрать):",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    finally:
        session.close()


async def handle_teaching_toggle_teacher_callback(callback: CallbackQuery) -> None:
    """Toggle teacher selection state"""
    # For now, just show that it's selected
    # In a full implementation, we'd store selected teachers in state
    await callback.answer("✅ Выбрана для обучения")


async def handle_teaching_confirm_callback(callback: CallbackQuery) -> None:
    """Process the teaching - apply XP and remove teachers"""
    if callback.from_user is None:
        return
    
    # Extract student ID from callback_data
    # Format: teaching_confirm_{waifu_id}
    # waifu_id can contain underscores (e.g., wf_5ddf4f29)
    parts = callback.data.split("_", 2)  # Split into max 3 parts
    if len(parts) < 3:
        await callback.answer("Ошибка обработки")
        return
    
    student_id = parts[2]  # Everything after "teaching_confirm_"
    
    tg_user_id = callback.from_user.id
    session = SessionLocal()
    try:
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Ошибка: пользователь не найден")
            return
        
        # Get student waifu
        student = session.execute(select(Waifu).where(
            Waifu.id == student_id,
            Waifu.owner_id == user.id
        )).scalar_one_or_none()
        
        if not student:
            await callback.answer("Вайфу не найдена!")
            return
        
        # For now, use simple logic: get all waifus except student
        # In full implementation, we'd check which were selected
        other_waifus = session.execute(
            select(Waifu).where(
                Waifu.owner_id == user.id,
                Waifu.id != student_id
            )
        ).scalars().all()
        
        if not other_waifus:
            await callback.answer("Нет вайфу для жертвования!")
            return
        
        # Calculate total XP from all teachers
        from bot.services.waifu_upgrade import calculate_teaching_xp
        total_xp = 0
        teacher_names = []
        
        for teacher in other_waifus:
            xp = calculate_teaching_xp(student.level, teacher.rarity, teacher.level, teacher.xp)
            total_xp += xp
            teacher_names.append(f"{teacher.name} (+{xp} XP)")
        
        # Apply XP to student
        new_xp = student.xp + total_xp
        student.xp = new_xp
        
        # Check for level up
        from bot.services.level_up import LevelUpService
        new_level = LevelUpService.calculate_level_from_xp(new_xp)
        
        # Apply level up if needed
        level_up_result = {'leveled_up': False, 'message': ''}
        if new_level > student.level:
            # Prepare waifu data
            waifu_data = {
                "level": student.level,
                "xp": new_xp,
                "stats": dict(student.stats)
            }
            
            # Apply level up
            level_up_info = LevelUpService.apply_level_up(waifu_data, new_level)
            
            # Update student waifu
            student.level = new_level
            student.stats = level_up_info["updated_stats"]
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(student, "stats")
            
            # Format level up message
            from bot.services.level_up import LevelUpService
            level_up_result = {
                'leveled_up': True,
                'message': LevelUpService.format_level_up_message(student.name, level_up_info)
            }
        
        # Delete all teacher waifus
        for teacher in other_waifus:
            session.delete(teacher)
        
        session.commit()
        
        # Show result
        result_text = (
            f"📚 <b>Обучение завершено!</b>\n\n"
            f"👤 Ученик: {student.name}\n"
            f"📊 Получено XP: +{total_xp}\n"
            f"📈 Новый уровень: {student.level}\n"
            f"⭐ Текущий XP: {student.xp}\n"
        )
        
        if level_up_result.get('leveled_up'):
            result_text += f"\n{level_up_result['message']}\n"
        
        result_text += "\n💔 Пожертвованные вайфу:\n"
        for name in teacher_names:
            result_text += f"• {name}\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к вайфу", callback_data="back_to_waifu_menu")]
        ])
        
        await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer("✅ Обучение завершено!")
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()




async def handle_waifu_details_menu_callback(callback: CallbackQuery) -> None:
    """Обработка меню детальной информации о вайфу"""
    if callback.from_user is None:
        return
    
    # Парсим callback data: waifu_details_menu_{page}_{sort_by}
    parts = callback.data.split("_")
    if len(parts) >= 5:
        page = int(parts[3])  # parts[3] = page
        # sort_by может содержать подчеркивания (например, "created_at")
        sort_by = "_".join(parts[4:]) if len(parts) > 4 else "created_at"
        
        tg_user_id = callback.from_user.id
        session = SessionLocal()
        try:
            # Получаем пользователя
            result = session.execute(select(User).where(User.tg_id == tg_user_id))
            user = result.scalar_one_or_none()

            if user is None:
                await callback.answer("Сначала используйте /start")
                return

            # Получаем вайфу пользователя для текущей страницы
            order_clause = {
                "created_at": Waifu.created_at.desc(),
                "name": Waifu.name.asc(),
                "level": Waifu.level.desc(),
                "rarity": Waifu.rarity.desc()
            }.get(sort_by, Waifu.created_at.desc())

            waifus_result = session.execute(
                select(Waifu).where(Waifu.owner_id == user.id).order_by(order_clause)
            )
            waifus = waifus_result.scalars().all()

            if not waifus:
                await callback.answer("У вас нет вайфу!")
                return

            # Пагинация
            WAIFUS_PER_PAGE = 5
            start_idx = page * WAIFUS_PER_PAGE
            end_idx = start_idx + WAIFUS_PER_PAGE
            current_waifus = waifus[start_idx:end_idx]

            # Создаем кнопки для каждой вайфу на текущей странице
            import logging
            logger = logging.getLogger(__name__)
            
            keyboard_buttons = []
            for waifu in current_waifus:
                logger.info(f"📋 DISPLAYING WAIFU IN LIST: {waifu.id} ({waifu.name})")
                logger.info(f"   XP: {waifu.xp}")
                logger.info(f"   Dynamic: {waifu.dynamic}")
                
                power = calculate_waifu_power({
                    "stats": waifu.stats,
                    "dynamic": waifu.dynamic,
                    "level": waifu.level
                })
                rarity_icon = get_rarity_color(waifu.rarity)
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"🖼️ {waifu.name} - Ур.{waifu.level} {rarity_icon} 💪{power}",
                        web_app=WebAppInfo(url=f"https://waifu-bot-webapp.onrender.com/waifu-card/{waifu.id}?waifu_id={waifu.id}")
                    )
                ])
            
            # Кнопки навигации
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"waifu_details_menu_{page-1}_{sort_by}"))
            if end_idx < len(waifus):
                nav_buttons.append(InlineKeyboardButton(text="Далее ➡️", callback_data=f"waifu_details_menu_{page+1}_{sort_by}"))
            
            if nav_buttons:
                keyboard_buttons.append(nav_buttons)
            
            # Кнопка возврата
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к списку", callback_data=f"waifu_list_page_{page}_{sort_by}")])

            text = (
                f"ℹ️ <b>Детальная информация</b>\n\n"
                f"📄 Страница {page + 1}/{(len(waifus) + WAIFUS_PER_PAGE - 1) // WAIFUS_PER_PAGE}\n"
                f"🔀 Сортировка: {get_sort_display_name(sort_by)}\n\n"
                f"Выберите вайфу для просмотра карточки в WebApp:"
            )

            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()

        except Exception as e:
            await callback.answer(f"Ошибка: {str(e)}")
        finally:
            session.close()
    else:
        await callback.answer("Ошибка обработки запроса")
