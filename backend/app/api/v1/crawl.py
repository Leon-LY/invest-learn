"""Manual crawl trigger endpoint."""
from fastapi import APIRouter
from app.tasks.jobs import crawl_a_stock_list, crawl_global_stocks, crawl_funds, crawl_news

router = APIRouter()


@router.post("/trigger/{name}")
async def trigger_crawl(name: str):
    """Manually trigger a crawler job. name: a_stock | global | funds | news"""
    jobs = {
        "a_stock": crawl_a_stock_list,
        "global": crawl_global_stocks,
        "funds": crawl_funds,
        "news": crawl_news,
    }
    job = jobs.get(name)
    if not job:
        return {"error": f"Unknown job: {name}. Try: {list(jobs.keys())}"}
    try:
        await job()
        return {"status": "ok", "job": name}
    except Exception as e:
        return {"status": "error", "job": name, "error": str(e)}
