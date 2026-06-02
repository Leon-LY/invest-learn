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
        auto_analyze_news,
        crawl_etf,
        generate_expert_predictions,
        refresh_expert_tracker,
    )

    # Daily: sync stock list and historical data (off-hours)
    scheduler.add_job(
        crawl_a_stock_list,
        CronTrigger(hour=17, minute=0),
        id="crawl_a_stock_daily",
        replace_existing=True,
    )

    # Trading hours: spot prices every 3 minutes (reduced from 60s to avoid rate limits)
    scheduler.add_job(
        crawl_a_stock_spot,
        IntervalTrigger(minutes=3),
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

    # Daily: ETF list
    scheduler.add_job(
        crawl_etf,
        CronTrigger(hour=8, minute=0),
        id="crawl_etf",
        replace_existing=True,
    )

    # Every 2 hours: refresh expert tracker data
    scheduler.add_job(
        refresh_expert_tracker,
        IntervalTrigger(hours=2),
        id="expert_tracker",
        replace_existing=True,
    )

    # Every 30 min: pre-generate expert predictions
    scheduler.add_job(
        generate_expert_predictions,
        IntervalTrigger(minutes=30),
        id="expert_predictions",
        replace_existing=True,
    )

    # Every 5 min: auto AI analysis for unanalyzed articles
    scheduler.add_job(
        auto_analyze_news,
        IntervalTrigger(minutes=5),
        id="auto_analyze_news",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    # Fire all crawlers immediately at startup
    import asyncio
    async def initial_crawl():
        await asyncio.sleep(10)  # Let server fully start
        jobs = [
            ("A-Stock List", crawl_a_stock_list),
            ("ETF", crawl_etf),
            ("Global Stocks", crawl_global_stocks),
            ("Funds", crawl_funds),
            ("News", crawl_news),
        ]
        for name, job in jobs:
            logger.info(f"Initial crawl: {name}...")
            try:
                await job()
                logger.info(f"Initial crawl: {name} ✓")
            except Exception as e:
                logger.error(f"Initial crawl: {name} ✗ — {e}")
            await asyncio.sleep(3)

        logger.info("Initial AI analysis...")
        try: await auto_analyze_news()
        except Exception as e: logger.error(f"Failed: {e}")

        logger.info("Initial expert predictions...")
        try: await generate_expert_predictions()
        except Exception as e: logger.error(f"Failed: {e}")

        logger.info("Initial expert tracker...")
        try: await refresh_expert_tracker()
        except Exception as e: logger.error(f"Failed: {e}")
    asyncio.create_task(initial_crawl())


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
