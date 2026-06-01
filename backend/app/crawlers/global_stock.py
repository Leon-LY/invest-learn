"""
Global stock & index data crawler using AKShare (primary) with yfinance fallback.
AKShare is accessible from China; yfinance is blocked by GFW.
"""
import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseCrawler, retry_on_failure
from app.models.market import Stock, StockDailyPrice, Index, IndexDailyPrice
from app.core.config import settings

logger = logging.getLogger(__name__)

# Key global indices — AKShare codes where available, yfinance as fallback
GLOBAL_INDICES = [
    {"code": ".INX",  "name": "S&P 500",      "market": "US", "country": "US", "ak_code": "S&P 500"},
    {"code": ".IXIC", "name": "NASDAQ",        "market": "US", "country": "US", "ak_code": "纳斯达克"},
    {"code": ".DJI",  "name": "道琼斯工业",     "market": "US", "country": "US", "ak_code": "道琼斯"},
    {"code": "HSI",   "name": "恒生指数",       "market": "HK", "country": "HK", "ak_code": "恒生指数"},
    {"code": "HSCEI", "name": "国企指数",       "market": "HK", "country": "HK", "ak_code": "国企指数"},
    {"code": "N225",  "name": "日经225",       "market": "JP", "country": "JP", "ak_code": "日经225"},
]

# Popular US stocks
POPULAR_US_STOCKS = [
    ("AAPL", "Apple Inc.", "Technology"),
    ("MSFT", "Microsoft Corp.", "Technology"),
    ("GOOGL", "Alphabet Inc.", "Technology"),
    ("AMZN", "Amazon.com", "Consumer Cyclical"),
    ("NVDA", "NVIDIA Corp.", "Technology"),
    ("META", "Meta Platforms", "Technology"),
    ("TSLA", "Tesla Inc.", "Automotive"),
    ("BRK-B", "Berkshire Hathaway", "Financial"),
    ("JPM", "JPMorgan Chase", "Financial"),
    ("V", "Visa Inc.", "Financial"),
]

POPULAR_HK_STOCKS = [
    ("00700", "腾讯控股", "Technology"),
    ("09988", "阿里巴巴-SW", "Technology"),
    ("03690", "美团-W", "Technology"),
    ("09618", "京东集团-SW", "Technology"),
    ("01810", "小米集团-W", "Technology"),
    ("02318", "中国平安", "Financial"),
    ("00388", "香港交易所", "Financial"),
]


