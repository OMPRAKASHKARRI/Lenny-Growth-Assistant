from .base import LLMProvider
from .cloud_provider import CloudProvider
from .ollama_provider import OllamaProvider


def get_provider(name: str) -> LLMProvider:
    if name.lower() == "cloud":
        return CloudProvider()
    return OllamaProvider()
