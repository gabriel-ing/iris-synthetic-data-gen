from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Counts:
    customers: int
    merchants: int
    cards: int
    transactions: int
    disputes: int


def _default_config() -> dict[str, Any]:
    return {
        "seed": 42,
        "currency": "GBP",
        "time": {
            "start_date": "2026-01-01",
            "days": 90,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "factor": 1,
            "base_counts": {
                "customers": 1000,
                "merchants": 500,
                "cards": 1500,
                "transactions": 10000,
                "disputes": 200,
            },
            "counts": {
                "customers": 1000,
                "merchants": 500,
                "cards": 1500,
                "transactions": 10000,
                "disputes": 200,
            },
        },
        "output": {
            "format": "csv",
            "path": "./out",
            "partition_transactions_by": "none",
            "overwrite": True,
        },
        "behavior": {
            "segments": [
                {
                    "name": "STUDENT",
                    "weight": 0.15,
                    "txn_rate_multiplier": 0.8,
                    "avg_amount_multiplier": 0.7,
                    "ecom_multiplier": 1.4,
                    "decline_multiplier": 1.0,
                    "dispute_multiplier": 1.1,
                },
                {
                    "name": "MASS",
                    "weight": 0.50,
                    "txn_rate_multiplier": 1.0,
                    "avg_amount_multiplier": 1.0,
                    "ecom_multiplier": 1.0,
                    "decline_multiplier": 1.0,
                    "dispute_multiplier": 1.0,
                },
                {
                    "name": "AFFLUENT",
                    "weight": 0.15,
                    "txn_rate_multiplier": 1.2,
                    "avg_amount_multiplier": 1.6,
                    "ecom_multiplier": 0.9,
                    "decline_multiplier": 0.8,
                    "dispute_multiplier": 0.9,
                },
                {
                    "name": "HIGHRISK",
                    "weight": 0.10,
                    "txn_rate_multiplier": 1.0,
                    "avg_amount_multiplier": 1.0,
                    "ecom_multiplier": 1.4,
                    "decline_multiplier": 1.6,
                    "dispute_multiplier": 1.8,
                },
                {
                    "name": "DORMANT",
                    "weight": 0.10,
                    "txn_rate_multiplier": 0.1,
                    "avg_amount_multiplier": 0.8,
                    "ecom_multiplier": 1.0,
                    "decline_multiplier": 1.0,
                    "dispute_multiplier": 1.0,
                },
            ],
            "merchants": {
                "category_weights": {
                    "GROCERY": 0.22,
                    "FUEL": 0.10,
                    "DINING": 0.18,
                    "TRAVEL": 0.08,
                    "RETAIL": 0.30,
                    "DIGITAL": 0.12,
                },
                "risk_tier_weights": {"LOW": 0.80, "MED": 0.15, "HIGH": 0.05},
                "popularity_pareto_alpha": 2.0,
            },
            "transactions": {
                "base_decline_rate": 0.08,
                "base_refund_rate": 0.02,
                "base_ecom_share": 0.20,
                "weekly_seasonality": True,
            },
            "disputes": {
                "target_count": 200,
                "base_rate": 0.02,
                "ecom_multiplier": 2.0,
                "highrisk_customer_multiplier": 2.0,
                "highrisk_merchant_multiplier": 2.5,
                "reason_weights": {
                    "FRAUD": 0.40,
                    "NOT_RECEIVED": 0.25,
                    "DUPLICATE": 0.10,
                    "NOT_AS_DESCRIBED": 0.20,
                    "CANCELLED": 0.05,
                },
                "outcome_weights": {
                    "CUSTOMER_WON": 0.55,
                    "MERCHANT_WON": 0.30,
                    "WITHDRAWN": 0.10,
                    "CHARGEBACK": 0.05,
                },
            },
        },
        "edge_cases": {
            "enable": True,
            "customers_with_no_cards": 10,
            "cards_with_only_declines": 10,
            "blocked_cards_mid_window": 20,
            "fraud_bursts": {
                "count_cards": 8,
                "txns_per_card": 20,
                "burst_hours": 2,
                "amount_range": [1.0, 25.0],
            },
        },
    }


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _selected_base_counts(scale: dict[str, Any]) -> dict[str, int]:
    source = scale["counts"] if scale["mode"] == "explicit" else scale["base_counts"]
    return {key: int(value) for key, value in source.items()}


def _apply_scale_factor_override(config: dict[str, Any], scale_factor_override: int | None) -> dict[str, Any]:
    if scale_factor_override is None:
        return config

    factor = int(scale_factor_override)
    if factor <= 0:
        raise ValueError("scale_factor_override must be a positive integer")

    scale = dict(config["scale"])
    scale["mode"] = "factor"
    scale["factor"] = factor
    scale["base_counts"] = _selected_base_counts(config["scale"])
    config["scale"] = scale
    return config


def _derive_counts(config: dict[str, Any]) -> Counts:
    scale = config["scale"]
    mode = scale["mode"]
    if mode == "explicit":
        counts = scale["counts"]
    elif mode == "factor":
        factor = int(scale.get("factor", 1))
        base_counts = scale["base_counts"]
        counts = {k: int(v * factor) for k, v in base_counts.items()}
    else:
        raise ValueError(f"Unsupported scale.mode: {mode}")

    return Counts(
        customers=int(counts["customers"]),
        merchants=int(counts["merchants"]),
        cards=int(counts["cards"]),
        transactions=int(counts["transactions"]),
        disputes=int(counts["disputes"]),
    )


def load_config(config_path: str | Path, scale_factor_override: int | None = None) -> dict[str, Any]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as f:
        user_cfg = yaml.safe_load(f) or {}

    merged = _deep_merge(_default_config(), user_cfg)
    merged = _apply_scale_factor_override(merged, scale_factor_override)
    counts = _derive_counts(merged)
    merged["resolved_counts"] = {
        "customers": counts.customers,
        "merchants": counts.merchants,
        "cards": counts.cards,
        "transactions": counts.transactions,
        "disputes": counts.disputes,
    }
    merged["behavior"]["disputes"]["target_count"] = counts.disputes
    return merged
