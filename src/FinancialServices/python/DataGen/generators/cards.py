from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd


def _allocate_cards_to_customers(rng, customer_ids: np.ndarray, card_count: int) -> np.ndarray:
    multipliers = rng.choice([1, 2, 3, 4], size=len(customer_ids), p=[0.72, 0.20, 0.06, 0.02])
    expanded = np.repeat(customer_ids, multipliers)
    rng.shuffle(expanded)
    if len(expanded) >= card_count:
        return expanded[:card_count]
    fill = rng.choice(customer_ids, size=card_count - len(expanded), replace=True)
    return np.concatenate([expanded, fill])


def generate_cards(config: dict, customers: pd.DataFrame, rng) -> pd.DataFrame:
    count = config["resolved_counts"]["cards"]
    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    customer_ids = customers["CustomerId"].to_numpy()
    assigned_customers = _allocate_cards_to_customers(rng, customer_ids, count)

    opened_days_before = rng.integers(1, 365 * 2, size=count)
    opened_seconds = rng.integers(0, 24 * 3600, size=count)
    opened_ts = [
        start_date - timedelta(days=int(d), seconds=int(s))
        for d, s in zip(opened_days_before, opened_seconds)
    ]

    status = rng.choice(["ACTIVE", "BLOCKED", "CLOSED"], size=count, p=[0.90, 0.05, 0.05])
    card_type = rng.choice(["DEBIT", "CREDIT"], size=count, p=[0.65, 0.35])
    closed_at: list[str | None] = []
    for i in range(count):
        if status[i] == "CLOSED":
            days_delta = int(rng.integers(15, 450))
            ts = opened_ts[i] + timedelta(days=days_delta)
            closed_at.append(ts.isoformat())
        else:
            closed_at.append(None)

    limits = []
    for t in card_type:
        if t == "DEBIT":
            limits.append(0)
        else:
            limits.append(int(rng.choice([1000, 2000, 3000, 5000, 8000, 12000], p=[0.16, 0.24, 0.20, 0.18, 0.14, 0.08])))

    suffixes = rng.integers(100000, 999999, size=count)
    df = pd.DataFrame(
        {
            "CardId": range(1, count + 1),
            "Customer": assigned_customers,
            "CardType": card_type,
            "Status": status,
            "OpenedAt": [x.isoformat() for x in opened_ts],
            "ClosedAt": closed_at,
            "CardToken": [f"tok_{i}_{suffixes[i - 1]}" for i in range(1, count + 1)],
            "CreditLimit": limits,
        }
    )
    return df
