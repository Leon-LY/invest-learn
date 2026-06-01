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
