"""News models: sources, articles."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
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

    __table_args__ = (
        UniqueConstraint("source_id", "title", "published_at", name="uq_news_article"),
        Index("ix_news_published", "published_at", postgresql_using="brin"),
    )
