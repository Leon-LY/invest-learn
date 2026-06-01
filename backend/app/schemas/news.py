"""News Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NewsItem(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    sentiment: Optional[str] = None
    categories: Optional[list] = None
    tags: Optional[list] = None
    related_stocks: Optional[list] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsDetail(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    categories: Optional[list] = None
    tags: Optional[list] = None
    related_stocks: Optional[list] = None
    published_at: Optional[datetime] = None
    related_news: Optional[List[NewsItem]] = None

    class Config:
        from_attributes = True


class SentimentStats(BaseModel):
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    top_tags: Optional[list] = None


class CalendarEvent(BaseModel):
    id: int
    event_date: str
    event_type: str
    title: str
    description: Optional[str] = None
    importance: str = "medium"
    country: str = "CN"

    class Config:
        from_attributes = True
