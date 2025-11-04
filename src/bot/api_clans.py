"""
Clan system API endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import and_, or_
from urllib.parse import parse_qs, unquote
import json
from datetime import datetime, timedelta

from bot.db import get_db
from bot.models import (
    User, Clan, ClanMember, ClanEvent, ClanEventParticipation, ClanChatMessage,
    Waifu
)

logger = logging.getLogger(__name__)

router = APIRouter()


def get_telegram_user_id(request: Request) -> Optional[int]:
    """Extract user_id from Telegram WebApp initData"""
    try:
        # Get initData from header or query params
        init_data = request.headers.get("X-Telegram-Init-Data") or request.query_params.get("initData")
        
        if not init_data:
            logger.warning("⚠️ No initData provided")
            return None
        
        # Decode initData
        data_str = unquote(init_data)
        parsed_data = parse_qs(data_str)
        
        # Get user from parsed_data
        user_str = parsed_data.get('user', [None])[0]
        if not user_str:
            logger.warning("⚠️ No user data in initData")
            return None
        
        # Parse JSON with user data
        user_data = json.loads(user_str)
        telegram_user_id = user_data.get('id')
        
        return telegram_user_id
    except Exception as e:
        logger.error(f"❌ Error extracting user ID: {e}")
        return None


def get_user_from_request(request: Request, db: Session) -> User:
    """Get user from request initData"""
    telegram_user_id = get_telegram_user_id(request)
    
    if telegram_user_id:
        user = db.query(User).filter(User.tg_id == telegram_user_id).first()
        if user:
            return user
    
    # Fallback to first user if initData not available (for testing)
    logger.warning("⚠️ No telegram_user_id, using first user as fallback")
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def calculate_total_power(db: Session, clan_id: int) -> int:
    """Calculate total power of all clan members"""
    members = db.query(ClanMember).filter(ClanMember.clan_id == clan_id).all()
    
    total = 0
    for member in members:
        # Get user's active waifu
        waifu = db.query(Waifu).filter(
            and_(Waifu.owner_id == member.user_id, Waifu.is_active == True)
        ).first()
        
        if waifu:
            # Simple power calculation (can be enhanced)
            from bot.services.waifu_generator import calculate_waifu_power
            power = calculate_waifu_power({
                'stats': waifu.stats or {},
                'dynamic': waifu.dynamic or {},
                'level': waifu.level
            })
            total += power
    
    return total


def update_clan_power_for_user(db: Session, user_id: int) -> None:
    """Update clan power if user is in a clan"""
    try:
        # Check if user is in a clan
        member = db.query(ClanMember).filter(ClanMember.user_id == user_id).first()
        if not member:
            return
        
        # Get clan
        clan = db.query(Clan).filter(Clan.id == member.clan_id).first()
        if not clan:
            return
        
        # Recalculate and update clan power
        new_power = calculate_total_power(db, clan.id)
        clan.total_power = new_power
        
        logger.debug(f"✅ Updated clan {clan.id} power: {new_power} (triggered by user {user_id})")
    except Exception as e:
        logger.error(f"❌ Error updating clan power for user {user_id}: {e}")


@router.post("/api/clans/create")
async def create_clan(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Create a new clan"""
    try:
        user = get_user_from_request(request, db)
        
        # Check if user is already in a clan
        existing_member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="Вы уже состоите в клане")
        
        # Parse request body
        body = await request.json()
        name = body.get('name', '').strip()
        tag = body.get('tag', '').strip().upper()
        description = body.get('description', '').strip()
        clan_type = body.get('type', 'open')
        
        # Validate
        if not name or len(name) < 3 or len(name) > 50:
            raise HTTPException(status_code=400, detail="Название клана должно быть от 3 до 50 символов")
        
        if not tag or len(tag) < 2 or len(tag) > 10:
            raise HTTPException(status_code=400, detail="Тег клана должен быть от 2 до 10 символов")
        
        if clan_type not in ['open', 'invite', 'closed']:
            raise HTTPException(status_code=400, detail="Неверный тип клана")
        
        # Check if name or tag already exists
        existing_clan = db.query(Clan).filter(
            or_(Clan.name == name, Clan.tag == tag)
        ).first()
        
        if existing_clan:
            raise HTTPException(status_code=400, detail="Клан с таким названием или тегом уже существует")
        
        # Check cost (1000 gold)
        if user.coins < 1000:
            raise HTTPException(status_code=400, detail="Недостаточно золота. Требуется: 1000")
        
        # Deduct coins
        user.coins -= 1000
        
        # Create clan
        clan = Clan(
            name=name,
            tag=tag,
            description=description,
            type=clan_type,
            leader_id=user.id,
            emblem_id=1
        )
        db.add(clan)
        db.flush()  # Get clan ID
        
        # Add leader as member
        member = ClanMember(
            clan_id=clan.id,
            user_id=user.id,
            role='leader'
        )
        db.add(member)
        
        # Update user's clan_id
        user.clan_id = clan.id
        
        db.commit()
        db.refresh(clan)
        
        logger.info(f"✅ Clan created: {name} ({tag}) by user {user.id}")
        
        return {
            "success": True,
            "clan": {
                "id": clan.id,
                "name": clan.name,
                "tag": clan.tag,
                "type": clan.type,
                "level": clan.level,
                "members_count": 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/clans/search")
async def search_clans(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Search for clans"""
    try:
        query = request.query_params.get('q', '').strip()
        clan_type = request.query_params.get('type', 'open')
        
        # Build query
        clans_query = db.query(Clan)
        
        if query:
            clans_query = clans_query.filter(
                or_(Clan.name.ilike(f"%{query}%"), Clan.tag.ilike(f"%{query}%"))
            )
        
        if clan_type:
            clans_query = clans_query.filter(Clan.type == clan_type)
        
        # Limit results
        clans = clans_query.limit(20).all()
        
        # Get member counts
        result = []
        for clan in clans:
            member_count = db.query(ClanMember).filter(ClanMember.clan_id == clan.id).count()
            result.append({
                "id": clan.id,
                "name": clan.name,
                "tag": clan.tag,
                "description": clan.description,
                "type": clan.type,
                "level": clan.level,
                "total_power": clan.total_power,
                "members_count": member_count
            })
        
        return {
            "clans": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/clans/my-clan")
async def get_my_clan(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get user's clan information"""
    try:
        user = get_user_from_request(request, db)
        
        # Get user's clan membership
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            return {"clan": None}
        
        # Get clan info
        clan = db.query(Clan).filter(Clan.id == member.clan_id).first()
        if not clan:
            return {"clan": None}
        
        # Get members
        members = db.query(ClanMember).filter(ClanMember.clan_id == clan.id).all()
        members_data = []
        for m in members:
            member_user = db.query(User).filter(User.id == m.user_id).first()
            members_data.append({
                "user_id": m.user_id,
                "username": member_user.username if member_user else "Unknown",
                "role": m.role,
                "joined_at": m.joined_at.isoformat(),
                "donated_gold": m.donated_gold,
                "donated_skills": m.donated_skills
            })
        
        # Get recent chat messages
        recent_messages = db.query(ClanChatMessage).filter(
            and_(
                ClanChatMessage.clan_id == clan.id,
                ClanChatMessage.is_deleted == False
            )
        ).order_by(ClanChatMessage.created_at.desc()).limit(50).all()
        
        messages_data = []
        for msg in reversed(recent_messages):  # Reverse to show oldest first
            msg_user = db.query(User).filter(User.id == msg.user_id).first()
            messages_data.append({
                "id": msg.id,
                "user_id": msg.user_id,
                "username": msg_user.username if msg_user else "Unknown",
                "message": msg.message,
                "created_at": msg.created_at.isoformat()
            })
        
        # Get clan image from settings
        clan_image = None
        if clan.settings and isinstance(clan.settings, dict):
            clan_image = clan.settings.get('image')
        
        return {
            "clan": {
                "id": clan.id,
                "name": clan.name,
                "tag": clan.tag,
                "description": clan.description,
                "type": clan.type,
                "level": clan.level,
                "experience": clan.experience,
                "total_power": clan.total_power,
                "members": members_data,
                "messages": messages_data,
                "my_role": member.role,
                "image": clan_image
            }
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/join")
async def join_clan(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Join a clan"""
    try:
        user = get_user_from_request(request, db)
        
        # Parse request body
        body = await request.json()
        clan_id = body.get('clan_id')
        
        if not clan_id:
            raise HTTPException(status_code=400, detail="clan_id is required")
        
        # Check if user is already in a clan
        existing_member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="Вы уже состоите в клане")
        
        # Get clan
        clan = db.query(Clan).filter(Clan.id == clan_id).first()
        if not clan:
            raise HTTPException(status_code=404, detail="Клан не найден")
        
        # Check clan type
        if clan.type == 'closed':
            raise HTTPException(status_code=403, detail="Этот клан закрыт")
        
        # Check member limit
        member_count = db.query(ClanMember).filter(ClanMember.clan_id == clan.id).count()
        max_members = 50 + (clan.level * 5)  # 50 base + 5 per level
        
        if member_count >= max_members:
            raise HTTPException(status_code=400, detail="Клан переполнен")
        
        # Add user to clan
        member = ClanMember(
            clan_id=clan.id,
            user_id=user.id,
            role='member'
        )
        db.add(member)
        
        # Update user's clan_id
        user.clan_id = clan.id
        
        # Update clan total power
        clan.total_power = calculate_total_power(db, clan.id)
        
        db.commit()
        
        logger.info(f"✅ User {user.id} joined clan {clan.name}")
        
        return {
            "success": True,
            "message": f"Вы присоединились к клану {clan.name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/leave")
async def leave_clan(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Leave a clan"""
    try:
        user = get_user_from_request(request, db)
        
        # Get user's clan membership
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=400, detail="Вы не состоите в клане")
        
        clan_id = member.clan_id
        clan = db.query(Clan).filter(Clan.id == clan_id).first()
        
        # If leader, clan must have at least one other member to transfer leadership
        if member.role == 'leader':
            other_members = db.query(ClanMember).filter(
                and_(ClanMember.clan_id == clan_id, ClanMember.user_id != user.id)
            ).all()
            
            if other_members:
                # Transfer leadership to the first officer, or to first member
                new_leader = None
                for m in other_members:
                    if m.role == 'officer':
                        new_leader = m
                        break
                
                if not new_leader:
                    new_leader = other_members[0]
                
                new_leader.role = 'leader'
                if clan:
                    clan.leader_id = new_leader.user_id
            else:
                # No other members, disband clan
                db.delete(clan)
        
        # Remove user from clan
        db.delete(member)
        
        # Update user's clan_id
        user.clan_id = None
        
        # Update clan total power if clan still exists
        if clan and db.query(Clan).filter(Clan.id == clan.id).first():
            clan.total_power = calculate_total_power(db, clan.id)
        
        db.commit()
        
        logger.info(f"✅ User {user.id} left clan")
        
        return {
            "success": True,
            "message": "Вы покинули клан"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/chat/send")
async def send_clan_message(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Send a message to clan chat"""
    try:
        user = get_user_from_request(request, db)
        
        # Parse request body
        body = await request.json()
        message = body.get('message', '').strip()
        
        if not message:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
        
        # Get user's clan membership
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Вы не состоите в клане")
        
        # Create chat message
        chat_message = ClanChatMessage(
            clan_id=member.clan_id,
            user_id=user.id,
            message=message
        )
        db.add(chat_message)
        
        # Keep only last 500 messages
        all_messages = db.query(ClanChatMessage).filter(
            ClanChatMessage.clan_id == member.clan_id
        ).order_by(ClanChatMessage.created_at.desc()).all()
        
        if len(all_messages) > 500:
            for old_msg in all_messages[500:]:
                db.delete(old_msg)
        
        db.commit()
        
        logger.info(f"✅ Message sent to clan chat by user {user.id}")
        
        return {
            "success": True,
            "message": "Сообщение отправлено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/clans/upload-image")
async def upload_clan_image(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Upload clan image"""
    try:
        logger.info(f"📡 API REQUEST: POST /api/clans/upload-image")
        
        # Get user
        user = get_user_from_request(request, db)
        
        # Get user's clan
        member = db.query(ClanMember).filter(ClanMember.user_id == user.id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Вы не состоите в клане")
        
        # Check if user is leader
        if member.role != 'leader':
            raise HTTPException(status_code=403, detail="Только лидер может загрузить изображение")
        
        # Get request body
        body = await request.json()
        image_data = body.get('image')
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Изображение не предоставлено")
        
        # Validate image format
        if not image_data.startswith('data:image'):
            raise HTTPException(status_code=400, detail="Неверный формат изображения")
        
        # Get clan
        clan = db.query(Clan).filter(Clan.id == member.clan_id).first()
        if not clan:
            raise HTTPException(status_code=404, detail="Клан не найден")
        
        # Update clan settings
        if clan.settings is None:
            clan.settings = {}
        
        clan.settings['image'] = image_data
        flag_modified(clan, 'settings')
        db.commit()
        
        logger.info(f"✅ Clan {clan.id} image uploaded by user {user.id}")
        return {
            "success": True,
            "message": "Изображение загружено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")

