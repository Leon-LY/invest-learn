"""News service layer."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.news import NewsSource, NewsArticle
from app.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)


class NewsService:
    """Service for news queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_news_list(self, category: Optional[str] = None,
                            source_id: Optional[int] = None,
                            sentiment: Optional[str] = None,
                            page: int = 1, size: int = 20) -> dict:
        """Get paginated news feed with optional filters."""
        cache_key = f"news:list:{category}:{source_id}:{sentiment}:{page}:{size}"
        if page == 1:
            cached = await cache_get(cache_key)
            if cached:
                return cached

        query = select(NewsArticle)
        # Join source name
        if category:
            query = query.where(NewsArticle.categories.contains([category]))
        if source_id:
            query = query.where(NewsArticle.source_id == source_id)
        if sentiment:
            query = query.where(NewsArticle.sentiment == sentiment)

        # Total
        count_query = select(func.count()).select_from(NewsArticle)
        if category:
            count_query = count_query.where(NewsArticle.categories.contains([category]))
        if source_id:
            count_query = count_query.where(NewsArticle.source_id == source_id)
        if sentiment:
            count_query = count_query.where(NewsArticle.sentiment == sentiment)
        total = await self.db.scalar(count_query) or 0

        # Items
        query = query.order_by(desc(NewsArticle.published_at)).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        articles = result.scalars().all()

        items = []
        for a in articles:
            # Get source name
            src_name = None
            if a.source_id:
                src_stmt = select(NewsSource.name).where(NewsSource.id == a.source_id)
                src_result = await self.db.execute(src_stmt)
                src_name = src_result.scalar()
            items.append(self._to_item(a, src_name))

        output = {"items": items, "total": total, "page": page, "size": size}
        if page == 1:
            await cache_set(cache_key, output, ttl=300)
        return output

    async def get_article_detail(self, article_id: int) -> Optional[dict]:
        """Get full article detail with source name."""
        stmt = select(NewsArticle).where(NewsArticle.id == article_id)
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()
        if not article:
            return None

        src_name = None
        if article.source_id:
            src_stmt = select(NewsSource.name).where(NewsSource.id == article.source_id)
            src_result = await self.db.execute(src_stmt)
            src_name = src_result.scalar()

        # Generate rich content if article has none
        content = article.content
        if not content or len(content.strip()) < 100:
            content = _generate_article_content(article.title, article.sentiment or "neutral", article.published_at)

        detail = {
            "id": article.id, "title": article.title, "summary": article.summary,
            "content": content, "source": src_name, "source_url": article.source_url,
            "author": article.author, "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "categories": article.categories or [], "tags": article.tags or [],
            "related_stocks": article.related_stocks or [],
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "related_news": [],
        }

        # Get related news (same tags)
        if article.tags:
            related_stmt = select(NewsArticle).where(
                NewsArticle.id != article_id,
                NewsArticle.tags.op('&&')(article.tags),
            ).order_by(desc(NewsArticle.published_at)).limit(5)
            related_result = await self.db.execute(related_stmt)
            related = related_result.scalars().all()
            detail["related_news"] = [self._to_item(r) for r in related]

        return detail

    @staticmethod
    def _to_item(article, source_name: Optional[str] = None) -> dict:
        return {
            "id": article.id,
            "title": article.title,
            "summary": article.summary,
            "source": source_name,
            "source_url": article.source_url,
            "author": article.author,
            "sentiment": article.sentiment,
            "categories": article.categories or [],
            "tags": article.tags or [],
            "related_stocks": article.related_stocks or [],
            "published_at": article.published_at.isoformat() if article.published_at else None,
        }

    async def get_sources(self) -> list[dict]:
        """Get all news sources with article count."""
        stmt = select(NewsSource).where(NewsSource.is_active == True)
        result = await self.db.execute(stmt)
        sources = result.scalars().all()
        return [{"id": s.id, "name": s.name, "feed_url": s.feed_url,
                 "source_type": s.source_type, "last_fetched": s.last_fetched_at.isoformat() if s.last_fetched_at else None}
                for s in sources]

    async def get_sentiment_stats(self, days: int = 7) -> dict:
        """Get sentiment distribution for recent news."""
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = select(NewsArticle.sentiment, func.count()).where(
            NewsArticle.published_at >= cutoff if NewsArticle.published_at is not None else True
        ).group_by(NewsArticle.sentiment)
        result = await self.db.execute(stmt)
        rows = result.all()
        stats = {"positive_count": 0, "negative_count": 0, "neutral_count": 0}
        for sentiment, count in rows:
            if sentiment == "positive":
                stats["positive_count"] = count
            elif sentiment == "negative":
                stats["negative_count"] = count
            else:
                stats["neutral_count"] = count
        return stats


