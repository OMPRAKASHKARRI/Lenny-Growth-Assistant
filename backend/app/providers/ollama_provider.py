import json
import httpx
from collections.abc import AsyncIterator
from .base import LLMProvider
from ..config import settings


class OllamaProvider(LLMProvider):
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        payload = {"model": settings.ollama_model, "prompt": prompt, "stream": True, "options": {"num_predict": 1800}}
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=5)) as client:
                async with client.stream("POST", f"{settings.ollama_base_url}/api/generate", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            if data.get("response"):
                                yield data["response"]
        except httpx.TimeoutException as exc:
            raise RuntimeError("Ollama timed out while generating a response") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("Ollama is unavailable or rejected the request") from exc