class GlobalStockCrawler(BaseCrawler):
    """Crawler for global indices + US/HK stocks. AKShare-first, yfinance optional."""
    source_name = "global_stock"

    async def run(self) -> dict:
        BaseCrawler.setup_proxy()
        result = {"indices_synced": 0, "hk_tracked": 0, "us_tracked": 0}
        try:
            result["indices_synced"] = await self.sync_global_indices()
        except Exception as e:
            logger.error(f"Global indices sync failed: {e}")
        try:
            result["hk_tracked"] = await self.sync_hk_stocks()
        except Exception as e:
            logger.error(f"HK stock sync failed: {e}")
        try:
            result["us_tracked"] = await self.sync_us_stocks()
        except Exception as e:
            logger.error(f"US stock sync failed: {e}")
        return result

    @retry_on_failure(max_retries=2, delay=5.0)
    async def sync_global_indices(self) -> int:
        """Sync global indices using AKShare (no GFW issues)."""
        import akshare as ak
        count = 0

        # AKShare global index spot (covers S&P, NASDAQ, DJIA, Hang Seng, Nikkei, etc.)
        try:
            df = await asyncio.to_thread(ak.index_global_spot_em)
        except Exception as e:
            logger.warning(f"AKShare global indices failed: {e}, trying individual indices")
            df = None

        if df is not None and not df.empty:
            for _, row in df.iterrows():
                name = str(row.get("名称", ""))
                # Match against our watched list
                matched = next((i for i in GLOBAL_INDICES if i["ak_code"] in name or name in i["ak_code"]), None)
                if not matched:
                    continue
                code = matched["code"]
                # Upsert index
                stmt = select(Index).where(Index.code == code)
                result = await self.db.execute(stmt)
                idx = result.scalar_one_or_none()
                if idx is None:
                    idx = Index(code=code, name=matched["name"], market=matched["market"], country=matched["country"])
                    self.db.add(idx)
                    await self.db.flush()

                today = date.today()
                stmt2 = select(IndexDailyPrice).where(
                    IndexDailyPrice.index_id == idx.id,
                    IndexDailyPrice.trade_date == today,
                )
                r2 = await self.db.execute(stmt2)
                dp = r2.scalar_one_or_none()
                if dp is None:
                    dp = IndexDailyPrice(index_id=idx.id, trade_date=today)
                    self.db.add(dp)

                dp.close = self.safe_decimal(row.get("最新价"))
                dp.change_pct = self.safe_decimal(row.get("涨跌幅"))
                dp.open = self.safe_decimal(row.get("今开价"))
                dp.high = self.safe_decimal(row.get("最高价"))
                dp.low = self.safe_decimal(row.get("最低价"))
                count += 1

        await self.db.commit()
        logger.info(f"Synced {count} global index records")
        return count

    async def sync_hk_stocks(self) -> int:
        """Sync HK stocks using AKShare."""
        import akshare as ak
        count = 0
        try:
            df = await asyncio.to_thread(ak.stock_hk_spot_em)
        except Exception as e:
            logger.warning(f"AKShare HK spot failed: {e}")
            return 0

        for _, row in df.iterrows():
            code = str(row.get("代码", ""))
            matched = next((s for s in POPULAR_HK_STOCKS if s[0] == code), None)
            if not matched:
                continue
            _, name, sector = matched
            symbol = f"{code}.HK"
            stmt = select(Stock).where(Stock.code == symbol)
            result = await self.db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock is None:
                stock = Stock(code=symbol, name=name, market="HK", security_type="stock", sector=sector)
                self.db.add(stock)
                await self.db.flush()

            today = date.today()
            stmt2 = select(StockDailyPrice).where(
                StockDailyPrice.stock_id == stock.id,
                StockDailyPrice.trade_date == today,
            )
            r2 = await self.db.execute(stmt2)
            sp = r2.scalar_one_or_none()
            if sp is None:
                sp = StockDailyPrice(stock_id=stock.id, trade_date=today)
                self.db.add(sp)
            sp.close = self.safe_decimal(row.get("最新价"))
            sp.change_pct = self.safe_decimal(row.get("涨跌幅"))
            count += 1

        await self.db.commit()
        logger.info(f"Synced {count} HK stocks")
        return count

    async def sync_us_stocks(self) -> int:
        """Sync US stocks. Requires proxy or yfinance alternative (limited)."""
        # Try AKShare for US spot first
        import akshare as ak
        count = 0
        try:
            df = await asyncio.to_thread(ak.stock_us_spot_em)
        except Exception:
            logger.warning("AKShare US spot failed — US stocks unavailable without proxy")
            return 0

        for _, row in df.iterrows():
            code = str(row.get("代码", ""))
            matched = next((s for s in POPULAR_US_STOCKS if s[0] == code), None)
            if not matched:
                continue
            _, name, sector = matched
            stmt = select(Stock).where(Stock.code == code)
            result = await self.db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock is None:
                stock = Stock(code=code, name=name, market="US", security_type="stock", sector=sector)
                self.db.add(stock)
                await self.db.flush()

            today = date.today()
            stmt2 = select(StockDailyPrice).where(
                StockDailyPrice.stock_id == stock.id,
                StockDailyPrice.trade_date == today,
            )
            r2 = await self.db.execute(stmt2)
            sp = r2.scalar_one_or_none()
            if sp is None:
                sp = StockDailyPrice(stock_id=stock.id, trade_date=today)
                self.db.add(sp)
            sp.close = self.safe_decimal(row.get("最新价"))
            sp.change_pct = self.safe_decimal(row.get("涨跌幅"))
            count += 1

        await self.db.commit()
        logger.info(f"Synced {count} US stocks via AKShare")
        return count

    @staticmethod
    def safe_decimal(val, default=None):
        if val is None:
            return default
        try:
            return Decimal(str(round(float(val), 4)))
        except Exception:
            return default
