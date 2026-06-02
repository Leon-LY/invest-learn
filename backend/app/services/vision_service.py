"""
Qwen Vision service — analyze fund/investment images via 通义千问 VL.
"""
import base64
import logging
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的基金投资信息提取助手。用户会上传各种类型的截图，包括但不限于：

- 小红书/抖音/微博等社交平台的UP主观点截图
- 手机备忘录里的投资笔记截图
- 基金/股票持仓页面截图
- K线图或技术分析图表截图
- 聊天记录里讨论投资的截图
- 任何包含投资相关信息的图片

请仔细阅读图片中的所有文字，识别出有价值的信息。根据图片类型灵活处理：

1. 如果是UP主观点类：提取核心观点、逻辑、结论
2. 如果是笔记类：提取投资思路、关注方向
3. 如果是持仓截图：提取基金代码、收益率、金额等数字
4. 如果是图表类：判断趋势方向
5. 如果是聊天记录：提取讨论的核心观点

返回JSON：
{
  "title": "15字以内概括",
  "content": "从图片中提取的核心内容（保持原意，不要编造。如果是观点，提炼原话；如果是数据，准确摘录）",
  "direction": "看多/看空/中性",
  "confidence": 50-90,
  "tags": ["标签1", "标签2", "标签3"],
  "relatedFunds": ["基金代码"],
  "image_type": "观点截图/持仓截图/笔记截图/图表截图/聊天截图/其他",
  "key_points": ["要点1", "要点2"],
  "numbers_extracted": "如果提取到具体数字（收益率、净值、金额、点位等），列出来"
}

重要规则：
- 只分析图片中实际存在的内容，绝对不能编造
- 如果图片模糊或无法识别，如实说明
- 社交平台截图通常包含昵称、发布时间、正文、评论区，请重点提取正文观点
- 如果是多个图片区域的拼接，逐一分析每个区域"""


async def analyze_image(image_data: bytes, content_type: str = "image/jpeg") -> Optional[dict]:
    """Send image to Qwen Vision for investment analysis."""
    if not settings.QWEN_API_KEY:
        logger.warning("Qwen API key not configured")
        return None

    # Compress large images to avoid timeout
    if len(image_data) > 500_000:  # >500KB
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_data))
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=70)
            image_data = buf.getvalue()
            content_type = "image/jpeg"
            logger.info(f"Image compressed: {len(image_data)} bytes")
        except Exception:
            pass  # Continue with original if PIL not available

    image_b64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:{content_type};base64,{image_b64}"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
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
