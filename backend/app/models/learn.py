"""Learning content models: categories, articles, glossary, strategies, calendar."""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, Boolean, Date, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class LearnCategory(Base):
    __tablename__ = "learn_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("learn_categories.id"))


class LearnArticle(Base):
    __tablename__ = "learn_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("learn_categories.id"))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)  # Markdown
    level: Mapped[str] = mapped_column(String(20), default="beginner")  # 'beginner','intermediate','advanced'
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    estimated_read: Mapped[Optional[int]] = mapped_column(Integer)  # minutes
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_articles_category_level", "category_id", "level"),
    )


class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    term_en: Mapped[Optional[str]] = mapped_column(String(200))
    definition: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))  # 'fundamental','technical','macro','general'
    related_terms: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)


class InvestmentStrategy(Base):
    __tablename__ = "investment_strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)  # Markdown
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    suitable_for: Mapped[Optional[str]] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")  # 'low','medium','high'
    key_metrics: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MarketCalendar(Base):
    __tablename__ = "market_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'earnings','dividend','economic','ipo','holiday'
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    related_stocks: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    importance: Mapped[str] = mapped_column(String(10), default="medium")
    country: Mapped[str] = mapped_column(String(50), default="CN")
