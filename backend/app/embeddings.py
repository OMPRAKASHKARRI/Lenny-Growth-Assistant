import hashlib
import math

DIMENSIONS = 64


def embed(text: str) -> list[float]:
    """Small deterministic embedding that keeps the demo self-contained."""
    values = [0.0] * DIMENSIONS
    for token in text.lower().split():
        index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % DIMENSIONS
        values[index] += 1.0
    length = math.sqrt(sum(value * value for value in values)) or 1.0
    return [value / length for value in values]


def similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
