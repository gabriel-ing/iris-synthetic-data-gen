from __future__ import annotations

import math
from typing import Iterable

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
    generate_purchase_order_lines,
    generate_sales_order_lines,
    generate_shipment_lines,
)
from DataGen.rng import make_rng
from DataGen.validate import validate_all


def _summary(
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
            "sales_order_lines": len(sales_order_lines),
            "purchase_order_lines": len(purchase_order_lines),
            "shipment_lines": len(shipment_lines),
            "inventory_snapshot_daily": len(inventory_snapshot_daily),
        },
    }


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
            return None
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
        yield tuple(_normalize_value(v) for v in row)


def _exec_sql(iris, sql: str) -> None:
    stmt = iris.sql.prepare(sql)
    stmt.execute()


def _insert_df(iris, table_name: str, columns: list[str], df: pd.DataFrame, commit_every: int) -> int:
    placeholders = ", ".join(["?"] * len(columns))
    col_sql = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({col_sql}) VALUES ({placeholders})"
    stmt = iris.sql.prepare(sql)

    inserted = 0
    for row in _iter_rows(df, columns):
        try:
            stmt.execute(*row)
        except Exception:
            print(f"SQL insert failed for {table_name} at row {inserted + 1}")
            for col, val in zip(columns, row):
                print(f"  {col}: {val!r} ({type(val).__name__})")
            raise
        inserted += 1
        if commit_every > 0 and inserted % commit_every == 0:
            _exec_sql(iris, "COMMIT")

    _exec_sql(iris, "COMMIT")
    return inserted


def _without_object_id(df: pd.DataFrame, id_column: str) -> pd.DataFrame:
    # Insert in deterministic ID order, but let IRIS generate RowIDs.
    return df.sort_values(id_column).drop(columns=[id_column]).reset_index(drop=True)


def _prepare_dim_date_for_iris(df: pd.DataFrame) -> pd.DataFrame:
    out = _without_object_id(df, "DateId")
    base = pd.Timestamp("1840-12-31")
    parsed = pd.to_datetime(out["CalendarDate"], format="%Y-%m-%d", errors="raise")
    out["CalendarDate"] = (parsed - base).dt.days.astype(int)
    return out


def _prepare_dim_product_for_iris(df: pd.DataFrame) -> pd.DataFrame:
    out = _without_object_id(df, "ProductId")
    out["ShelfLifeDays"] = pd.to_numeric(out["ShelfLifeDays"], errors="coerce").round().astype("Int64")
    return out


