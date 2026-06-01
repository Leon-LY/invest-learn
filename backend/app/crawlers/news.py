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
        "name": "东方财富-基金",
        "feed_url": "https://fund.eastmoney.com/api/RSS.aspx",
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
        "name": "雪球",
        "feed_url": "https://xueqiu.com/hots/topic/rss",
        "source_type": "rss",
        "fetch_interval": 900,
    },
]

# Article title/summary must match at least one of these to be saved
FINANCE_KEYWORDS = [
    "基金", "股", "ETF", "指数", "债", "利率", "央行", "银行",
    "保险", "投资", "理财", "分红", "A股", "港股", "美股",
    "证券", "期货", "黄金", "原油", "汇率", "人民币", "美元",
    "通胀", "GDP", "PMI", "CPI", "PPI", "降息", "加息",
    "IPO", "REIT", "QDII", "FOF", "定投", "净值",
    "上市公司", "茅台", "宁德", "科创", "创业板", "主板", "北交所",
    "医药", "新能源", "光伏", "锂电", "半导体", "芯片", "AI",
    "消费", "白酒", "地产", "基建", "煤炭", "钢铁",
    "养老金", "社保", "险资", "北向", "外资",
    "经理", "张坤", "谢治宇", "葛兰",
    "策略", "配置", "仓位", "回撤", "收益",
    "涨停", "跌停", "牛", "熊", "市值", "营收", "利润",
    "宏观", "数据", "政策", "监管", "改革", "国九条",
]


def _is_finance_article(title: str, summary: str) -> bool:
    """Check if an article is finance-related by keyword matching."""
    text = title + " " + (summary or "")
    return any(kw in text for kw in FINANCE_KEYWORDS)


def _classify_categories(title: str, summary: str) -> list:
    """Auto-assign Chinese categories based on keyword matching."""
    cats = set()
    text = title + " " + (summary or "")
    # 基金
    if any(kw in text for kw in ["基金", "ETF", "QDII", "FOF", "REIT", "定投", "净值", "基金经理", "公募", "私募"]):
        cats.add("基金")
    # 行业
    if any(kw in text for kw in ["行业", "板块", "赛道", "科技", "消费", "医药", "新能源", "半导体",
                                   "白酒", "银行", "地产", "光伏", "锂电", "芯片", "AI", "基建", "煤炭", "钢铁"]):
        cats.add("行业")
    # 大佬
    if any(kw in text for kw in ["经理", "张坤", "谢治宇", "葛兰", "侯昊", "刘格菘", "大佬", "牛散"]):
        cats.add("大佬")
    # 策略
    if any(kw in text for kw in ["策略", "配置", "仓位", "止损", "止盈", "轮动", "红利", "价值投资", "平衡",
                                   "定投", "回撤", "收益", "风险"]):
        cats.add("策略")
    return list(cats) if cats else ["基金"]  # default to 基金


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
            s = str(row.get("内容", row.get("content", "")))[:500]
            article = NewsArticle(
                source_id=source.id,
                title=title[:500],
                summary=s,
                source_url=str(row.get("链接", row.get("url", ""))),
                published_at=datetime.now(timezone.utc),
                categories=_classify_categories(title, s),
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

            # Strip HTML from summary (only if it looks like HTML)
            raw_summary = entry.get("summary", "") or ""
            if raw_summary.strip().startswith("<"):
                try:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(raw_summary, "lxml")
                    summary = soup.get_text()[:500]
                except Exception:
                    summary = raw_summary[:500]
            else:
                summary = raw_summary[:500]

            # Filter: only keep finance-related articles
            if not _is_finance_article(title, summary):
                continue

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
                summary=summary,
                source_url=entry.get("link", ""),
                author=entry.get("author", ""),
                published_at=self._parse_date(entry.get("published")),
                categories=_classify_categories(title, summary),
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
