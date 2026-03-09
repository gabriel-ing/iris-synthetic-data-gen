from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from DataGen.config import load_config
from DataGen.generators.dimensions import (
    generate_dim_customer,
    generate_dim_date,
    generate_dim_location,
    generate_dim_product,
    generate_dim_supplier,
    generate_product_supplier,
)
from DataGen.generators.inventory import (
    generate_inventory_movements,
    generate_inventory_snapshot_daily,
    generate_stock_count_events,
)
from DataGen.generators.orders import (
    generate_purchase_order_lines,
    generate_sales_order_lines,
    generate_shipment_lines,
)
from DataGen.rng import make_rng


def build_dataset(config: dict) -> dict[str, pd.DataFrame]:
    seed = int(config["seed"])
    dim_date = generate_dim_date(config)
    products = generate_dim_product(config, dim_date, make_rng(seed, "dim_product"))
    locations = generate_dim_location(config, make_rng(seed, "dim_location"))
    suppliers = generate_dim_supplier(config, locations, make_rng(seed, "dim_supplier"))
    customers = generate_dim_customer(config, locations, make_rng(seed, "dim_customer"))
    product_supplier = generate_product_supplier(config, products, suppliers, make_rng(seed, "product_supplier"))
    sales_order_lines = generate_sales_order_lines(config, dim_date, products, locations, customers, make_rng(seed, "sales_order_lines"))
    purchase_order_lines = generate_purchase_order_lines(config, dim_date, product_supplier, suppliers, locations, make_rng(seed, "purchase_order_lines"))
    shipment_lines = generate_shipment_lines(config, dim_date, sales_order_lines, make_rng(seed, "shipment_lines"))
    stock_count_events = generate_stock_count_events(config, dim_date, products, locations, make_rng(seed, "stock_count_events"))
    inventory_movements = generate_inventory_movements(config, dim_date, products, locations, purchase_order_lines, shipment_lines, stock_count_events, make_rng(seed, "inventory_movements"))
    inventory_snapshot_daily = generate_inventory_snapshot_daily(dim_date, inventory_movements, sales_order_lines, purchase_order_lines, shipment_lines)

    return {
        "dim_date": dim_date,
        "dim_product": products,
        "dim_location": locations,
        "dim_supplier": suppliers,
        "dim_customer": customers,
        "product_supplier": product_supplier,
        "sales_order_line": sales_order_lines,
        "purchase_order_line": purchase_order_lines,
        "shipment_line": shipment_lines,
        "stock_count_event": stock_count_events,
        "inventory_movement": inventory_movements,
        "inventory_snapshot_daily": inventory_snapshot_daily,
    }


def write_config(tmp_path: Path, data: dict) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return config_path


def small_config_dict(tmp_path: Path, seed: int = 42) -> dict:
    return {
        "seed": seed,
        "time": {
            "start_date": "2026-01-01",
            "days": 45,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "products": 45,
                "locations": 20,
                "suppliers": 15,
                "customers": 80,
                "product_suppliers": 90,
                "sales_order_lines": 550,
                "purchase_order_lines": 220,
                "stock_count_events": 35,
            },
        },
        "output": {
            "path": str(tmp_path / "out_supply_chain"),
            "overwrite": True,
        },
    }


def load_small_config(tmp_path: Path, seed: int = 42) -> dict:
    cfg = small_config_dict(tmp_path, seed=seed)
    path = write_config(tmp_path, cfg)
    return load_config(path)
