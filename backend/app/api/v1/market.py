"""Market data API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_market_service
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/indices")
async def get_indices(service: MarketService = Depends(get_market_service)):
    """Get all tracked indices with real-time data and sparklines."""
    return await service.get_indices()


@router.get("/indices/{code}")
async def get_index_detail(code: str, days: int = 90, service: MarketService = Depends(get_market_service)):
    """Get single index detail with K-line history."""
    result = await service.get_index_detail(code, days)
    if not result:
        raise HTTPException(status_code=404, detail="Index not found")
    return result


@router.get("/stocks/{code}")
async def get_stock_detail(code: str, kline_days: int = 250, service: MarketService = Depends(get_market_service)):
    """Get full stock detail: info, quote, fundamentals, K-lines."""
    result = await service.get_stock_detail(code, kline_days)
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    return result


@router.get("/stocks/{code}/kline")
async def get_stock_kline(
    code: str,
    period: str = "daily",
    start: Optional[str] = None,
    end: Optional[str] = None,
    service: MarketService = Depends(get_market_service),
):
    """Get K-line data for a stock."""
    result = await service.get_stock_kline(code, period, start, end)
    if result is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"klines": result}


@router.get("/funds/{code}")
async def get_fund_detail(code: str, service: MarketService = Depends(get_market_service)):
    """Get fund detail with NAV history."""
    result = await service.get_fund_detail(code)
    if not result:
        raise HTTPException(status_code=404, detail="Fund not found")
    return result


@router.get("/etfs")
async def get_etfs(service: MarketService = Depends(get_market_service)):
    """Get ETF list with performance. (Simplified — returns stocks with type 'etf')"""
    from sqlalchemy import select
    from app.models.market import Stock
    stmt = select(Stock).where(Stock.security_type == "etf").limit(50)
    result = await service.db.execute(stmt)
    etfs = result.scalars().all()
    return [{"code": e.code, "name": e.name, "market": e.market} for e in etfs]


@router.get("/sectors")
async def get_sectors(service: MarketService = Depends(get_market_service)):
    """Get sector performance board."""
    return await service.get_sectors()


@router.get("/capital-flow")
async def get_capital_flow(days: int = 30, service: MarketService = Depends(get_market_service)):
    """Get north/south bound capital flow."""
    return await service.get_capital_flow(days)


@router.get("/breadth")
async def get_market_breadth(service: MarketService = Depends(get_market_service)):
    """Get market breadth stats (advance/decline)."""
    return await service.get_market_breadth()


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1),
    market: Optional[str] = None,
    limit: int = 20,
    service: MarketService = Depends(get_market_service),
):
    """Search stocks by code or name."""
    return await service.search_stocks(q, market, limit)


@router.get("/screener")
async def screen_stocks(
    market: str = "A",
    pe_min: Optional[float] = None,
    pe_max: Optional[float] = None,
    pb_min: Optional[float] = None,
    pb_max: Optional[float] = None,
    roe_min: Optional[float] = None,
    sector: Optional[str] = None,
    sort: str = "pe",
    order: str = "asc",
    page: int = 1,
    size: int = 20,
    service: MarketService = Depends(get_market_service),
):
    """Screen stocks by fundamental criteria."""
    return await service.screen_stocks(market, pe_min, pe_max, pb_min, pb_max, roe_min, sector, sort, order, page, size)
