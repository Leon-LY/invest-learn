"""Watchlist + user API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.models.user import WatchlistItem, PriceAlert, UserNote
from app.schemas.watchlist import (
    WatchlistItemCreate, WatchlistItemUpdate, WatchlistItemResponse,
    WatchlistReorder, PriceAlertCreate, PriceAlertResponse,
)

router = APIRouter()

# For MVP, use a default user_id = 1 (no auth system yet)
DEFAULT_USER_ID = 1


# ─── Watchlist ──────────────────────────────────────

@router.get("")
async def get_watchlist(
    item_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get user's watchlist with quotes."""
    query = select(WatchlistItem).where(WatchlistItem.user_id == DEFAULT_USER_ID)
    if item_type:
        query = query.where(WatchlistItem.item_type == item_type)
    query = query.order_by(WatchlistItem.sort_order, WatchlistItem.added_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    output = []
    for item in items:
        item_dict = {
            "id": item.id, "item_type": item.item_type, "item_code": item.item_code,
            "item_name": item.item_name, "alias": item.alias,
            "tags": item.tags or [], "notes": item.notes,
            "sort_order": item.sort_order,
            "added_at": item.added_at.isoformat() if item.added_at else None,
            "quote": None,
        }
        # Try to get latest price
        try:
            if item.item_type == "stock":
                from app.models.market import Stock, StockDailyPrice
                stmt = select(StockDailyPrice).join(Stock).where(
                    Stock.code == item.item_code,
                ).order_by(StockDailyPrice.trade_date.desc()).limit(1)
                r = await db.execute(stmt)
                price = r.scalar_one_or_none()
                if price:
                    item_dict["quote"] = {
                        "latest_price": float(price.close) if price.close else None,
                        "change_pct": float(price.change_pct) if price.change_pct else None,
                    }
            elif item.item_type == "fund":
                from app.models.market import Fund, FundNAV
                stmt = select(FundNAV).join(Fund).where(
                    Fund.code == item.item_code,
                ).order_by(FundNAV.nav_date.desc()).limit(1)
                r = await db.execute(stmt)
                nav = r.scalar_one_or_none()
                if nav:
                    item_dict["quote"] = {
                        "latest_price": float(nav.unit_nav) if nav.unit_nav else None,
                        "change_pct": float(nav.daily_return) if nav.daily_return else None,
                    }
        except Exception:
            pass
        output.append(item_dict)

    return output


@router.post("", status_code=201)
async def add_watchlist_item(
    data: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add item to watchlist."""
    # Check duplicates
    stmt = select(WatchlistItem).where(
        WatchlistItem.user_id == DEFAULT_USER_ID,
        WatchlistItem.item_type == data.item_type,
        WatchlistItem.item_code == data.item_code,
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in watchlist")

    item = WatchlistItem(
        user_id=DEFAULT_USER_ID,
        item_type=data.item_type,
        item_code=data.item_code,
        item_name=data.item_name,
        alias=data.alias,
        tags=data.tags or [],
        notes=data.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "item_type": item.item_type, "item_code": item.item_code}


@router.put("/{item_id}")
async def update_watchlist_item(
    item_id: int,
    data: WatchlistItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update watchlist item tags, alias, notes."""
    stmt = select(WatchlistItem).where(WatchlistItem.id == item_id, WatchlistItem.user_id == DEFAULT_USER_ID)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    if data.alias is not None:
        item.alias = data.alias
    if data.tags is not None:
        item.tags = data.tags
    if data.notes is not None:
        item.notes = data.notes
    await db.commit()
    return {"success": True}


@router.delete("/{item_id}")
async def delete_watchlist_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Remove from watchlist."""
    stmt = select(WatchlistItem).where(WatchlistItem.id == item_id, WatchlistItem.user_id == DEFAULT_USER_ID)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(item)
    await db.commit()
    return {"success": True}


@router.post("/reorder")
async def reorder_watchlist(data: WatchlistReorder, db: AsyncSession = Depends(get_db)):
    """Reorder watchlist items."""
    for entry in data.items:
        await db.execute(
            update(WatchlistItem).where(WatchlistItem.id == entry["id"]).values(sort_order=entry.get("sort_order", 0))
        )
    await db.commit()
    return {"success": True}


# ─── Price Alerts ──────────────────────────────────

@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    """Get user's price alerts."""
    stmt = select(PriceAlert).where(PriceAlert.user_id == DEFAULT_USER_ID).order_by(PriceAlert.created_at.desc())
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return [{
        "id": a.id, "item_type": a.item_type, "item_code": a.item_code,
        "condition": a.condition, "target_value": float(a.target_value),
        "is_triggered": a.is_triggered,
        "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    } for a in alerts]


@router.post("/alerts", status_code=201)
async def create_alert(data: PriceAlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a price alert."""
    alert = PriceAlert(
        user_id=DEFAULT_USER_ID,
        item_type=data.item_type,
        item_code=data.item_code,
        condition=data.condition,
        target_value=data.target_value,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {"id": alert.id, "condition": alert.condition, "target_value": float(alert.target_value)}


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a price alert."""
    stmt = select(PriceAlert).where(PriceAlert.id == alert_id, PriceAlert.user_id == DEFAULT_USER_ID)
    result = await db.execute(stmt)
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(alert)
    await db.commit()
    return {"success": True}
