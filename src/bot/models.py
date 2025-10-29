from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Integer, String, Text, text, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    coins: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=text("0"))
    gems: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    last_daily: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("TIMESTAMPTZ '1970-01-01'")
    )
    daily_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    pity_counter: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    daily_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    last_xp_reset: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    # Global account XP system
    account_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    global_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    skill_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    last_global_xp: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    # Daily gold tracking
    daily_gold: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    last_gold_reset: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    # Tokens (special currency for rare purchases)
    tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    # User skills (passive upgrades)
    user_skills: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict, server_default=text("'{}'"))

    # Relationships
    waifus: Mapped[list["WaifuInstance"]] = relationship("WaifuInstance", back_populates="owner")
    user_skills: Mapped["UserSkills"] = relationship("UserSkills", back_populates="user", uselist=False)


class WaifuTemplate(Base):
    __tablename__ = "waifu_templates"

    template_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rarity: Mapped[str] = mapped_column(String, nullable=False)  # common, uncommon, rare, epic, legendary
    artwork_url: Mapped[str | None] = mapped_column(String, nullable=True)
    base_stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    skills: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )

    # Relationships
    instances: Mapped[list["WaifuInstance"]] = relationship("WaifuInstance", back_populates="template")


class WaifuInstance(Base):
    __tablename__ = "waifus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("waifu_templates.template_id"), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    xp: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=text("0"))
    affection: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    skin_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    last_xp_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("TIMESTAMPTZ '1970-01-01'")
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="waifus")
    template: Mapped["WaifuTemplate"] = relationship("WaifuTemplate", back_populates="instances")


class XPLog(Base):
    __tablename__ = "xp_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    waifu_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("waifus.id"), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)  # message, box, duel, quest
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


class PullHistory(Base):
    __tablename__ = "pull_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # daily, 10pull, premium
    cost: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    pity_counter: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)  # spend, earn
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)  # coins, gems
    reason: Mapped[str] = mapped_column(String, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


class Waifu(Base):
    __tablename__ = "waifu"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # wf_00123
    card_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rarity: Mapped[str] = mapped_column(String, nullable=False)
    race: Mapped[str] = mapped_column(String, nullable=False)
    profession: Mapped[str] = mapped_column(String, nullable=False)
    nationality: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))
    stats: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    dynamic: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=text("false"))
    is_favorite: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default=text("true"))
    start_time: Mapped[datetime] = mapped_column(nullable=False, server_default=text("now()"))
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    rewards: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


class EventParticipation(Base):
    __tablename__ = "event_participations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    waifu_id: Mapped[str] = mapped_column(String, ForeignKey("waifu.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    rewards_received: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    participated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )


