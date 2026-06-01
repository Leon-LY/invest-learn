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
    """Get full article detail."""
    result = await service.get_article_detail(article_id)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.get("/sources/list")
async def get_sources(service: NewsService = Depends(get_news_service)):
    """Get available news sources."""
    return await service.get_sources()


@router.get("/sentiment/stats")
async def get_sentiment_stats(days: int = 7, service: NewsService = Depends(get_news_service)):
    """Get sentiment distribution."""
    return await service.get_sentiment_stats(days)
