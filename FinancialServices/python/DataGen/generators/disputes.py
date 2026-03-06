from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.rng import normalize_weights


def generate_disputes(config: dict, customers: pd.DataFrame, cards: pd.DataFrame, merchants: pd.DataFrame, transactions: pd.DataFrame, rng) -> pd.DataFrame:
    disputes_cfg = config["behavior"]["disputes"]
    target_count = int(config["resolved_counts"]["disputes"])
    base_rate = float(disputes_cfg["base_rate"])
    ecom_mult = float(disputes_cfg["ecom_multiplier"])
    highrisk_customer_mult = float(disputes_cfg["highrisk_customer_multiplier"])
    highrisk_merchant_mult = float(disputes_cfg["highrisk_merchant_multiplier"])

    tx = transactions.copy()
    tx = tx.merge(cards[["CardId", "Customer"]], left_on="Card", right_on="CardId", how="left")
    tx = tx.merge(customers[["CustomerId", "Segment", "SegmentDisputeMultiplier"]], left_on="Customer", right_on="CustomerId", how="left")
    tx = tx.merge(merchants[["MerchantId", "RiskTier", "Category"]], left_on="Merchant", right_on="MerchantId", how="left")

    p = np.full(len(tx), base_rate, dtype=float)
    p *= np.where(tx["Channel"] == "ECOM", ecom_mult, 1.0)
    p *= tx["SegmentDisputeMultiplier"].to_numpy(dtype=float)
    p *= np.where(tx["Segment"] == "HIGHRISK", highrisk_customer_mult, 1.0)
    p *= np.where(tx["RiskTier"] == "HIGH", highrisk_merchant_mult, 1.0)
    p *= np.where(tx["Category"].isin(["TRAVEL", "DIGITAL"]), 1.4, 1.0)
    p *= np.where(tx["Status"] == "DECLINED", 0.02, 1.0)
    p = np.clip(p, 1e-6, 0.99)

    target_count = min(target_count, len(tx))
    probs = normalize_weights(p)
    selected_idx = rng.choice(np.arange(len(tx)), size=target_count, replace=False, p=probs)
    selected = tx.iloc[selected_idx].copy().reset_index(drop=True)

    opened = pd.to_datetime(selected["PostedAt"], utc=True) + pd.to_timedelta(rng.integers(1, 46, size=target_count), unit="D")
    states = rng.choice(["OPEN", "UNDER_REVIEW", "RESOLVED"], size=target_count, p=[0.15, 0.20, 0.65])
    resolved_at = []
    for i in range(target_count):
        if states[i] == "RESOLVED":
            resolved_at.append((opened.iloc[i] + timedelta(days=int(rng.integers(3, 61)))).strftime("%Y-%m-%dT%H:%M:%SZ"))
        else:
            resolved_at.append(None)

    reason_weights = disputes_cfg["reason_weights"]
    outcome_weights = disputes_cfg["outcome_weights"]
    reasons = list(reason_weights.keys())
    outcomes = list(outcome_weights.keys())
    reason_vals = rng.choice(reasons, size=target_count, p=normalize_weights(list(reason_weights.values())))
    outcome_vals = []
    for state in states:
        if state == "RESOLVED":
            outcome_vals.append(rng.choice(outcomes, p=normalize_weights(list(outcome_weights.values()))))
        else:
            outcome_vals.append(None)

    amounts = selected["Amount"].to_numpy(dtype=float)
    partial = rng.random(target_count) < 0.2
    amounts = np.where(partial, np.round(amounts * rng.uniform(0.3, 0.9, size=target_count), 2), amounts)

    disputes = pd.DataFrame(
        {
            "DisputeId": np.arange(1, target_count + 1),
            "Transactions": selected["TransactionId"].to_numpy(),
            "OpenedAt": opened.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ResolvedAt": resolved_at,
            "ReasonCode": reason_vals,
            "State": states,
            "Outcome": outcome_vals,
            "DisputedAmount": np.round(amounts, 2),
        }
    )
    return disputes
