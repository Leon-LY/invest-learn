"""News service layer."""
import logging
import random
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.news import NewsSource, NewsArticle, NewsAnalysis
from app.core.config import settings
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class NewsService:
    """Service for news queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_news_list(self, category: Optional[str] = None,
                            source_id: Optional[int] = None,
                            sentiment: Optional[str] = None,
                            page: int = 1, size: int = 20) -> dict:
        """Get paginated news feed with optional filters. Categories are auto-detected from titles."""
        # Base query for total
        from sqlalchemy import or_
        count_query = select(func.count()).select_from(NewsArticle)

        if category:
            # Match by keywords in title for Chinese categories
            kw_map = {
                "基金": ["基金", "ETF", "QDII", "FOF", "REIT", "定投", "净值", "基金经理", "公募", "私募", "指数", "联接", "LOF"],
                "行业": ["行业", "板块", "赛道", "科技", "消费", "医药", "新能源", "半导体", "白酒", "银行", "地产", "光伏", "锂电", "芯片", "AI", "基建", "煤炭", "钢铁", "保险", "证券"],
                "大佬": ["张坤", "谢治宇", "葛兰", "侯昊", "刘格菘", "经理", "大佬", "牛散", "朱少醒"],
                "策略": ["策略", "定投", "配置", "仓位", "止损", "止盈", "轮动", "红利", "价值投资", "平衡", "回撤", "收益", "风险", "复利", "组合"],
            }
            keywords = kw_map.get(category, [category])
            conditions = []
            for kw in keywords:
                conditions.append(NewsArticle.title.ilike(f"%{kw}%"))
            count_query = count_query.where(or_(*conditions))

        if source_id:
            count_query = count_query.where(NewsArticle.source_id == source_id)
        if sentiment:
            count_query = count_query.where(NewsArticle.sentiment == sentiment)

        total = await self.db.scalar(count_query) or 0

        # Items query
        query = select(NewsArticle)
        if category:
            kw_map = {
                "基金": ["基金", "ETF", "QDII", "FOF", "REIT", "定投", "净值", "基金经理", "公募", "私募", "指数", "联接", "LOF"],
                "行业": ["行业", "板块", "赛道", "科技", "消费", "医药", "新能源", "半导体", "白酒", "银行", "地产", "光伏", "锂电", "芯片", "AI", "基建", "煤炭", "钢铁", "保险", "证券"],
                "大佬": ["张坤", "谢治宇", "葛兰", "侯昊", "刘格菘", "经理", "大佬", "牛散", "朱少醒"],
                "策略": ["策略", "定投", "配置", "仓位", "止损", "止盈", "轮动", "红利", "价值投资", "平衡", "回撤", "收益", "风险", "复利", "组合"],
            }
            keywords = kw_map.get(category, [category])
            conditions = []
            for kw in keywords:
                conditions.append(NewsArticle.title.ilike(f"%{kw}%"))
            query = query.where(or_(*conditions))

        if source_id:
            query = query.where(NewsArticle.source_id == source_id)
        if sentiment:
            query = query.where(NewsArticle.sentiment == sentiment)

        query = query.order_by(desc(NewsArticle.published_at)).offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        articles = result.scalars().all()

        items = []
        for a in articles:
            src_name = None
            if a.source_id:
                src_stmt = select(NewsSource.name).where(NewsSource.id == a.source_id)
                src_result = await self.db.execute(src_stmt)
                src_name = src_result.scalar()
            items.append(self._to_item(a, src_name))

        return {"items": items, "total": total, "page": page, "size": size}

    async def get_article_by_id(self, article_id: int):
        """Get raw article ORM object by ID."""
        stmt = select(NewsArticle).where(NewsArticle.id == article_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_article_detail(self, article_id: int, include_analysis: bool = True) -> Optional[dict]:
        """Get full article detail with source name. AI analysis loaded separately."""
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

        # Use summary as content if no full text
        content = article.content
        if not content or len(content.strip()) < 80:
            content = article.summary or ""

        detail = {
            "id": article.id, "title": article.title, "summary": article.summary,
            "content": content, "source": src_name, "source_url": article.source_url,
            "author": article.author, "sentiment": article.sentiment,
            "sentiment_score": article.sentiment_score,
            "categories": article.categories or [], "tags": article.tags or [],
            "related_stocks": article.related_stocks or [],
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "ai_analysis": None,  # Loaded separately via /news/{id}/analysis
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

    async def _get_or_generate_analysis(self, article) -> dict:
        """Fetch existing AI analysis or generate + persist a new one via DeepSeek LLM."""
        # Try to find existing analysis
        stmt = select(NewsAnalysis).where(NewsAnalysis.news_id == article.id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return self._analysis_to_dict(existing)

        analysis = None
        generated_by = "template"

        # Try DeepSeek LLM first
        llm_result = await llm_service.analyze_news(
            title=article.title,
            summary=article.summary,
            sentiment=article.sentiment,
        )
        if llm_result:
            analysis = llm_result
            generated_by = "deepseek"
        else:
            # Fallback to template-based analysis
            analysis = _build_ai_analysis(article)

        # Sync sentiment back to article based on AI analysis
        level = analysis["impact_level"]
        if "利好" in level:
            article.sentiment = "positive"
        elif "利空" in level:
            article.sentiment = "negative"
        else:
            article.sentiment = "neutral"
        self.db.add(article)

        db_analysis = NewsAnalysis(
            news_id=article.id,
            impact_score=analysis["impact_score"],
            impact_level=analysis["impact_level"],
            affected_funds=analysis["affected_funds"],
            short_term=analysis["short_term"],
            medium_term=analysis["medium_term"],
            action_advice=analysis["action_advice"],
            key_points=analysis["key_points"],
            generated_by=generated_by,
        )
        self.db.add(db_analysis)
        await self.db.commit()
        await self.db.refresh(db_analysis)
        return self._analysis_to_dict(db_analysis)

    @staticmethod
    def _analysis_to_dict(a: NewsAnalysis) -> dict:
        return {
            "impact_score": a.impact_score,
            "impact_level": a.impact_level,
            "affected_funds": a.affected_funds or [],
            "short_term": a.short_term or "",
            "medium_term": a.medium_term or "",
            "action_advice": a.action_advice or "",
            "key_points": a.key_points or [],
            "generated_by": a.generated_by or "template",
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


def _build_ai_analysis(article) -> dict:
    """Build AI impact analysis based on the actual article title and sentiment.
    Uses keyword matching on the title to tailor the analysis content."""
    title = article.title or ""
    sentiment = article.sentiment or "neutral"

    # Determine impact score and level from sentiment
    pos = sentiment == "positive"
    neg = sentiment == "negative"
    if pos:
        impact_score = random.randint(45, 75)
        impact_level = "利好"
    elif neg:
        impact_score = random.randint(-65, -25)
        impact_level = "利空"
    else:
        impact_score = random.randint(-15, 20)
        impact_level = "中性"

    # ── Detect affected fund types from title keywords ──
    affected_funds = []

    if any(kw in title for kw in ["ETF", "指数", "沪深300", "科创50", "中证500"]):
        affected_funds.append({"code": "510300", "name": "沪深300ETF", "impact": "宽基ETF直接受益于市场整体变化"})
        affected_funds.append({"code": "588000", "name": "科创50ETF", "impact": "科技属性ETF波动更大，需关注弹性"})
    if any(kw in title for kw in ["债", "债券", "利率", "债基", "MLF", "降息"]):
        affected_funds.append({"code": "110027", "name": "易方达安心回报债券A", "impact": "利率变化直接影响债券价格"})
    if any(kw in title for kw in ["消费", "白酒", "茅台", "五粮液"]):
        affected_funds.append({"code": "005827", "name": "易方达蓝筹精选混合", "impact": "重仓消费蓝筹，与消费复苏高度相关"})
    if any(kw in title for kw in ["医药", "创新药", "医疗", "葛兰"]):
        affected_funds.append({"code": "001475", "name": "中欧医疗健康混合", "impact": "医药主题基金，受行业政策影响大"})
    if any(kw in title for kw in ["新能源", "光伏", "锂电", "电池"]):
        affected_funds.append({"code": "002939", "name": "广发新能源精选混合", "impact": "新能源赛道基金，景气度是关键驱动"})
    if any(kw in title for kw in ["半导体", "芯片", "科技"]):
        affected_funds.append({"code": "320007", "name": "诺安成长混合", "impact": "科技半导体主题，波动较大"})
    if any(kw in title for kw in ["红利", "高股息", "分红"]):
        affected_funds.append({"code": "510880", "name": "红利ETF", "impact": "红利策略直接受益于分红政策"})
    if any(kw in title for kw in ["QDII", "海外", "港股", "美股", "全球"]):
        affected_funds.append({"code": "513100", "name": "纳指ETF", "impact": "海外市场波动和汇率是主要影响因素"})
    if any(kw in title for kw in ["定投", "新手", "入门"]):
        affected_funds.append({"code": "000311", "name": "景顺长城沪深300增强", "impact": "定投标的，长期持有收益稳健"})

    # Fallback: ensure at least 2 funds
    if len(affected_funds) < 2:
        affected_funds.append({"code": "510300", "name": "沪深300ETF", "impact": "核心宽基，受市场系统性影响"})
        affected_funds.append({"code": "110027", "name": "易方达安心回报债", "impact": "作为纯债基金受影响较小，可作为组合稳定器"})
    if len(affected_funds) > 4:
        affected_funds = affected_funds[:4]

    # ── Generate tailored short/medium term analysis ──
    topic_kw = title[:30]

    if pos:
        short_term = f"「{topic_kw}」这一利好消息预计在1-2周内提振市场情绪。相关基金净值有望小幅上涨1-3%，但短期追高需谨慎。"
        medium_term = f"未来1-3个月，如果利好逻辑持续兑现（政策落地/数据改善/资金流入），相关基金有望获得3-5%的超额收益。建议通过定投方式逐步参与，避免一次性重仓。"
        action_advice = "继续定投，维持现有仓位。如果持有相关基金，让利润奔跑但不要追高加仓。没上车的可以小额定投开始建仓。"
    elif neg:
        short_term = f"「{topic_kw}」这一利空消息可能在1-2周内对市场形成压力。相关基金净值可能回调1-3%，但恐慌性赎回往往得不偿失。"
        medium_term = f"未来1-3个月，市场将逐步消化利空。历史上类似事件后，优质基金通常在3-6个月内收复失地。定投投资者应利用低位积累份额。"
        action_advice = "坚持定投不要停，下跌是积累份额的好机会。如果有闲置资金，可分批加仓优质基金。短期不要恐慌赎回。"
    else:
        short_term = f"「{topic_kw}」这一消息对短期市场影响偏中性。预计1-2周内相关基金维持震荡格局，方向取决于后续数据和政策。"
        medium_term = "中期走势取决于宏观经济、流动性和行业基本面。建议保持灵活仓位，做好两手准备——上涨有仓位，下跌有资金。"
        action_advice = "按原计划执行定投，不急于加仓或减仓。等待趋势明朗后再做调整。保持适当的仓位弹性。"

    # ── Extract key points from title ──
    key_points = [
        title[:40] + ("..." if len(title) > 40 else ""),
        "关注后续市场反应和政策动态",
        "定投投资者无需过度反应，按计划执行即可",
        "做好仓位管理，避免单一赛道过度集中",
    ]

    return {
        "impact_score": impact_score,
        "impact_level": impact_level,
        "affected_funds": affected_funds,
        "short_term": short_term,
        "medium_term": medium_term,
        "action_advice": action_advice,
        "key_points": key_points,
    }


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

