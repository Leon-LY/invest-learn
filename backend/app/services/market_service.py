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
        """Search stocks AND funds by code or name."""
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

        # Search funds
        from app.models.market import Fund
        fund_stmt = select(Fund).where(
            or_(
                Fund.code.ilike(f"%{q}%"),
                Fund.name.ilike(f"%{q}%"),
            )
        ).limit(limit - len(results))
        fr = await self.db.execute(fund_stmt)
        for f in fr.scalars().all():
            results.append({
                "code": f.code, "name": f.name, "market": "CN",
                "security_type": "fund", "match_score": 1.0,
            })

        return results[:limit]

    # ─── Funds ──────────────────────────────────────────

    async def get_fund_detail(self, code: str) -> Optional[dict]:
        """Get fund detail with NAV history."""
        stmt = select(Fund).where(Fund.code == code)
        result = await self.db.execute(stmt)
        fund = result.scalar_one_or_none()
        if not fund:
            return None

        nav_stmt = select(FundNAV).where(
            FundNAV.fund_id == fund.id
        ).order_by(FundNAV.nav_date.desc()).limit(90)
        nav_result = await self.db.execute(nav_stmt)
        navs = nav_result.scalars().all()

        latest_nav = _to_float(navs[0].unit_nav) if navs else None
        latest_return = _to_float(navs[0].daily_return) if navs else None

        return {
            "info": {
                "code": fund.code, "name": fund.name, "fund_type": fund.fund_type,
                "company": fund.company, "inception_date": fund.inception_date.isoformat() if fund.inception_date else None,
                "aum": _to_float(fund.aum), "latest_nav": latest_nav, "latest_return": latest_return,
            },
            "nav_history": [{
                "date": n.nav_date.isoformat() if n.nav_date else None,
                "unit_nav": _to_float(n.unit_nav),
                "acc_nav": _to_float(n.acc_nav),
                "daily_return": _to_float(n.daily_return),
            } for n in reversed(navs)],
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
