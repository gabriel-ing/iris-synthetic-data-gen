from __future__ import annotations

import argparse
import math
from typing import Iterable

import pandas as pd

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


def _normalize_value(value):
    if value is None:
        return ""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float) and math.isnan(value):
        return ""
    if value is pd.NA:
        return ""
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return ""
        if value.tzinfo is not None:
            value = value.tz_convert("UTC").tz_localize(None)
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, str) and "T" in value and value.endswith("Z"):
        return value.replace("T", " ").removesuffix("Z")
    return value


def _iter_rows(df: pd.DataFrame, columns: list[str]) -> Iterable[tuple]:
    for row in df[columns].itertuples(index=False, name=None):
        yield tuple(_normalize_value(value) for value in row)


def _exec_sql(iris, sql: str) -> None:
    stmt = iris.sql.prepare(sql)
    stmt.execute()


def _insert_df(iris, table_name: str, columns: list[str], df: pd.DataFrame, commit_every: int) -> int:
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    stmt = iris.sql.prepare(sql)

    inserted = 0
    for row in _iter_rows(df, columns):
        stmt.execute(*row)
        inserted += 1
        if commit_every > 0 and inserted % commit_every == 0:
            _exec_sql(iris, "COMMIT")

    _exec_sql(iris, "COMMIT")
    return inserted


