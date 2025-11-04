"""
Debug menu handlers for Waifu Bot
Admin/debug commands for testing and troubleshooting
"""

import logging
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from sqlalchemy import select, update
from datetime import datetime
import random

from bot.db import SessionLocal
from bot.models import User, Waifu, XPLog

logger = logging.getLogger(__name__)

# Import skills models
try:
    from bot.models import UserSkills, UserSkillLevel, Skill
    SKILLS_ENABLED = True
except ImportError:
    UserSkills = None
    UserSkillLevel = None
    Skill = None
    SKILLS_ENABLED = False

router = Router()


async def handle_debug_menu_callback(callback: CallbackQuery) -> None:
    """Отображение меню отладки"""
    # Check if admin
    ADMIN_ID = 305174198
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Восстановить энергию всем вайфу", callback_data="debug_restore_energy")],
        [InlineKeyboardButton(text="💰 +10000 монет и +100 гемов", callback_data="debug_add_currency")],
        [InlineKeyboardButton(text="✨ +1000 XP для вайфу", callback_data="debug_add_xp_menu")],
        [InlineKeyboardButton(text="🧬 +100 очков прокачки", callback_data="debug_add_skill_points")],
        [InlineKeyboardButton(text="🗑️ Убрать все очки прокачки", callback_data="debug_wipe_skill_points")],
        [InlineKeyboardButton(text="🗑️ Удалить всех вайфу", callback_data="debug_wipe_confirm")],
        [InlineKeyboardButton(text="🎯 Запустить событие", callback_data="debug_trigger_event")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Debug Menu</b>\n\n"
        "Меню для тестирования и отладки:\n\n"
        "⚠️ Эти действия влияют на игровой баланс!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


async def handle_debug_action_callback(callback: CallbackQuery) -> None:
    """Обработка действий дебаг-меню"""
    if callback.from_user is None:
        return
    
    tg_user_id = callback.from_user.id
    
    if callback.data == "debug_restore_energy":
        await handle_debug_restore_energy(callback, tg_user_id)
    elif callback.data == "debug_add_currency":
        await handle_debug_add_currency(callback, tg_user_id)
    elif callback.data == "debug_add_xp_menu":
        await handle_debug_add_xp_menu(callback, tg_user_id)
    elif callback.data == "debug_add_skill_points":
        await handle_debug_add_skill_points(callback, tg_user_id)
    elif callback.data == "debug_wipe_skill_points":
        await handle_debug_wipe_skill_points(callback, tg_user_id)
    elif callback.data == "debug_wipe_confirm":
        await handle_debug_wipe_confirm(callback, tg_user_id)
    elif callback.data == "debug_wipe_execute":
        await handle_debug_wipe_execute(callback, tg_user_id)
    elif callback.data.startswith("debug_add_xp_"):
        await handle_debug_add_xp_to_waifu(callback, tg_user_id)
    elif callback.data == "debug_trigger_event":
        await handle_debug_trigger_event(callback, tg_user_id)
    elif callback.data.startswith("debug_event_chat_"):
        await handle_debug_event_select_chat(callback, tg_user_id)


async def handle_debug_restore_energy(callback: CallbackQuery, tg_user_id: int) -> None:
    """Восстановление энергии всем вайфу"""
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Получаем всех вайфу пользователя
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()
        
        if not waifus:
            await callback.answer("❌ У вас нет вайфу")
            return
        
        # Восстанавливаем энергию всем
        from sqlalchemy.orm.attributes import flag_modified
        
        count = 0
        for waifu in waifus:
            if waifu.dynamic:
                waifu.dynamic = {
                    **waifu.dynamic,
                    "energy": 100,
                    "last_restore": datetime.now().isoformat()
                }
                flag_modified(waifu, "dynamic")
                count += 1
        
        session.commit()
        
        await callback.answer(f"✅ Энергия восстановлена для {count} вайфу!")
        await callback.message.edit_text(
            f"⚡ <b>Энергия восстановлена</b>\n\n"
            f"Восстановлено для {count} вайфу\n"
            f"Энергия установлена на 100%",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_add_currency(callback: CallbackQuery, tg_user_id: int) -> None:
    """Добавление валюты"""
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Добавляем валюту
        old_coins = user.coins
        old_gems = user.gems
        
        user.coins += 10000
        user.gems += 100
        
        session.commit()
        
        await callback.answer("✅ Валюта добавлена!")
        await callback.message.edit_text(
            f"💰 <b>Валюта добавлена</b>\n\n"
            f"💰 Монеты: {old_coins} → {user.coins} (+10000)\n"
            f"💎 Гемы: {old_gems} → {user.gems} (+100)",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_add_xp_menu(callback: CallbackQuery, tg_user_id: int) -> None:
    """Меню выбора вайфу для добавления XP"""
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Получаем всех вайфу
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()
        
        if not waifus:
            await callback.answer("❌ У вас нет вайфу")
            return
        
        # Создаем кнопки для выбора вайфу
        keyboard_buttons = []
        for waifu in waifus[:10]:  # Показываем первые 10
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{waifu.name} - Ур.{waifu.level}",
                    callback_data=f"debug_add_xp_{waifu.id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            "✨ <b>Выберите вайфу для добавления 1000 XP:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_trigger_event(callback: CallbackQuery, tg_user_id: int) -> None:
    """Меню выбора чата для запуска события"""
    # Check if admin
    ADMIN_ID = 305174198
    if tg_user_id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    logger.info(f"🎯 Admin {tg_user_id} requested event trigger menu")
    
    session = SessionLocal()
    try:
        # Get all unique chat_ids from XPLog where source is 'message'
        # These are groups where users have been active
        result = session.execute(
            select(XPLog.meta)
            .where(XPLog.source == 'message')
            .distinct()
        )
        
        # Extract unique chat_ids from meta JSONB field
        chat_ids = []
        seen_chat_ids = set()
        
        for row in result:
            if row[0] and isinstance(row[0], dict):
                chat_id = row[0].get('chat_id')
                if chat_id and chat_id not in seen_chat_ids:
                    try:
                        chat_id_int = int(chat_id)
                        chat_ids.append(chat_id_int)
                        seen_chat_ids.add(chat_id)
                    except (ValueError, TypeError):
                        continue
        
        if not chat_ids:
            await callback.answer("❌ Нет активных чатов")
            await callback.message.edit_text(
                "❌ <b>Активных чатов не найдено</b>\n\n"
                "Нет групп, где пользователи писали сообщения.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
                ]),
                parse_mode="HTML"
            )
            return
        
        # Create keyboard with chat selection buttons
        keyboard_buttons = []
        for chat_id in chat_ids[:20]:  # Limit to 20 chats
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"💬 Chat ID: {chat_id}",
                    callback_data=f"debug_event_chat_{chat_id}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            f"🎯 <b>Выберите чат для запуска события:</b>\n\n"
            f"Найдено активных чатов: {len(chat_ids)}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_event_select_chat(callback: CallbackQuery, tg_user_id: int) -> None:
    """Trigger event in selected chat"""
    # Check if admin
    ADMIN_ID = 305174198
    if tg_user_id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    # Extract chat_id from callback_data: debug_event_chat_{chat_id}
    chat_id = int(callback.data.replace("debug_event_chat_", ""))
    
    logger.info(f"🎯 Admin {tg_user_id} selected chat {chat_id} for event trigger")
    
    bot = callback.bot
    
    # Check if there's already an active event in this chat
    from bot.services.group_event_system import group_event_manager
    existing_event = group_event_manager.get_event(chat_id)
    
    if existing_event and not existing_event.is_expired():
        await callback.answer("⚠️ Уже есть активное событие в этом чате!")
        return
    
    # Select random event type
    from bot.data_tables import EVENTS
    event_type = random.choice(list(EVENTS.keys()))
    
    logger.info(f"🎪 Starting event '{event_type}' in chat {chat_id}")
    
    # Start the event
    event_state = group_event_manager.start_event(chat_id, event_type)
    
    session = SessionLocal()
    try:
        # Get all users who are members of this chat
        result = session.execute(
            select(XPLog.user_id, XPLog.meta)
            .where(XPLog.source == 'message')
        )
        
        # Filter and collect unique user_ids from this chat
        user_ids = []
        seen_user_ids = set()
        
        for row in result:
            user_id, meta = row[0], row[1]
            if meta and isinstance(meta, dict):
                if meta.get('chat_id') == chat_id and user_id not in seen_user_ids:
                    user_ids.append(user_id)
                    seen_user_ids.add(user_id)
        
        # Send invitations to all users in this chat
        from bot.services.group_event_system import send_event_invitation
        import asyncio
        
        invitations_sent = 0
        for user_id in user_ids:
            try:
                # Get user
                user_result = session.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    continue
                
                # Send invitation
                message_id = await send_event_invitation(
                    bot,
                    session,
                    user,
                    event_type,
                    chat_id,
                    event_state.event_id
                )
                
                if message_id:
                    invitations_sent += 1
                    group_event_manager.add_message_to_delete(chat_id, message_id)
                    
            except Exception as e:
                logger.error(f"Error sending invitation to user {user_id}: {e}", exc_info=True)
                continue
        
        # Announce event in group
        event = EVENTS.get(event_type, {})
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"🎪 <b>Начинается соревнование!</b>\n\n"
                f"🎯 <b>{event['name']}</b>\n"
                f"📝 {event.get('description', '')}\n\n"
                f"⏱️ У вас есть <b>60 секунд</b> чтобы принять участие!"
            ),
            parse_mode="HTML"
        )
        
        # Schedule finalization after 60 seconds
        async def finalize_after_delay():
            await asyncio.sleep(60)
            from bot.services.group_event_system import finalize_group_event
            
            session = SessionLocal()
            try:
                results_text = await finalize_group_event(bot, session, chat_id)
                if results_text:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=results_text,
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"Error finalizing event in chat {chat_id}: {e}", exc_info=True)
            finally:
                session.close()
        
        asyncio.create_task(finalize_after_delay())
        
        logger.info(f"✅ Event '{event_type}' started in chat {chat_id} with {invitations_sent} invitations")
        
        await callback.answer("✅ Событие запущено!")
        await callback.message.edit_text(
            f"🎯 <b>Событие запущено!</b>\n\n"
            f"💬 Чат ID: {chat_id}\n"
            f"🎪 Событие: {event['name']}\n"
            f"📬 Приглашений отправлено: {invitations_sent}\n"
            f"⏱️ Результаты через 60 секунд",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_add_xp_to_waifu(callback: CallbackQuery, tg_user_id: int) -> None:
    """Добавление 1000 XP выбранной вайфу"""
    session = SessionLocal()
    try:
        # Парсим ID вайфу из callback_data
        waifu_id = callback.data.replace("debug_add_xp_", "")
        
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Получаем вайфу
        waifu_result = session.execute(
            select(Waifu).where(Waifu.id == waifu_id, Waifu.owner_id == user.id)
        )
        waifu = waifu_result.scalar_one_or_none()
        
        if not waifu:
            await callback.answer("❌ Вайфу не найдена")
            return
        
        # Добавляем XP и проверяем level-up
        from bot.services.level_up import level_up_service
        from sqlalchemy.orm.attributes import flag_modified
        
        old_xp = waifu.xp
        old_level = waifu.level
        
        waifu.xp += 1000
        
        # Проверяем level-up
        should_level_up, new_level = level_up_service.check_level_up(waifu.xp, waifu.level)
        level_up_info = None
        
        if should_level_up:
            waifu_data = {
                "level": waifu.level,
                "xp": waifu.xp,
                "stats": dict(waifu.stats)
            }
            level_up_info = level_up_service.apply_level_up(waifu_data, new_level)
            waifu.level = new_level
            waifu.stats = level_up_info["updated_stats"]
            flag_modified(waifu, "stats")
        
        session.commit()
        session.refresh(waifu)
        
        # Формируем сообщение
        xp_info = level_up_service.get_xp_progress_info(waifu.xp, waifu.level)
        
        text = (
            f"✨ <b>XP добавлен!</b>\n\n"
            f"👤 {waifu.name}\n"
            f"⚡ Уровень: {old_level} → {waifu.level}\n"
            f"📊 XP: {old_xp} → {waifu.xp}\n"
            f"📈 Прогресс: {xp_info['xp_in_current_level']}/{xp_info['xp_needed_in_level']}\n"
        )
        
        if level_up_info:
            # Add formatted level-up message
            level_up_message = level_up_service.format_level_up_message(waifu.name, level_up_info)
            text += f"\n{level_up_message}"
        
        await callback.answer("✅ 1000 XP добавлено!")
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_wipe_confirm(callback: CallbackQuery, tg_user_id: int) -> None:
    """Подтверждение удаления всех вайфу"""
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Подсчитываем количество вайфу
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()
        count = len(waifus)
        
        if count == 0:
            await callback.answer("❌ У вас нет вайфу для удаления")
            return
        
        # Показываем подтверждение
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Да, удалить всех", callback_data="debug_wipe_execute")],
            [InlineKeyboardButton(text="✅ Нет, отменить", callback_data="debug_menu")]
        ])
        
        await callback.message.edit_text(
            f"🗑️ <b>Удаление всех вайфу</b>\n\n"
            f"⚠️ <b>ВНИМАНИЕ!</b> Это действие нельзя отменить!\n\n"
            f"У вас {count} вайфу. Вы уверены, что хотите удалить их всех?\n\n"
            f"Все данные вайфу (уровень, опыт, характеристики) будут безвозвратно потеряны!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_wipe_execute(callback: CallbackQuery, tg_user_id: int) -> None:
    """Выполнение удаления всех вайфу"""
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Удаляем всех вайфу пользователя
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id)
        )
        waifus = waifus_result.scalars().all()
        count = len(waifus)
        
        for waifu in waifus:
            session.delete(waifu)
        
        session.commit()
        
        await callback.answer("✅ Все вайфу удалены!")
        await callback.message.edit_text(
            f"🗑️ <b>Вайфу удалены</b>\n\n"
            f"✅ Удалено вайфу: {count}\n\n"
            f"Теперь вы можете начать заново!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_add_skill_points(callback: CallbackQuery, tg_user_id: int) -> None:
    """Добавление 100 очков навыков"""
    if not SKILLS_ENABLED:
        await callback.answer("⚠️ Система навыков пока не активирована")
        return
    
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Получаем или создаем запись UserSkills
        user_skills_result = session.execute(
            select(UserSkills).where(UserSkills.user_id == user.id)
        )
        user_skills = user_skills_result.scalar_one_or_none()
        
        if not user_skills:
            user_skills = UserSkills(user_id=user.id, skill_points=0, total_earned_points=0)
            session.add(user_skills)
        
        old_points = user_skills.skill_points
        old_total = user_skills.total_earned_points
        
        user_skills.skill_points += 100
        user_skills.total_earned_points += 100
        
        session.commit()
        
        await callback.answer("✅ Очки навыков добавлены!")
        await callback.message.edit_text(
            f"🧬 <b>Очки навыков добавлены</b>\n\n"
            f"💰 Текущие очки: {old_points} → {user_skills.skill_points} (+100)\n"
            f"📊 Всего получено: {old_total} → {user_skills.total_earned_points}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


async def handle_debug_wipe_skill_points(callback: CallbackQuery, tg_user_id: int) -> None:
    """Удаление всех очков навыков и уровней с возвратом потраченных очков"""
    if not SKILLS_ENABLED:
        await callback.answer("⚠️ Система навыков пока не активирована")
        return
    
    session = SessionLocal()
    try:
        # Получаем пользователя
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await callback.answer("Пользователь не найден")
            return
        
        # Получаем запись UserSkills
        user_skills_result = session.execute(
            select(UserSkills).where(UserSkills.user_id == user.id)
        )
        user_skills = user_skills_result.scalar_one_or_none()
        
        if not user_skills:
            await callback.answer("❌ У вас нет очков навыков")
            return
        
        # Получаем все уровни навыков и считаем возврат очков
        skill_levels_result = session.execute(
            select(UserSkillLevel).join(Skill).where(UserSkillLevel.user_id == user.id)
        )
        skill_levels = skill_levels_result.scalars().all()
        
        # Рассчитываем возврат очков за каждый уровень каждого навыка
        points_refunded = 0
        for skill_level in skill_levels:
            skill = skill_level.skill
            for level in range(1, skill_level.level + 1):
                # Calculate cost for this level
                cost = skill.base_cost + (level - 1) * skill.cost_increase
                points_refunded += cost
        
        # Удаляем все уровни навыков
        skills_count = len(skill_levels)
        for skill_level in skill_levels:
            session.delete(skill_level)
        
        # Возвращаем очки
        old_points = user_skills.skill_points
        new_points = old_points + points_refunded
        
        user_skills.skill_points = new_points
        # Не сбрасываем total_earned_points, т.к. очки были заработаны легитимно
        
        session.commit()
        
        await callback.answer("✅ Все очки навыков возвращены!")
        await callback.message.edit_text(
            f"💰 <b>Очки навыков сброшены</b>\n\n"
            f"📊 Навыков сброшено: {skills_count}\n"
            f"💰 Возвращено очков: {points_refunded}\n"
            f"💵 Текущих очков: {old_points} → {new_points}\n\n"
            f"Все уровни навыков сброшены, очки возвращены!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="debug_menu")]
            ]),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()
