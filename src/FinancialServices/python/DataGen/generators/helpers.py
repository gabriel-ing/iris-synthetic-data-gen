from __future__ import annotations

from typing import Any

import numpy as np

from DataGen.rng import normalize_weights


def weighted_choice(rng: np.random.Generator, values: list[str], weights: dict[str, float], size: int) -> np.ndarray:
    probs = normalize_weights([weights[v] for v in values])
    return rng.choice(values, size=size, p=probs)


def segment_lookup(segments: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {segment["name"]: segment for segment in segments}
