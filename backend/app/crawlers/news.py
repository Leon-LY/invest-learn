"""
News RSS crawler — fetches financial news from RSS feeds.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import feedparser
import hashlib

from .base import BaseCrawler, retry_on_failure
from app.models.news import NewsSource, NewsArticle

logger = logging.getLogger(__name__)

NEWS_SOURCES = [
    {
        "name": "东方财富",
        "feed_url": "https://finance.eastmoney.com/a/czqyw.html",
        "source_type": "scrape",
        "fetch_interval": 900,
    },
    {
        "name": "雪球",
        "feed_url": "https://xueqiu.com/hots/topic/rss",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "华尔街见闻",
        "feed_url": "https://wallstreetcn.com/news/global/rss",
        "source_type": "rss",
        "fetch_interval": 900,
    },
    {
        "name": "新浪财经",
        "feed_url": "https://finance.sina.com.cn/china/",
        "source_type": "scrape",
        "fetch_interval": 1800,
    },
    {
        "name": "Yahoo Finance",
        "feed_url": "https://finance.yahoo.com/news/rssindex",
        "source_type": "rss",
        "fetch_interval": 1800,
    },
    {
        "name": "Investing.com",
        "feed_url": "https://www.investing.com/rss/news_1063.rss",
        "source_type": "rss",
        "fetch_interval": 1800,
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
        stmt = select(NewsSource).where(NewsSource.is_active == True)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        total = 0
        for source in sources:
            try:
                if source.source_type == "rss":
                    total += await self._fetch_rss(source)
                # scrape type is more complex; skip for MVP
            except Exception as e:
                logger.warning(f"Failed to fetch {source.name}: {e}")
                source.error_count = (source.error_count or 0) + 1
        await self.db.commit()
        logger.info(f"Fetched {total} news articles total")
        return total

    @retry_on_failure(max_retries=2, delay=2.0)
    async def _fetch_rss(self, source: NewsSource) -> int:
        """Parse an RSS feed and save new articles."""
        feed = feedparser.parse(source.feed_url)
        saved = 0
        for entry in feed.entries[:20]:  # Limit to 20 per source per run
            title = entry.get("title", "").strip()
            if not title:
                continue
            # Generate a stable unique key
            published_str = entry.get("published", entry.get("updated", ""))
            article_hash = hashlib.md5(f"{source.id}:{title}:{published_str}".encode()).hexdigest()

            # Check if exists
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
                summary=(entry.get("summary", "") or "")[:500],
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
