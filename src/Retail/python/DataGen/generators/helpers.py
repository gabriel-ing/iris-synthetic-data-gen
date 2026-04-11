from __future__ import annotations

import numpy as np

from DataGen.rng import normalize_weights


def weighted_choice(rng: np.random.Generator, values: list[str], weights: dict[str, float], size: int) -> np.ndarray:
    probs = normalize_weights([weights[value] for value in values])
    return rng.choice(values, size=size, p=probs)


def random_codes(prefix: str, size: int, pad: int = 6) -> list[str]:
    return [f"{prefix}{idx:0{pad}d}" for idx in range(1, size + 1)]
