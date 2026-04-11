from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Counts:
    products: int
    locations: int
    suppliers: int
    customers: int
    product_suppliers: int
    sales_order_lines: int
    purchase_order_lines: int
    stock_count_events: int


def _default_config() -> dict[str, Any]:
    return {
        "seed": 42,
        "time": {
            "start_date": "2026-01-01",
            "days": 365,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "factor": 1,
            "base_counts": {
                "products": 600,
                "locations": 80,
                "suppliers": 120,
                "customers": 1500,
                "product_suppliers": 1500,
                "sales_order_lines": 20000,
                "purchase_order_lines": 8000,
                "stock_count_events": 400,
            },
            "counts": {
                "products": 600,
                "locations": 80,
                "suppliers": 120,
                "customers": 1500,
                "product_suppliers": 1500,
                "sales_order_lines": 20000,
                "purchase_order_lines": 8000,
                "stock_count_events": 400,
            },
        },
        "output": {
            "path": "./out_supply_chain",
            "overwrite": True,
        },
        "behavior": {
            "product_categories": {
                "GROCERY": 0.28,
                "BEVERAGE": 0.14,
                "HOUSEHOLD": 0.18,
                "PERSONAL_CARE": 0.12,
                "ELECTRONICS": 0.10,
                "APPAREL": 0.10,
                "SEASONAL": 0.08,
            },
            "location_type_weights": {
                "Dc": 0.12,
                "Store": 0.55,
                "CustomerSite": 0.23,
                "SupplierSite": 0.10,
            },
            "customer_segment_weights": {
                "Value": 0.45,
                "Standard": 0.40,
                "Premium": 0.15,
            },
            "sales": {
                "channel_weights": {
                    "Store": 0.55,
                    "Ecomm": 0.30,
                    "B2B": 0.15,
                },
                "cancel_rate": 0.03,
                "partial_ship_rate": 0.20,
            },
            "purchase_orders": {
                "partial_receipt_rate": 0.18,
                "cancel_rate": 0.03,
                "late_receipt_rate": 0.12,
            },
            "shipments": {
                "split_shipment_rate": 0.25,
                "delay_rate": 0.11,
            },
            "inventory": {
                "initial_stock_min": 40,
                "initial_stock_max": 320,
                "adjustment_rate": 0.015,
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
        products=int(counts["products"]),
        locations=int(counts["locations"]),
        suppliers=int(counts["suppliers"]),
        customers=int(counts["customers"]),
        product_suppliers=int(counts["product_suppliers"]),
        sales_order_lines=int(counts["sales_order_lines"]),
        purchase_order_lines=int(counts["purchase_order_lines"]),
        stock_count_events=int(counts["stock_count_events"]),
    )


def load_config(config_path: str | Path, scale_factor_override: int | None = None) -> dict[str, Any]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as f:
        user_cfg = yaml.safe_load(f) or {}

    merged = _deep_merge(_default_config(), user_cfg)
    merged = _apply_scale_factor_override(merged, scale_factor_override)
    counts = _derive_counts(merged)
    merged["resolved_counts"] = {
        "days": int(merged["time"]["days"]),
        "products": counts.products,
        "locations": counts.locations,
        "suppliers": counts.suppliers,
        "customers": counts.customers,
        "product_suppliers": counts.product_suppliers,
        "sales_order_lines": counts.sales_order_lines,
        "purchase_order_lines": counts.purchase_order_lines,
        "stock_count_events": counts.stock_count_events,
    }
    return merged
