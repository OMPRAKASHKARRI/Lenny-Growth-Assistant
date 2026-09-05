import json
import httpx
from collections.abc import AsyncIterator
from .base import LLMProvider
from ..config import settings


class CloudProvider(LLMProvider):
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        headers = {"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01"}
        payload = {"model": settings.anthropic_model, "max_tokens": 1800, "stream": True,
                   "messages": [{"role": "user", "content": prompt}]}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as client:
                async with client.stream("POST", "https://api.anthropic.com/v1/messages", headers=headers, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            if data.get("type") == "content_block_delta":
                                yield data["delta"].get("text", "")
        except httpx.TimeoutException as exc:
            raise RuntimeError("Cloud provider timed out while generating a response") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("Cloud provider request failed") from exc
