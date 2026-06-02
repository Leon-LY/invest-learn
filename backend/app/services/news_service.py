"""News service layer."""
import logging
import random
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from app.models.news import NewsSource, NewsArticle, NewsAnalysis
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

    async def get_expert_predictions(self, limit: int = 6) -> list[dict]:
        """Generate expert-style predictions via DeepSeek on recent news."""
        # Get latest news for context
        stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(5)
        result = await self.db.execute(stmt)
        recent = result.scalars().all()
        if not recent:
            return []

        titles = "\n".join([f"- {a.title}" for a in recent])

        experts = [
            {"id": "value", "name": "价值投资视角", "style": "像张坤一样思考：关注企业护城河、自由现金流、长期竞争优势。偏爱消费和互联网龙头。"},
            {"id": "macro", "name": "宏观对冲视角", "style": "像李蓓一样思考：从宏观到微观，关注利率、汇率、政策周期和大类资产轮动。"},
            {"id": "growth", "name": "成长赛道视角", "style": "像刘格菘一样思考：关注产业景气度、技术革命和渗透率拐点。偏爱新能源、半导体、AI等成长行业。"},
            {"id": "quant", "name": "量化数据视角", "style": "用数据和概率思考：关注估值分位、资金流向、动量因子和市场情绪指标。"},
        ]

        predictions = []
        for exp in experts[:limit]:
            try:
                prompt = f"""你是一位资深中国投资专家。请以以下风格分析近期市场动态：

风格定位：{exp['style']}

近期重要新闻：
{titles}

请给出你的判断（JSON格式）：
{{"direction": "看多/看空/震荡", "title": "10字以内的观点标题", "content": "80-150字的分析，包含具体判断和逻辑", "tags": ["标签1", "标签2"], "relatedFunds": ["基金代码"], "confidence": 60-90的整数}}"""

                result = await llm_service.analyze_news(prompt, None, None)
                if result:
                    predictions.append({
                        "id": exp["id"],
                        "expert": exp["name"],
                        "direction": result.get("impact_level", "中性").replace("利好", "看多").replace("利空", "看空"),
                        "title": result.get("key_points", [""])[0] if result.get("key_points") else "最新市场分析",
                        "content": result.get("short_term", ""),
                        "tags": result.get("key_points", [])[:2],
                        "relatedFunds": [f["code"] for f in result.get("affected_funds", [])[:2]],
                        "confidence": abs(result.get("impact_score", 60)),
                    })
            except Exception as e:
                logger.warning(f"Expert prediction failed for {exp['name']}: {e}")

        return predictions

    async def get_expert_tracker(self) -> list[dict]:
        """Get real fund manager data from AKShare (cached 1h)."""
        import asyncio
        experts = []

        # Popular fund manager codes for AKShare
        manager_codes = [
            ("张坤", "005827", "易方达蓝筹精选"),
            ("谢治宇", "163406", "兴全合润"),
            ("葛兰", "001475", "中欧医疗健康"),
            ("刘格菘", "002939", "广发创新升级"),
            ("朱少醒", "161005", "富国天惠"),
            ("侯昊", "161725", "招商中证白酒"),
        ]

        for name, fund_code, fund_name in manager_codes:
            try:
                import akshare as ak
                # Get fund NAV data for performance calculation
                nav_df = await asyncio.to_thread(
                    ak.fund_open_fund_info_em, symbol=fund_code, indicator="单位净值走势"
                )
                perf = {"year1": None, "year3": None, "year5": None}
                if nav_df is not None and not nav_df.empty:
                    nav_df = nav_df.sort_values("净值日期")
                    nav_values = nav_df["单位净值"].dropna().values
                    if len(nav_values) > 250:
                        latest = float(nav_values[-1])
                        perf["year1"] = round((latest / float(nav_values[-250]) - 1) * 100, 1) if len(nav_values) > 250 else None
                        perf["year3"] = round((latest / float(nav_values[0]) - 1) * 100, 1) if len(nav_values) > 750 else None

                experts.append({
                    "name": name,
                    "fund_code": fund_code,
                    "fund_name": fund_name,
                    "performance": perf,
                    "style": "价值投资" if name in ("张坤","朱少醒") else "均衡配置" if name == "谢治宇" else "成长投资",
                    "data_source": "AKShare/天天基金",
                })
            except Exception as e:
                logger.warning(f"Expert tracker failed for {name}: {e}")

        return experts

    async def get_recent_analyses(self, limit: int = 10) -> list[dict]:
        """Get recent AI analyses with article info."""
        stmt = (
            select(NewsAnalysis, NewsArticle)
            .join(NewsArticle, NewsAnalysis.news_id == NewsArticle.id)
            .order_by(desc(NewsAnalysis.generated_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return [{
            "id": a.id,
            "news_id": a.news_id,
            "title": art.title,
            "impact_score": a.impact_score,
            "impact_level": a.impact_level,
            "affected_funds": a.affected_funds or [],
            "short_term": a.short_term or "",
            "medium_term": a.medium_term or "",
            "action_advice": a.action_advice or "",
            "key_points": a.key_points or [],
            "generated_by": a.generated_by,
            "generated_at": a.generated_at.isoformat() if a.generated_at else None,
        } for a, art in rows]

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



