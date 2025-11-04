"""
Clan events API endpoints (raid, quests, etc.)
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import random

from bot.db import get_db
from bot.models import (
    User, Clan, ClanMember, ClanEvent, ClanEventParticipation,
    Waifu
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_telegram_user_id(request) -> Optional[int]:
    """Extract user_id from Telegram WebApp initData"""
    try:
        from urllib.parse import parse_qs, unquote
        import json
        
        init_data = request.headers.get("X-Telegram-Init-Data") or request.query_params.get("initData")
        if not init_data:
            return None
        
        data_str = unquote(init_data)
        parsed_data = parse_qs(data_str)
        user_str = parsed_data.get('user', [None])[0]
        if not user_str:
            return None
        
        user_data = json.loads(user_str)
        return user_data.get('id')
    except Exception:
        return None


def get_user_from_request(request, db: Session) -> User:
    """Get user from request initData"""
    telegram_user_id = get_telegram_user_id(request)
    if telegram_user_id:
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if user:
            return user
    
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/api/clans/events")
async def get_clan_events(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get clan events"""
    try:
        user = get_user_from_request(request, db)
        
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Вы не состоите в клане")
        
        active_events = db.query(ClanEvent).filter(
            and_(ClanEvent.clan_id == member.clan_id, ClanEvent.status == 'active')
        ).all()
        
        recent_events = db.query(ClanEvent).filter(
            and_(ClanEvent.clan_id == member.clan_id, ClanEvent.status.in_(['completed', 'cancelled']))
        ).order_by(ClanEvent.started_at.desc()).limit(10).all()
        
        def format_event(event):
            event_data = {
                "id": event.id,
                "type": event.event_type,
                "status": event.status,
                "started_at": event.started_at.isoformat(),
                "data": event.data or {}
            }
            if event.ends_at:
                event_data["ends_at"] = event.ends_at.isoformat()
            if event.rewards:
                event_data["rewards"] = event.rewards
            return event_data
        
        return {"active": [format_event(e) for e in active_events], "recent": [format_event(e) for e in recent_events]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/raid/attack")
async def attack_raid_boss(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Attack raid boss"""
    try:
        user = get_user_from_request(request, db)
        
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Вы не состоите в клане")
        
        raid_event = db.query(ClanEvent).filter(
            and_(ClanEvent.clan_id == member.clan_id, ClanEvent.event_type == 'raid', ClanEvent.status == 'active')
        ).first()
        
        if not raid_event:
            raise HTTPException(status_code=404, detail="Активного рейда не найдено")
        
        waifu = db.query(Waifu).filter(and_(Waifu.owner_id == user.id, Waifu.is_active == True)).first()
        if not waifu:
            raise HTTPException(status_code=400, detail="Выберите активную вайфу")
        
        from bot.services.waifu_generator import calculate_waifu_power
        waifu_power = calculate_waifu_power({'stats': waifu.stats or {}, 'dynamic': waifu.dynamic or {}, 'level': waifu.level})
        damage = int(waifu_power * random.uniform(0.5, 1.5))
        
        participation = db.query(ClanEventParticipation).filter(
            and_(ClanEventParticipation.event_id == raid_event.id, ClanEventParticipation.user_id == user.id)
        ).first()
        
        if participation:
            participation.score += damage
            participation.contribution['attacks'] = participation.contribution.get('attacks', 0) + 1
            participation.contribution['total_damage'] = participation.contribution.get('total_damage', 0) + damage
        else:
            participation = ClanEventParticipation(
                event_id=raid_event.id,
                user_id=user.id,
                score=damage,
                contribution={'attacks': 1, 'total_damage': damage}
            )
            db.add(participation)
        
        event_data = raid_event.data or {}
        boss_hp = event_data.get('boss_hp', 0)
        boss_max_hp = event_data.get('boss_max_hp', 0)
        new_hp = max(0, boss_hp - damage)
        event_data['boss_hp'] = new_hp
        
        if new_hp <= 0:
            raid_event.status = 'completed'
            clan = db.query(Clan).filter(Clan.id == member.clan_id).first()
            
            all_participations = db.query(ClanEventParticipation).filter(
                ClanEventParticipation.event_id == raid_event.id
            ).order_by(ClanEventParticipation.score.desc()).all()
            
            for idx, part in enumerate(all_participations):
                participant = db.query(User).filter(User.id == part.user_id).first()
                if participant:
                    gold_reward = 500
                    skill_points_reward = 10
                    if idx == 0:
                        gold_reward = 2000
                        skill_points_reward = 50
                    elif idx < 3:
                        gold_reward = 1000
                        skill_points_reward = 30
                    elif idx < 10:
                        gold_reward = 750
                        skill_points_reward = 20
                    
                    participant.coins += gold_reward
                    
                    try:
                        from bot.models import UserSkills
                        user_skills = db.query(UserSkills).filter(UserSkills.user_id == participant.id).first()
                        if user_skills:
                            user_skills.skill_points += skill_points_reward
                    except:
                        pass
            
            clan.experience += 100
            xp_for_next = clan.level * 500
            if clan.experience >= xp_for_next:
                clan.level += 1
                clan.settings['max_members'] = 50 + (clan.level * 5)
        
        raid_event.data = event_data
        db.commit()
        
        logger.info(f"✅ User {user.id} attacked raid boss for {damage} damage")
        
        return {
            "success": True,
            "damage": damage,
            "boss_hp": new_hp,
            "boss_max_hp": boss_max_hp,
            "boss_defeated": new_hp <= 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/raid/start")
async def start_raid_event(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Start a new clan raid event"""
    try:
        user = get_user_from_request(request, db)
        
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Вы не состоите в клане")
        
        if member.role not in ['leader', 'officer']:
            raise HTTPException(status_code=403, detail="Только лидеры и офицеры могут запускать рейды")
        
        existing_raid = db.query(ClanEvent).filter(
            and_(ClanEvent.clan_id == member.clan_id, ClanEvent.event_type == 'raid', ClanEvent.status == 'active')
        ).first()
        
        if existing_raid:
            raise HTTPException(status_code=400, detail="Рейд уже активен")
        
        last_raid = db.query(ClanEvent).filter(
            and_(ClanEvent.clan_id == member.clan_id, ClanEvent.event_type == 'raid')
        ).order_by(ClanEvent.started_at.desc()).first()
        
        if last_raid and last_raid.started_at:
            days_since = (datetime.now() - last_raid.started_at).days
            if days_since < 3:
                raise HTTPException(status_code=400, detail=f"Рейд можно запустить через {3 - days_since} дней")
        
        clan = db.query(Clan).filter(Clan.id == member.clan_id).first()
        
        # Используем функцию расчета HP босса из сервиса
        from bot.services.clan_raid import calculate_boss_hp
        boss_max_hp = calculate_boss_hp(clan, db)
        
        raid_event = ClanEvent(
            clan_id=clan.id,
            event_type='raid',
            status='active',
            started_at=datetime.now(),
            ends_at=datetime.now() + timedelta(days=3),  # 3 дня на рейд
            data={
                'boss_name': 'Дракон Клана',
                'boss_max_hp': boss_max_hp,
                'boss_current_hp': boss_max_hp,
                'boss_hp': boss_max_hp,  # Для совместимости со старым кодом
                'damage_dealt': 0,
                'participant_count': 0,
                'activity_tracking': True,  # Включаем отслеживание активности
                'started_by': user.id
            }
        )
        db.add(raid_event)
        db.commit()
        
        logger.info(f"✅ Raid started for clan {clan.name} with {boss_max_hp} HP")
        
        return {
            "success": True,
            "event": {
                "id": raid_event.id,
                "boss_name": "Дракон Клана",
                "boss_max_hp": boss_max_hp,
                "boss_current_hp": boss_max_hp,
                "boss_hp": boss_max_hp
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/clans/raid/status")
async def get_raid_status(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получить статус активного рейда"""
    try:
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
                    'username': participant_user.display_name or participant_user.username or f"User {p.user_id}",
                    'damage': p.score,
                    'contribution': p.contribution or {}
                })
        
        boss_current_hp = event_data.get('boss_current_hp', event_data.get('boss_hp', 0))
        boss_max_hp = event_data.get('boss_max_hp', 0)
        
        return {
            "active": True,
            "boss_name": event_data.get('boss_name', 'Дракон Клана'),
            "boss_max_hp": boss_max_hp,
            "boss_current_hp": boss_current_hp,
            "damage_dealt": event_data.get('damage_dealt', 0),
            "hp_percentage": (boss_current_hp / boss_max_hp * 100) if boss_max_hp > 0 else 0,
            "leaderboard": leaderboard,
            "ends_at": raid_event.ends_at.isoformat() if raid_event.ends_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/clans/raid/my-contribution")
async def get_my_contribution(request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Получить свой вклад в активный рейд"""
    try:
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
        
        contribution = participation.contribution or {}
        
        return {
            "participating": True,
            "damage": participation.score,
            "contribution_percentage": round(contribution_rate, 2),
            "message_count": contribution.get('message_count', 0),
            "damage_by_type": contribution.get('damage_by_type', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

