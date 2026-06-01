"""Learning content API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_learn_service
from app.services.learn_service import LearnService

router = APIRouter()


@router.get("/categories")
async def get_categories(service: LearnService = Depends(get_learn_service)):
    """Get learning category tree."""
    return await service.get_categories()


@router.get("/articles")
async def get_articles(
    category: Optional[str] = None,
    level: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    service: LearnService = Depends(get_learn_service),
):
    """Get paginated article list."""
    return await service.get_articles(category, level, tag, page, size)


@router.get("/articles/{slug}")
async def get_article_by_slug(slug: str, service: LearnService = Depends(get_learn_service)):
    """Get full article by slug."""
    result = await service.get_article_by_slug(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.get("/glossary")
async def search_glossary(
    q: Optional[str] = None,
    category: Optional[str] = None,
    service: LearnService = Depends(get_learn_service),
):
    """Search glossary terms."""
    return await service.search_glossary(q, category)


@router.get("/strategies")
async def get_strategies(
    difficulty: Optional[str] = None,
    risk_level: Optional[str] = None,
    service: LearnService = Depends(get_learn_service),
):
    """Get investment strategies list."""
    return await service.get_strategies(difficulty, risk_level)


@router.get("/strategies/{slug}")
async def get_strategy(slug: str, service: LearnService = Depends(get_learn_service)):
    """Get strategy detail."""
    result = await service.get_strategy_by_slug(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return result


@router.get("/calendar")
async def get_calendar(service: LearnService = Depends(get_learn_service)):
    """Get market calendar events."""
    return await service.get_calendar_events()
