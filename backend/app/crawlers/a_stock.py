"""
A-share stock & index data crawler using AKShare.
Fetches stock list, daily K-line, and index data from East Money via AKShare.
"""
import logging
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select
import pandas as pd

from .base import BaseCrawler, retry_on_failure
from app.models.market import Stock, StockDailyPrice, Index, IndexDailyPrice

logger = logging.getLogger(__name__)

# Major A-share indices with AKShare codes
A_INDICES = [
    {"code": "000001", "name": "上证指数", "market": "A", "country": "CN"},
    {"code": "399001", "name": "深证成指", "market": "A", "country": "CN"},
    {"code": "399006", "name": "创业板指", "market": "A", "country": "CN"},
    {"code": "000688", "name": "科创50", "market": "A", "country": "CN"},
    {"code": "000300", "name": "沪深300", "market": "A", "country": "CN"},
    {"code": "000905", "name": "中证500", "market": "A", "country": "CN"},
]


class AStockCrawler(BaseCrawler):
    """Crawler for A-share stock list and daily K-line data via AKShare."""
    source_name = "akshare_a_stock"

    async def run(self) -> dict:
        """Run full A-share data crawl."""
        result = {"stocks_synced": 0, "prices_fetched": 0, "indices_synced": 0}
        try:
            result["stocks_synced"] = await self.sync_stock_list()
        except Exception as e:
            logger.error(f"Stock list sync failed: {e}")
        try:
            result["indices_synced"] = await self.sync_indices()
        except Exception as e:
            logger.error(f"Index sync failed: {e}")
        return result

    @retry_on_failure(max_retries=2, delay=5.0)
    async def sync_stock_list(self) -> int:
        """Sync popular A-share stocks (not all 5000+ — East Money blocks bulk requests)."""
        import akshare as ak

        # First try getting spot data for major indices components
        popular = [
            # 沪深300 核心蓝筹
            ("600519", "贵州茅台"), ("000858", "五粮液"), ("000568", "泸州老窖"),
            ("600036", "招商银行"), ("601318", "中国平安"), ("000333", "美的集团"),
            ("600276", "恒瑞医药"), ("000651", "格力电器"), ("600900", "长江电力"),
            ("002415", "海康威视"), ("300750", "宁德时代"), ("601012", "隆基绿能"),
            ("600030", "中信证券"), ("000002", "万科A"), ("002594", "比亚迪"),
            ("300059", "东方财富"), ("688111", "金山办公"), ("002475", "立讯精密"),
            ("600809", "山西汾酒"), ("000725", "京东方A"), ("601888", "中国中免"),
            ("600031", "三一重工"), ("000001", "平安银行"), ("600887", "伊利股份"),
            ("601166", "兴业银行"), ("300274", "阳光电源"), ("688981", "中芯国际"),
            ("002371", "北方华创"), ("300760", "迈瑞医疗"), ("600570", "恒生电子"),
            ("002230", "科大讯飞"), ("300124", "汇川技术"), ("000063", "中兴通讯"),
            ("600050", "中国联通"), ("601857", "中国石油"), ("601398", "工商银行"),
            ("601288", "农业银行"), ("603259", "药明康德"), ("300015", "爱尔眼科"),
            ("002714", "牧原股份"), ("601899", "紫金矿业"), ("600585", "海螺水泥"),
            ("000792", "盐湖股份"), ("002460", "赣锋锂业"), ("600104", "上汽集团"),
            ("000625", "长安汽车"), ("300498", "温氏股份"), ("300014", "亿纬锂能"),
            ("002352", "顺丰控股"), ("601615", "明阳智能"),
        ]

        count = 0
        for code, name in popular:
            stmt = select(Stock).where(Stock.code == code)
            result = await self.db.execute(stmt)
            stock = result.scalar_one_or_none()
            if stock is None:
                stock = Stock(code=code, name=name, market="A", security_type="stock")
                self.db.add(stock)
                count += 1
            else:
                stock.name = name
                stock.is_active = True

        if count > 0:
            await self.db.commit()
        logger.info(f"Synced {count} new A-share stocks (from {len(popular)} popular)")
        return count

    @retry_on_failure(max_retries=2, delay=3.0)
    async def fetch_daily_kline(self, code: str, days: int = 365) -> list[dict]:
        """Fetch daily K-line data for a single stock."""
        import akshare as ak
        end_date = date.today().strftime("%Y%m%d")
        start_date = (date.today() - timedelta(days=days)).strftime("%Y%m%d")
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            return df.to_dict(orient="records") if not df.empty else []
        except Exception as e:
            logger.warning(f"Failed to fetch K-line for {code}: {e}")
            return []

    async def save_kline(self, stock_id: int, records: list[dict]) -> int:
        """Save K-line records to database."""
        saved = 0
        for r in records:
            trade_date = r.get("日期")
            if trade_date is None:
                continue
            if isinstance(trade_date, str):
                trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
            # Upsert
            stmt = select(StockDailyPrice).where(
                StockDailyPrice.stock_id == stock_id,
                StockDailyPrice.trade_date == trade_date,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing is None:
                existing = StockDailyPrice(stock_id=stock_id, trade_date=trade_date)
                self.db.add(existing)
            existing.open = self.safe_decimal(r.get("开盘"))
            existing.high = self.safe_decimal(r.get("最高"))
            existing.low = self.safe_decimal(r.get("最低"))
            existing.close = self.safe_decimal(r.get("收盘"))
            existing.volume = self.safe_int(r.get("成交量"))
            existing.amount = self.safe_decimal(r.get("成交额"))
            existing.change_pct = self.safe_decimal(r.get("涨跌幅"))
            existing.turnover_rate = self.safe_decimal(r.get("换手率"))
            saved += 1
        await self.db.commit()
        return saved

    @staticmethod
    def safe_decimal(val, default=None):
        """Convert value to Decimal safely."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        try:
            return Decimal(str(val))
        except Exception:
            return default

    async def sync_indices(self) -> int:
        """Sync major A-share index daily prices."""
        import akshare as ak
        count = 0
        for idx_info in A_INDICES:
            # Upsert index
            stmt = select(Index).where(Index.code == idx_info["code"])
            result = await self.db.execute(stmt)
            idx = result.scalar_one_or_none()
            if idx is None:
                idx = Index(**idx_info)
                self.db.add(idx)
                await self.db.flush()
            try:
                df = ak.stock_zh_index_daily(symbol=f"sh{idx_info['code']}" if idx_info['code'].startswith("000") else f"sz{idx_info['code']}")
                for _, row in df.tail(30).iterrows():
                    trade_date = row.get("date")
                    if trade_date is None:
                        continue
                    if isinstance(trade_date, str):
                        trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
                    stmt2 = select(IndexDailyPrice).where(
                        IndexDailyPrice.index_id == idx.id,
                        IndexDailyPrice.trade_date == trade_date,
                    )
                    r2 = await self.db.execute(stmt2)
                    existing = r2.scalar_one_or_none()
                    if existing is None:
                        existing = IndexDailyPrice(index_id=idx.id, trade_date=trade_date)
                        self.db.add(existing)
                    existing.open = self.safe_decimal(row.get("open"))
                    existing.high = self.safe_decimal(row.get("high"))
                    existing.low = self.safe_decimal(row.get("low"))
                    existing.close = self.safe_decimal(row.get("close"))
                    existing.volume = self.safe_int(row.get("volume"))
                    count += 1
                await self.db.commit()
            except Exception as e:
                logger.warning(f"Failed to sync index {idx_info['name']}: {e}")
                await self.db.rollback()
        logger.info(f"Synced {count} index daily price records")
        return count


class AStockSpotCrawler(BaseCrawler):
    """Fetches real-time spot quotes for A-share stocks (during trading hours only)."""
    source_name = "akshare_spot"

    async def run(self) -> dict:
        if not self.is_trading_day():
            return {"status": "skipped", "reason": "not a trading day"}
        return {"quotes_fetched": await self.fetch_spot()}

    @retry_on_failure(max_retries=2, delay=5.0)
    async def fetch_spot(self) -> int:
        """Fetch real-time spot prices for tracked stocks (batched, not all 5000+)."""
        import akshare as ak
        import asyncio

        # Get tracked stock codes
        stmt = select(Stock.code).where(Stock.is_active != False)
        result = await self.db.execute(stmt)
        codes = [row[0] for row in result.all()]

        if not codes:
            return 0

        count = 0
        today = date.today()

        # Fetch in small batches to avoid triggering East Money rate limits
        batch_size = 10
        for i in range(0, len(codes), batch_size):
            batch = codes[i:i + batch_size]
            try:
                # Use individual stock spot (much lighter than full market scan)
                for code in batch:
                    try:
                        df = await asyncio.to_thread(ak.stock_zh_a_spot, symbol=code)
                        if df is None or df.empty:
                            continue
                        row = df.iloc[-1]  # latest row
                        close_val = self.safe_decimal(row.get("最新价"))
                        if close_val is None:
                            continue

                        # Get stock ID
                        stmt_s = select(Stock).where(Stock.code == code)
                        r_s = await self.db.execute(stmt_s)
                        stock = r_s.scalar_one_or_none()
                        if not stock:
                            continue

                        stmt2 = select(StockDailyPrice).where(
                            StockDailyPrice.stock_id == stock.id,
                            StockDailyPrice.trade_date == today,
                        )
                        r2 = await self.db.execute(stmt2)
                        sp = r2.scalar_one_or_none()
                        if sp is None:
                            sp = StockDailyPrice(stock_id=stock.id, trade_date=today)
                            self.db.add(sp)
                        sp.close = close_val
                        sp.change_pct = self.safe_decimal(row.get("涨跌幅"))
                        sp.volume = self.safe_int(row.get("成交量"))
                        sp.amount = self.safe_decimal(row.get("成交额"))
                        sp.turnover_rate = self.safe_decimal(row.get("换手率"))
                        sp.pe_ratio = self.safe_decimal(row.get("市盈率-动态"))
                        sp.pb_ratio = self.safe_decimal(row.get("市净率"))
                        sp.total_mv = self.safe_decimal(row.get("总市值"))
                        sp.circ_mv = self.safe_decimal(row.get("流通市值"))
                        count += 1
                    except Exception:
                        continue

                if i + batch_size < len(codes):
                    await asyncio.sleep(2)  # Rate limit between batches
            except Exception as e:
                logger.warning(f"Spot batch {i//batch_size} failed: {e}")

        if count > 0:
            await self.db.commit()
        return count
