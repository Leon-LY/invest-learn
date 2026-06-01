"""API v1 router — includes all sub-routers."""
from fastapi import APIRouter
from . import market, news, watchlist, learn, crawl

api_router = APIRouter()

api_router.include_router(market.router, prefix="/market", tags=["Market"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
api_router.include_router(learn.router, prefix="/learn", tags=["Learn"])
api_router.include_router(crawl.router, prefix="/crawl", tags=["Crawl"])
