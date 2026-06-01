"""
Global stock & index data crawler using yfinance.
Fetches US and HK stock data, plus global indices (S&P 500, NASDAQ, etc.).
"""
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseCrawler, retry_on_failure
from app.models.market import Stock, StockDailyPrice, Index, IndexDailyPrice

logger = logging.getLogger(__name__)

# Key global indices
GLOBAL_INDICES = [
    {"code": "^GSPC", "name": "S&P 500", "market": "US", "country": "US"},
    {"code": "^IXIC", "name": "NASDAQ", "market": "US", "country": "US"},
    {"code": "^DJI", "name": "道琼斯工业", "market": "US", "country": "US"},
    {"code": "^HSI", "name": "恒生指数", "market": "HK", "country": "HK"},
    {"code": "^HSCEI", "name": "国企指数", "market": "HK", "country": "HK"},
    {"code": "^N225", "name": "日经225", "market": "JP", "country": "JP"},
]

# Popular US stocks to track
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
    ("JNJ", "Johnson & Johnson", "Healthcare"),
    ("WMT", "Walmart Inc.", "Consumer Defensive"),
    ("PG", "Procter & Gamble", "Consumer Defensive"),
    ("XOM", "Exxon Mobil", "Energy"),
    ("UNH", "UnitedHealth Group", "Healthcare"),
]

POPULAR_HK_STOCKS = [
    ("0700", "腾讯控股", "Technology"),
    ("9988", "阿里巴巴-SW", "Technology"),
    ("3690", "美团-W", "Technology"),
    ("9618", "京东集团-SW", "Technology"),
    ("1810", "小米集团-W", "Technology"),
    ("2318", "中国平安", "Financial"),
    ("0388", "香港交易所", "Financial"),
    ("0939", "建设银行", "Financial"),
    ("1398", "工商银行", "Financial"),
    ("2269", "药明生物", "Healthcare"),
]


class GlobalStockCrawler(BaseCrawler):
    """Crawler for global (US + HK) stock data via yfinance."""
    source_name = "yfinance_global"

    async def run(self) -> dict:
        result = {"us_tracked": 0, "hk_tracked": 0, "indices_synced": 0}
        try:
            result["us_tracked"] = await self.sync_us_stocks()
        except Exception as e:
            logger.error(f"US stock sync failed: {e}")
        try:
            result["hk_tracked"] = await self.sync_hk_stocks()
        except Exception as e:
            logger.error(f"HK stock sync failed: {e}")
        try:
            result["indices_synced"] = await self.sync_global_indices()
        except Exception as e:
            logger.error(f"Global indices sync failed: {e}")
        return result

    async def sync_us_stocks(self) -> int:
        """Sync popular US stocks and their historical data."""
        import yfinance as yf
        count = 0
        for symbol, name, sector in POPULAR_US_STOCKS:
            stmt = select(Stock).where(Stock.code == symbol)
            result = await self.db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock is None:
                stock = Stock(code=symbol, name=name, market="US", security_type="stock", sector=sector)
                self.db.add(stock)
                await self.db.flush()
                count += 1
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                saved = await self._save_yf_history(stock.id, hist)
                logger.debug(f"  {symbol}: saved {saved} records")
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
        await self.db.commit()
        logger.info(f"Synced {count} new US stocks")
        return count

    async def sync_hk_stocks(self) -> int:
        """Sync popular HK stocks."""
        import yfinance as yf
        count = 0
        for code, name, sector in POPULAR_HK_STOCKS:
            symbol = f"{code}.HK"
            stmt = select(Stock).where(Stock.code == symbol)
            result = await self.db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock is None:
                stock = Stock(code=symbol, name=name, market="HK", security_type="stock", sector=sector)
                self.db.add(stock)
                await self.db.flush()
                count += 1
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1y")
                saved = await self._save_yf_history(stock.id, hist)
                logger.debug(f"  {symbol}: saved {saved} records")
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")
        await self.db.commit()
        logger.info(f"Synced {count} new HK stocks")
        return count

    async def sync_global_indices(self) -> int:
        """Sync global index daily prices."""
        import yfinance as yf
        count = 0
        for idx_info in GLOBAL_INDICES:
            stmt = select(Index).where(Index.code == idx_info["code"])
            result = await self.db.execute(stmt)
            idx = result.scalar_one_or_none()
            if idx is None:
                idx = Index(**idx_info)
                self.db.add(idx)
                await self.db.flush()
            try:
                ticker = yf.Ticker(idx_info["code"])
                hist = ticker.history(period="3mo")
                for dt, row in hist.iterrows():
                    trade_date = dt.date() if hasattr(dt, 'date') else dt
                    stmt2 = select(IndexDailyPrice).where(
                        IndexDailyPrice.index_id == idx.id,
                        IndexDailyPrice.trade_date == trade_date,
                    )
                    r2 = await self.db.execute(stmt2)
                    existing = r2.scalar_one_or_none()
                    if existing is None:
                        existing = IndexDailyPrice(index_id=idx.id, trade_date=trade_date)
                        self.db.add(existing)
                    existing.open = self.safe_decimal(row.get("Open"))
                    existing.high = self.safe_decimal(row.get("High"))
                    existing.low = self.safe_decimal(row.get("Low"))
                    existing.close = self.safe_decimal(row.get("Close"))
                    existing.volume = self.safe_int(row.get("Volume"))
                    count += 1
                await self.db.commit()
            except Exception as e:
                logger.warning(f"Failed to fetch index {idx_info['name']}: {e}")
                await self.db.rollback()
        logger.info(f"Synced {count} global index records")
        return count

    async def _save_yf_history(self, stock_id: int, hist) -> int:
        """Save yfinance history DataFrame to stock_daily_prices."""
        saved = 0
        for dt, row in hist.iterrows():
            trade_date = dt.date() if hasattr(dt, 'date') else dt
            stmt = select(StockDailyPrice).where(
                StockDailyPrice.stock_id == stock_id,
                StockDailyPrice.trade_date == trade_date,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing is None:
                existing = StockDailyPrice(stock_id=stock_id, trade_date=trade_date)
                self.db.add(existing)
            existing.open = self.safe_decimal(row.get("Open"))
            existing.high = self.safe_decimal(row.get("High"))
            existing.low = self.safe_decimal(row.get("Low"))
            existing.close = self.safe_decimal(row.get("Close"))
            existing.volume = self.safe_int(row.get("Volume"))
            saved += 1
        await self.db.flush()
        return saved

    @staticmethod
    def safe_decimal(val, default=None):
        if val is None:
            return default
        try:
            return Decimal(str(round(float(val), 4)))
        except Exception:
            return default
