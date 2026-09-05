from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def stream(self, prompt: str) -> AsyncIterator[str]:
        raise NotImplementedError
