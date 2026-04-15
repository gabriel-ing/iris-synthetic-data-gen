from __future__ import annotations

import argparse

import pandas as pd

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
    generate_purchase_orders,
    generate_purchase_order_lines,
    generate_sales_orders,
    generate_sales_order_lines,
    generate_shipment_lines,
)
from DataGen.rng import make_rng
from DataGen.validate import validate_all
from DataGen.writer import prepare_output_dir, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic supply chain dataset generator")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


def _summary(
    sales_orders: pd.DataFrame,
    purchase_orders: pd.DataFrame,
    sales_order_lines: pd.DataFrame,
    purchase_order_lines: pd.DataFrame,
    shipment_lines: pd.DataFrame,
    inventory_snapshot_daily: pd.DataFrame,
) -> dict:
    part_ship_rate = float((sales_order_lines["Status"] == "PartShipped").mean())
    cancel_rate = float((sales_order_lines["Status"] == "Cancelled").mean())
    po_closed = float((purchase_order_lines["Status"] == "Closed").mean())
    delayed = float((shipment_lines["ShipmentStatus"] == "Delayed").mean()) if len(shipment_lines) else 0.0
    neg_available = float((inventory_snapshot_daily["AvailableQty"] < 0).mean()) if len(inventory_snapshot_daily) else 0.0

    return {
        "rates": {
            "part_ship_rate": round(part_ship_rate, 4),
            "sales_cancel_rate": round(cancel_rate, 4),
            "po_closed_rate": round(po_closed, 4),
            "shipment_delayed_rate": round(delayed, 4),
            "negative_available_snapshot_rate": round(neg_available, 4),
        },
        "counts": {
            "sales_orders": len(sales_orders),
            "purchase_orders": len(purchase_orders),
            "sales_order_lines": len(sales_order_lines),
            "purchase_order_lines": len(purchase_order_lines),
            "shipment_lines": len(shipment_lines),
            "inventory_snapshot_daily": len(inventory_snapshot_daily),
        },
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config, scale_factor_override=args.scale_factor)
    seed = int(config["seed"])

    out_dir = prepare_output_dir(config["output"]["path"], config["output"].get("overwrite", True))

    dim_date = generate_dim_date(config)
    products = generate_dim_product(config, dim_date, make_rng(seed, "dim_product"))
    locations = generate_dim_location(config, make_rng(seed, "dim_location"))
    suppliers = generate_dim_supplier(config, locations, make_rng(seed, "dim_supplier"))
    customers = generate_dim_customer(config, locations, make_rng(seed, "dim_customer"))

    product_supplier = generate_product_supplier(config, products, suppliers, make_rng(seed, "product_supplier"))

    sales_order_lines = generate_sales_order_lines(
        config,
        dim_date,
        products,
        locations,
        customers,
        make_rng(seed, "sales_order_lines"),
    )
    purchase_order_lines = generate_purchase_order_lines(
        config,
        dim_date,
        product_supplier,
        suppliers,
        locations,
        make_rng(seed, "purchase_order_lines"),
    )
    sales_orders = generate_sales_orders(sales_order_lines)
    purchase_orders = generate_purchase_orders(purchase_order_lines)
    shipment_lines = generate_shipment_lines(
        config,
        dim_date,
        sales_order_lines,
        make_rng(seed, "shipment_lines"),
    )
    stock_count_events = generate_stock_count_events(
        config,
        dim_date,
        products,
        locations,
        make_rng(seed, "stock_count_events"),
    )

    inventory_movements = generate_inventory_movements(
        config,
        dim_date,
        products,
        locations,
        purchase_order_lines,
        shipment_lines,
        stock_count_events,
        make_rng(seed, "inventory_movements"),
    )
    inventory_snapshot_daily = generate_inventory_snapshot_daily(
        dim_date,
        inventory_movements,
        sales_order_lines,
        purchase_order_lines,
        shipment_lines,
    )

    tables = {
        "dim_date": dim_date,
        "dim_product": products,
        "dim_location": locations,
        "dim_supplier": suppliers,
        "dim_customer": customers,
        "product_supplier": product_supplier,
        "sales_orders": sales_orders,
        "purchase_orders": purchase_orders,
        "sales_order_line": sales_order_lines,
        "purchase_order_line": purchase_order_lines,
        "shipment_line": shipment_lines,
        "inventory_movement": inventory_movements,
        "inventory_snapshot_daily": inventory_snapshot_daily,
        "stock_count_event": stock_count_events,
    }
    for name, frame in tables.items():
        write_csv(frame, out_dir, name)

    validation = validate_all(
        config,
        dim_date,
        products,
        locations,
        suppliers,
        customers,
        product_supplier,
        sales_orders,
        purchase_orders,
        sales_order_lines,
        purchase_order_lines,
        shipment_lines,
        inventory_movements,
        inventory_snapshot_daily,
        stock_count_events,
    )

    summary = _summary(sales_orders, purchase_orders, sales_order_lines, purchase_order_lines, shipment_lines, inventory_snapshot_daily)
    print("Validation checks passed:", len(validation.checks))
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings:
            print(" -", warning)
    print("Run summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