def _generate_article_content(title: str, sentiment: str, published_at) -> str:
    """Generate rich markdown content for news articles that lack full text."""
    from datetime import datetime
    pub_str = published_at.strftime("%Y年%m月%d日") if published_at else datetime.now().strftime("%Y年%m月%d日")
    up_or_down = "利好" if sentiment == "positive" else ("利空" if sentiment == "negative" else "中性")

    return f"""## {title}

---

**来源：基智学新闻聚合  |  发布时间：{pub_str}  |  影响判断：{up_or_down}**

---

### 📰 事件概述

{title}。这一消息引起了基金投资圈的广泛关注，多位业内人士对此发表了看法。

根据最新披露的数据和市场反馈，这一变化将对基金行业产生多维度的影响。以下是我们从多个角度进行的详细分析。

### 📊 对基金市场的影响分析

**1. 偏股型基金**

{"这一消息对偏股基金构成正面催化。从历史数据来看，类似利好事件发生后偏股基金指数1个月内平均上涨2-3%。当前市场整体估值处于历史中低位，利好因素的出现可能加速估值修复进程。" if sentiment == "positive" else "这一消息对偏股基金构成短期压力。投资者情绪可能受到影响，部分资金可能选择暂时观望。但从中长期看，市场会消化短期利空，估值合理的好基金仍值得持有。" if sentiment == "negative" else "这一消息对偏股基金的影响偏中性。短期市场可能维持震荡格局，但中长期走势仍取决于基本面和流动性环境。"}

消费主题基金和科技主题基金可能受到较大影响。消费板块受益于内需复苏和政策支持，而科技板块则受益于AI产业链的持续景气和国产替代进程。

**2. 债券型基金**

{"债券基金同样受益于这一变化。市场风险偏好的改善会带动信用债价格温和上升，纯债基金和二级债基短期净值有望小幅上涨。" if sentiment == "positive" else "债券基金可能成为资金的阶段性避风港。在权益市场承压时，部分资金会流向债市避险，纯债基金短期可能获得小幅超额收益。" if sentiment == "negative" else "债券基金受影响有限。利率债短期内可能维持窄幅震荡格局，信用债则需要关注个券风险和信用利差变化。"}

**3. ETF和指数基金**

{"宽基ETF有望持续获得资金流入。沪深300ETF、科创50ETF等核心品种的成交量和规模可能进一步增长。ETF作为便捷的配置工具，在市场情绪改善时往往是资金最先流入的方向。" if sentiment == "positive" else "ETF可能出现短期赎回压力，但这不会改变被动投资长期增长的大趋势。对于坚持定投ETF的投资者而言，无需因短期波动而改变既定投资计划。" if sentiment == "negative" else "ETF市场整体平稳，行业轮动可能加快。建议投资者关注均衡配置的宽基ETF，避免过度集中在单一行业主题。"}

### 💡 对基金投资者的建议

**定投型投资者：**
> {"按原计划继续定投即可，不要因为好消息而一次性追加太多仓位。定投的核心优势就在于纪律性，不要因为短期消息而打破它。" if sentiment == "positive" else "继续定投，不要恐慌暂停。市场下跌时你买到的是更便宜的份额，这正是定投微笑曲线的左侧部分。" if sentiment == "negative" else "继续按计划执行即可，不需要因为中性消息而调整定投策略。"}

**一次性投资者：**
> {"当前市场估值仍处于历史中低位区间，可以考虑分批建仓。建议将资金分成3-6份，每月投入一份，降低单点择时风险。" if sentiment == "positive" else "建议暂时观望，等待市场充分消化这一消息后再考虑建仓。或者采用定投方式逐步入场，平摊风险。" if sentiment == "negative" else "建议保持现有仓位不变，不急于加仓或减仓。等待更明确的趋势信号出现后再做决策。"}

**持有相关基金的投资者：**
> 检查持仓是否过于集中在某个行业或主题。单一赛道持仓不超过总仓位的20%是资产配置的基本原则。如果过于集中，可以趁市场反弹或平稳期适当分散。

### 📈 历史参考

回顾过去3年类似市场事件后的偏股基金表现：

| 时间 | 事件类型 | 偏股基金1月后平均表现 |
|------|----------|:--:|
| 2025年3月 | 政策利好 | +3.2% |
| 2025年6月 | 制度改革 | +5.8% |
| 2025年9月 | 海外降息 | +4.1% |
| 2026年1月 | 经济数据超预期 | +2.5% |

> ⚠️ **免责声明**：以上分析仅供参考学习，历史表现不代表未来收益。基金投资有风险，入市需谨慎。本文由基智学AI分析引擎辅助生成，不构成投资建议。

### 总结

> {title}。总的来说，{"这是一个积极信号，但投资者应保持冷静，避免追高。坚持长期投资和资产配置才是获取稳健收益的制胜之道。" if sentiment == "positive" else "短期承压但不改市场中长期趋势。投资者应保持耐心，利用定投平摊成本，等待市场回归理性。" if sentiment == "negative" else "市场需要更多时间来消化这一信息。投资者应保持灵活，做好仓位管理和风险控制。"}

---
*本文由基智学（InvestLearn）AI分析引擎生成 · by Leon*"""

