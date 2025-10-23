from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from datetime import datetime

from bot.db import SessionLocal
from bot.models import User, Waifu, Transaction
from bot.services.waifu_generator import generate_waifu, format_waifu_card, calculate_waifu_power

router = Router()

# ID администратора
ADMIN_ID = 305174198

@router.message(Command("debug"))
async def cmd_debug(message: Message) -> None:
    """Debug команда для диагностики проблем"""
    if message.from_user is None:
        return
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для использования debug команд.")
        return
    
    session = SessionLocal()
    try:
        # Проверяем пользователя
        result = session.execute(select(User).where(User.tg_id == message.from_user.id))
        user = result.scalar_one_or_none()
        
        if user is None:
            await message.answer("❌ Пользователь не найден в базе данных.")
            return
        
        # Получаем статистику
        waifu_count = session.execute(
            select(func.count(Waifu.id)).where(Waifu.owner_id == user.id)
        ).scalar()
        
        total_waifu = session.execute(select(func.count(Waifu.id))).scalar()
        
        # Проверяем последние транзакции
        last_transactions = session.execute(
            select(Transaction).where(Transaction.user_id == user.id)
            .order_by(Transaction.created_at.desc()).limit(5)
        ).scalars().all()
        
        debug_text = f"""
🔍 <b>DEBUG INFO</b>

👤 <b>Пользователь:</b>
ID: {user.id}
TG ID: {user.tg_id}
Имя: {user.display_name}
Монеты: {user.coins}
Гемы: {user.gems}

📊 <b>Статистика:</b>
Мои вайфу: {waifu_count}
Всего вайфу в системе: {total_waifu}

💰 <b>Последние транзакции:</b>
"""
        
        if last_transactions:
            for tx in last_transactions:
                debug_text += f"• {tx.kind} {tx.amount} {tx.currency} ({tx.reason})\n"
        else:
            debug_text += "Нет транзакций\n"
        
        # Тест генерации вайфу
        try:
            test_waifu = generate_waifu(999999, user.id)
            debug_text += f"\n✅ Генератор вайфу работает\n"
            debug_text += f"Тестовая вайфу: {test_waifu['name']} [{test_waifu['rarity']}]\n"
        except Exception as e:
            debug_text += f"\n❌ Ошибка генератора: {str(e)}\n"
        
        # Кнопки для тестирования
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🧪 Тестовый призыв", callback_data="admin_test_pull")],
            [InlineKeyboardButton(text="📋 Список вайфу", callback_data="admin_list_waifu")],
            [InlineKeyboardButton(text="🗑️ Очистить вайфу", callback_data="admin_clear_waifu")],
            [InlineKeyboardButton(text="💰 Добавить монеты", callback_data="admin_add_coins")]
        ])
        
        await message.answer(debug_text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка debug: {str(e)}")
    finally:
        session.close()


@router.callback_query(lambda c: c.data == "admin_test_pull")
async def handle_admin_test_pull(callback: CallbackQuery) -> None:
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


@router.callback_query(lambda c: c.data == "admin_list_waifu")
async def handle_admin_list_waifu(callback: CallbackQuery) -> None:
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


@router.callback_query(lambda c: c.data == "admin_clear_waifu")
async def handle_admin_clear_waifu(callback: CallbackQuery) -> None:
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


@router.callback_query(lambda c: c.data == "admin_add_coins")
async def handle_admin_add_coins(callback: CallbackQuery) -> None:
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


@router.callback_query(lambda c: c.data == "debug_back")
async def handle_debug_back(callback: CallbackQuery) -> None:
    """Возврат к debug меню"""
    if callback.from_user is None or callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав")
        return
    
    # Возвращаемся к debug команде
    await callback.message.edit_text("🔍 <b>DEBUG MENU</b>\n\nИспользуйте /debug для просмотра информации")
    await callback.answer()
