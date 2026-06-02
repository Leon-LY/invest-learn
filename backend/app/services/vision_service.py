"""
Qwen Vision service — analyze fund/investment images via 通义千问 VL.
"""
import base64
import logging
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的基金投资分析师。用户会上传投资相关的截图（可能是K线图、基金持仓、收益率数据、大佬观点等）。

请分析图片中的内容，提取关键投资信息，返回JSON：
{
  "title": "15字以内的概括标题",
  "content": "图片中提取出的观点或数据（原文提炼，不要编造）",
  "direction": "看多/看空/中性",
  "confidence": 50-90,
  "tags": ["关键词1", "关键词2"],
  "relatedFunds": ["相关基金代码"],
  "has_data": true/false,
  "data_points": "如果有具体的数字数据（如收益率、净值、涨跌幅），提取出来"
}

注意：只分析图片中实际存在的内容，不要编造数据。如果图片中提到了具体的基金代码、收益率、净值等数字，请准确提取。"""


async def analyze_image(image_data: bytes, content_type: str = "image/png") -> Optional[dict]:
    """Send image to Qwen Vision for investment analysis."""
    if not settings.QWEN_API_KEY:
        logger.warning("Qwen API key not configured")
        return None

    image_b64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{content_type};base64,{image_b64}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.QWEN_MODEL,
                    "messages": [{
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    }, {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url}},
                            {"type": "text", "text": "请分析这张图片中的投资相关信息"},
                        ],
                    }],
                    "max_tokens": 800,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            import json
            content = data["choices"][0]["message"]["content"]
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content)
            logger.info(f"Qwen Vision analyzed image: {result.get('title', '')}")
            return result
    except Exception as e:
        logger.error(f"Qwen Vision failed: {e}")
        return None
