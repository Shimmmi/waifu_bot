"""
Skills system API endpoints
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from bot.database import get_db
from bot.models import User

# Import skills models
try:
    from bot.models.skills import UserSkills, Skill, UserSkillLevel, SkillPointEarning
    SKILLS_ENABLED = True
except ImportError:
    # If skills models are not available, set flag to False
    UserSkills = None
    Skill = None
    UserSkillLevel = None
    SkillPointEarning = None
    SKILLS_ENABLED = False

from bot.utils import get_user_from_request

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/skills/status")
async def get_skills_status(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get user's skill points and progress"""
    if not SKILLS_ENABLED:
        raise HTTPException(status_code=503, detail="Skills system is not available")
    
    try:
        user = get_user_from_request(request, db)
        
        # Get or create user skills record
        user_skills = db.query(UserSkills).filter(UserSkills.user_id == user.id).first()
        if not user_skills:
            user_skills = UserSkills(user_id=user.id, skill_points=0, total_earned_points=0)
            db.add(user_skills)
            db.commit()
            db.refresh(user_skills)
        
        # Get user's skill levels
        skill_levels = db.query(UserSkillLevel).filter(UserSkillLevel.user_id == user.id).all()
        skill_levels_dict = {sl.skill_id: sl.level for sl in skill_levels}
        
        # Get category progress
        category_progress = {}
        for category in ['account', 'passive', 'training']:
            category_skills = db.query(UserSkillLevel).join(Skill).filter(
                and_(
                    UserSkillLevel.user_id == user.id,
                    Skill.category == category
                )
            ).all()
            total_points = sum(sl.level for sl in category_skills)
            category_progress[category] = total_points
        
        return {
            "skill_points": user_skills.skill_points,
            "total_earned_points": user_skills.total_earned_points,
            "skill_levels": skill_levels_dict,
            "category_progress": category_progress
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/skills/tree")
async def get_skills_tree(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get skills tree with user's progress"""
    if not SKILLS_ENABLED:
        raise HTTPException(status_code=503, detail="Skills system is not available")
    
    try:
        user = get_user_from_request(request, db)
        
        # Get all skills - check if table exists
        try:
            skills = db.query(Skill).all()
        except Exception as e:
            logger.error(f"Error querying skills table: {e}")
            raise HTTPException(status_code=503, detail="Skills table not created yet. Please wait for migration.")
        
        # Get user's skill levels
        skill_levels = db.query(UserSkillLevel).filter(UserSkillLevel.user_id == user.id).all()
        skill_levels_dict = {sl.skill_id: sl.level for sl in skill_levels}
        
        # Get category progress
        category_progress = {}
        for category in ['account', 'passive', 'training']:
            category_skills = db.query(UserSkillLevel).join(Skill).filter(
                and_(
                    UserSkillLevel.user_id == user.id,
                    Skill.category == category
                )
            ).all()
            total_points = sum(sl.level for sl in category_skills)
            category_progress[category] = total_points
        
        # Build skills tree
        skills_tree = {}
        for category in ['account', 'passive', 'training']:
            category_skills = [s for s in skills if s.category == category]
            skills_tree[category] = []
            
            for skill in category_skills:
                current_level = skill_levels_dict.get(skill.skill_id, 0)
                is_unlocked = category_progress[category] >= skill.unlock_requirement
                can_upgrade = current_level < skill.max_level
                
                # Calculate cost for next level
                next_level_cost = 0
                if can_upgrade:
                    next_level = current_level + 1
                    next_level_cost = skill.base_cost + (next_level - 1) * skill.cost_increase
                
                skills_tree[category].append({
                    "skill_id": skill.skill_id,
                    "name": skill.name,
                    "description": skill.description,
                    "icon": skill.icon,
                    "category": skill.category,
                    "max_level": skill.max_level,
                    "current_level": current_level,
                    "is_unlocked": is_unlocked,
                    "can_upgrade": can_upgrade,
                    "next_level_cost": next_level_cost,
                    "effects": skill.effects,
                    "unlock_requirement": skill.unlock_requirement
                })
        
        return {
            "skills_tree": skills_tree,
            "category_progress": category_progress
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/skills/upgrade")
async def upgrade_skill(
    request: Request, 
    skill_id: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upgrade a skill"""
    try:
        user = get_user_from_request(request, db)
        
        # Get skill definition
        skill = db.query(Skill).filter(Skill.skill_id == skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Навык не найден")
        
        # Get user skills
        user_skills = db.query(UserSkills).filter(UserSkills.user_id == user.id).first()
        if not user_skills:
            user_skills = UserSkills(user_id=user.id, skill_points=0, total_earned_points=0)
            db.add(user_skills)
            db.commit()
            db.refresh(user_skills)
        
        # Get current skill level
        skill_level = db.query(UserSkillLevel).filter(
            and_(
                UserSkillLevel.user_id == user.id,
                UserSkillLevel.skill_id == skill_id
            )
        ).first()
        
        current_level = skill_level.level if skill_level else 0
        
        # Check if skill can be upgraded
        if current_level >= skill.max_level:
            raise HTTPException(status_code=400, detail="Навык уже достиг максимального уровня")
        
        # Check if skill is unlocked
        category_progress = db.query(func.sum(UserSkillLevel.level)).join(Skill).filter(
            and_(
                UserSkillLevel.user_id == user.id,
                Skill.category == skill.category
            )
        ).scalar() or 0
        
        if category_progress < skill.unlock_requirement:
            raise HTTPException(status_code=400, detail="Навык еще не разблокирован")
        
        # Calculate cost
        next_level = current_level + 1
        cost = skill.base_cost + (next_level - 1) * skill.cost_increase
        
        # Check if user has enough points
        if user_skills.skill_points < cost:
            raise HTTPException(status_code=400, detail="Недостаточно очков навыков")
        
        # Upgrade skill
        if skill_level:
            skill_level.level = next_level
        else:
            skill_level = UserSkillLevel(
                user_id=user.id,
                skill_id=skill_id,
                level=next_level
            )
            db.add(skill_level)
        
        # Deduct points
        user_skills.skill_points -= cost
        
        db.commit()
        
        return {
            "success": True,
            "skill_id": skill_id,
            "new_level": next_level,
            "remaining_points": user_skills.skill_points,
            "cost_paid": cost
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.post("/api/skills/earn-points")
async def earn_skill_points(
    request: Request,
    points: int,
    source: str,
    source_details: Dict[str, Any] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Earn skill points (internal API)"""
    try:
        user = get_user_from_request(request, db)
        
        # Get or create user skills
        user_skills = db.query(UserSkills).filter(UserSkills.user_id == user.id).first()
        if not user_skills:
            user_skills = UserSkills(user_id=user.id, skill_points=0, total_earned_points=0)
            db.add(user_skills)
            db.commit()
            db.refresh(user_skills)
        
        # Add points
        user_skills.skill_points += points
        user_skills.total_earned_points += points
        
        # Record earning
        earning = SkillPointEarning(
            user_id=user.id,
            points_earned=points,
            source=source,
            source_details=source_details or {}
        )
        db.add(earning)
        
        db.commit()
        
        return {
            "success": True,
            "points_earned": points,
            "total_points": user_skills.skill_points
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")


@router.get("/api/skills/effects")
async def get_skill_effects(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all active skill effects for user"""
    try:
        user = get_user_from_request(request, db)
        
        # Get user's skill levels
        skill_levels = db.query(UserSkillLevel).join(Skill).filter(
            UserSkillLevel.user_id == user.id
        ).all()
        
        effects = {}
        for skill_level in skill_levels:
            skill = skill_level.skill
            current_level = skill_level.level
            
            if current_level > 0 and str(current_level) in skill.effects:
                level_effects = skill.effects[str(current_level)]
                for effect_name, effect_value in level_effects.items():
                    if effect_name not in effects:
                        effects[effect_name] = 0
                    effects[effect_name] += effect_value
        
        return {
            "effects": effects,
            "total_skills": len(skill_levels),
            "active_skills": len([sl for sl in skill_levels if sl.level > 0])
        }
        
    except Exception as e:
        logger.error(f"❌ API ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {type(e).__name__}: {str(e)}")
