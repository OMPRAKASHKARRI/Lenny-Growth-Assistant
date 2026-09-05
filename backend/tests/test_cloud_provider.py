import pytest
from unittest.mock import patch

from app.providers.cloud_provider import CloudProvider


class FakeStream:
    def __init__(self):
        self.text_stream = self._text_stream()

    async def _text_stream(self):
        yield "first "
        yield "second"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


class FakeMessages:
    def stream(self, **kwargs):
        assert kwargs["model"]
        assert kwargs["max_tokens"] == 1800
        return FakeStream()


class FakeClient:
    messages = FakeMessages()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


@pytest.mark.asyncio
async def test_cloud_provider_yields_sdk_text_stream(monkeypatch):
    monkeypatch.setattr("app.providers.cloud_provider.settings.anthropic_api_key", "test-key")
    with patch("app.providers.cloud_provider.anthropic.AsyncAnthropic", return_value=FakeClient()):
        chunks = [chunk async for chunk in CloudProvider().stream("test prompt")]
    assert chunks == ["first ", "second"]