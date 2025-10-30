"""
Skills system models for the waifu bot
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

# Import Base from the main models module
from bot.models import Base


class UserSkills(Base):
    """User skill points and progress"""
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    skill_points = Column(Integer, nullable=False, default=0)
    total_earned_points = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_skills")
    skill_levels = relationship("UserSkillLevel", back_populates="user_skills", cascade="all, delete-orphan")


class Skill(Base):
    """Skill definitions"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=False)  # 'account', 'passive', 'training'
    max_level = Column(Integer, nullable=False, default=5)
    base_cost = Column(Integer, nullable=False, default=1)
    cost_increase = Column(Integer, nullable=False, default=1)
    unlock_requirement = Column(Integer, nullable=False, default=0)  # Points needed in category to unlock
    effects = Column(JSON, nullable=False, default={})  # Skill effects per level
    icon = Column(String(20), nullable=False, default="⭐")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_levels = relationship("UserSkillLevel", back_populates="skill")


class UserSkillLevel(Base):
    """User skill levels"""
    __tablename__ = "user_skill_levels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(String(50), ForeignKey("skills.skill_id", ondelete="CASCADE"), nullable=False)
    level = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_skills = relationship("UserSkills", back_populates="skill_levels")
    skill = relationship("Skill", back_populates="user_levels")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),)


class SkillPointEarning(Base):
    """Skill point earnings from chat activity"""
    __tablename__ = "skill_point_earnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    points_earned = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)  # 'chat_message', 'daily_bonus', 'special_event'
    source_details = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
