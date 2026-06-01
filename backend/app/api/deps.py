"""FastAPI dependencies: DB session, cache, current user."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.market_service import MarketService
from app.services.news_service import NewsService
from app.services.learn_service import LearnService


async def get_market_service(db: AsyncSession = Depends(get_db)) -> MarketService:
    return MarketService(db)


async def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)


async def get_learn_service(db: AsyncSession = Depends(get_db)) -> LearnService:
    return LearnService(db)
