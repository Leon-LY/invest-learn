"""Market data Pydantic schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel


class IndexInfo(BaseModel):
    code: str
    name: str
    market: Optional[str] = None
    country: Optional[str] = None
    latest_price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    sparkline: Optional[List[float]] = None

    class Config:
        from_attributes = True


class StockInfo(BaseModel):
    code: str
    name: str
    market: str
    security_type: str = "stock"
    sector: Optional[str] = None
    industry: Optional[str] = None

    class Config:
        from_attributes = True


class StockQuote(BaseModel):
    code: str
    name: str
    market: str
    latest_price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None
    amount: Optional[float] = None
    turnover_rate: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    total_mv: Optional[float] = None
    circ_mv: Optional[float] = None

    class Config:
        from_attributes = True


class KLineItem(BaseModel):
    date: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    amount: Optional[float] = None


class StockDetail(BaseModel):
    info: StockInfo
    quote: Optional[StockQuote] = None
    fundamentals: Optional[dict] = None
    klines: Optional[List[KLineItem]] = None


class FundInfo(BaseModel):
    code: str
    name: str
    fund_type: Optional[str] = None
    company: Optional[str] = None
    inception_date: Optional[date] = None
    aum: Optional[float] = None
    latest_nav: Optional[float] = None
    latest_return: Optional[float] = None

    class Config:
        from_attributes = True


class NAVItem(BaseModel):
    date: str
    unit_nav: Optional[float] = None
    acc_nav: Optional[float] = None
    daily_return: Optional[float] = None


class FundDetail(BaseModel):
    info: FundInfo
    nav_history: Optional[List[NAVItem]] = None


class SectorItem(BaseModel):
    sector_name: str
    change_pct: Optional[float] = None
    net_inflow: Optional[float] = None
    top_stock: Optional[str] = None
    top_stock_pct: Optional[float] = None


class CapitalFlowItem(BaseModel):
    date: str
    net_inflow: Optional[float] = None
    balance: Optional[float] = None


class MarketBreadth(BaseModel):
    up_count: int = 0
    down_count: int = 0
    flat_count: int = 0
    limit_up: int = 0
    limit_down: int = 0
    total_amount: Optional[float] = None


class StockSearchResult(BaseModel):
    code: str
    name: str
    market: str
    security_type: str = "stock"
    match_score: float = 1.0


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
