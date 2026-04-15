from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Counts:
    customers: int
    users: int
    stores: int
    products: int
    supplier_products: int
    promotions: int
    purchase_orders: int
    stock_transfers: int
    sales_transactions: int
    inventory_snapshots: int


def _default_config() -> dict[str, Any]:
    return {
        "seed": 42,
        "currency": "USD",
        "time": {
            "start_date": "2026-01-01",
            "days": 90,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "factor": 1,
            "base_counts": {
                "users": 48,
                "stores": 36,
                "products": 320,
                "supplier_products": 780,
                "promotions": 140,
                "purchase_orders": 1200,
                "stock_transfers": 320,
                "sales_transactions": 18000,
                "inventory_snapshots": 9000,
            },
            "counts": {
                "users": 48,
                "stores": 36,
                "products": 320,
                "supplier_products": 780,
                "promotions": 140,
                "purchase_orders": 1200,
                "stock_transfers": 320,
                "sales_transactions": 18000,
                "inventory_snapshots": 9000,
            },
        },
        "output": {
            "path": "./out_retail",
            "overwrite": True,
        },
        "behavior": {
            "products": {
                "department_weights": {
                    "GROCERY": 0.23,
                    "BEVERAGE": 0.14,
                    "HOUSEHOLD": 0.17,
                    "PERSONAL_CARE": 0.12,
                    "ELECTRONICS": 0.11,
                    "APPAREL": 0.13,
                    "TOYS": 0.10,
                },
                "private_label_share": 0.24,
            },
            "stores": {
                "format_weights": {
                    "FLAGSHIP": 0.12,
                    "SUBURBAN": 0.42,
                    "URBAN": 0.26,
                    "OUTLET": 0.20,
                }
            },
            "access": {
                "role_weights": {
                    "StoreLead": 0.42,
                    "RegionalViewer": 0.30,
                    "MerchandisingManager": 0.16,
                    "InventoryOpsManager": 0.12,
                },
                "partial_store_min": 2,
                "partial_store_max": 8,
            },
            "sales": {
                "channel_weights": {
                    "INSTORE": 0.74,
                    "CLICK_COLLECT": 0.11,
                    "DELIVERY": 0.09,
                    "SHIP_FROM_STORE": 0.06,
                },
                "return_rate": 0.045,
                "stockout_rate": 0.035,
                "promo_attach_rate": 0.72,
            },
            "supply": {
                "preferred_supplier_share": 0.55,
                "late_po_rate": 0.14,
                "transfer_delay_rate": 0.09,
            },
            "promotions": {
                "chainwide_share": 0.38,
                "type_weights": {
                    "PCT_OFF": 0.54,
                    "MULTIBUY": 0.18,
                    "CLEARANCE": 0.18,
                    "DIGITAL_COUPON": 0.10,
                },
            },
            "inventory": {
                "low_stock_share": 0.16,
                "markdown_share": 0.12,
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
        counts = {key: int(value * factor) for key, value in base_counts.items()}
    else:
        raise ValueError(f"Unsupported scale.mode: {mode}")

    return Counts(
        customers=max(500, int(counts["sales_transactions"]) // 3),
        users=int(counts["users"]),
        stores=int(counts["stores"]),
        products=int(counts["products"]),
        supplier_products=int(counts["supplier_products"]),
        promotions=int(counts["promotions"]),
        purchase_orders=int(counts["purchase_orders"]),
        stock_transfers=int(counts["stock_transfers"]),
        sales_transactions=int(counts["sales_transactions"]),
        inventory_snapshots=int(counts["inventory_snapshots"]),
    )


def load_config(config_path: str | Path, scale_factor_override: int | None = None) -> dict[str, Any]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as handle:
        user_cfg = yaml.safe_load(handle) or {}

    merged = _deep_merge(_default_config(), user_cfg)
    merged = _apply_scale_factor_override(merged, scale_factor_override)
    counts = _derive_counts(merged)
    merged["resolved_counts"] = {
        "days": int(merged["time"]["days"]),
        "customers": counts.customers,
        "users": counts.users,
        "stores": counts.stores,
        "products": counts.products,
        "supplier_products": counts.supplier_products,
        "promotions": counts.promotions,
        "purchase_orders": counts.purchase_orders,
        "stock_transfers": counts.stock_transfers,
        "sales_transactions": counts.sales_transactions,
        "inventory_snapshots": counts.inventory_snapshots,
        "roles": 4,
    }
    return merged
