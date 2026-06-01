"""User models: users, watchlist, price alerts, notes."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Text, DateTime, Boolean, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(200))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=lambda: {
        "theme": "system",
        "language": "zh-CN",
        "default_market": "A",
        "color_scheme": "red_up_green_down",
        "notifications_enabled": True,
    })
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'stock','fund','index'
    item_code: Mapped[str] = mapped_column(String(20), nullable=False)
    item_name: Mapped[Optional[str]] = mapped_column(String(100))
    alias: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "item_type", "item_code", name="uq_watchlist_item"),
    )


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    item_code: Mapped[str] = mapped_column(String(20), nullable=False)
    condition: Mapped[str] = mapped_column(String(10), nullable=False)  # 'above','below','pct_up','pct_down'
    target_value: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notify_channel: Mapped[str] = mapped_column(String(20), default="in_app")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserNote(Base):
    __tablename__ = "user_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    related_type: Mapped[Optional[str]] = mapped_column(String(20))  # 'stock','fund','general'
    related_code: Mapped[Optional[str]] = mapped_column(String(20))
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
