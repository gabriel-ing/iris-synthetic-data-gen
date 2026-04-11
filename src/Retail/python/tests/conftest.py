from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from DataGen.config import load_config
from DataGen.generators.dimensions import (
    generate_calendar,
    generate_products,
    generate_roles,
    generate_stores,
    generate_user_store_access,
    generate_users,
)
from DataGen.generators.operations import generate_inventory_snapshot, generate_sales_transactions
from DataGen.generators.planning import (
    generate_promotions,
    generate_purchase_orders,
    generate_stock_transfers,
    generate_supplier_product,
)
from DataGen.rng import make_rng


def build_dataset(config: dict) -> dict[str, pd.DataFrame]:
    seed = int(config["seed"])
    calendar = generate_calendar(config)
    roles = generate_roles()
    stores = generate_stores(config, make_rng(seed, "stores"))
    products = generate_products(config, calendar, make_rng(seed, "products"))
    users = generate_users(config, roles, stores, make_rng(seed, "users"))
    user_store_access = generate_user_store_access(config, users, stores, make_rng(seed, "user_store_access"))
    supplier_product = generate_supplier_product(config, products, make_rng(seed, "supplier_product"))
    promotions = generate_promotions(config, calendar, stores, products, make_rng(seed, "promotions"))
    purchase_orders = generate_purchase_orders(config, calendar, stores, supplier_product, make_rng(seed, "purchase_orders"))
    stock_transfers = generate_stock_transfers(config, calendar, stores, products, make_rng(seed, "stock_transfers"))
    sales_transactions = generate_sales_transactions(config, calendar, stores, products, promotions, make_rng(seed, "sales_transactions"))
    inventory_snapshot = generate_inventory_snapshot(
        config,
        calendar,
        stores,
        products,
        supplier_product,
        promotions,
        purchase_orders,
        stock_transfers,
        sales_transactions,
        make_rng(seed, "inventory_snapshot"),
    )

    return {
        "calendar": calendar,
        "roles": roles,
        "users": users,
        "user_store_access": user_store_access,
        "stores": stores,
        "products": products,
        "supplier_product": supplier_product,
        "promotions": promotions,
        "purchase_orders": purchase_orders,
        "stock_transfers": stock_transfers,
        "sales_transactions": sales_transactions,
        "inventory_snapshot": inventory_snapshot,
    }


def write_config(tmp_path: Path, data: dict) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return config_path


def small_config_dict(tmp_path: Path, seed: int = 42) -> dict:
    return {
        "seed": seed,
        "currency": "USD",
        "time": {
            "start_date": "2026-01-01",
            "days": 35,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "users": 18,
                "stores": 12,
                "products": 64,
                "supplier_products": 140,
                "promotions": 28,
                "purchase_orders": 120,
                "stock_transfers": 45,
                "sales_transactions": 950,
                "inventory_snapshots": 520,
            },
        },
        "output": {
            "path": str(tmp_path / "out_retail"),
            "overwrite": True,
        },
    }


def load_small_config(tmp_path: Path, seed: int = 42) -> dict:
    cfg = small_config_dict(tmp_path, seed=seed)
    path = write_config(tmp_path, cfg)
    return load_config(path)
