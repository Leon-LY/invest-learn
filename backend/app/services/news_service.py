"""News service layer."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.news import NewsSource, NewsArticle
from app.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)


class NewsService:
    """Service for news queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_news_list(self, category: Optional[str] = None,
                            source_id: Optional[int] = None,
                            sentiment: Optional[str] = None,
                            page: int = 1, size: int = 20) -> dict:
        """Get paginated news feed with optional filters."""
        cache_key = f"news:list:{category}:{source_id}:{sentiment}:{page}:{size}"
        if page == 1:
            cached = await cache_get(cache_key)
            if cached:
                return cached

        query = select(NewsArticle)
        # Join source name
        if category:
            query = query.where(NewsArticle.categories.contains([category]))
        if source_id:
            query = query.where(NewsArticle.source_id == source_id)
        if sentiment:
            query = query.where(NewsArticle.sentiment == sentiment)

        # Total
        count_query = select(func.count()).select_from(NewsArticle)
        if category:
            count_query = count_query.where(NewsArticle.categories.contains([category]))
        if source_id:
            count_query = count_query.where(NewsArticle.source_id == source_id)
        if sentiment:
            count_query = count_query.where(NewsArticle.sentiment == sentiment)
        total = await self.db.scalar(count_query) or 0

        # Items
        query = query.order_by(desc(NewsArticle.published_at)).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        articles = result.scalars().all()

        items = []
        for a in articles:
            # Get source name
            src_name = None
            if a.source_id:
                src_stmt = select(NewsSource.name).where(NewsSource.id == a.source_id)
                src_result = await self.db.execute(src_stmt)
                src_name = src_result.scalar()
            items.append(self._to_item(a, src_name))

        output = {"items": items, "total": total, "page": page, "size": size}
        if page == 1:
            await cache_set(cache_key, output, ttl=300)
        return output

    async def get_article_detail(self, article_id: int) -> Optional[dict]:
        """Get full article detail with source name."""
        stmt = select(NewsArticle).where(NewsArticle.id == article_id)
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            return None

        src_name = None
        if article.source_id:
            src_stmt = select(NewsSource.name).where(NewsSource.id == article.source_id)
            src_result = await self.db.execute(src_stmt)
            src_name = src_result.scalar()

        detail = {
            "id": article.id, "title": article.title, "summary": article.summary,
            "content": article.content, "source": src_name, "source_url": article.source_url,
            "author": article.author, "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "categories": article.categories or [], "tags": article.tags or [],
            "related_stocks": article.related_stocks or [],
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "related_news": [],
        }

        # Get related news (same tags)
        if article.tags:
            related_stmt = select(NewsArticle).where(
                NewsArticle.id != article_id,
                NewsArticle.tags.op('&&')(article.tags),
            ).order_by(desc(NewsArticle.published_at)).limit(5)
            related_result = await self.db.execute(related_stmt)
            related = related_result.scalars().all()
            detail["related_news"] = [self._to_item(r) for r in related]

        return detail

    @staticmethod
    def _to_item(article, source_name: Optional[str] = None) -> dict:
        return {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "source": source_name,
            "source_url": article.source_url,
            "author": article.author,
            "sentiment": article.sentiment,
            "categories": article.categories or [],
            "tags": article.tags or [],
            "related_stocks": article.related_stocks or [],
            "published_at": article.published_at.isoformat() if article.published_at else None,
        }

    async def get_sources(self) -> list[dict]:
        """Get all news sources with article count."""
        stmt = select(NewsSource).where(NewsSource.is_active == True)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        return [{"id": s.id, "name": s.name, "feed_url": s.feed_url,
                 "source_type": s.source_type, "last_fetched": s.last_fetched_at.isoformat() if s.last_fetched_at else None}
                for s in sources]

    async def get_sentiment_stats(self, days: int = 7) -> dict:
        """Get sentiment distribution for recent news."""
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(NewsArticle.sentiment, func.count()).where(
            NewsArticle.published_at >= cutoff if NewsArticle.published_at is not None else True
        ).group_by(NewsArticle.sentiment)
        result = await self.db.execute(stmt)
        rows = result.all()
        stats = {"positive_count": 0, "negative_count": 0, "neutral_count": 0}
        for sentiment, count in rows:
            if sentiment == "positive":
                stats["positive_count"] = count
            elif sentiment == "negative":
                stats["negative_count"] = count
            else:
                stats["neutral_count"] = count
        return stats
