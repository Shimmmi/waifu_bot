"""
Clan Raid Service

Обрабатывает активность игроков в групповых чатах для нанесения урона боссу.
"""

import logging
from datetime import datetime
from typing import Dict, Tuple, Optional, Any

from aiogram.types import Message
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from bot.models import (
    ClanMember, ClanEvent, ClanEventParticipation, ClanRaidActivity,
    User, Clan, Waifu
)

logger = logging.getLogger(__name__)


class ClanRaidService:
    """Service for processing clan raid activities from group chat messages"""
    
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
        
        Args:
            session: SQLAlchemy сессия
            user_id: ID пользователя
            chat_id: ID чата Telegram
            message: Сообщение от aiogram
            
        Returns:
            Dict с информацией об уроне или None, если рейдов нет
        """
        try:
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
                contribution = participation.contribution.copy() if participation.contribution else {}
                contribution['total_damage'] = contribution.get('total_damage', 0) + damage
                contribution['message_count'] = contribution.get('message_count', 0) + 1
                
                damage_by_type = contribution.get('damage_by_type', {}).copy()
                damage_by_type[message_type] = damage_by_type.get(message_type, 0) + damage
                contribution['damage_by_type'] = damage_by_type
                
                participation.contribution = contribution
                flag_modified(participation, 'contribution')
            
            # 9. Проверяем, побежден ли босс
            boss_defeated = False
            if new_hp <= 0:
                boss_defeated = True
                await self._finalize_raid(session, raid_event)
            
            # 10. Обновляем событие
            raid_event.data = event_data
            flag_modified(raid_event, 'data')
            
            session.commit()
            
            logger.info(f"✅ Raid damage: User {user_id} dealt {damage} damage to raid {raid_event.id}. Boss HP: {new_hp}")
            
            return {
                'damage': damage,
                'boss_hp': new_hp,
                'boss_max_hp': event_data.get('boss_max_hp', 0),
                'boss_defeated': boss_defeated
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing raid message: {e}", exc_info=True)
            session.rollback()
            return None
    
    def _get_message_damage(self, message: Message) -> Tuple[str, int]:
        """
        Определяет тип сообщения и соответствующий урон.
        
        Args:
            message: Сообщение от aiogram
            
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
        
        Args:
            session: SQLAlchemy сессия
            raid_event: Событие рейда
        """
        try:
            # 1. Обновляем статус рейда
            raid_event.status = 'completed'
            raid_event.ends_at = datetime.utcnow()
            
            # 2. Получаем всех участников с их уроном
            participations = session.query(ClanEventParticipation).filter(
                ClanEventParticipation.event_id == raid_event.id
            ).order_by(ClanEventParticipation.score.desc()).all()
            
            if not participations:
                session.commit()
                logger.warning(f"⚠️ Raid {raid_event.id} completed with no participants")
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
                user.skill_points += skill_points_reward
                
                # Сохраняем награды в participation
                contribution = participation.contribution.copy() if participation.contribution else {}
                contribution['rewards'] = {
                    'gold': gold_reward,
                    'gems': gems_reward,
                    'skill_points': skill_points_reward
                }
                participation.contribution = contribution
                flag_modified(participation, 'contribution')
                
                logger.info(
                    f"✅ Raid rewards for user {user.id} (place {idx + 1}): "
                    f"{gold_reward} gold, {gems_reward} gems, {skill_points_reward} skill points"
                )
            
            # 6. Обновляем опыт клана
            clan = session.query(Clan).filter(Clan.id == raid_event.clan_id).first()
            if clan:
                clan.experience += 500  # Бонус опыта за победу в рейде
                logger.info(f"✅ Clan {clan.id} received 500 experience for raid victory")
            
            # 7. Сохраняем награды в событии
            raid_event.rewards = {
                'distributed': True,
                'total_participants': len(participations),
                'total_damage': total_damage
            }
            
            session.commit()
            
            logger.info(f"✅ Raid {raid_event.id} completed! Total damage: {total_damage}, Participants: {len(participations)}")
            
        except Exception as e:
            logger.error(f"❌ Error finalizing raid: {e}", exc_info=True)
            session.rollback()
            raise


def calculate_boss_hp(clan: Clan, session: Session) -> int:
    """
    Рассчитывает максимальное HP босса на основе силы клана.
    
    Формула:
    - Базовая сила клана = sum(мощь активных вайфу всех участников)
    - HP босса = Базовая сила × коэффициент сложности × коэффициент уровня клана
    
    Коэффициенты:
    - Базовая сложность: 100 (босс должен быть достаточно сильным)
    - Множитель уровня клана: 1 + (уровень_клана * 0.1)
    
    Args:
        clan: Клан
        session: SQLAlchemy сессия
        
    Returns:
        Максимальное HP босса
    """
    try:
        # Получаем всех участников
        members = session.query(ClanMember).filter(
            ClanMember.clan_id == clan.id
        ).all()
        
        total_power = 0
        for member in members:
            try:
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
                        'level': waifu.level or 1,
                        'rarity': waifu.rarity or 'Common'
                    }, skill_effects)
                    
                    total_power += power
            except Exception as e:
                logger.warning(f"⚠️ Error calculating power for member {member.user_id}: {e}")
                continue
        
        # Базовая сложность
        BASE_DIFFICULTY = 100
        
        # Множитель уровня клана
        clan_level = getattr(clan, 'level', 1) or 1
        level_multiplier = 1 + (clan_level * 0.1)
        
        # Рассчитываем HP
        boss_hp = int(total_power * BASE_DIFFICULTY * level_multiplier)
        
        # Минимальное HP (для маленьких кланов)
        min_hp = 100000
        boss_hp = max(boss_hp, min_hp)
        
        return boss_hp
    except Exception as e:
        logger.error(f"❌ Error calculating boss HP: {e}", exc_info=True)
        # Return minimum HP on error
        return 100000
