"""APScheduler lifecycle management."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the APScheduler and register all jobs."""
    from .jobs import (
        crawl_a_stock_list,
        crawl_a_stock_spot,
        crawl_global_stocks,
        crawl_funds,
        crawl_news,
    )

    # Daily: sync stock list and historical data (off-hours)
    scheduler.add_job(
        crawl_a_stock_list,
        CronTrigger(hour=17, minute=0),
        id="crawl_a_stock_daily",
        replace_existing=True,
    )

    # Trading hours: spot prices every 60 seconds
    scheduler.add_job(
        crawl_a_stock_spot,
        IntervalTrigger(seconds=60),
        id="crawl_a_stock_spot",
        replace_existing=True,
    )

    # Every 30 min: global stocks (yfinance has rate limits)
    scheduler.add_job(
        crawl_global_stocks,
        IntervalTrigger(minutes=30),
        id="crawl_global_stocks",
        replace_existing=True,
    )

    # Daily: fund NAV
    scheduler.add_job(
        crawl_funds,
        CronTrigger(hour=21, minute=0),
        id="crawl_funds",
        replace_existing=True,
    )

    # Every 15 min: news
    scheduler.add_job(
        crawl_news,
        IntervalTrigger(minutes=15),
        id="crawl_news",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
