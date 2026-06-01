"""Paper trading models: simulated portfolios, holdings, transactions."""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Text, DateTime, ForeignKey, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SimPortfolio(Base):
    __tablename__ = "sim_portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    total_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    total_return: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SimHolding(Base):
    __tablename__ = "sim_holdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey("sim_portfolios.id", ondelete="CASCADE"), nullable=False)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_name: Mapped[Optional[str]] = mapped_column(String(100))
    market: Mapped[Optional[str]] = mapped_column(String(10))
    shares: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4))
    market_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    profit_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2))
    profit_loss_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("portfolio_id", "stock_code", name="uq_sim_holding"),
    )


class SimTransaction(Base):
    __tablename__ = "sim_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(Integer, ForeignKey("sim_portfolios.id", ondelete="CASCADE"), nullable=False)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_name: Mapped[Optional[str]] = mapped_column(String(100))
    tx_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'buy','sell'
    shares: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    transacted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_transactions_portfolio", "portfolio_id", "transacted_at"),
    )
