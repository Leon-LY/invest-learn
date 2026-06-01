"""Scheduled job definitions — called by APScheduler."""
import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.crawlers.a_stock import AStockCrawler, AStockSpotCrawler
from app.crawlers.global_stock import GlobalStockCrawler
from app.crawlers.a_fund import FundCrawler
from app.crawlers.news import NewsCrawler

logger = logging.getLogger(__name__)


async def _run_crawler(crawler_class, name: str):
    """Run a crawler with session management and error handling."""
    try:
        async with AsyncSessionLocal() as db:
            crawler = crawler_class(db)
            result = await crawler.run()
            logger.info(f"[{name}] Result: {result}")
    except Exception as e:
        logger.error(f"[{name}] Failed: {e}")


async def crawl_a_stock_list():
    """Daily: sync A-share stock list and historical K-line."""
    await _run_crawler(AStockCrawler, "AStockList")


async def crawl_a_stock_spot():
    """During trading: fetch live spot quotes."""
    await _run_crawler(AStockSpotCrawler, "AStockSpot")


async def crawl_global_stocks():
    """Periodic: sync US/HK stocks and global indices."""
    await _run_crawler(GlobalStockCrawler, "GlobalStocks")


async def crawl_funds():
    """Daily: sync fund NAV data."""
    await _run_crawler(FundCrawler, "Funds")


async def crawl_news():
    """Every 15 min: fetch latest news."""
    await _run_crawler(NewsCrawler, "News")


async def auto_analyze_news():
    """Every 5 min: generate AI analysis for unanalyzed articles."""
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            from app.models.news import NewsArticle, NewsAnalysis
            from app.services.news_service import NewsService

            svc = NewsService(db)
            # Find articles without analysis (limit 5 per batch to control cost)
            stmt = (
                select(NewsArticle)
                .outerjoin(NewsAnalysis, NewsArticle.id == NewsAnalysis.news_id)
                .where(NewsAnalysis.id == None)
                .order_by(NewsArticle.id.desc())
                .limit(5)
            )
            result = await db.execute(stmt)
            unanalyzed = result.scalars().all()

            for a in unanalyzed:
                try:
                    analysis = await svc._get_or_generate_analysis(a)
                    logger.info(f"[AutoAnalysis] id={a.id} → {analysis['impact_level']} ({analysis['generated_by']})")
                except Exception as e:
                    logger.error(f"[AutoAnalysis] id={a.id} FAILED: {e}")
    except Exception as e:
        logger.error(f"[AutoAnalysis] Job failed: {e}")
