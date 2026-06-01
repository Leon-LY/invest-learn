"""
Fund & ETF data crawler using AKShare.
Fetches fund NAV history and ETF real-time data.
"""
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseCrawler, retry_on_failure
from app.models.market import Fund, FundNAV, Stock

logger = logging.getLogger(__name__)

# Popular funds to track
POPULAR_FUNDS = [
    ("000001", "华夏成长混合"),
    ("110022", "易方达消费行业"),
    ("161725", "招商中证白酒"),
    ("005827", "易方达蓝筹精选混合"),
    ("163406", "兴全合润混合"),
    ("320007", "诺安成长混合"),
    ("001475", "易方达国防军工混合"),
    ("002939", "广发创新升级混合"),
    ("519674", "银河创新成长混合"),
    ("007119", "睿远成长价值混合A"),
]


class FundCrawler(BaseCrawler):
    """Crawler for fund NAV history via AKShare."""
    source_name = "akshare_fund"

    async def run(self) -> dict:
        result = {"funds_synced": 0, "nav_records": 0}
        try:
            result["funds_synced"] = await self.sync_fund_list()
        except Exception as e:
            logger.error(f"Fund list sync failed: {e}")
        try:
            result["nav_records"] = await self.fetch_fund_nav()
        except Exception as e:
            logger.error(f"Fund NAV fetch failed: {e}")
        return result

    async def sync_fund_list(self) -> int:
        """Sync popular fund list."""
        count = 0
        for code, name in POPULAR_FUNDS:
            stmt = select(Fund).where(Fund.code == code)
            result = await self.db.execute(stmt)
            fund = result.scalar_one_or_none()
            if fund is None:
                fund = Fund(code=code, name=name, fund_type="mixed", is_active=True)
                self.db.add(fund)
                count += 1
        if count > 0:
            await self.db.commit()
        logger.info(f"Synced {count} new funds")
        return count

    @retry_on_failure(max_retries=2, delay=3.0)
    async def fetch_fund_nav(self) -> int:
        """Fetch recent NAV history for tracked funds."""
        import akshare as ak
        total = 0
        stmt = select(Fund).where(Fund.is_active == True)
        result = await self.db.execute(stmt)
        funds = result.scalars().all()
        for fund in funds:
            try:
                df = ak.fund_open_fund_info_em(symbol=fund.code, indicator="单位净值走势")
                if df.empty:
                    continue
                for _, row in df.tail(90).iterrows():
                    nav_date = row.get("净值日期")
                    if nav_date is None:
                        continue
                    if isinstance(nav_date, str):
                        nav_date = datetime.strptime(nav_date, "%Y-%m-%d").date()
                    stmt2 = select(FundNAV).where(
                        FundNAV.fund_id == fund.id,
                        FundNAV.nav_date == nav_date,
                    )
                    r2 = await self.db.execute(stmt2)
                    existing = r2.scalar_one_or_none()
                    if existing is None:
                        existing = FundNAV(fund_id=fund.id, nav_date=nav_date)
                        self.db.add(existing)
                    existing.unit_nav = self.safe_decimal(row.get("单位净值"))
                    existing.acc_nav = self.safe_decimal(row.get("累计净值"))
                    existing.daily_return = self.safe_decimal(row.get("日增长率"))
                    total += 1
                await self.db.commit()
            except Exception as e:
                logger.warning(f"Failed to fetch NAV for {fund.code} {fund.name}: {e}")
                await self.db.rollback()
        logger.info(f"Saved {total} fund NAV records")
        return total

    @staticmethod
    def safe_decimal(val, default=None):
        if val is None:
            return default
        try:
            return Decimal(str(val))
        except Exception:
            return default


class ETFCrawler(BaseCrawler):
    """Crawler for ETF real-time data via AKShare."""
    source_name = "akshare_etf"

    async def run(self) -> dict:
        if not self.is_trading_day():
            return {"status": "skipped", "reason": "not a trading day"}
        import akshare as ak
        try:
            df = ak.fund_etf_spot_em()
            count = 0
            for _, row in df.iterrows():
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))
                if not code or not name:
                    continue
                stmt = select(Stock).where(Stock.code == code)
                result = await self.db.execute(stmt)
                stock = result.scalar_one_or_none()
                if stock is None:
                    stock = Stock(code=code, name=name, market="A", security_type="etf")
                    self.db.add(stock)
                    count += 1
            if count > 0:
                await self.db.commit()
            return count
        except Exception as e:
            logger.error(f"ETF sync failed: {e}")
            await self.db.rollback()
            raise
