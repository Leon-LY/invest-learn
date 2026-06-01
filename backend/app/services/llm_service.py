"""
LLM service — calls DeepSeek API (OpenAI-compatible) for financial news analysis.
Falls back gracefully when API key is not configured or call fails.
"""
import json
import logging
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的中国基金投资分析师。你需要根据给定的财经新闻，生成一份结构化的投资影响分析。

请严格按照以下 JSON 格式返回（不要包含任何其他文本）：

{
  "impact_score": <整数，-100到100，正值=利好，负值=利空，0=中性>,
  "impact_level": "<重大利好|利好|中性|利空|重大利空>",
  "affected_funds": [
    {"code": "<6位基金代码>", "name": "<基金名称>", "impact": "<对该基金的具体影响，一句话>"}
  ],
  "short_term": "<1-2周短期影响分析，50-100字>",
  "medium_term": "<1-3个月中期影响分析，50-100字>",
  "action_advice": "<给投资者的具体操作建议，30-60字>",
  "key_points": ["<要点1，15字以内>", "<要点2>", "<要点3>", "<要点4>"]
}

规则：
- affected_funds 至少包含2个、最多4个受影响的真实中国基金
- impact_score 结合新闻的情绪和影响程度综合判断
- 分析要具体、专业，不要泛泛而谈
- 如新闻涉及具体行业（如医药、科技、消费），请找到该行业相关的知名基金
"""


class LLMService:
    """Calls DeepSeek API for AI-powered financial analysis."""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def analyze_news(
        self, title: str, summary: Optional[str], sentiment: Optional[str]
    ) -> Optional[dict]:
        """Send news to DeepSeek and get structured investment impact analysis.
        Returns None if API is not configured or call fails."""
        if not self.is_configured:
            logger.warning("DeepSeek API key not configured, skipping AI analysis")
            return None

        user_prompt = f"""请分析以下财经新闻对基金投资的影响：

标题：{title}
摘要：{summary or '暂无'}
当前情绪判断：{sentiment or '未判断'}"""

        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1024,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()

            # Parse the assistant's response
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)

            # Validate required fields
            required = ["impact_score", "impact_level", "affected_funds",
                        "short_term", "medium_term", "action_advice", "key_points"]
            for field in required:
                if field not in result:
                    logger.warning(f"DeepSeek response missing field: {field}")
                    return None

            # Ensure impact_score is an int
            result["impact_score"] = int(result["impact_score"])

            # Ensure affected_funds is a list of dicts with required fields
            result["affected_funds"] = result["affected_funds"][:4]
            for f in result["affected_funds"]:
                if not all(k in f for k in ("code", "name", "impact")):
                    logger.warning("DeepSeek affected_funds item missing fields")
                    return None

            # Ensure key_points is a list of strings
            result["key_points"] = [str(kp) for kp in result["key_points"][:4]]

            logger.info(f"DeepSeek analysis generated: score={result['impact_score']}, level={result['impact_level']}")
            return result

        except httpx.TimeoutException:
            logger.error("DeepSeek API timed out")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"DeepSeek response parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"DeepSeek API unexpected error: {e}")
            return None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# Module-level singleton
llm_service = LLMService()
