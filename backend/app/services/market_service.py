"""Market data service layer — database queries with caching."""
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
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
            fund_info = await asyncio.to_thread(self._fetch_fund_from_akshare, code)
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
        """Use AKShare to get basic fund info by code. Tries multiple sources."""
        import akshare as ak
        import logging
        log = logging.getLogger(__name__)

        # Method 1: East Money fund info (most reliable, covers all public funds)
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if df is not None and not df.empty:
                name = str(df.iloc[0].get("基金简称", ""))
                if name:
                    log.info(f"Fund {code} found via East Money: {name}")
                    return {"name": name[:100], "fund_type": "mixed", "company": ""}
            else:
                log.warning(f"Fund {code}: East Money returned empty")
        except Exception as e:
            log.warning(f"Fund {code}: East Money failed — {e}")

        # Method 2: ETF fund info (for ETF/ETF-feeder funds)
        try:
            df = ak.fund_etf_fund_info_em(fund=code)
            if df is not None and not df.empty:
                name = str(df.iloc[0].get("基金简称", ""))
                if name:
                    log.info(f"Fund {code} found via ETF info: {name}")
                    return {"name": name[:100], "fund_type": "指数型", "company": ""}
        except Exception as e:
            log.warning(f"Fund {code}: ETF info failed — {e}")

        # Method 3: Xueqiu individual fund info
        try:
            info = ak.fund_individual_basic_info_xq(symbol=code)
            if info is not None and not info.empty:
                row = info.iloc[0]
                name = str(row.get("基金全称", row.get("基金简称", "")))
                if name:
                    log.info(f"Fund {code} found via Xueqiu: {name}")
                    return {
                        "name": name[:100],
                        "fund_type": str(row.get("基金类型", "mixed"))[:30],
                        "company": str(row.get("基金管理人", ""))[:100],
                    }
        except Exception as e:
            log.warning(f"Fund {code}: Xueqiu failed — {e}")

        # Method 4: Direct TianTian fund API (no AKShare dependency)
        try:
            import httpx, json, re
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            resp = httpx.get(url, timeout=(5, 10))
            if resp.status_code == 200:
                # Parse JSONP: jsonpgz({...});
                match = re.search(r'jsonpgz\((.+)\)', resp.text)
                if match:
                    data = json.loads(match.group(1))
                    name = data.get("name", "")
                    if name:
                        log.info(f"Fund {code} found via TianTian: {name}")
                        return {"name": name[:100], "fund_type": "混合型", "company": ""}
        except Exception as e:
            log.warning(f"Fund {code}: TianTian API failed — {e}")

        log.error(f"Fund {code}: ALL sources failed")
        return None

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
            "ytd": calc_return(260),  # approximate
        }

        # Get real-time quote from TianTian
        rt_quote = None
        try:
            import httpx, json, re
            url = f"http://fundgz.1234567.com.cn/js/{code}.js"
            resp = httpx.get(url, timeout=(3, 8))
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

        # Basic risk assessment based on returns
        risk_level = "中"
        if returns.get("m3") is not None:
            v = abs(returns["m3"])
            if v > 20: risk_level = "高"
            elif v > 10: risk_level = "中高"
            elif v < 3: risk_level = "低"
            elif v < 6: risk_level = "中低"

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
            "performance": returns,
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
