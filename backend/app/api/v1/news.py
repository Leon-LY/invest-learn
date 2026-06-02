"""News API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_news_service
from app.services.news_service import NewsService

router = APIRouter()


@router.get("")
async def get_news_list(
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    service: NewsService = Depends(get_news_service),
):
    """Get paginated news feed."""
    return await service.get_news_list(category, source_id, sentiment, page, size)


# ── Specific named routes must come BEFORE /{article_id} wildcard ──

@router.get("/analyses")
async def get_ai_analyses(limit: int = 10, service: NewsService = Depends(get_news_service)):
    """Get recent AI analyses (cached 5 min)."""
    from app.core.cache import cache_get, cache_set
    cache_key = f"analysis:recent:{limit}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    data = await service.get_recent_analyses(limit)
    if data:
        await cache_set(cache_key, data, ttl=300)
    return data


@router.get("/expert-predictions")
async def get_expert_predictions(limit: int = 6, service: NewsService = Depends(get_news_service)):
    """Get cached DeepSeek-generated expert predictions (pre-generated every 30min)."""
    from app.core.cache import cache_get
    cached = await cache_get("analysis:expert_predictions")
    if cached:
        return cached[:limit]
    return await service.get_expert_predictions(limit)


@router.get("/expert-tracker")
async def get_expert_tracker(service: NewsService = Depends(get_news_service)):
    """Get real expert data (cached 1h)."""
    from app.core.cache import cache_get, cache_set
    cached = await cache_get("analysis:expert_tracker")
    if cached:
        return cached
    data = await service.get_expert_tracker()
    if data:
        await cache_set("analysis:expert_tracker", data, ttl=3600)
    return data


@router.get("/sources/list")
async def get_sources(service: NewsService = Depends(get_news_service)):
    """Get available news sources."""
    return await service.get_sources()


@router.get("/sentiment/stats")
async def get_sentiment_stats(days: int = 7, service: NewsService = Depends(get_news_service)):
    """Get sentiment distribution."""
    return await service.get_sentiment_stats(days)


# ── Wildcard routes (must be last) ──

@router.get("/{article_id}")
async def get_news_detail(article_id: int, service: NewsService = Depends(get_news_service)):
    """Get full article detail (AI analysis loads separately)."""
    result = await service.get_article_detail(article_id, include_analysis=False)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.get("/{article_id}/analysis")
async def get_news_analysis(article_id: int, service: NewsService = Depends(get_news_service)):
    """Get or generate AI analysis for a news article."""
    article = await service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    analysis = await service._get_or_generate_analysis(article)
    return analysis
