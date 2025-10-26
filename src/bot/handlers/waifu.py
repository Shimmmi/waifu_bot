from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import logging
import traceback

from bot.db import SessionLocal
from bot.models import User, Waifu, Event, EventParticipation
from bot.services.waifu_generator import generate_waifu, format_waifu_card, calculate_waifu_power
from bot.services.event_system import (
    calculate_event_score, get_event_rewards, get_random_event, 
    get_event_description, format_event_result, get_available_events,
    can_participate_in_event
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("waifu"))
async def cmd_waifu(message: Message) -> None:
    """Главная команда вайфу"""
    if message.from_user is None:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Призвать вайфу", callback_data="waifu_pull")],
        [InlineKeyboardButton(text="📋 Мои вайфу", callback_data="waifu_list")],
        [InlineKeyboardButton(text="🎯 События", callback_data="waifu_events")],
        [InlineKeyboardButton(text="🏆 Турниры", callback_data="waifu_tournaments")]
    ])

    await message.answer(
        "🎭 <b>Вайфу система</b>\n\n"
        "Добро пожаловать в мир вайфу! Здесь вы можете:\n"
        "• Призывать новых вайфу\n"
        "• Участвовать в событиях\n"
        "• Соревноваться в турнирах\n"
        "• Развивать своих вайфу\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "waifu_pull")
async def handle_waifu_pull(callback: CallbackQuery) -> None:
    """Обработка призыва вайфу"""
    if callback.from_user is None:
        logger.warning("Waifu pull callback with no user")
        return

    tg_user_id = callback.from_user.id
    logger.info(f"🎰 Waifu pull requested by user {tg_user_id}")
    
    session = SessionLocal()
    try:
        # Проверяем пользователя
        logger.debug(f"Checking user {tg_user_id} in database")
        result = session.execute(select(User).where(User.tg_id == tg_user_id))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User {tg_user_id} not found in database")
            await callback.answer("Сначала используйте /start")
            return

        logger.info(f"User found: {user.username}, coins: {user.coins}")

        # Проверяем баланс
        if user.coins < 100:
            logger.info(f"Insufficient coins for user {user.username}: {user.coins}")
            await callback.answer("Недостаточно монет! Нужно 100 монет для призыва.")
            return

        # Генерируем новую вайфу
        logger.debug("Getting max card number")
        max_card = session.execute(select(func.max(Waifu.card_number))).scalar() or 0
        logger.info(f"Max card number: {max_card}, generating new waifu #{max_card + 1}")
        
        try:
            new_waifu_data = generate_waifu(max_card + 1, user.id)
            logger.info(f"✅ Generated waifu: {new_waifu_data['name']} ({new_waifu_data['race']}, {new_waifu_data['rarity']})")
            logger.debug(f"Waifu data: {new_waifu_data}")
        except Exception as gen_error:
            logger.error(f"❌ Error generating waifu: {gen_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Создаем вайфу в базе
        try:
            logger.debug("Creating Waifu model instance")
            waifu = Waifu(**new_waifu_data)
            session.add(waifu)
            logger.debug("Waifu added to session")
        except Exception as db_error:
            logger.error(f"❌ Error creating Waifu in database: {db_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Списываем монеты
        user.coins -= 100
        logger.debug(f"Deducted 100 coins, remaining: {user.coins}")
        
        # Записываем транзакцию
        try:
            from bot.models import Transaction
            transaction = Transaction(
                user_id=user.id,
                kind="spend",
                amount=100,
                currency="coins",
                reason="waifu_pull",
                meta={"waifu_id": waifu.id}
            )
            session.add(transaction)
            logger.debug("Transaction added to session")
        except Exception as trans_error:
            logger.error(f"❌ Error creating transaction: {trans_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Commit to database
        try:
            logger.debug("Committing to database...")
            session.commit()
            logger.info("✅ Database commit successful")
        except Exception as commit_error:
            logger.error(f"❌ Error committing to database: {commit_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        # Отправляем результат
        try:
            logger.debug("Formatting waifu card")
            card_text = format_waifu_card(new_waifu_data)
            logger.debug("Sending response to user")
            await callback.message.edit_text(
                f"🎰 <b>Призыв завершен!</b>\n\n{card_text}\n\n"
                f"💰 Осталось монет: {user.coins}",
                parse_mode="HTML"
            )
            await callback.answer("Вайфу успешно призвана!")
            logger.info(f"✅ Successfully summoned waifu {new_waifu_data['name']} for user {user.username}")
        except Exception as msg_error:
            logger.error(f"❌ Error sending message: {msg_error}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    except Exception as e:
        logger.error(f"❌ WAIFU PULL ERROR for user {tg_user_id}: {type(e).__name__}: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        await callback.answer(f"Ошибка при призыве: {str(e)}")
        session.rollback()
    finally:
        session.close()
        logger.debug("Session closed")


@router.callback_query(lambda c: c.data == "waifu_list")
async def handle_waifu_list(callback: CallbackQuery) -> None:
    """Список вайфу пользователя"""
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

        # Получаем вайфу пользователя
        waifus_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id).order_by(Waifu.created_at.desc())
        )
        waifus = waifus_result.scalars().all()

        if not waifus:
            await callback.message.edit_text(
                "📋 <b>Мои вайфу</b>\n\n"
                "У вас пока нет вайфу.\n"
                "Используйте призыв, чтобы получить свою первую вайфу!",
                parse_mode="HTML"
            )
            await callback.answer()
            return

        # Формируем список
        text = f"📋 <b>Мои вайфу ({len(waifus)})</b>)\n\n"
        
        for i, waifu in enumerate(waifus[:5], 1):  # Показываем первые 5
            power = calculate_waifu_power({
                "stats": waifu.stats,
                "dynamic": waifu.dynamic,
                "level": waifu.level
            })
            text += f"{i}. {waifu.name} [{waifu.rarity}] - 💪{power}\n"

        if len(waifus) > 5:
            text += f"\n... и еще {len(waifus) - 5} вайфу"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_waifu_menu")]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


@router.callback_query(lambda c: c.data == "waifu_events")
async def handle_waifu_events(callback: CallbackQuery) -> None:
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
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_waifu_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "random_event")
async def handle_random_event(callback: CallbackQuery) -> None:
    """Участие в случайном событии"""
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

        # Получаем первую вайфу пользователя
        waifu_result = session.execute(
            select(Waifu).where(Waifu.owner_id == user.id).limit(1)
        )
        waifu = waifu_result.scalar_one_or_none()

        if not waifu:
            await callback.answer("У вас нет вайфу для участия в событиях!")
            return

        # Выбираем случайное событие
        event_type = get_random_event()
        
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
        waifu.xp += rewards["xp"]
        waifu.dynamic["energy"] = max(0, waifu.dynamic["energy"] - 20)
        waifu.dynamic["mood"] = min(100, waifu.dynamic["mood"] + 5)
        waifu.dynamic["loyalty"] = min(100, waifu.dynamic["loyalty"] + 2)
        
        # Обновляем пользователя
        user.coins += rewards["coins"]
        
        session.commit()

        # Формируем результат
        result_text = format_event_result({
            "name": waifu.name,
            "stats": waifu.stats,
            "dynamic": waifu.dynamic
        }, event_type, score, rewards)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к событиям", callback_data="waifu_events")]
        ])

        await callback.message.edit_text(result_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Ошибка: {str(e)}")
    finally:
        session.close()


@router.callback_query(lambda c: c.data == "back_to_waifu_menu")
async def handle_back_to_waifu_menu(callback: CallbackQuery) -> None:
    """Возврат в меню вайфу"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Призвать вайфу", callback_data="waifu_pull")],
        [InlineKeyboardButton(text="📋 Мои вайфу", callback_data="waifu_list")],
        [InlineKeyboardButton(text="🎯 События", callback_data="waifu_events")],
        [InlineKeyboardButton(text="🏆 Турниры", callback_data="waifu_tournaments")]
    ])

    await callback.message.edit_text(
        "🎭 <b>Вайфу система</b>\n\n"
        "Добро пожаловать в мир вайфу! Здесь вы можете:\n"
        "• Призывать новых вайфу\n"
        "• Участвовать в событиях\n"
        "• Соревноваться в турнирах\n"
        "• Развивать своих вайфу\n\n"
        "Выберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()
