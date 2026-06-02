"""Market data service layer — database queries with caching."""
import logging
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, and_

from app.models.market import Stock, StockDailyPrice, Fund, FundNAV, Index, IndexDailyPrice, CapitalFlow, SectorPerformance
from app.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)


def _to_float(val) -> Optional[float]:
    """Convert Decimal/None to float for JSON serialization."""
    if val is None:
        return None
    return float(val)


def _kline_to_dict(row) -> dict:
    return {
        "date": row.trade_date.isoformat() if row.trade_date else None,
        "open": _to_float(row.open),
        "high": _to_float(row.high),
        "low": _to_float(row.low),
        "close": _to_float(row.close),
        "volume": row.volume,
        "amount": _to_float(row.amount),
    }


class MarketService:
    """Service for market data queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Indices ────────────────────────────────────────

    async def get_indices(self) -> list[dict]:
        """Get all tracked indices with latest price and 30-day sparkline."""
        cached = await cache_get("market:indices:latest")
        if cached:
            return cached

        stmt = select(Index).order_by(Index.id)
        result = await self.db.execute(stmt)
        indices = result.scalars().all()

        output = []
        for idx in indices:
            # Latest price
            price_stmt = select(IndexDailyPrice).where(
                IndexDailyPrice.index_id == idx.id
            ).order_by(desc(IndexDailyPrice.trade_date)).limit(1)
            price_result = await self.db.execute(price_stmt)
            latest = price_result.scalar_one_or_none()

            # Last 30 days for sparkline
            spark_stmt = select(IndexDailyPrice).where(
                IndexDailyPrice.index_id == idx.id
            ).order_by(IndexDailyPrice.trade_date.desc()).limit(30)
            spark_result = await self.db.execute(spark_stmt)
            sparklines = spark_result.scalars().all()
            spark_data = [_to_float(p.close) for p in reversed(sparklines)]

            prev_close = None
            if len(sparklines) >= 2:
                prev_close = sparklines[1].close

            output.append({
                "code": idx.code,
                "name": idx.name,
                "market": idx.market,
                "country": idx.country,
                "latest_price": _to_float(latest.close) if latest else None,
                "change": _to_float(latest.close - prev_close) if latest and prev_close else None,
                "change_pct": _to_float(latest.change_pct) if latest else None,
                "sparkline": spark_data,
            })

        await cache_set("market:indices:latest", output, ttl=60)
        return output

    async def get_index_detail(self, code: str, days: int = 90) -> Optional[dict]:
        """Get single index detail with K-line history."""
        stmt = select(Index).where(Index.code == code)
        result = await self.db.execute(stmt)
        idx = result.scalar_one_or_none()
        if not idx:
            return None

        kline_stmt = select(IndexDailyPrice).where(
            IndexDailyPrice.index_id == idx.id
        ).order_by(IndexDailyPrice.trade_date.desc()).limit(days)
        kline_result = await self.db.execute(kline_stmt)
        klines = [_kline_to_dict(k) for k in reversed(kline_result.scalars().all())]

        return {
            "info": {"code": idx.code, "name": idx.name, "market": idx.market, "country": idx.country},
            "klines": klines,
        }

    # ─── Stocks ─────────────────────────────────────────

    async def get_stock_detail(self, code: str, kline_days: int = 250) -> Optional[dict]:
        """Get full stock detail: info, quote, fundamentals, K-lines."""
        stmt = select(Stock).where(Stock.code == code)
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()
        if not stock:
            return None

        # Latest price data
        price_stmt = select(StockDailyPrice).where(
            StockDailyPrice.stock_id == stock.id
        ).order_by(desc(StockDailyPrice.trade_date)).limit(1)
        price_result = await self.db.execute(price_stmt)
        latest = price_result.scalar_one_or_none()

        # Previous close for change calculation
        prev_stmt = select(StockDailyPrice).where(
            StockDailyPrice.stock_id == stock.id
        ).order_by(desc(StockDailyPrice.trade_date)).offset(1).limit(1)
        prev_result = await self.db.execute(prev_stmt)
        prev = prev_result.scalar_one_or_none()

        # K-lines
        kline_stmt = select(StockDailyPrice).where(
            StockDailyPrice.stock_id == stock.id
        ).order_by(StockDailyPrice.trade_date.desc()).limit(kline_days)
        kline_result = await self.db.execute(kline_stmt)
        klines = [_kline_to_dict(k) for k in reversed(kline_result.scalars().all())]

        change = None
        change_pct = None
        if latest and prev:
            change = _to_float(latest.close - prev.close) if latest.close and prev.close else None
            change_pct = _to_float(latest.change_pct)

        return {
            "info": {
                "code": stock.code, "name": stock.name, "market": stock.market,
                "security_type": stock.security_type, "sector": stock.sector, "industry": stock.industry,
            },
            "quote": {
                "code": stock.code, "name": stock.name, "market": stock.market,
                "latest_price": _to_float(latest.close) if latest else None,
                "change": change,
                "change_pct": change_pct,
                "volume": latest.volume if latest else None,
                "amount": _to_float(latest.amount) if latest else None,
                "turnover_rate": _to_float(latest.turnover_rate) if latest else None,
                "pe_ratio": _to_float(latest.pe_ratio) if latest else None,
                "pb_ratio": _to_float(latest.pb_ratio) if latest else None,
                "total_mv": _to_float(latest.total_mv) if latest else None,
                "circ_mv": _to_float(latest.circ_mv) if latest else None,
            } if latest else None,
            "fundamentals": {
                "pe": _to_float(latest.pe_ratio) if latest else None,
                "pb": _to_float(latest.pb_ratio) if latest else None,
                "total_mv": _to_float(latest.total_mv) if latest else None,
                "circ_mv": _to_float(latest.circ_mv) if latest else None,
            } if latest else None,
            "klines": klines,
        }

    async def get_stock_kline(self, code: str, period: str = "daily",
                              start: Optional[str] = None, end: Optional[str] = None) -> Optional[list]:
        """Get K-line data for a stock."""
        stmt = select(Stock).where(Stock.code == code)
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()
        if not stock:
            return None

        kline_stmt = select(StockDailyPrice).where(
            StockDailyPrice.stock_id == stock.id
        ).order_by(StockDailyPrice.trade_date.asc())

        if start:
            kline_stmt = kline_stmt.where(StockDailyPrice.trade_date >= date.fromisoformat(start))
        if end:
            kline_stmt = kline_stmt.where(StockDailyPrice.trade_date <= date.fromisoformat(end))

        kline_result = await self.db.execute(kline_stmt)
        return [_kline_to_dict(k) for k in kline_result.scalars().all()]

    async def search_stocks(self, q: str, market: Optional[str] = None, limit: int = 20) -> list[dict]:
        """Search stocks AND funds by code or name. Auto-fetches unknown funds from AKShare."""
        results = []

        # Search stocks
        stmt = select(Stock).where(
            or_(
                Stock.code.ilike(f"%{q}%"),
                Stock.name.ilike(f"%{q}%"),
            )
        )
        if market:
            stmt = stmt.where(Stock.market == market)
        stmt = stmt.limit(limit)
        r = await self.db.execute(stmt)
        for s in r.scalars().all():
            results.append({
                "code": s.code, "name": s.name, "market": s.market,
                "security_type": s.security_type, "match_score": 1.0,
            })

        # Search funds (with auto-fetch for 6-digit codes)
        fund_stmt = select(Fund).where(
            or_(
                Fund.code.ilike(f"%{q}%"),
                Fund.name.ilike(f"%{q}%"),
            )
        ).limit(limit - len(results))
        fr = await self.db.execute(fund_stmt)
        funds = fr.scalars().all()

        # If no fund found and query looks like a fund code (6 digits), auto-fetch from AKShare
        if not funds and q.strip().isdigit() and len(q.strip()) == 6:
            fetched = await self._fetch_and_save_fund(q.strip())
            if fetched:
                funds = [fetched]

        for f in funds:
            results.append({
                "code": f.code, "name": f.name, "market": "CN",
                "security_type": "fund", "match_score": 1.0,
            })

        return results[:limit]

    async def _fetch_and_save_fund(self, code: str):
        """Fetch fund info from AKShare and save to DB. Returns Fund or None."""
        import asyncio
        try:
            fund_info = await self._fetch_fund_from_akshare(code)
            if not fund_info:
                return None

            fund = Fund(
                code=code,
                name=fund_info["name"],
                fund_type=fund_info.get("fund_type", "mixed"),
                company=fund_info.get("company"),
                is_active=True,
            )
            self.db.add(fund)
            await self.db.commit()
            await self.db.refresh(fund)
            logger.info(f"Auto-fetched fund: {code} {fund_info['name']}")
            return fund
        except Exception as e:
            logger.warning(f"Auto-fetch fund {code} failed: {e}")
            await self.db.rollback()
            return None

    @staticmethod
    def _fetch_fund_from_akshare(code: str) -> Optional[dict]:
        """Get fund name from TianTian API (most reliable, no AKShare dependency)."""
        import logging
        log = logging.getLogger(__name__)

        # Primary: TianTian fund API (runs in thread, no async needed)
        try:
            import json, re, urllib.request
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            with urllib.request.urlopen(url, timeout=8) as resp:
                text = resp.read().decode('utf-8')
            match = re.search(r'jsonpgz\((.+)\)', text)
            if match:
                match = re.search(r'jsonpgz\((.+)\)', resp.text)
                if match:
                    data = json.loads(match.group(1))
                    name = data.get("name", "")
                    if name:
                        log.info(f"Fund {code} → {name} (TianTian)")
                        return {"name": name[:100], "fund_type": "混合型", "company": ""}
        except Exception as e:
            log.warning(f"Fund {code}: TianTian failed — {e}")

        # Fallback: East Money via AKShare
        try:
            import akshare as ak
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if df is not None and not df.empty:
                name = str(df.iloc[0].get("基金简称", ""))
                if name:
                    log.info(f"Fund {code} → {name} (East Money)")
                    return {"name": name[:100], "fund_type": "mixed", "company": ""}
        except Exception as e:
            log.warning(f"Fund {code}: East Money failed — {e}")

        log.error(f"Fund {code}: ALL sources failed")
        return None

    async def get_market_summary(self) -> dict:
        """Get real-time market overview (cached 60s, first call is slow due to API fetch)."""
        from datetime import date as dt_date

        cached = await cache_get("market:summary")
        if cached:
            return cached

        today = dt_date.today()

        # Latest index prices
        idx_stmt = select(IndexDailyPrice, Index).join(Index).where(
            IndexDailyPrice.trade_date == today
        ).order_by(desc(IndexDailyPrice.trade_date)).limit(10)
        idx_result = await self.db.execute(idx_stmt)
        indices = []
        for dp, idx in idx_result.all():
            change = _to_float(dp.change_pct)
            # Fallback: compute from previous day close if change_pct is null
            if change is None:
                prev_stmt = select(IndexDailyPrice.close).where(
                    IndexDailyPrice.index_id == idx.id,
                    IndexDailyPrice.trade_date < today
                ).order_by(desc(IndexDailyPrice.trade_date)).limit(1)
                prev_result = await self.db.execute(prev_stmt)
                prev_close = prev_result.scalar()
                cur_close = _to_float(dp.close)
                if prev_close and cur_close and prev_close > 0:
                    change = round((cur_close / float(prev_close) - 1) * 100, 2)
            indices.append({
                "code": idx.code, "name": idx.name, "market": idx.market,
                "close": _to_float(dp.close), "change_pct": change,
            })

        # If no today data, get most recent from DB
        if not indices:
            idx_stmt2 = select(IndexDailyPrice, Index).join(Index).order_by(
                desc(IndexDailyPrice.trade_date)
            ).limit(10)
            idx_result2 = await self.db.execute(idx_stmt2)
            for dp, idx in idx_result2.all():
                indices.append({
                    "code": idx.code, "name": idx.name, "market": idx.market,
                    "close": _to_float(dp.close), "change_pct": _to_float(dp.change_pct),
                })

        # Fallback: fetch live from Sina API (async, no blocking)
        if not indices:
            try:
                import httpx, re
                async with httpx.AsyncClient(timeout=8) as client:
                    resp = await client.get("http://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000300",
                        headers={"Referer": "https://finance.sina.com.cn"})
                if resp.status_code == 200:
                    for line in resp.text.strip().split("\n"):
                        parts = line.split('"')[1].split(",") if '"' in line else []
                        if len(parts) < 4: continue
                        name = parts[0]
                        close = float(parts[1]) if parts[1] else None
                        prev = float(parts[2]) if parts[2] else None
                        change_pct = round((close/prev-1)*100, 2) if close and prev else None
                        code_map = {"上证指数":"000001","深证成指":"399001","创业板指":"399006","沪深300":"000300"}
                        code = code_map.get(name, name)
                        indices.append({"code":code, "name":name, "market":"A", "close":close, "change_pct":change_pct})
            except Exception as e:
                logger.warning(f"Sina index fetch failed: {e}")

        # Last resort: hardcoded placeholder
        if not indices:
            indices = [
                {"code": "000001", "name": "上证指数", "market": "A", "close": None, "change_pct": None},
                {"code": "399001", "name": "深证成指", "market": "A", "close": None, "change_pct": None},
                {"code": "000300", "name": "沪深300", "market": "A", "close": None, "change_pct": None},
            ]

        # Latest news sentiment stats
        from app.models.news import NewsArticle
        from sqlalchemy import func as sqlfunc
        sent_stmt = select(NewsArticle.sentiment, sqlfunc.count()).group_by(NewsArticle.sentiment)
        sent_result = await self.db.execute(sent_stmt)
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for s, c in sent_result.all():
            if s in sentiment_counts:
                sentiment_counts[s] = c

        # Latest sectors
        sector_stmt = select(SectorPerformance).order_by(
            desc(SectorPerformance.trade_date)
        ).limit(6)
        sector_result = await self.db.execute(sector_stmt)
        sectors = [{
            "name": s.sector_name,
            "change_pct": _to_float(s.change_pct),
            "net_inflow": _to_float(s.net_inflow),
        } for s in sector_result.scalars().all()]

        # Market direction from index performance
        up_count = sum(1 for i in indices if (i["change_pct"] or 0) > 0)
        down_count = sum(1 for i in indices if (i["change_pct"] or 0) < 0)
        direction = "强势" if up_count >= 4 else "偏强" if up_count > down_count else "偏弱" if down_count > up_count else "震荡"

        # Generate advice based on direction
        advice_map = {
            "强势": "市场情绪积极，持仓者可继续持有但不宜追高。定投按计划执行。",
            "偏强": "市场稳步向好，逢回调可适当加仓优质基金。",
            "震荡": "市场方向不明，建议保持仓位灵活，等待趋势明朗。",
            "偏弱": "市场承压，定投者可逢低积累份额，不必恐慌。",
        }
        advice = advice_map.get(direction, "按原计划执行定投，保持耐心。")

        result = {
            "date": today.strftime("%m月%d日"),
            "weekday": ["一","二","三","四","五","六","日"][today.weekday()],
            "indices": indices[:6],
            "sectors": sectors,
            "sentiment": sentiment_counts,
            "direction": direction,
            "advice": advice,
            "hot_news_count": sum(sentiment_counts.values()),
        }
        await cache_set("market:summary", result, ttl=60)
        return result

    async def get_portfolio_summary(self, funds: list) -> dict:
        """Rich portfolio analysis: real NAV + news + market context + AI advice."""
        import httpx, json, re, asyncio

        holdings = []
        type_dist = {}
        fund_codes = []

        # Step 1: Fetch real-time data for each fund
        for item in funds:
            code = str(item.get("code", "")).strip()
            amount = float(item.get("amount", 0))
            if not code or len(code) != 6 or amount <= 0:
                continue
            fund_codes.append(code)

            info = {"code": code, "amount": amount}
            # TianTian real-time quote
            try:
                async with httpx.AsyncClient(timeout=6) as client:
                    resp = await client.get(f"http://fundgz.1234567.com.cn/js/{code}.js")
                    if resp.status_code == 200:
                        m = re.search(r'jsonpgz\((.+)\)', resp.text)
                        if m:
                            d = json.loads(m.group(1))
                            info["name"] = d.get("name", "")
                            info["nav"] = float(d.get("dwjz", 0)) if d.get("dwjz") else None
                            info["est_return"] = float(d.get("gszzl", 0)) if d.get("gszzl") else None
                            info["nav_date"] = d.get("jzrq", "")
            except Exception:
                pass

            # Classification + performance from DB
            stmt = select(Fund).where(Fund.code == code)
            r = await self.db.execute(stmt)
            fund = r.scalar_one_or_none()
            if fund:
                info["type"] = fund.fund_type or "混合型"
                type_dist[info["type"]] = type_dist.get(info["type"], 0) + amount
            else:
                info["type"] = "混合型"
                type_dist["混合型"] = type_dist.get("混合型", 0) + amount

            holdings.append(info)

        if not holdings or not fund_codes:
            return {"error": "请提供有效的基金代码和金额", "holdings": [], "allocation": [], "advice": []}

        total_amount = sum(h["amount"] for h in holdings)

        # Step 2: Get market context
        market_ctx = ""
        try:
            mkt = await cache_get("market:summary")
            if mkt:
                market_ctx = f"当前市场{mkt.get('direction','震荡')}，{mkt.get('advice','')[:80]}"
        except Exception:
            market_ctx = "市场数据暂不可用"

        # Step 3: Find relevant recent news for these funds
        from app.models.news import NewsArticle
        relevant_news = []
        for code in fund_codes[:5]:
            stmt = select(Fund).where(Fund.code == code)
            r = await self.db.execute(stmt)
            f = r.scalar_one_or_none()
            if f:
                kw = f.name[:4] if f.name else code
                news_stmt = select(NewsArticle).where(
                    or_(NewsArticle.title.ilike(f"%{kw}%"), NewsArticle.title.ilike(f"%{f.fund_type}%"))
                ).order_by(desc(NewsArticle.published_at)).limit(3)
                nr = await self.db.execute(news_stmt)
                for n in nr.scalars().all():
                    relevant_news.append({
                        "fund_code": code,
                        "title": n.title[:100],
                        "sentiment": n.sentiment or "",
                        "date": n.published_at.strftime("%m-%d") if n.published_at else "",
                    })
        relevant_news = relevant_news[:10]

        # Step 4: Allocation + risk
        allocation = [{"type": t, "ratio": round(amt/total_amount*100, 1)} for t, amt in type_dist.items()]
        scores = {"股票型":8,"混合型":6,"指数型":5,"ETF":5,"债券型":2,"货币型":1,"QDII":7}
        risk_score = round(sum(scores.get(h.get("type",""),5)*h["amount"]/total_amount for h in holdings), 1)
        risk_level = "高" if risk_score>7 else "中高" if risk_score>5 else "中" if risk_score>3 else "低"

        # Step 5: Generate grounded advice (no AI hallucination — based on real data)
        advice = []
        # Diversification check
        type_count = len(type_dist)
        if type_count == 1:
            advice.append({"level":"warning","text":f"⚠️ 你的{len(holdings)}只基金全部属于同一类型（{list(type_dist.keys())[0]}），一旦该类型回调，整个组合都会受冲击。建议增加1-2只不同类型基金分散风险。"})
        elif type_count >= 3:
            advice.append({"level":"good","text":f"✅ 配置了{type_count}种不同类型的基金，分散度较好。不同类型在市场不同阶段表现各异，可以平滑波动。"})

        # Risk check
        if risk_level in ("高","中高"):
            advice.append({"level":"warning","text":f"⚡ 组合风险等级为「{risk_level}」（评分{risk_score}）。如果这是你的主要资金，建议增加债券或货币基金（占比20-30%）做安全垫，降低整体波动。"})

        # Fund count check
        if len(holdings) == 1:
            advice.append({"level":"warning","text":"📌 只持有1只基金风险集中。即使是最优秀的基金经理也会有回撤期，建议至少配置3-5只不同类型基金。"})
        elif len(holdings) > 8:
            advice.append({"level":"info","text":"💡 持有超过8只基金，注意是否有重复配置。不同基金可能持有相似的股票，看似分散实则集中。"})

        # Market-aware advice
        if market_ctx:
            advice.append({"level":"info","text":f"📊 市场背景：{market_ctx}"})

        # Specific fund advice based on real data
        for h in holdings:
            if h.get("est_return") is not None and abs(h["est_return"]) > 1:
                direction = "涨" if h["est_return"] > 0 else "跌"
                advice.append({"level":"info","text":f"📈 {h.get('name',h['code'])} 今日{direction}{abs(h['est_return']):.2f}%，净值{h.get('nav','?')}。短期波动属于正常现象，不建议因单日涨跌调整仓位。"})

        return {
            "holdings": holdings,
            "total_amount": round(total_amount, 2),
            "allocation": allocation,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "advice": advice,
            "relevant_news": relevant_news,
            "fund_count": len(holdings),
            "market_context": market_ctx,
        }

    # ─── Funds ──────────────────────────────────────────

    async def get_fund_detail(self, code: str) -> Optional[dict]:
        """Get comprehensive fund detail with NAV history + real-time data."""
        import asyncio

        stmt = select(Fund).where(Fund.code == code)
        result = await self.db.execute(stmt)
        fund = result.scalar_one_or_none()

        # Auto-fetch if not in DB
        if not fund:
            fund = await self._fetch_and_save_fund(code)
        if not fund:
            return None

        # Get NAV history from DB
        nav_stmt = select(FundNAV).where(
            FundNAV.fund_id == fund.id
        ).order_by(FundNAV.nav_date.desc()).limit(120)
        nav_result = await self.db.execute(nav_stmt)
        navs = list(nav_result.scalars().all())

        # If no NAV data, try to fetch it now
        if not navs:
            try:
                from app.crawlers.a_fund import FundCrawler
                crawler = FundCrawler(self.db)
                await crawler.fetch_fund_nav()
                nav_result2 = await self.db.execute(nav_stmt)
                navs = list(nav_result2.scalars().all())
            except Exception as e:
                logger.warning(f"Failed to fetch NAV for {code}: {e}")

        navs_sorted = list(reversed(navs))  # oldest first
        latest_nav = _to_float(navs_sorted[-1].unit_nav) if navs_sorted else None

        # Calculate performance
        def calc_return(days: int) -> Optional[float]:
            if len(navs_sorted) < max(2, days):
                return None
            idx = max(0, len(navs_sorted) - 1 - min(days, len(navs_sorted) - 1))
            old_nav = _to_float(navs_sorted[idx].unit_nav)
            new_nav = _to_float(navs_sorted[-1].unit_nav)
            if old_nav and new_nav and old_nav > 0:
                return round(((new_nav / old_nav) - 1) * 100, 2)
            return None

        returns = {
            "d1": _to_float(navs_sorted[-1].daily_return) if navs_sorted else None,
            "w1": calc_return(5),
            "m1": calc_return(22),
            "m3": calc_return(66),
            "m6": calc_return(132),
            "y1": calc_return(260),
            "y3": calc_return(780) if len(navs_sorted) > 260 else None,
            "ytd": calc_return(260),
        }

        # Annual returns (approximate: group by year buckets)
        nav_values = [(_to_float(n.unit_nav), n.nav_date) for n in navs_sorted if _to_float(n.unit_nav)]
        annual_returns = []
        if len(nav_values) > 260:
            for yr_offset in range(3):  # last 3 years
                year = date.today().year - yr_offset
                yearly = [(v, d) for v, d in nav_values if d and d.year == year]
                if len(yearly) >= 2:
                    y0, y1 = yearly[0][0], yearly[-1][0]
                    if y0 > 0:
                        annual_returns.append({"year": year, "return": round(((y1/y0)-1)*100, 2)})
        annual_returns.reverse()

        # Max drawdown
        max_dd = 0.0
        if len(nav_values) > 20:
            peak = nav_values[0][0]
            for v, _ in nav_values:
                if v > peak: peak = v
                dd = (v - peak) / peak * 100 if peak > 0 else 0
                if dd < max_dd: max_dd = dd
            max_dd = round(max_dd, 2)

        # Annualized volatility (from daily returns)
        vol = None
        daily_rets = [_to_float(n.daily_return) for n in navs_sorted[-260:] if _to_float(n.daily_return) is not None]
        if len(daily_rets) > 60:
            mean_r = sum(daily_rets) / len(daily_rets)
            variance = sum((r - mean_r)**2 for r in daily_rets) / (len(daily_rets) - 1)
            vol = round((variance ** 0.5) * (252 ** 0.5), 2)  # Annualize

        # Sharpe ratio (assuming risk-free rate ~2%)
        sharpe = None
        if vol and vol > 0:
            avg_return = sum(daily_rets) / len(daily_rets) * 252
            sharpe = round((avg_return - 2.0) / vol, 2)

        # Get real-time quote from TianTian
        rt_quote = None
        try:
            import httpx, json, re
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.get(url)
            if resp.status_code == 200:
                match = re.search(r'jsonpgz\((.+)\)', resp.text)
                if match:
                    rt_quote = json.loads(match.group(1))
        except Exception:
            pass

        latest_return = returns.get("d1")
        estimated_nav = rt_quote.get("gsz") if rt_quote else None
        estimated_return = float(rt_quote.get("gszzl", 0)) if rt_quote and rt_quote.get("gszzl") else None
        nav_date = rt_quote.get("jzrq") if rt_quote else None

        # Risk assessment based on computed volatility + drawdown
        risk_level = "中"
        if vol is not None:
            if vol >= 25: risk_level = "高"
            elif vol >= 18: risk_level = "中高"
            elif vol >= 13: risk_level = "中"
            elif vol >= 8: risk_level = "中低"
            else: risk_level = "低"
        elif max_dd is not None:
            if max_dd <= -20: risk_level = "中高"
            elif max_dd <= -10: risk_level = "中"
            else: risk_level = "中低"

        return {
            "info": {
                "code": fund.code,
                "name": fund.name,
                "fund_type": fund.fund_type or "混合型",
                "company": fund.company or "",
                "inception_date": fund.inception_date.isoformat() if fund.inception_date else None,
                "aum": _to_float(fund.aum),
                "latest_nav": estimated_nav or latest_nav,
                "nav_date": nav_date,
                "latest_return": estimated_return or latest_return,
                "risk_level": risk_level,
            },
            "performance": {
                **returns,
                "max_drawdown": max_dd,
                "volatility": vol,
                "sharpe": sharpe,
                "annual_returns": annual_returns,
            },
            "nav_history": [{
                "date": n.nav_date.isoformat() if n.nav_date else None,
                "unit_nav": _to_float(n.unit_nav),
                "acc_nav": _to_float(n.acc_nav),
                "daily_return": _to_float(n.daily_return),
            } for n in navs_sorted[-90:]],  # last 90 days
        }

    # ─── Sectors & Capital Flow ─────────────────────────

    async def get_sectors(self) -> list[dict]:
        """Get latest sector performance data."""
        cached = await cache_get("market:sectors:latest")
        if cached:
            return cached

        # Get most recent date
        max_date_stmt = select(func.max(SectorPerformance.trade_date))
        result = await self.db.execute(max_date_stmt)
        max_date = result.scalar()

        if not max_date:
            return []

        stmt = select(SectorPerformance).where(
            SectorPerformance.trade_date == max_date
        ).order_by(SectorPerformance.change_pct.desc())
        result = await self.db.execute(stmt)
        sectors = result.scalars().all()

        output = [{
            "sector_name": s.sector_name,
            "change_pct": _to_float(s.change_pct),
            "net_inflow": _to_float(s.net_inflow),
            "top_stock": s.top_stock,
            "top_stock_pct": _to_float(s.top_stock_pct),
        } for s in sectors]

        await cache_set("market:sectors:latest", output, ttl=300)
        return output

    async def get_capital_flow(self, days: int = 30) -> dict:
        """Get north/south bound capital flow."""
        cached = await cache_get(f"market:capital_flow:{days}d")
        if cached:
            return cached

        cutoff = date.today() - timedelta(days=days)
        stmt = select(CapitalFlow).where(
            CapitalFlow.trade_date >= cutoff
        ).order_by(CapitalFlow.trade_date.asc())
        result = await self.db.execute(stmt)
        flows = result.scalars().all()

        north = [{"date": f.trade_date.isoformat(), "net_inflow": _to_float(f.net_inflow), "balance": _to_float(f.balance)}
                 for f in flows if f.flow_type == "north"]
        south = [{"date": f.trade_date.isoformat(), "net_inflow": _to_float(f.net_inflow), "balance": _to_float(f.balance)}
                 for f in flows if f.flow_type == "south"]

        output = {"north": north, "south": south}
        await cache_set(f"market:capital_flow:{days}d", output, ttl=300)
        return output

    async def get_market_breadth(self) -> dict:
        """Get market breadth (advance/decline stats)."""
        # For MVP, return placeholder; real data comes from AKShare spot crawler
        today = date.today()
        stmt = select(StockDailyPrice).where(StockDailyPrice.trade_date == today)
        result = await self.db.execute(stmt)
        prices = result.scalars().all()

        up = down = flat = 0
        total_amount = 0
        for p in prices:
            if p.change_pct is None:
                flat += 1
            elif p.change_pct > 0:
                up += 1
            elif p.change_pct < 0:
                down += 1
            else:
                flat += 1
            if p.amount:
                total_amount += float(p.amount)

        return {
            "up_count": up, "down_count": down, "flat_count": flat,
            "limit_up": 0, "limit_down": 0,  # Needs separate data source
            "total_amount": total_amount,
        }

    # ─── Screener ───────────────────────────────────────

    async def screen_stocks(self, market: str = "A", pe_min: Optional[float] = None,
                            pe_max: Optional[float] = None, pb_min: Optional[float] = None,
                            pb_max: Optional[float] = None, roe_min: Optional[float] = None,
                            sector: Optional[str] = None, sort: str = "pe",
                            order: str = "asc", page: int = 1, size: int = 20) -> dict:
        """Screen stocks by fundamental criteria."""
        # Get latest price for each stock
        subquery = (
            select(
                StockDailyPrice.stock_id,
                StockDailyPrice.close,
                StockDailyPrice.pe_ratio,
                StockDailyPrice.pb_ratio,
                StockDailyPrice.change_pct,
                StockDailyPrice.total_mv,
                func.row_number()
                .over(partition_by=StockDailyPrice.stock_id, order_by=desc(StockDailyPrice.trade_date))
                .label("rn"),
            ).subquery()
        )

        query = (
            select(Stock, subquery.c.close, subquery.c.pe_ratio, subquery.c.pb_ratio,
                   subquery.c.change_pct, subquery.c.total_mv)
            .join(subquery, and_(Stock.id == subquery.c.stock_id, subquery.c.rn == 1))
            .where(Stock.market == market)
        )

        if pe_min is not None:
            query = query.where(subquery.c.pe_ratio >= pe_min)
        if pe_max is not None:
            query = query.where(subquery.c.pe_ratio <= pe_max)
        if pb_min is not None:
            query = query.where(subquery.c.pb_ratio >= pb_min)
        if pb_max is not None:
            query = query.where(subquery.c.pb_ratio <= pb_max)
        if sector:
            query = query.where(Stock.sector == sector)

        # Sort
        sort_col = {"pe": subquery.c.pe_ratio, "pb": subquery.c.pb_ratio, "mv": subquery.c.total_mv}.get(sort, subquery.c.pe_ratio)
        query = query.order_by(sort_col.asc() if order == "asc" else sort_col.desc())

        # Pagination
        total = await self.db.scalar(select(func.count()).select_from(query.subquery()))
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        rows = result.all()

        items = [{
            "code": row[0].code, "name": row[0].name, "market": row[0].market,
            "sector": row[0].sector, "latest_price": _to_float(row[1]),
            "pe_ratio": _to_float(row[2]), "pb_ratio": _to_float(row[3]),
            "change_pct": _to_float(row[4]), "total_mv": _to_float(row[5]),
        } for row in rows]

        return {"items": items, "total": total or 0, "page": page, "size": size}
