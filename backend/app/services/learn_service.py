"""Learning content service layer."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.learn import LearnCategory, LearnArticle, GlossaryTerm, InvestmentStrategy, MarketCalendar
from app.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)


class LearnService:
    """Service for learning content."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_categories(self) -> list[dict]:
        """Get category tree."""
        cached = await cache_get("learn:categories")
        if cached:
            return cached

        stmt = select(LearnCategory).where(LearnCategory.parent_id.is_(None)).order_by(LearnCategory.sort_order)
        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        output = []
        for cat in categories:
            children_stmt = select(LearnCategory).where(LearnCategory.parent_id == cat.id).order_by(LearnCategory.sort_order)
            children_result = await self.db.execute(children_stmt)
            children = children_result.scalars().all()
            output.append({
                "id": cat.id, "name": cat.name, "slug": cat.slug,
                "description": cat.description, "icon": cat.icon,
                "children": [{"id": c.id, "name": c.name, "slug": c.slug} for c in children],
            })

        await cache_set("learn:categories", output, ttl=3600)
        return output

    async def get_articles(self, category: Optional[str] = None, level: Optional[str] = None,
                           tag: Optional[str] = None, page: int = 1, size: int = 20) -> dict:
        """Get paginated article list."""
        query = select(LearnArticle).where(LearnArticle.is_published == True)
        count_query = select(func.count()).select_from(LearnArticle).where(LearnArticle.is_published == True)

        if category:
            cat_stmt = select(LearnCategory.id).where(LearnCategory.slug == category)
            cat_result = await self.db.execute(cat_stmt)
            cat_id = cat_result.scalar()
            if cat_id:
                query = query.where(LearnArticle.category_id == cat_id)
                count_query = count_query.where(LearnArticle.category_id == cat_id)

        if level:
            query = query.where(LearnArticle.level == level)
            count_query = count_query.where(LearnArticle.level == level)

        if tag:
            query = query.where(LearnArticle.tags.contains([tag]))
            count_query = count_query.where(LearnArticle.tags.contains([tag]))

        total = await self.db.scalar(count_query) or 0
        query = query.order_by(LearnArticle.published_at.desc()).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        articles = result.scalars().all()

        return {
            "items": [self._article_to_item(a) for a in articles],
            "total": total, "page": page, "size": size,
        }

    async def get_article_by_slug(self, slug: str) -> Optional[dict]:
        """Get full article by slug with prev/next navigation."""
        stmt = select(LearnArticle).where(LearnArticle.slug == slug, LearnArticle.is_published == True)
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            return None

        # Increment view count
        article.view_count = (article.view_count or 0) + 1
        await self.db.commit()

        # Prev / next articles
        prev_stmt = select(LearnArticle).where(
            LearnArticle.is_published == True,
            LearnArticle.published_at < article.published_at,
        ).order_by(LearnArticle.published_at.desc()).limit(1)
        prev_result = await self.db.execute(prev_stmt)
        prev_article = prev_result.scalar_one_or_none()

        next_stmt = select(LearnArticle).where(
            LearnArticle.is_published == True,
            LearnArticle.published_at > article.published_at,
        ).order_by(LearnArticle.published_at.asc()).limit(1)
        next_result = await self.db.execute(next_stmt)
        next_article = next_result.scalar_one_or_none()

        return {
            **self._article_to_item(article),
            "content": article.content,
            "prev_article": self._article_to_item(prev_article) if prev_article else None,
            "next_article": self._article_to_item(next_article) if next_article else None,
        }

    async def search_glossary(self, q: Optional[str] = None, category: Optional[str] = None) -> list[dict]:
        """Search glossary terms."""
        query = select(GlossaryTerm)
        if q:
            query = query.where(or_(
                GlossaryTerm.term.ilike(f"%{q}%"),
                GlossaryTerm.term_en.ilike(f"%{q}%"),
                GlossaryTerm.definition.ilike(f"%{q}%"),
            ))
        if category:
            query = query.where(GlossaryTerm.category == category)
        query = query.order_by(GlossaryTerm.term)
        result = await self.db.execute(query)
        terms = result.scalars().all()
        return [{"term": t.term, "term_en": t.term_en, "definition": t.definition,
                 "category": t.category, "related_terms": t.related_terms or []} for t in terms]

    async def get_strategies(self, difficulty: Optional[str] = None, risk_level: Optional[str] = None) -> list[dict]:
        """Get investment strategies list."""
        query = select(InvestmentStrategy)
        if difficulty:
            query = query.where(InvestmentStrategy.difficulty == difficulty)
        if risk_level:
            query = query.where(InvestmentStrategy.risk_level == risk_level)
        query = query.order_by(InvestmentStrategy.difficulty)
        result = await self.db.execute(query)
        strategies = result.scalars().all()
        return [{
            "id": s.id, "name": s.name, "slug": s.slug, "summary": s.summary,
            "difficulty": s.difficulty, "risk_level": s.risk_level,
            "suitable_for": s.suitable_for, "key_metrics": s.key_metrics or [],
        } for s in strategies]

    async def get_strategy_by_slug(self, slug: str) -> Optional[dict]:
        """Get strategy detail with full content."""
        stmt = select(InvestmentStrategy).where(InvestmentStrategy.slug == slug)
        result = await self.db.execute(stmt)
        s = result.scalar_one_or_none()
        if not s:
            return None
        return {
            "id": s.id, "name": s.name, "slug": s.slug, "summary": s.summary,
            "content": s.content, "difficulty": s.difficulty,
            "suitable_for": s.suitable_for, "risk_level": s.risk_level,
            "key_metrics": s.key_metrics or [],
        }

    async def get_calendar_events(self, month: Optional[str] = None) -> list[dict]:
        """Get market calendar events for a month."""
        from datetime import date
        today = date.today()
        stmt = select(MarketCalendar).where(MarketCalendar.event_date >= today).order_by(MarketCalendar.event_date).limit(50)
        result = await self.db.execute(stmt)
        events = result.scalars().all()
        return [{
            "id": e.id, "event_date": e.event_date.isoformat(), "event_type": e.event_type,
            "title": e.title, "description": e.description,
            "importance": e.importance, "country": e.country,
        } for e in events]

    @staticmethod
    def _article_to_item(a) -> dict:
        return {
            "id": a.id, "title": a.title, "slug": a.slug, "summary": a.summary,
            "level": a.level, "tags": a.tags or [], "estimated_read": a.estimated_read,
            "view_count": a.view_count or 0,
            "published_at": a.published_at.isoformat() if a.published_at else None,
        }