def _without_object_id(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    return df.sort_values(id_column).drop(columns=[id_column]).reset_index(drop=True)


def _prepare_calendar_for_iris(df: pd.DataFrame) -> pd.DataFrame:
    out = _without_object_id(df, "CalendarId")
    base = pd.Timestamp("1840-12-31")
    parsed = pd.to_datetime(out["CalendarDate"], format="%Y-%m-%d", errors="raise")
    out["CalendarDate"] = (parsed - base).dt.days.astype(int)
    return out


def main(
    config_path: str,
    package: str = "Retail",
    clear_existing: bool = False,
    commit_every: int = 20000,
    scale_factor_override: int | None = None,
) -> dict:
    config = load_config(config_path, scale_factor_override=scale_factor_override)
    seed = int(config["seed"])

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
    print("Validation checks passed:", len(validation.checks))
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings:
            print(" -", warning)

    try:
        import iris
    except ImportError as exc:
        raise ImportError(
            "iris module not found. Run this in IRIS Embedded Python or install intersystems-irispython."
        ) from exc

    tables = {
        "Calendar": f"{package}.Calendar",
        "Role": f"{package}.Roles",
        "Store": f"{package}.Stores",
        "Product": f"{package}.Products",
        "Customer": f"{package}.Customers",
        "User": f"{package}.Users",
        "UserStoreAccess": f"{package}.UserStoreAccess",
        "SupplierProduct": f"{package}.SupplierProduct",
        "Promotion": f"{package}.Promotions",
        "PurchaseOrder": f"{package}.PurchaseOrders",
        "StockTransfer": f"{package}.StockTransfers",
        "SalesTransaction": f"{package}.SalesTransactions",
        "InventorySnapshot": f"{package}.InventorySnapshot",
    }

    if clear_existing:
        delete_order = [
            "InventorySnapshot",
            "SalesTransaction",
            "StockTransfer",
            "PurchaseOrder",
            "Promotion",
            "SupplierProduct",
            "UserStoreAccess",
            "User",
            "Customer",
            "Product",
            "Store",
            "Role",
            "Calendar",
        ]
        for name in delete_order:
            _exec_sql(iris, f"TRUNCATE TABLE {tables[name]}")
            print(f"Truncated {tables[name]}")
        _exec_sql(iris, "COMMIT")

    calendar_cols = [
        "DateKey",
        "CalendarDate",
        "Year",
        "Quarter",
        "Month",
        "WeekOfYear",
        "DayOfWeek",
        "IsWeekend",
        "Season",
        "FiscalPeriod",
        "RetailEvent",
    ]
    role_cols = [
        "RoleName",
        "AccessLevel",
        "ToolTier",
        "CanSeeCostData",
        "CanSeeSupplierData",
        "CanSeeChainwidePricing",
        "CanSeeInventoryForecast",
    ]
    store_cols = [
        "StoreCode",
        "StoreName",
        "StoreFormat",
        "Region",
        "District",
        "City",
        "State",
        "OpenDate",
        "SquareFeet",
        "ActiveFlag",
    ]
    product_cols = [
        "Sku",
        "ProductName",
        "Department",
        "Category",
        "Subcategory",
        "Brand",
        "PrivateLabelFlag",
        "Seasonality",
        "UnitSize",
        "BaseUnitCost",
        "BaseRegularPrice",
        "LaunchDate",
        "DiscontinueDate",
    ]
    user_cols = [
        "UserName",
        "FullName",
        "Email",
        "RoleRef",
        "AccessScope",
        "ToolTier",
        "CategoryScope",
        "Region",
        "PrimaryStore",
        "CreatedAt",
        "ActiveFlag",
    ]
    customer_cols = [
        "CustomerNumber",
        "Segment",
        "LoyaltyTier",
        "HomeStore",
        "PreferredChannel",
        "JoinDate",
        "ActiveFlag",
    ]
    user_store_access_cols = [
        "UserRef",
        "Store",
        "AccessType",
    ]
    supplier_product_cols = [
        "Product",
        "SupplierCode",
        "SupplierName",
        "SupplierCountry",
        "SupplierTier",
        "PreferredSupplierFlag",
        "LeadTimeDays",
        "MinOrderQty",
        "OrderMultipleQty",
        "UnitCost",
        "Currency",
        "RiskScore",
        "ShipMode",
    ]
    promotion_cols = [
        "PromotionCode",
        "Product",
        "Store",
        "StartDate",
        "EndDate",
        "PromoType",
        "DiscountPct",
        "PromoPrice",
        "ExpectedLiftPct",
        "FundingSource",
    ]
    purchase_order_cols = [
        "PoNumber",
        "Store",
        "SupplierProduct",
        "OrderDate",
        "ExpectedReceiptDate",
        "ActualReceiptDate",
        "OrderedQty",
        "ReceivedQty",
        "UnitCost",
        "Status",
        "UrgentFlag",
    ]
    stock_transfer_cols = [
        "TransferNumber",
        "Product",
        "FromStore",
        "ToStore",
        "RequestDate",
        "ShipDate",
        "ReceiptDate",
        "Quantity",
        "Status",
        "ReasonCode",
    ]
    sales_transaction_cols = [
        "TransactionNumber",
        "BasketNumber",
        "TransactionDate",
        "Store",
        "Customer",
        "Product",
        "Channel",
        "PaymentMethod",
        "Units",
        "GrossSalesAmount",
        "DiscountAmount",
        "NetSalesAmount",
        "CogsAmount",
        "Promotion",
        "FulfillmentType",
        "ReturnFlag",
        "StockoutFlag",
    ]
    inventory_snapshot_cols = [
        "SnapshotDate",
        "Store",
        "Product",
        "OnHandQty",
        "ReservedQty",
        "AvailableQty",
        "InTransitQty",
        "OnOrderQty",
        "SafetyStockQty",
        "ReorderPointQty",
        "ReorderTargetQty",
        "UnitCost",
        "RegularPrice",
        "MarkdownPrice",
        "DaysOfSupply",
    ]

    inserted = {
        "Calendar": _insert_df(iris, tables["Calendar"], calendar_cols, _prepare_calendar_for_iris(calendar), commit_every),
        "Role": _insert_df(iris, tables["Role"], role_cols, _without_object_id(roles, "RoleId"), commit_every),
        "Store": _insert_df(iris, tables["Store"], store_cols, _without_object_id(stores, "StoreId"), commit_every),
        "Product": _insert_df(iris, tables["Product"], product_cols, _without_object_id(products, "ProductId"), commit_every),
        "Customer": _insert_df(iris, tables["Customer"], customer_cols, _without_object_id(customers, "CustomerId"), commit_every),
        "User": _insert_df(iris, tables["User"], user_cols, _without_object_id(users, "UserId"), commit_every),
        "UserStoreAccess": _insert_df(iris, tables["UserStoreAccess"], user_store_access_cols, _without_object_id(user_store_access, "UserStoreAccessId"), commit_every),
        "SupplierProduct": _insert_df(iris, tables["SupplierProduct"], supplier_product_cols, _without_object_id(supplier_products, "SupplierProductId"), commit_every),
        "Promotion": _insert_df(iris, tables["Promotion"], promotion_cols, _without_object_id(promotions, "PromotionId"), commit_every),
        "PurchaseOrder": _insert_df(iris, tables["PurchaseOrder"], purchase_order_cols, _without_object_id(purchase_orders, "PurchaseOrderId"), commit_every),
        "StockTransfer": _insert_df(iris, tables["StockTransfer"], stock_transfer_cols, _without_object_id(stock_transfers, "StockTransferId"), commit_every),
        "SalesTransaction": _insert_df(iris, tables["SalesTransaction"], sales_transaction_cols, _without_object_id(sales_transactions, "SalesTransactionId"), commit_every),
        "InventorySnapshot": _insert_df(iris, tables["InventorySnapshot"], inventory_snapshot_cols, _without_object_id(inventory_snapshot, "InventorySnapshotId"), commit_every),
    }
    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate retail data and insert directly into IRIS")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--package", default="Retail", help="IRIS SQL package/schema prefix")
    parser.add_argument("--clear-existing", action="store_true", help="Truncate existing tables before insert")
    parser.add_argument("--commit-every", type=int, default=20000, help="Commit frequency during inserts")
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = main(
        config_path=arguments.config,
        package=arguments.package,
        clear_existing=arguments.clear_existing,
        commit_every=arguments.commit_every,
        scale_factor_override=arguments.scale_factor,
    )
    for key, value in result.items():
        print(f"Inserted {value} rows into {key}")