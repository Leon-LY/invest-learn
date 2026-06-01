"""Market data models: stocks, funds, indices, prices, capital flow, sectors."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Date, DateTime, Numeric, Boolean, Text, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from .base import TimestampMixin


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)  # 'A', 'HK', 'US'
    security_type: Mapped[str] = mapped_column(String(20), default="stock")  # 'stock','etf','index'
    sector: Mapped[Optional[str]] = mapped_column(String(50))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    listing_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    daily_prices: Mapped[list["StockDailyPrice"]] = relationship(back_populates="stock", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_stocks_market_type", "market", "security_type"),
    )


class StockDailyPrice(Base):
    __tablename__ = "stock_daily_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    close: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    volume: Mapped[Optional[int]] = mapped_column(BigInteger)
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    turnover_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    pe_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    pb_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    total_mv: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 2))
    circ_mv: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stock: Mapped["Stock"] = relationship(back_populates="daily_prices")

    __table_args__ = (
        UniqueConstraint("stock_id", "trade_date", name="uq_stock_daily"),
    )


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fund_type: Mapped[Optional[str]] = mapped_column(String(30))  # 'stock','bond','mixed','money','etf','lof','qdi'
    company: Mapped[Optional[str]] = mapped_column(String(100))
    inception_date: Mapped[Optional[date]] = mapped_column(Date)
    aum: Mapped[Optional[Decimal]] = mapped_column(Numeric(24, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    nav_records: Mapped[list["FundNAV"]] = relationship(back_populates="fund", cascade="all, delete-orphan")


class FundNAV(Base):
    __tablename__ = "fund_nav"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), nullable=False)
    nav_date: Mapped[date] = mapped_column(Date, nullable=False)
    unit_nav: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6))
    acc_nav: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6))
    daily_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    fund: Mapped["Fund"] = relationship(back_populates="nav_records")

    __table_args__ = (
        UniqueConstraint("fund_id", "nav_date", name="uq_fund_nav"),
    )


class Index(Base):
    __tablename__ = "indices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    market: Mapped[Optional[str]] = mapped_column(String(10))
    country: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IndexDailyPrice(Base):
    __tablename__ = "index_daily_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    index_id: Mapped[int] = mapped_column(Integer, ForeignKey("indices.id", ondelete="CASCADE"), nullable=False)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    close: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    volume: Mapped[Optional[int]] = mapped_column(BigInteger)
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("index_id", "trade_date", name="uq_index_daily"),
    )


class CapitalFlow(Base):
    __tablename__ = "capital_flow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    flow_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'north', 'south'
    net_inflow: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("trade_date", "flow_type", name="uq_capital_flow"),
    )


class SectorPerformance(Base):
    __tablename__ = "sector_performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    sector_name: Mapped[str] = mapped_column(String(100), nullable=False)
    change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    net_inflow: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    top_stock: Mapped[Optional[str]] = mapped_column(String(20))
    top_stock_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("trade_date", "sector_name", name="uq_sector_perf"),
    )
