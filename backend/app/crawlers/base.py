"""Abstract base crawler with common utilities."""
import asyncio
import logging
import socket
from datetime import date, datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseCrawler:
    """Base class for all data crawlers."""

    source_name: str = "base"

    def __init__(self, db: AsyncSession):
        self.db = db
        # Set socket timeout for AKShare/yfinance underlying requests
        socket.setdefaulttimeout(settings.CRAWLER_HTTP_TIMEOUT)

    async def run(self) -> dict:
        """Run the crawler. Returns status dict."""
        raise NotImplementedError

    @staticmethod
    def is_trading_day(d: Optional[date] = None) -> bool:
        """Check if the given date is a trading day (Mon-Fri, not weekend)."""
        if d is None:
            d = date.today()
        return d.weekday() < 5

    @staticmethod
    def today_str() -> str:
        return date.today().strftime("%Y%m%d")

    @staticmethod
    def safe_float(val, default=None):
        """Safely convert a value to float."""
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_int(val, default=None):
        """Safely convert a value to int."""
        if val is None:
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def setup_proxy():
        """Configure HTTP proxy for crawlers if configured."""
        if settings.HTTP_PROXY:
            import os
            os.environ["HTTP_PROXY"] = settings.HTTP_PROXY
            os.environ["HTTPS_PROXY"] = settings.HTTPS_PROXY or settings.HTTP_PROXY
            os.environ["http_proxy"] = settings.HTTP_PROXY
            os.environ["https_proxy"] = settings.HTTPS_PROXY or settings.HTTP_PROXY
            logger.info(f"Proxy configured: {settings.HTTP_PROXY}")


def retry_on_failure(max_retries: int = None, delay: float = None):
    """Decorator to retry an async function on failure with exponential backoff."""
    max_retries = max_retries if max_retries is not None else settings.CRAWLER_RETRY_MAX
    delay = delay if delay is not None else settings.CRAWLER_RETRY_DELAY

    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator
