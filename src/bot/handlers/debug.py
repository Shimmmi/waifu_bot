"""
Debug menu handlers for Waifu Bot
Admin/debug commands for testing and troubleshooting
"""

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from sqlalchemy import select, update
from datetime import datetime

from bot.db import SessionLocal
from bot.models import User, Waifu

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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Восстановить энергию всем вайфу", callback_data="debug_restore_energy")],
        [InlineKeyboardButton(text="💰 +10000 монет и +100 гемов", callback_data="debug_add_currency")],
        [InlineKeyboardButton(text="✨ +1000 XP для вайфу", callback_data="debug_add_xp_menu")],
        [InlineKeyboardButton(text="🧬 +100 очков прокачки", callback_data="debug_add_skill_points")],
        [InlineKeyboardButton(text="🗑️ Убрать все очки прокачки", callback_data="debug_wipe_skill_points")],
        [InlineKeyboardButton(text="🗑️ Удалить всех вайфу", callback_data="debug_wipe_confirm")],
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
