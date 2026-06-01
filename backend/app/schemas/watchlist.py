"""Watchlist Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class WatchlistItemCreate(BaseModel):
    item_type: str  # 'stock','fund','index'
    item_code: str
    item_name: Optional[str] = None
    alias: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WatchlistItemUpdate(BaseModel):
    alias: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WatchlistItemResponse(BaseModel):
    id: int
    item_type: str
    item_code: str
    item_name: Optional[str] = None
    alias: Optional[str] = None
    tags: Optional[list] = None
    notes: Optional[str] = None
    sort_order: int = 0
    quote: Optional[dict] = None  # {price, change_pct, latest_price}
    added_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WatchlistReorder(BaseModel):
    items: List[dict]  # [{id, sort_order}]


class PriceAlertCreate(BaseModel):
    item_type: str
    item_code: str
    condition: str  # 'above','below','pct_up','pct_down'
    target_value: float


class PriceAlertResponse(BaseModel):
    id: int
    item_type: str
    item_code: str
    condition: str
    target_value: float
    is_triggered: bool = False
    triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
