from __future__ import annotations

import hashlib

import numpy as np


def sub_seed(master_seed: int, namespace: str) -> int:
    payload = f"{master_seed}:{namespace}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return int(digest[:16], 16) % (2**32)


def make_rng(master_seed: int, namespace: str) -> np.random.Generator:
    return np.random.default_rng(sub_seed(master_seed, namespace))


def normalize_weights(values: list[float] | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = arr.sum()
    if total <= 0:
        raise ValueError("Weights must sum to a positive value")
    return arr / total
