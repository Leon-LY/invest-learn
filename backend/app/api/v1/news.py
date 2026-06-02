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


@router.get("/analyses")
async def get_ai_analyses(limit: int = 10, service: NewsService = Depends(get_news_service)):
    """Get recent AI analyses from the news_analyses table (real DeepSeek data)."""
    return await service.get_recent_analyses(limit)


@router.get("/sources/list")
async def get_sources(service: NewsService = Depends(get_news_service)):
    """Get available news sources."""
    return await service.get_sources()


@router.get("/sentiment/stats")
async def get_sentiment_stats(days: int = 7, service: NewsService = Depends(get_news_service)):
    """Get sentiment distribution."""
    return await service.get_sentiment_stats(days)
