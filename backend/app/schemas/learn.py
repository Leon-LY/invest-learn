"""Learning content Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CategoryItem(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    children: Optional[list] = None

    class Config:
        from_attributes = True


class ArticleItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    level: str = "beginner"
    tags: Optional[list] = None
    estimated_read: Optional[int] = None
    view_count: int = 0
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleDetail(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: Optional[str] = None
    level: str = "beginner"
    tags: Optional[list] = None
    estimated_read: Optional[int] = None
    view_count: int = 0
    published_at: Optional[datetime] = None
    prev_article: Optional[ArticleItem] = None
    next_article: Optional[ArticleItem] = None
    related_articles: Optional[List[ArticleItem]] = None

    class Config:
        from_attributes = True


class GlossaryItem(BaseModel):
    term: str
    term_en: Optional[str] = None
    definition: str
    category: Optional[str] = None
    related_terms: Optional[list] = None

    class Config:
        from_attributes = True


class StrategyItem(BaseModel):
    id: int
    name: str
    slug: str
    summary: Optional[str] = None
    difficulty: str = "beginner"
    risk_level: str = "medium"
    suitable_for: Optional[str] = None
    key_metrics: Optional[list] = None

    class Config:
        from_attributes = True
