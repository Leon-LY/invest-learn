"""News API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from app.api.deps import get_news_service
from app.services.news_service import NewsService

router = APIRouter()


@router.get("")
async def get_news_list(
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    service: NewsService = Depends(get_news_service),
):
    """Get paginated news feed."""
    return await service.get_news_list(category, source_id, sentiment, page, size)


# ── Specific named routes must come BEFORE /{article_id} wildcard ──

@router.get("/analyses")
async def get_ai_analyses(limit: int = 10, service: NewsService = Depends(get_news_service)):
    """Get recent AI analyses (cached 5 min)."""
    from app.core.cache import cache_get, cache_set
    cache_key = f"analysis:recent:{limit}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    data = await service.get_recent_analyses(limit)
    if data:
        await cache_set(cache_key, data, ttl=300)
    return data


@router.get("/expert-predictions")
async def get_expert_predictions(limit: int = 6, service: NewsService = Depends(get_news_service)):
    """Get cached DeepSeek expert predictions (pre-generated every 30min)."""
    from app.core.cache import cache_get, cache_set
    cached = await cache_get("analysis:expert_predictions")
    if cached:
        return cached[:limit]
    data = await service.get_expert_predictions(limit)
    if data:
        await cache_set("analysis:expert_predictions", data, ttl=1800)
    return data


@router.get("/expert-predictions/{expert_id}")
async def get_expert_prediction_detail(expert_id: str, service: NewsService = Depends(get_news_service)):
    """Get detailed predictions for one expert across multiple news."""
    return await service.get_expert_prediction_detail(expert_id)


@router.get("/expert-tracker")
async def get_expert_tracker(service: NewsService = Depends(get_news_service)):
    """Get real expert data (cached 1h)."""
    from app.core.cache import cache_get, cache_set
    cached = await cache_get("analysis:expert_tracker")
    if cached:
        return cached
    data = await service.get_expert_tracker()
    if data:
        await cache_set("analysis:expert_tracker", data, ttl=3600)
    return data


@router.get("/expert-tracker/{expert_id}")
async def get_expert_detail(expert_id: str, service: NewsService = Depends(get_news_service)):
    """Get expert detail — always from cache, no fallback generation."""
    from app.core.cache import cache_get
    cached = await cache_get(f"analysis:expert_detail:{expert_id}")
    if cached:
        return cached
    # Cache miss: just return basic — scheduler fills cache every 2h
    return {"id":expert_id,"name":expert_id,"type":"加载中","title":"数据生成中，请稍后刷新","related_news":[],"related_analyses":[],"operations":[],"fund_operations":[],"predictive_view":None,"nav_history":[],"size_history":[]}


@router.post("/viewpoints")
async def create_viewpoint(request: Request, service: NewsService = Depends(get_news_service)):
    import logging, base64
    log = logging.getLogger(__name__)
    data = {}
    try: data = await request.json()
    except: pass
    image_data = data.get("image", "")
    content = data.get("content", "")
    if image_data:
        try:
            from app.services.vision_service import analyze_image
            vr = await analyze_image(base64.b64decode(image_data))
            if vr:
                vt = chr(10).join(filter(None, [vr.get("content",""), vr.get("key_points") and ("要点: "+"; ".join(vr["key_points"])), vr.get("numbers_extracted") and ("数据: "+vr["numbers_extracted"])]))
                content = (content.strip() + "[截图]: " + vt) if content.strip() else vt
        except Exception as e: log.warning(f"Vision: {e}")
    if not content.strip(): return {"error": "请提供文本或上传图片"}
    try:
        return await service.create_viewpoint(content=content, source=data.get("source","用户投稿"), author=data.get("author",""), link=data.get("link",""))
    except Exception as e:
        log.error(f"Viewpoint: {e}", exc_info=True)
        return {"error": str(e)}


@router.get("/viewpoints")
async def list_viewpoints(limit: int = 20, service: NewsService = Depends(get_news_service)):
    """List user-submitted viewpoints."""
    return await service.list_viewpoints(limit)


@router.get("/sources/list")
async def get_sources(service: NewsService = Depends(get_news_service)):
    """Get available news sources."""
    return await service.get_sources()


@router.get("/sentiment/stats")
async def get_sentiment_stats(days: int = 7, service: NewsService = Depends(get_news_service)):
    """Get sentiment distribution."""
    return await service.get_sentiment_stats(days)


# ── Wildcard routes (must be last) ──

@router.get("/{article_id}")
async def get_news_detail(article_id: int, service: NewsService = Depends(get_news_service)):
    """Get full article detail (AI analysis loads separately)."""
    result = await service.get_article_detail(article_id, include_analysis=False)
    if not result:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


@router.get("/{article_id}/analysis")
async def get_news_analysis(article_id: int, service: NewsService = Depends(get_news_service)):
    """Get or generate AI analysis (cached 1h)."""
    from app.core.cache import cache_get, cache_set
    cache_key = f"analysis:article:{article_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    article = await service.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    analysis = await service._get_or_generate_analysis(article)
    if analysis:
        await cache_set(cache_key, analysis, ttl=3600)
    return analysis
