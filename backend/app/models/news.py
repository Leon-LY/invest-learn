"""News models: sources, articles, AI analysis."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class NewsSource(Base):
    __tablename__ = "news_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    feed_url: Mapped[Optional[str]] = mapped_column(String(500))
    source_type: Mapped[str] = mapped_column(String(20), default="rss")  # 'rss','scrape','api'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fetch_interval: Mapped[int] = mapped_column(Integer, default=1800)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("news_sources.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    author: Mapped[Optional[str]] = mapped_column(String(100))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    categories: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    sentiment: Mapped[Optional[str]] = mapped_column(String(10))  # 'positive','negative','neutral'
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    related_stocks: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)

    # Relationship to AI analysis
    analysis = relationship("NewsAnalysis", back_populates="article", uselist=False)

    __table_args__ = (
        UniqueConstraint("source_id", "title", "published_at", name="uq_news_article"),
        Index("ix_news_published", "published_at", postgresql_using="brin"),
    )


class NewsAnalysis(Base):
    """AI-generated impact analysis for each news article."""
    __tablename__ = "news_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey("news_articles.id", ondelete="CASCADE"), unique=True)
    impact_score: Mapped[int] = mapped_column(Integer, default=0)  # -100 to 100
    impact_level: Mapped[str] = mapped_column(String(20), default="中性")  # 重大利好/利好/中性/利空/重大利空
    affected_funds: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)  # [{code, name, impact}]
    short_term: Mapped[Optional[str]] = mapped_column(Text)  # 短期影响（1-2周）
    medium_term: Mapped[Optional[str]] = mapped_column(Text)  # 中期影响（1-3月）
    action_advice: Mapped[Optional[str]] = mapped_column(Text)  # 操作建议
    key_points: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)  # 关键要点
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship back to article
    article = relationship("NewsArticle", back_populates="analysis")
