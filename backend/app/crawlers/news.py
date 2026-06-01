"""
News RSS crawler — fetches financial news from RSS feeds accessible in China.
"""
import asyncio
import logging
import socket
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import feedparser
import hashlib

from .base import BaseCrawler, retry_on_failure
from app.models.news import NewsSource, NewsArticle
from app.core.config import settings

logger = logging.getLogger(__name__)

NEWS_SOURCES = [
    {
        "name": "华尔街见闻",
        "feed_url": "https://wallstreetcn.com/news/global/rss",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "证券时报",
        "feed_url": "https://www.stcn.com/article/rss.html",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "第一财经",
        "feed_url": "https://www.yicai.com/feed",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "36氪",
        "feed_url": "https://36kr.com/feed",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "东方财富-基金",
        "feed_url": "https://fund.eastmoney.com/api/RSS.aspx",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "雪球",
        "feed_url": "https://xueqiu.com/hots/topic/rss",
        "source_type": "rss",
        "fetch_interval": 900,
    },
]


class NewsCrawler(BaseCrawler):
    """Crawler for financial news from RSS feeds and scraping."""
    source_name = "news_rss"

    async def run(self) -> dict:
        result = {"sources_synced": 0, "articles_fetched": 0}
        try:
            result["sources_synced"] = await self.sync_sources()
        except Exception as e:
            logger.error(f"Source sync failed: {e}")
        try:
            result["articles_fetched"] = await self.fetch_all_sources()
        except Exception as e:
            logger.error(f"News fetch failed: {e}")
        return result

    async def sync_sources(self) -> int:
        """Ensure all news sources exist in DB."""
        count = 0
        for src in NEWS_SOURCES:
            stmt = select(NewsSource).where(NewsSource.name == src["name"])
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing is None:
                source = NewsSource(**src)
                self.db.add(source)
                count += 1
            else:
                existing.feed_url = src["feed_url"]
                existing.fetch_interval = src["fetch_interval"]
        if count > 0:
            await self.db.commit()
        return count

    async def fetch_all_sources(self) -> int:
        """Fetch news from all active sources."""
        BaseCrawler.setup_proxy()
        stmt = select(NewsSource).where(NewsSource.is_active == True)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        total = 0
        for source in sources:
            try:
                if source.source_type == "rss":
                    total += await self._fetch_rss(source)
                elif source.source_type == "api":
                    total += await self._fetch_api(source)
            except Exception as e:
                logger.warning(f"Failed to fetch {source.name}: {e}")
                source.error_count = (source.error_count or 0) + 1
        await self.db.commit()
        logger.info(f"Fetched {total} news articles total")
        return total

    async def _fetch_api(self, source: NewsSource) -> int:
        """Fetch news from AKShare API for Chinese financial news."""
        try:
            import akshare as ak
            df = await asyncio.to_thread(ak.stock_info_global_em)
        except Exception as e:
            logger.warning(f"AKShare news API failed: {e}")
            return 0

        saved = 0
        for _, row in df.iterrows()[:15]:
            title = str(row.get("标题", row.get("title", ""))).strip()
            if not title or len(title) < 4:
                continue
            stmt = select(NewsArticle).where(
                NewsArticle.source_id == source.id,
                NewsArticle.title == title,
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue
            article = NewsArticle(
                source_id=source.id,
                title=title[:500],
                summary=str(row.get("内容", row.get("content", "")))[:500],
                source_url=str(row.get("链接", row.get("url", ""))),
                published_at=datetime.now(timezone.utc),
                categories=[],
                tags=[],
                sentiment=None,
            )
            self.db.add(article)
            saved += 1
        await self.db.flush()
        source.last_fetched_at = datetime.now(timezone.utc)
        source.error_count = 0
        return saved

    @retry_on_failure(max_retries=2, delay=3.0)
    async def _fetch_rss(self, source: NewsSource) -> int:
        """Parse an RSS feed and save new articles (async wrapper)."""
        socket.setdefaulttimeout(settings.CRAWLER_HTTP_TIMEOUT)
        feed = await asyncio.to_thread(feedparser.parse, source.feed_url)
        saved = 0
        for entry in feed.entries[:20]:
            title = entry.get("title", "").strip()
            if not title:
                continue

            # Check if exists
            stmt = select(NewsArticle).where(
                NewsArticle.source_id == source.id,
                NewsArticle.title == title,
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                continue

            # Strip HTML from summary
            summary = entry.get("summary", "") or ""
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(summary, "lxml")
                summary = soup.get_text()[:500]
            except Exception:
                summary = summary[:500]

            article = NewsArticle(
                source_id=source.id,
                title=title[:500],
                summary=summary,
                source_url=entry.get("link", ""),
                author=entry.get("author", ""),
                published_at=self._parse_date(entry.get("published")),
                categories=[],
                tags=[],
                sentiment=None,
            )
            self.db.add(article)
            saved += 1
        await self.db.flush()
        source.last_fetched_at = datetime.now(timezone.utc)
        source.error_count = 0
        return saved

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse various date formats to datetime."""
        if not date_str:
            return None
        from dateutil import parser
        try:
            return parser.parse(date_str)
        except Exception:
            return None