def main(
    config_path: str,
    package: str = "SupplyChain",
    clear_existing: bool = False,
    commit_every: int = 20000,
    scale_factor_override: int | None = None,
) -> dict:
    config = load_config(config_path, scale_factor_override=scale_factor_override)
    seed = int(config["seed"])

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

    validation = validate_all(
        config,
        dim_date,
        products,
        locations,
        suppliers,
        customers,
        product_supplier,
        sales_order_lines,
        purchase_order_lines,
        shipment_lines,
        inventory_movements,
        inventory_snapshot_daily,
        stock_count_events,
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

    pkg = package
    tables = {
        "DimDate": f"{pkg}.DimDate",
        "DimProduct": f"{pkg}.DimProduct",
        "DimLocation": f"{pkg}.DimLocation",
        "DimSupplier": f"{pkg}.DimSupplier",
        "DimCustomer": f"{pkg}.DimCustomer",
        "ProductSupplier": f"{pkg}.ProductSupplier",
        "SalesOrderLine": f"{pkg}.SalesOrderLine",
        "PurchaseOrderLine": f"{pkg}.PurchaseOrderLine",
        "ShipmentLine": f"{pkg}.ShipmentLine",
        "StockCountEvent": f"{pkg}.StockCountEvent",
        "InventoryMovement": f"{pkg}.InventoryMovement",
        "InventorySnapshotDaily": f"{pkg}.InventorySnapshotDaily",
    }

    # Clear children first to respect object-reference constraints.
    if clear_existing:
        delete_order = [
            "InventorySnapshotDaily",
            "InventoryMovement",
            "StockCountEvent",
            "ShipmentLine",
            "PurchaseOrderLine",
            "SalesOrderLine",
            "ProductSupplier",
            "DimCustomer",
            "DimSupplier",
            "DimLocation",
            "DimProduct",
            "DimDate",
        ]
        for key in delete_order:
            _exec_sql(iris, f"TRUNCATE TABLE {tables[key]}")
            print(f"Truncated {tables[key]}")
        _exec_sql(iris, "COMMIT")

    dim_date_cols = [
        "DateKey",
        "CalendarDate",
        "Year",
        "Quarter",
        "Month",
        "WeekOfYear",
        "DayOfWeek",
        "IsWeekend",
    ]
    dim_product_cols = [
        "Sku",
        "ProductName",
        "Brand",
        "Category",
        "Subcategory",
        "Uom",
        "UnitsPerCase",
        "UnitWeightKg",
        "UnitVolumeM3",
        "TemperatureZone",
        "IsPerishable",
        "ShelfLifeDays",
        "StandardCost",
        "ListPrice",
        "LaunchDate",
        "DiscontinueDate",
    ]
    dim_location_cols = [
        "LocationCode",
        "LocationName",
        "LocationType",
        "Country",
        "Region",
        "City",
        "Postcode",
        "TimeZone",
        "IsActive",
    ]
    dim_supplier_cols = [
        "SupplierCode",
        "SupplierName",
        "SupplierTier",
        "Country",
        "PreferredFlag",
        "PaymentTermsDays",
        "RiskScore",
        "DefaultShipFromLocation",
    ]
    dim_customer_cols = [
        "CustomerNumber",
        "CustomerName",
        "CustomerType",
        "Segment",
        "Country",
        "Region",
        "ServiceLevelTargetPct",
        "DefaultShipToLocation",
    ]
    product_supplier_cols = [
        "Product",
        "Supplier",
        "IsPrimarySupplier",
        "MinOrderQty",
        "OrderMultipleQty",
        "PackSize",
        "PlannedLeadTimeDays",
        "UnitPurchaseCost",
        "Incoterm",
        "ShipMode",
    ]
    sales_order_line_cols = [
        "SalesOrderId",
        "LineNumber",
        "Customer",
        "Product",
        "ShipFromLocation",
        "ShipToLocation",
        "OrderDate",
        "RequestedShipDate",
        "PromisedDeliveryDate",
        "ActualDeliveryDate",
        "OrderedQty",
        "AllocatedQty",
        "ShippedQty",
        "BackorderedQty",
        "UnitSellPrice",
        "Status",
        "Channel",
    ]
    purchase_order_line_cols = [
        "PurchaseOrderId",
        "LineNumber",
        "Supplier",
        "Product",
        "ShipFromLocation",
        "DeliverToLocation",
        "OrderDate",
        "ExpectedReceiptDate",
        "ReceiptDate",
        "OrderedQty",
        "ReceivedQty",
        "UnitPurchaseCost",
        "Status",
        "CancelReason",
        "PlannedLeadTimeDays",
        "ActualLeadTimeDays",
    ]
    shipment_line_cols = [
        "ShipmentId",
        "LineNumber",
        "SalesOrderLine",
        "Product",
        "OriginLocation",
        "DestinationLocation",
        "ShipDate",
        "DeliveryDate",
        "ShippedQty",
        "CarrierName",
        "ServiceLevel",
        "PlannedTransitDays",
        "ActualTransitDays",
        "FreightCost",
        "ShipmentStatus",
        "DelayReason",
    ]
    stock_count_event_cols = [
        "Location",
        "Product",
        "CountDate",
        "SystemQty",
        "CountedQty",
        "VarianceQty",
        "VarianceReason",
    ]
    inventory_movement_cols = [
        "Product",
        "FromLocation",
        "ToLocation",
        "MovementDate",
        "MovementTimestamp",
        "MovementType",
        "ReferenceType",
        "ReferenceId",
        "Qty",
        "UnitCost",
        "ReasonCode",
    ]
    inventory_snapshot_daily_cols = [
        "SnapshotDate",
        "Product",
        "Location",
        "OnHandQty",
        "AllocatedQty",
        "AvailableQty",
        "InTransitQty",
        "SafetyStockQty",
        "OnOrderQty",
        "InventoryValue",
    ]

    inserted = _insert_df(iris, tables["DimDate"], dim_date_cols, _prepare_dim_date_for_iris(dim_date), commit_every)
    print(f"Inserted {inserted:,} rows into {tables['DimDate']}")
    inserted = _insert_df(
        iris,
        tables["DimProduct"],
        dim_product_cols,
        _prepare_dim_product_for_iris(products),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['DimProduct']}")
    inserted = _insert_df(
        iris,
        tables["DimLocation"],
        dim_location_cols,
        _without_object_id(locations, "LocationId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['DimLocation']}")
    inserted = _insert_df(
        iris,
        tables["DimSupplier"],
        dim_supplier_cols,
        _without_object_id(suppliers, "SupplierId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['DimSupplier']}")
    inserted = _insert_df(
        iris,
        tables["DimCustomer"],
        dim_customer_cols,
        _without_object_id(customers, "CustomerId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['DimCustomer']}")
    inserted = _insert_df(
        iris,
        tables["ProductSupplier"],
        product_supplier_cols,
        _without_object_id(product_supplier, "ProductSupplierId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['ProductSupplier']}")
    inserted = _insert_df(
        iris,
        tables["SalesOrderLine"],
        sales_order_line_cols,
        _without_object_id(sales_order_lines, "SalesOrderLineId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['SalesOrderLine']}")
    inserted = _insert_df(
        iris,
        tables["PurchaseOrderLine"],
        purchase_order_line_cols,
        _without_object_id(purchase_order_lines, "PurchaseOrderLineId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['PurchaseOrderLine']}")
    inserted = _insert_df(
        iris,
        tables["ShipmentLine"],
        shipment_line_cols,
        _without_object_id(shipment_lines, "ShipmentLineId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['ShipmentLine']}")
    inserted = _insert_df(
        iris,
        tables["StockCountEvent"],
        stock_count_event_cols,
        _without_object_id(stock_count_events, "StockCountEventId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['StockCountEvent']}")
    inserted = _insert_df(
        iris,
        tables["InventoryMovement"],
        inventory_movement_cols,
        _without_object_id(inventory_movements, "InventoryMovementId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['InventoryMovement']}")
    inserted = _insert_df(
        iris,
        tables["InventorySnapshotDaily"],
        inventory_snapshot_daily_cols,
        _without_object_id(inventory_snapshot_daily, "InventorySnapshotDailyId"),
        commit_every,
    )
    print(f"Inserted {inserted:,} rows into {tables['InventorySnapshotDaily']}")

    summary = _summary(sales_order_lines, purchase_order_lines, shipment_lines, inventory_snapshot_daily)
    print("Run summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")

    return summary


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic supply chain data and insert directly into IRIS (no CSV files)."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--package", default="SupplyChain", help="IRIS SQL package/schema prefix")
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Delete existing rows before insert (child tables first)",
    )
    parser.add_argument(
        "--commit-every",
        type=int,
        default=20000,
        help="Issue SQL COMMIT every N inserted rows per table",
    )
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(
        config_path=args.config,
        package=args.package,
        clear_existing=args.clear_existing,
        commit_every=args.commit_every,
        scale_factor_override=args.scale_factor,
    )
