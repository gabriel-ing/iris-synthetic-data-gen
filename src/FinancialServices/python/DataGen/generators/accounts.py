from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd


def generate_accounts(config: dict, customers: pd.DataFrame, rng) -> pd.DataFrame:
    customer_base = customers[["CustomerId", "CreatedAt", "Status", "Segment"]].copy().sort_values("CustomerId").reset_index(drop=True)
    count = len(customer_base)
    if count != int(config["resolved_counts"]["accounts"]):
        raise ValueError("Account count must match customer count in the current Financial Services model")

    created_at = pd.to_datetime(customer_base["CreatedAt"], utc=True)
    segments = customer_base["Segment"].astype(str).to_numpy()
    customer_status = customer_base["Status"].astype(str).to_numpy()

    account_type: list[str] = []
    for segment in segments:
        if segment == "AFFLUENT":
            account_type.append(str(rng.choice(["DEPOSIT", "REVOLVING_CREDIT"], p=[0.35, 0.65])))
        elif segment == "HIGHRISK":
            account_type.append(str(rng.choice(["DEPOSIT", "REVOLVING_CREDIT"], p=[0.55, 0.45])))
        else:
            account_type.append(str(rng.choice(["DEPOSIT", "REVOLVING_CREDIT"], p=[0.62, 0.38])))

    opened_offsets = rng.integers(0, 45, size=count)
    opened_at = created_at + pd.to_timedelta(opened_offsets, unit="D")

    status = np.where(customer_status == "CLOSED", "CLOSED", "ACTIVE")
    closed_offsets = rng.integers(60, 900, size=count)
    closed_at: list[str | None] = []
    for index in range(count):
        if status[index] == "CLOSED":
            closed_at.append((opened_at.iloc[index] + timedelta(days=int(closed_offsets[index]))).isoformat())
        else:
            closed_at.append(None)

    return pd.DataFrame(
        {
            "AccountId": np.arange(1, count + 1),
            "AccountNumber": [f"ACC{i:09d}" for i in range(1, count + 1)],
            "Customer": customer_base["CustomerId"].to_numpy(dtype=int),
            "AccountType": account_type,
            "Status": status,
            "OpenedAt": [value.isoformat() for value in opened_at],
            "ClosedAt": closed_at,
            "BillingCycleDay": rng.integers(1, 29, size=count),
            "AutopayFlag": [(acct_type == "REVOLVING_CREDIT") and bool(rng.random() < 0.44) for acct_type in account_type],
        }
    )