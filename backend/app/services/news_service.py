"""News service layer."""
import logging
import random
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_
from app.models.news import NewsSource, NewsArticle, NewsAnalysis, Viewpoint
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
            kw_map = {
                "基金": ["基金", "ETF", "QDII", "FOF", "REIT", "定投", "净值", "基金经理", "公募", "私募", "指数", "联接", "LOF"],
                "行业": ["行业", "板块", "赛道", "科技", "消费", "医药", "新能源", "半导体", "白酒", "银行", "地产", "光伏", "锂电", "芯片", "AI", "基建", "煤炭", "钢铁", "保险", "证券"],
                "宏观": ["央行", "利率", "通胀", "GDP", "PMI", "CPI", "降息", "加息", "货币政策", "财政", "汇率", "人民币", "美元", "宏观", "经济数据", "美联储"],
                "策略": ["策略", "定投", "配置", "仓位", "止损", "止盈", "轮动", "红利", "价值投资", "平衡", "回撤", "收益", "风险", "复利", "组合"],
                "海外": ["美股", "港股", "QDII", "纳斯达克", "标普", "恒生", "全球", "海外", "美元", "日元", "欧股"],
                "大佬": ["zhangkun", "张坤", "xiezhiyu", "谢治宇", "gelan", "葛兰", "houhao", "侯昊", "刘格菘", "经理", "大佬", "牛散", "朱少醒", "任泽平", "李蓓", "林园", "但斌", "洪灏"],
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
                "宏观": ["央行", "利率", "通胀", "GDP", "PMI", "CPI", "降息", "加息", "货币政策", "财政", "汇率", "人民币", "美元", "宏观", "经济数据", "美联储"],
                "策略": ["策略", "定投", "配置", "仓位", "止损", "止盈", "轮动", "红利", "价值投资", "平衡", "回撤", "收益", "风险", "复利", "组合"],
                "海外": ["美股", "港股", "QDII", "纳斯达克", "标普", "恒生", "全球", "海外", "美元", "日元", "欧股"],
                "大佬": ["zhangkun", "张坤", "xiezhiyu", "谢治宇", "gelan", "葛兰", "houhao", "侯昊", "刘格菘", "经理", "大佬", "牛散", "朱少醒", "任泽平", "李蓓", "林园", "但斌", "洪灏"],
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
        """Generate per-article expert predictions — each expert analyzes 2-3 news individually."""
        import random, asyncio as _asyncio
        stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(36)
        result = await self.db.execute(stmt)
        all_news = result.scalars().all()
        if len(all_news) < 12:
            return []

        experts = [
            {"id":"zhangkun","name":"张坤","title":"易方达·价值投资","focus":"只关注消费、互联网和白酒龙头。寻找有护城河、自由现金流充裕的优质公司。","prefers":"消费/互联网/白酒"},
            {"id":"libei","name":"李蓓","title":"半夏·宏观对冲","focus":"从宏观到微观，关注利率汇率政策周期。善于发现市场定价错误和资产轮动机会。","prefers":"债券/黄金/大宗商品"},
            {"id":"renzeping","name":"任泽平","title":"泽平·政策解读","focus":"从政策文件和经济数据中解读市场信号。关注货币宽松、产业政策方向。","prefers":"基建/新能源/地产"},
            {"id":"liugesong","name":"刘格菘","title":"广发·成长赛道","focus":"寻找景气上升行业，关注技术革命和渗透率拐点。坚信赛道比估值重要。","prefers":"半导体/AI/新能源/光伏"},
            {"id":"honghao","name":"洪灏","title":"思睿·量化周期","focus":"用数据和模型判断市场周期。关注估值分位、资金流向、情绪指标。","prefers":"沪深300/中证500/创业板"},
            {"id":"linyuan","name":"林园","title":"林园·逆向思维","focus":"极度逆向，市场恐慌时贪婪。相信垄断性消费和医药能穿越周期。","prefers":"医药/消费/中药"},
            {"id":"qiuguolu","name":"邱国鹭","title":"高毅·品质投资","focus":"寻找便宜的好公司，关注估值、品质和时机三个维度。坚持逆向投资，人多的地方不去。","prefers":"低估值蓝筹/金融/消费"},
            {"id":"zhaodanyang","name":"赵丹阳","title":"赤子之心·全球价值","focus":"用全球视野做价值投资，善于跨市场比较。关注企业长期自由现金流，不追逐短期热点。","prefers":"消费/互联网/全球资产"},
            {"id":"zhushaoxing","name":"朱少醒","title":"富国·长跑冠军","focus":"不跟风不抱团，均衡分散持仓。追求长期稳健复利，15年年化超18%。","prefers":"均衡/分散/成长"},
            {"id":"xiaonan","name":"萧楠","title":"易方达·消费赛道","focus":"专注消费行业深度研究，对白酒、家电、食品饮料有极致理解。长期持有优质消费品牌。","prefers":"消费/白酒/家电/食品饮料"},
        ]

        results = []
        random.shuffle(all_news)
        for i, exp in enumerate(experts[:limit]):
            expert_predictions = []
            # Each expert gets 5 unique news articles
            my_news = all_news[i*6:i*6+6] if i*6+6 <= len(all_news) else all_news[i*5:i*5+5]

            for j, news in enumerate(my_news[:5]):
                try:
                    prompt = f"""你是投资专家{exp['name']}。风格：{exp['focus']}关注领域：{exp['prefers']}。

针对这条新闻，从你的专业视角分析：

新闻：{news.title[:100]}
摘要：{news.summary or ''}

返回JSON（15字内标题，80字内分析）：
{{"title":"你的判断标题","content":"你的分析","tags":["标签"],"relatedFunds":["代码"],"confidence":60-90}}"""

                    result = await llm_service.analyze_news(prompt, None, None)
                    if result:
                        expert_predictions.append({
                            "news_title": news.title[:50],
                            "news_id": news.id,
                            "title": result.get("title", result.get("key_points",[""])[0] if result.get("key_points") else "分析"),
                            "content": (result.get("short_term") or result.get("action_advice") or "")[:120],
                            "tags": (result.get("tags") or result.get("key_points", []))[:2],
                            "relatedFunds": [f["code"] for f in result.get("affected_funds", [])[:2]] if result.get("affected_funds") else [],
                            "confidence": abs(result.get("impact_score", 65)),
                        })
                except Exception as e:
                    logger.warning(f"Prediction failed: {exp['name']}: {e}")
                await _asyncio.sleep(0.3)

            if expert_predictions:
                avg_conf = sum(p["confidence"] for p in expert_predictions) // max(len(expert_predictions), 1)
                results.append({
                    "id": exp["id"],
                    "expert": exp["name"],
                    "title_role": exp["title"],
                    "prefers": exp["prefers"],
                    "prediction_count": len(expert_predictions),
                    "latest_title": expert_predictions[0]["title"],
                    "latest_content": expert_predictions[0]["content"],
                    "confidence": avg_conf,
                    "predictions": expert_predictions,
                    "tags": expert_predictions[0].get("tags", []),
                })

        return results

    async def get_expert_prediction_detail(self, expert_id: str) -> dict:
        # Read from cache first — don't regenerate
        from app.core.cache import cache_get
        cached = await cache_get("analysis:expert_predictions")
        all_preds = cached if cached else await self.get_expert_predictions(limit=6)
        for p in (all_preds or []):
            if p["id"] == expert_id:
                return p
        return {"id": expert_id, "error": "未找到数据"}

    async def get_expert_tracker(self) -> list[dict]:
        """Get diverse expert data: fund managers (AKShare) + economists/analysts."""
        import asyncio
        experts = []

        # Fund managers with AKShare detailed data
        fund_managers = [
            ("zhangkun", "张坤", "005827", "易方达蓝筹精选", "价值投资·消费龙头", "公募一哥，管理规模曾超千亿。以重仓白酒和互联网平台闻名，坚持长期持有伟大企业。代表作易方达蓝筹精选5年年化超15%。"),
            ("xiezhiyu", "谢治宇", "163406", "兴全合润", "均衡配置·性价比", "兴全基金灵魂人物，不追热点不赌单一赛道。牛熊市中均表现稳健，注重持有体验，回撤控制出色。"),
            ("gelan", "葛兰", "001475", "中欧医疗健康", "医药赛道·深度研究", "美国西北大学生物医学博士，对创新药产业链有远超同行的理解。经历医药板块大幅调整仍在坚守，逆向加仓。"),
            ("houhao", "侯昊", "161725", "招商中证白酒", "指数增强·白酒专家", "管理国内规模最大的白酒主题基金，对白酒行业周期有独到判断。擅长在行业低迷时逆向布局。"),
            ("zhushaoxing", "朱少醒", "161005", "富国天惠成长", "成长价值·长跑冠军", "中国唯一从未换过基金的10年+基金经理。15年年化超18%，穿越牛熊。持仓分散，不跟风不抱团。"),
            ("xiaonan", "萧楠", "110022", "易方达消费行业", "消费赛道·深度研究", "A股消费投资第一人，管理易方达消费超10年。对白酒、家电、食品饮料有极致深度研究。"),
            ("wangzonghe", "王宗合", "001632", "天弘中证食品饮料", "消费指数·被动投资", "专注消费赛道被动投资，跟踪食品饮料指数。费率低，适合看好消费长期趋势的投资者。"),
        ]
        for eid, name, code, fname, style, bio in fund_managers:
            try:
                import akshare as ak
                nav_df = await asyncio.to_thread(ak.fund_open_fund_info_em, symbol=code, indicator='单位净值走势')
                perf = {'year1': None, 'year3': None, 'latest_nav': None}
                if nav_df is not None and not nav_df.empty:
                    nav_df = nav_df.sort_values('净值日期')
                    vals = nav_df['单位净值'].dropna().values
                    if len(vals) > 0:
                        perf['latest_nav'] = float(vals[-1])
                    if len(vals) > 250:
                        latest = float(vals[-1])
                        perf['year1'] = round((latest/float(vals[-250])-1)*100, 1) if len(vals)>250 else None
                        perf['year3'] = round((latest/float(vals[0])-1)*100, 1) if len(vals)>750 else None
                experts.append({'id':eid, 'name':name, 'title':style, 'fund_name':fname, 'fund_code':code, 'bio':bio, 'performance':perf, 'type':'基金经理', 'source':'AKShare/天天基金(实时净值)'})
            except Exception as e:
                logger.warning(f'Tracker failed for {name}: {e}')

        # Economists & analysts
        for e in [
            {'name':'任泽平','id':'renzeping', 'title':'著名经济学家', 'bio':'前恒大首席经济学家，以新周期理论闻名，对宏观政策和房地产周期有深度研究', 'type':'经济学家'},
            {'name':'洪灏','id':'honghao', 'title':'思睿集团首席经济学家', 'bio':'前交银国际研究主管，CFA持证人，多次精准预判A股关键转折点', 'type':'经济学家'},
            {'name':'李蓓','id':'libei', 'title':'半夏投资创始人', 'bio':'私募行业少有的女性掌门人，宏观对冲策略，擅长大类资产配置', 'type':'宏观对冲'},
        ]:
            experts.append({**e, 'performance': {'year1': None, 'year3': None}, 'source': '公开资料'})

        # Media & independent investors
        for m in [
            {'name':'林园','id':'linyuan', 'title':'民间投资传奇', 'bio':'从8000元到百亿身家，极度看好消费和医药，嘴巴经济理论提出者', 'type':'民间投资家'},
            {'name':'但斌','id':'danbin', 'title':'东方港湾董事长', 'bio':'中国价值投资旗帜人物，时间的玫瑰理念提出者，穿越牛熊坚持理念', 'type':'价值投资家'},
            {'name':'邱国鹭','id':'qiuguolu', 'title':'高毅资产董事长', 'bio':'前南方基金投资总监，著有《投资中最简单的事》。坚持逆向投资，管理规模超千亿', 'type':'私募大佬'},
            {'name':'李大霄','id':'lidaxiao', 'title':'英大证券首席经济学家', 'bio':'A股最具争议的分析师，以婴儿底钻石底等底部判断闻名，极度悲观时的逆向提醒有价值', 'type':'证券分析师'},
            {'name':'赵丹阳','id':'zhaodanyang', 'title':'赤子之心创始人', 'bio':'中国私募基金行业开创者之一，以价值投资和全球视野著称，曾与巴菲特共进午餐', 'type':'私募教父'},
        ]:
            experts.append({**m, 'performance': {'year1': None, 'year3': None}, 'source': '公开资料'})

        return experts

    async def get_expert_detail(self, expert_id: str) -> dict:
        """Get comprehensive expert detail with news, analyses, performance, and operations."""
        import asyncio
        from app.core.cache import cache_get

        manager_map = {
            "zhangkun": ("005827", "zhangkun", "张坤", "易方达蓝筹精选", "价值投资·消费龙头", "公募一哥，管理规模曾超千亿。以重仓白酒和互联网平台闻名，坚持长期持有伟大企业。代表作易方达蓝筹精选5年年化超15%。"),
            "xiezhiyu": ("163406", "xiezhiyu", "谢治宇", "兴全合润", "均衡配置·性价比", "兴全基金灵魂人物，不追热点不赌单一赛道。牛熊市中均表现稳健，注重持有体验，回撤控制出色。"),
            "gelan": ("001475", "gelan", "葛兰", "中欧医疗健康", "医药赛道·深度研究", "美国西北大学生物医学博士，对创新药产业链有远超同行的理解。经历医药板块大幅调整仍在坚守，逆向加仓。"),
            "houhao": ("161725", "houhao", "侯昊", "招商中证白酒", "指数增强·白酒专家", "管理国内规模最大的白酒主题基金，对白酒行业周期有独到判断。"),
            "zhushaoxing": ("161005", "zhushaoxing", "朱少醒", "富国天惠成长", "成长价值·长跑冠军", "中国唯一一位从未换过基金的10年+基金经理。15年年化超18%，穿越多轮牛熊。持仓分散，不跟风不抱团。"),
            "xiaonan": ("110022", "xiaonan", "萧楠", "易方达消费行业", "消费赛道·深度研究", "A股消费投资第一人，管理易方达消费行业超10年。对白酒、家电、食品饮料行业有极致深度的研究。"),
            "wangzonghe": ("001632", "wangzonghe", "王宗合", "天弘中证食品饮料", "消费指数·被动投资", "专注消费赛道被动投资，跟踪食品饮料指数。费率低，适合看好消费长期趋势的投资者。"),
        }

        non_manager = {
            "renzeping": ("renzeping","任泽平","经济学家","泽平宏观创始人","前恒大首席经济学家，国务院发展研究中心宏观部研究室副主任。以新周期理论闻名，对宏观政策和房地产周期有深度研究。"),
            "honghao": ("honghao","洪灏","经济学家","思睿集团首席经济学家","前交银国际研究主管，CFA持证人。自主研发市场情绪和周期模型，多次精准预判A股关键转折点。"),
            "libei": ("libei","李蓓","宏观对冲","半夏投资创始人","私募行业少有的女性掌门人，以宏观对冲策略闻名。擅长从宏观到微观的大类资产配置，判断犀利。"),
            "linyuan": ("linyuan","林园","民间投资家","林园投资董事长","从8000元到百亿身家的投资传奇。极度看好消费和医药赛道，嘴巴经济理论提出者。"),
            "danbin": ("danbin","但斌","价值投资家","东方港湾董事长","中国价值投资旗帜人物，时间的玫瑰理念提出者。重仓茅台腾讯十余年，穿越牛熊坚持理念。"),
            "qiuguolu": ("qiuguolu","邱国鹭","私募大佬","高毅资产董事长","前南方基金投资总监，著有《投资中最简单的事》。坚持逆向投资，以合理价格买入优质公司，管理规模超千亿。"),
            "lidaxiao": ("lidaxiao","李大霄","证券分析师","英大证券首席经济学家","A股最具争议的分析师，以\"婴儿底\"\"钻石底\"等底部判断闻名。虽然常被调侃，但对市场极度悲观时的逆向提醒有价值。"),
            "zhaodanyang": ("zhaodanyang","赵丹阳","私募教父","赤子之心创始人","中国私募基金行业开创者之一，2004年发行首只阳光私募。以价值投资和全球视野著称，曾与巴菲特共进午餐。"),
        }

        # Multi-strategy news search: by name, by fund code, by sector keywords
        expert_config = {
            "zhangkun": {"names":["张坤","蓝筹精选","易方达蓝筹"], "keywords":["白酒","消费","互联网","茅台","腾讯"], "fund":"005827"},
            "xiezhiyu": {"names":["谢治宇","兴全合润"], "keywords":["均衡","性价比","宁德时代","半导体"], "fund":"163406"},
            "gelan":     {"names":["葛兰","中欧医疗","医疗健康"], "keywords":["医药","创新药","CXO","医疗器械","恒瑞"], "fund":"001475"},
            "houhao":    {"names":["侯昊","招商中证","中证白酒"], "keywords":["白酒","茅台","五粮液","泸州老窖","消费"], "fund":"161725"},
            "renzeping": {"names":["任泽平","泽平"], "keywords":["宏观","政策","新周期","PMI","GDP","利率","改革"], "fund":""},
            "honghao":   {"names":["洪灏","交银国际"], "keywords":["量化","周期","估值分位","资金流向","情绪","A股"], "fund":""},
            "libei":     {"names":["李蓓","半夏投资"], "keywords":["宏观对冲","利率","汇率","大类资产","大宗商品","黄金","债券"], "fund":""},
            "linyuan":   {"names":["林园","林园投资"], "keywords":["医药","消费","中药","老龄化","垄断","嘴巴经济"], "fund":""},
            "danbin":    {"names":["但斌","东方港湾"], "keywords":["价值投资","时间的玫瑰","茅台","腾讯","长期持有"], "fund":""},
            "qiuguolu": {"names":["邱国鹭","高毅资产"], "keywords":["逆向投资","价值投资","低估值","品质","时机"], "fund":""},
            "lidaxiao": {"names":["李大霄","英大证券"], "keywords":["市场底部","婴儿底","钻石底","蓝筹","估值","机会"], "fund":""},
            "zhaodanyang":{"names":["赵丹阳","赤子之心"], "keywords":["价值投资","全球视野","长期持有","消费","互联网"], "fund":""},
            "zhushaoxing":{"names":["朱少醒","富国天惠"], "keywords":["成长","均衡","分散","长跑","不抱团"], "fund":"161005"},
            "xiaonan":{"names":["萧楠","易方达消费"], "keywords":["消费","白酒","家电","食品饮料","品牌"], "fund":"110022"},
            "wangzonghe":{"names":["王宗合","天弘食品饮料"], "keywords":["消费","食品饮料","指数","被动投资"], "fund":"001632"},
        }

        cfg = expert_config.get(expert_id, {"names":[], "keywords":[], "fund":""})
        search_terms = cfg["names"] + cfg["keywords"]

        # Search news by multiple terms
        related_news = []
        if search_terms:
            conditions = []
            for term in search_terms[:6]:
                conditions.append(NewsArticle.title.ilike(f"%{term}%"))
            stmt = select(NewsArticle).where(or_(*conditions)).order_by(desc(NewsArticle.published_at)).limit(15)
            result = await self.db.execute(stmt)
            related_news = [self._to_item(a) for a in result.scalars().all()]

        # Get ALL recent AI analyses and filter those related to this expert's domain
        all_analyses_stmt = select(NewsAnalysis).order_by(desc(NewsAnalysis.generated_at)).limit(30)
        ana_result = await self.db.execute(all_analyses_stmt)
        related_analyses = []
        for a in ana_result.scalars().all():
            # Check if analysis mentions expert's keywords
            text = (a.short_term or "") + (a.action_advice or "")
            if any(kw in text for kw in cfg["keywords"][:4]):
                related_analyses.append({
                    "news_id": a.news_id,
                    "impact_level": a.impact_level,
                    "impact_score": a.impact_score,
                    "short_term": a.short_term or "",
                    "action_advice": a.action_advice or "",
                    "generated_by": a.generated_by,
                })

        # Build profile
        profile = {}
        if expert_id in manager_map:
            code, eid, ename, fname, style, bio = manager_map[expert_id]
            profile = {"id":expert_id,"name":ename,"type":"基金经理","title":f"{fname} · {style}","bio":bio,"fund_name":fname,"fund_code":code}
        elif expert_id in non_manager:
            eid, ename, etype, etitle, ebio = non_manager[expert_id]
            profile = {"id":expert_id,"name":ename,"type":etype,"title":etitle,"bio":ebio}
        else:
            return {"id": expert_id, "error": "未找到该专家"}

        # Predictive views from cache
        pred_view = None
        cached_preds = await cache_get("analysis:expert_predictions")
        if cached_preds:
            for p in cached_preds:
                if p.get("id") == expert_id:
                    pred_view = p
                    break

        result = {
            **profile,
            "related_news": related_news[:10],
            "related_analyses": related_analyses[:8],
            "operations": [],
            "fund_operations": [],
            "predictive_view": pred_view,
            "nav_history": [],
            "size_history": [],
            "performance_highlights": {},
        }

        # Try to add fund performance data + holdings
        if expert_id in manager_map:
            code = manager_map[expert_id][0]
            try:
                import akshare as ak
                nav_df = await asyncio.to_thread(ak.fund_open_fund_info_em, symbol=code, indicator="单位净值走势")
                if nav_df is not None and not nav_df.empty:
                    nav_df = nav_df.sort_values("净值日期")
                    for _, row in nav_df.tail(90).iterrows():
                        result["nav_history"].append({
                            "date": str(row.get("净值日期", ""))[:10],
                            "nav": float(row.get("单位净值", 0)),
                            "daily_return": float(row.get("日增长率", 0)) if row.get("日增长率") else None,
                        })

                    # Generate fund operations from real NAV data
                    ops = []
                    tail = nav_df.tail(60)
                    rets = tail["日增长率"].dropna()
                    if len(rets) > 10:
                        vals = rets.values
                        best_i = vals.argmax(); worst_i = vals.argmin()
                        ops.append({"date": str(tail.iloc[best_i].get("净值日期",""))[:10], "action":"📈 单日最佳","detail":f"日涨幅 +{float(vals[best_i]):.2f}%，近60日最佳表现"})
                        ops.append({"date": str(tail.iloc[worst_i].get("净值日期",""))[:10], "action":"📉 单日回撤","detail":f"日跌幅 {float(vals[worst_i]):.2f}%，近60日最大回撤"})

                        # Find streaks
                        streak_up = streak_down = 0
                        max_up = max_down = 0
                        for v in vals:
                            if v > 0: streak_up += 1; streak_down = 0
                            elif v < 0: streak_down += 1; streak_up = 0
                            else: streak_up = streak_down = 0
                            max_up = max(max_up, streak_up); max_down = max(max_down, streak_down)
                        if max_up >= 3:
                            ops.append({"date": "近60日", "action":"🔥 连涨纪录", "detail":f"最高连续 {max_up} 个交易日上涨"})
                        if max_down >= 3:
                            ops.append({"date": "近60日", "action":"❄️ 连跌纪录", "detail":f"最高连续 {max_down} 个交易日下跌"})

                        # NAV milestones
                        first_nav = float(tail.iloc[0].get("单位净值",0))
                        last_nav = float(tail.iloc[-1].get("单位净值",0))
                        if first_nav > 0:
                            chg = round((last_nav/first_nav-1)*100, 2)
                            ops.append({"date": "近60日", "action":"📊 期净值变化", "detail":f"净值从 {first_nav:.4f} → {last_nav:.4f}，变动 {chg:+.2f}%"})

                    result["fund_operations"] = ops

                size_df = await asyncio.to_thread(ak.fund_open_fund_info_em, symbol=code, indicator="季度规模变动")
                if size_df is not None and not size_df.empty:
                    for _, row in size_df.tail(6).iterrows():
                        result["size_history"].append({
                            "date": str(row.get("报告期", ""))[:10],
                            "size": float(row.get("资产规模", row.get("期末总份额", 0)) or 0),
                        })

                # Performance highlights
                if result["nav_history"]:
                    navs = result["nav_history"]
                    result["performance_highlights"] = {
                        "latest_nav": navs[-1]["nav"],
                        "nav_date": navs[-1]["date"],
                        "day_change": navs[-1]["daily_return"],
                    }

                # Top holdings from quarterly report
                try:
                    holdings_df = await asyncio.to_thread(ak.fund_portfolio_hold_em, symbol=code, date="2025")
                    if holdings_df is not None and not holdings_df.empty:
                        holdings = []
                        for _, row in holdings_df.head(10).iterrows():
                            holdings.append({
                                "stock": str(row.get("股票名称", "")),
                                "code": str(row.get("股票代码", "")),
                                "ratio": float(row.get("占净值比例", 0) or 0),
                                "shares": str(row.get("持股数", "")),
                                "market_value": str(row.get("持仓市值", "")),
                                "quarter": str(row.get("季度", "")),
                            })
                        result["holdings"] = holdings
                except Exception:
                    pass

                # Quarterly position CHANGES (增持/减持/新增/剔除)
                try:
                    change_df = await asyncio.to_thread(ak.fund_portfolio_change_em, symbol=code, date="2025")
                    if change_df is not None and not change_df.empty:
                        changes = []
                        for _, row in change_df.head(15).iterrows():
                            changes.append({
                                "stock": str(row.get("股票名称", "")),
                                "code": str(row.get("股票代码", "")),
                                "change_type": str(row.get("变动类型", row.get("操作", ""))),
                                "change_ratio": str(row.get("变动比例", row.get("占净值比例", ""))),
                                "quarter": str(row.get("季度", "")),
                            })
                        result["position_changes"] = changes
                except Exception:
                    pass

                # Daily-like operations from NAV data (best/worst days, streaks, volatility)
                if result["nav_history"] and len(result["nav_history"]) > 20:
                    navs = result["nav_history"]
                    daily_ops = []
                    # Top 3 best days
                    best = sorted(navs, key=lambda x: abs(x.get("daily_return") or 0), reverse=True)[:3]
                    for b in best:
                        ret = b.get("daily_return") or 0
                        if abs(ret) > 0.5:
                            daily_ops.append({
                                "date": b["date"],
                                "action": "大涨" if ret > 0 else "大跌",
                                "detail": f"净值 {b['nav']:.4f}，日{'涨' if ret>0 else '跌'}幅 {ret:+.2f}%",
                                "amount": f"估算规模变动 {('+' if ret>0 else '')}{abs(ret)*0.8:.1f}%",
                            })
                    # Consecutive up/down streaks
                    streak = 0; streak_start = ""
                    for n in navs:
                        ret = n.get("daily_return") or 0
                        if ret > 0:
                            if streak <= 0: streak = 1; streak_start = n["date"]
                            else: streak += 1
                        elif ret < 0:
                            if streak >= 0: streak = -1; streak_start = n["date"]
                            else: streak -= 1
                    if abs(streak) >= 3:
                        direction = "连涨" if streak > 0 else "连跌"
                        daily_ops.append({
                            "date": streak_start,
                            "action": direction,
                            "detail": f"连续{abs(streak)}个交易日{direction}",
                            "amount": "",
                        })
                    result["daily_operations"] = sorted(daily_ops, key=lambda x: x["date"], reverse=True)[:8]
            except Exception as e:
                logger.warning(f"Fund data failed for {expert_id}: {e}")
            except Exception as e:
                logger.warning(f"Fund data failed for {expert_id}: {e}")

        # ── Investment insights: what to learn from this expert ──
        insights = []
        if expert_id in manager_map:
            insights = [
                {"icon":"📊","title":"持仓风格","detail":f"{profile.get('bio','')[:80]}..."},
                {"icon":"🎯","title":"投资理念","detail":"长期持有优质企业，不因短期波动卖出。在市场恐慌时反而是加仓良机。"},
                {"icon":"📉","title":"回撤应对","detail":"即使优秀基金也会有20-30%的回撤。关键是不在底部割肉，坚持定投摊成本。"},
                {"icon":"💡","title":"学习要点","detail":"关注基金经理季报中的观点变化，判断其是否言行一致。换手率低说明真正在践行长期主义。"},
            ]
        else:
            insights = [
                {"icon":"🔍","title":"研究风格","detail":f"{profile.get('bio','')[:80]}..."},
                {"icon":"📰","title":"观点价值","detail":"关注其对宏观数据和政策走向的判断，作为自己投资决策的参考而非盲从。"},
                {"icon":"⚠️","title":"独立思考","detail":"大佬观点≠投资建议。每个人的资金量、风险承受能力不同，不能简单复制。"},
            ]

        # ── News digest: curated news with market context ──
        news_digest = []
        for n in related_news[:8]:
            entry = {
                "date": (n.get("published_at") or "")[:10],
                "title": n.get("title", ""),
                "news_id": n.get("id"),
                "sentiment": n.get("sentiment", ""),
            }
            # Tag each news with relevant sector
            for kw in cfg["keywords"][:6]:
                if kw in (n.get("title","") + (n.get("summary") or "")):
                    entry["tag"] = kw
                    break
            news_digest.append(entry)

        # ── Market context summary ──
        market_context = ""
        if related_analyses:
            contexts = [a["short_term"] for a in related_analyses[:3] if a.get("short_term")]
            market_context = "；".join(contexts[:2])[:200] if contexts else ""

        result["insights"] = insights
        result["news_digest"] = news_digest
        result["market_context"] = market_context
        result["fund_style"] = cfg.get("keywords", [])[:4]

        # ── Merge operations: fund performance events only ──
        result["operations"] = result.get("fund_operations", [])

        return result

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

    async def create_viewpoint(self, content: str, source: str = "用户投稿", author: str = "") -> dict:
        """Submit a user viewpoint and auto-analyze with DeepSeek."""
        if not content.strip():
            return {"error": "内容不能为空"}

        # DeepSeek analysis
        ai_result = None
        try:
            prompt = f"""分析以下投资观点，提取关键信息。来源：{source}，作者：{author or '未知'}

内容：{content}

返回JSON：
{{"title":"15字以内的标题","summary":"50-80字摘要","direction":"看多/看空/中性","confidence":50-90,"tags":["标签1","标签2"],"relatedFunds":["基金代码1","基金代码2"]}}"""
            ai_result = await llm_service.analyze_news(prompt, None, None)
        except Exception as e:
            logger.warning(f"Viewpoint AI analysis failed: {e}")

        vp = Viewpoint(
            source=source, author=author or None, content=content,
            ai_title=ai_result.get("title", "") if ai_result else None,
            ai_summary=ai_result.get("summary", ai_result.get("short_term", "")) if ai_result else None,
            direction=ai_result.get("direction", ai_result.get("impact_level", "中性")) if ai_result else None,
            confidence=int(ai_result.get("confidence", ai_result.get("impact_score", 50))) if ai_result else None,
            related_funds=ai_result.get("relatedFunds", ai_result.get("affected_funds", [])) if ai_result else [],
            tags=ai_result.get("tags", ai_result.get("key_points", [])) if ai_result else [],
        )
        self.db.add(vp)
        await self.db.commit()
        await self.db.refresh(vp)
        return self._viewpoint_to_dict(vp)

    async def list_viewpoints(self, limit: int = 20) -> list[dict]:
        stmt = select(Viewpoint).order_by(desc(Viewpoint.created_at)).limit(limit)
        result = await self.db.execute(stmt)
        return [self._viewpoint_to_dict(v) for v in result.scalars().all()]

    @staticmethod
    def _viewpoint_to_dict(v: Viewpoint) -> dict:
        return {
            "id": v.id, "source": v.source, "author": v.author,
            "content": v.content, "ai_title": v.ai_title,
            "ai_summary": v.ai_summary, "direction": v.direction,
            "confidence": v.confidence, "related_funds": v.related_funds or [],
            "tags": v.tags or [], "created_at": v.created_at.isoformat() if v.created_at else None,
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



