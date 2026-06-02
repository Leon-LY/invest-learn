"""
Crawl Tiantian Fund (天天基金) public portfolio plans.
"""
import logging, json, re, asyncio
from datetime import datetime
from sqlalchemy import select
import httpx
from .base import BaseCrawler

logger = logging.getLogger(__name__)


class PortfolioPlanCrawler(BaseCrawler):
    """Crawl public investment portfolios/plans from Tiantian Fund."""
    source_name = "tiantian_plans"

    async def run(self) -> dict:
        plans = await self.fetch_popular_plans()
        return {"plans_fetched": len(plans), "plans": plans}

    async def fetch_popular_plans(self, limit: int = 10) -> list[dict]:
        """Fetch popular public plans from Tiantian Fund plan square."""
        plans = []
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                # Try multiple possible API endpoints
                urls = [
                    "https://planapi.1234567.com.cn/plan/square/list?pageIndex=1&pageSize=30&orderBy=returnRate&orderDir=desc",
                    "https://plan.1234567.com.cn/api/square/list?pageIndex=1&pageSize=30&orderBy=returnRate&orderDir=desc",
                ]
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Referer": "https://plan.1234567.com.cn/",
                    "Accept": "application/json",
                }
                for url in urls:
                    resp = await client.get(url, headers=headers)
                    logger.info(f"Tried {url}: {resp.status_code}")
                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            items = data.get("data", {}).get("list", data.get("data", []))
                            if not isinstance(items, list):
                                items = data.get("list", [])
                            for item in items:
                                plans.append({
                                    "plan_id": str(item.get("planId", item.get("id", ""))),
                                    "name": str(item.get("planName", item.get("name", ""))),
                                    "owner": str(item.get("userName", item.get("nickname", ""))),
                                    "return_rate": float(item.get("totalReturnRate", item.get("returnRate", 0)) or 0),
                                    "followers": int(item.get("followCount", item.get("fans", 0)) or 0),
                                    "funds_count": int(item.get("fundCount", item.get("count", 0)) or 0),
                                })
                            if plans:
                                break
                        except Exception:
                            continue
            logger.info(f"Fetched {len(plans)} plans")
        except Exception as e:
            logger.error(f"Plan fetch failed: {e}")

        return plans[:limit]

    async def fetch_plan_detail(self, plan_id: str) -> dict:
        """Fetch detailed holdings for a specific plan."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                url = f"https://api.1234567.com.cn/plan/detail?planId={plan_id}"
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": f"https://plan.1234567.com.cn/plan/{plan_id}",
                })
                if resp.status_code == 200:
                    data = resp.json()
                    detail = data.get("data", {})
                    holdings = detail.get("holdings", [])
                    operations = detail.get("tradeRecords", [])
                    return {
                        "plan_id": plan_id,
                        "name": detail.get("planName", ""),
                        "owner": detail.get("userName", ""),
                        "total_return": detail.get("totalReturnRate", 0),
                        "holdings": [{
                            "fund_code": h.get("fundCode", ""),
                            "fund_name": h.get("fundName", ""),
                            "ratio": h.get("ratio", 0),
                            "profit": h.get("profit", 0),
                        } for h in holdings],
                        "recent_ops": [{
                            "date": op.get("tradeDate", ""),
                            "action": op.get("tradeType", ""),
                            "fund_code": op.get("fundCode", ""),
                            "fund_name": op.get("fundName", ""),
                            "amount": op.get("tradeAmount", 0),
                        } for op in operations[:10]],
                    }
        except Exception as e:
            logger.error(f"Plan detail failed for {plan_id}: {e}")
            return {"plan_id": plan_id, "error": str(e)}
