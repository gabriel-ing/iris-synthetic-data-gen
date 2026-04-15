from __future__ import annotations

import argparse

from DataGen.config import load_config
from DataGen.generators.dimensions import (
    generate_calendar,
    generate_customers,
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
from DataGen.validate import validate_all
from DataGen.writer import prepare_output_dir, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic retail dataset generator")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


def _summary(customers, users, user_store_access, stores, products, promotions, sales_transactions, inventory_snapshot) -> dict:
    full_user_share = float((users["AccessScope"] == "FULL").mean())
    promo_penetration = float(sales_transactions["Promotion"].notna().mean())
    return_rate = float(sales_transactions["ReturnFlag"].mean())
    low_stock_rate = float((inventory_snapshot["OnHandQty"] < inventory_snapshot["ReorderPointQty"]).mean())
    markdown_rate = float(inventory_snapshot["MarkdownPrice"].notna().mean())
    baskets_per_customer = float(sales_transactions["BasketNumber"].nunique() / max(1, len(customers)))

    top_departments = (
        sales_transactions.merge(products[["ProductId", "Department"]], left_on="Product", right_on="ProductId", how="left")
        .groupby("Department", observed=True)["NetSalesAmount"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .round(2)
        .to_dict()
    )

    return {
        "counts": {
            "customers": len(customers),
            "users": len(users),
            "user_store_access": len(user_store_access),
            "stores": len(stores),
            "products": len(products),
            "promotions": len(promotions),
            "sales_transactions": len(sales_transactions),
            "inventory_snapshot": len(inventory_snapshot),
        },
        "rates": {
            "full_user_share": round(full_user_share, 4),
            "promo_penetration": round(promo_penetration, 4),
            "return_rate": round(return_rate, 4),
            "low_stock_rate": round(low_stock_rate, 4),
            "markdown_rate": round(markdown_rate, 4),
            "baskets_per_customer": round(baskets_per_customer, 4),
        },
        "top_departments_by_net_sales": top_departments,
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config, scale_factor_override=args.scale_factor)
    seed = int(config["seed"])

    out_dir = prepare_output_dir(config["output"]["path"], config["output"].get("overwrite", True))

    calendar = generate_calendar(config)
    roles = generate_roles()
    stores = generate_stores(config, make_rng(seed, "stores"))
    products = generate_products(config, calendar, make_rng(seed, "products"))
    customers = generate_customers(config, stores, make_rng(seed, "customers"))
    users = generate_users(config, roles, stores, make_rng(seed, "users"))
    user_store_access = generate_user_store_access(config, users, stores, make_rng(seed, "user_store_access"))
    supplier_products = generate_supplier_product(config, products, make_rng(seed, "supplier_product"))
    promotions = generate_promotions(config, calendar, stores, products, make_rng(seed, "promotions"))
    purchase_orders = generate_purchase_orders(config, calendar, stores, supplier_products, make_rng(seed, "purchase_orders"))
    stock_transfers = generate_stock_transfers(config, calendar, stores, products, make_rng(seed, "stock_transfers"))
    sales_transactions = generate_sales_transactions(config, calendar, stores, products, promotions, customers, make_rng(seed, "sales_transactions"))
    inventory_snapshot = generate_inventory_snapshot(
        config,
        calendar,
        stores,
        products,
        supplier_products,
        promotions,
        purchase_orders,
        stock_transfers,
        sales_transactions,
        make_rng(seed, "inventory_snapshot"),
    )

    tables = {
        "calendar": calendar,
        "roles": roles,
        "customers": customers,
        "users": users,
        "user_store_access": user_store_access,
        "stores": stores,
        "products": products,
        "supplier_product": supplier_products,
        "promotions": promotions,
        "purchase_orders": purchase_orders,
        "stock_transfers": stock_transfers,
        "sales_transactions": sales_transactions,
        "inventory_snapshot": inventory_snapshot,
    }
    for name, frame in tables.items():
        write_csv(frame, out_dir, name)

    validation = validate_all(
        config,
        calendar,
        roles,
        customers,
        users,
        user_store_access,
        stores,
        products,
        supplier_products,
        promotions,
        purchase_orders,
        stock_transfers,
        sales_transactions,
        inventory_snapshot,
    )
    summary = _summary(customers, users, user_store_access, stores, products, promotions, sales_transactions, inventory_snapshot)

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
