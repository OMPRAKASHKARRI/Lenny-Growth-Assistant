from collections.abc import AsyncIterator
import anthropic
from .base import LLMProvider
from ..config import settings


class CloudProvider(LLMProvider):
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        try:
            async with anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key) as client:
                async with client.messages.stream(
                    model=settings.anthropic_model,
                    max_tokens=1800,
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
        except anthropic.APITimeoutError as exc:
            raise RuntimeError("Cloud provider timed out while generating a response") from exc
        except anthropic.APIStatusError as exc:
            raise RuntimeError(f"Anthropic API error ({exc.status_code}): {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise RuntimeError("Cloud provider connection failed") from exc
        except anthropic.APIError as exc:
            raise RuntimeError(f"Anthropic API error: {exc.message}") from exc
