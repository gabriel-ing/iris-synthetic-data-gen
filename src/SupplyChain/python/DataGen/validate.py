from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ValidationResult:
    ok: bool
    checks: list[str]
    warnings: list[str]


def _assert(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise ValueError(message)
    checks.append(message)


def validate_all(
    config: dict,
    dim_date: pd.DataFrame,
    products: pd.DataFrame,
    locations: pd.DataFrame,
    suppliers: pd.DataFrame,
    customers: pd.DataFrame,
    product_supplier: pd.DataFrame,
    sales_orders: pd.DataFrame,
    purchase_orders: pd.DataFrame,
    sales_order_lines: pd.DataFrame,
    purchase_order_lines: pd.DataFrame,
    shipment_lines: pd.DataFrame,
    inventory_movements: pd.DataFrame,
    inventory_snapshot_daily: pd.DataFrame,
    stock_count_events: pd.DataFrame,
) -> ValidationResult:
    checks: list[str] = []
    warnings: list[str] = []

    date_ids = set(dim_date["DateId"].tolist())
    product_ids = set(products["ProductId"].tolist())
    location_ids = set(locations["LocationId"].tolist())
    supplier_ids = set(suppliers["SupplierId"].tolist())
    customer_ids = set(customers["CustomerId"].tolist())

    _assert(product_supplier["Product"].isin(product_ids).all(), "FK product_supplier.product valid", checks)
    _assert(product_supplier["Supplier"].isin(supplier_ids).all(), "FK product_supplier.supplier valid", checks)

    _assert(sales_orders["Customer"].isin(customer_ids).all(), "FK sales_orders.customer valid", checks)
    _assert(sales_orders["ShipFromLocation"].isin(location_ids).all(), "FK sales_orders.ship_from valid", checks)
    _assert(sales_orders["ShipToLocation"].isin(location_ids).all(), "FK sales_orders.ship_to valid", checks)
    _assert(purchase_orders["Supplier"].isin(supplier_ids).all(), "FK purchase_orders.supplier valid", checks)
    _assert(purchase_orders["ShipFromLocation"].isin(location_ids).all(), "FK purchase_orders.ship_from valid", checks)
    _assert(purchase_orders["DeliverToLocation"].isin(location_ids).all(), "FK purchase_orders.deliver_to valid", checks)

    _assert(sales_order_lines["Customer"].isin(customer_ids).all(), "FK sales_order.customer valid", checks)
    _assert(sales_order_lines["Product"].isin(product_ids).all(), "FK sales_order.product valid", checks)
    _assert(sales_order_lines["ShipFromLocation"].isin(location_ids).all(), "FK sales_order.ship_from valid", checks)
    _assert(sales_order_lines["ShipToLocation"].isin(location_ids).all(), "FK sales_order.ship_to valid", checks)

    _assert(purchase_order_lines["Supplier"].isin(supplier_ids).all(), "FK po.supplier valid", checks)
    _assert(purchase_order_lines["Product"].isin(product_ids).all(), "FK po.product valid", checks)
    _assert(purchase_order_lines["ShipFromLocation"].isin(location_ids).all(), "FK po.ship_from valid", checks)
    _assert(purchase_order_lines["DeliverToLocation"].isin(location_ids).all(), "FK po.deliver_to valid", checks)

    if not shipment_lines.empty:
        _assert(shipment_lines["SalesOrderLine"].isin(sales_order_lines["SalesOrderLineId"]).all(), "FK shipment.sales_order_line valid", checks)
        _assert(shipment_lines["Product"].isin(product_ids).all(), "FK shipment.product valid", checks)
        _assert(shipment_lines["OriginLocation"].isin(location_ids).all(), "FK shipment.origin valid", checks)
        _assert(shipment_lines["DestinationLocation"].isin(location_ids).all(), "FK shipment.destination valid", checks)

    _assert(inventory_movements["Product"].isin(product_ids).all(), "FK movement.product valid", checks)
    _assert(inventory_movements["MovementDate"].isin(date_ids).all(), "FK movement.date valid", checks)
    _assert(stock_count_events["Location"].isin(location_ids).all(), "FK stock_count.location valid", checks)
    _assert(stock_count_events["Product"].isin(product_ids).all(), "FK stock_count.product valid", checks)
    _assert(stock_count_events["CountDate"].isin(date_ids).all(), "FK stock_count.date valid", checks)

    for col in ["OrderDate", "RequestedShipDate", "PromisedDeliveryDate"]:
        _assert(sales_order_lines[col].isin(date_ids).all(), f"FK sales_order.{col} valid", checks)
    actual_dates = sales_order_lines["ActualDeliveryDate"].dropna()
    _assert(actual_dates.isin(date_ids).all(), "FK sales_order.actual_delivery valid", checks)

    _assert((sales_order_lines["RequestedShipDate"] >= sales_order_lines["OrderDate"]).all(), "Sales requested ship after order", checks)
    _assert((sales_order_lines["PromisedDeliveryDate"] >= sales_order_lines["RequestedShipDate"]).all(), "Sales promised delivery after request", checks)

    if not shipment_lines.empty:
        ship_date_ok = shipment_lines["ShipDate"].isin(date_ids).all()
        _assert(ship_date_ok, "FK shipment.ship_date valid", checks)
        delivered = shipment_lines["DeliveryDate"].dropna()
        _assert(delivered.isin(date_ids).all(), "FK shipment.delivery_date valid", checks)

    resolved = config["resolved_counts"]
    _assert(len(dim_date) == int(resolved["days"]), "Date count matches config window", checks)
    _assert(len(products) == int(resolved["products"]), "Product count matches config", checks)
    _assert(len(locations) == int(resolved["locations"]), "Location count matches config", checks)
    _assert(len(suppliers) == int(resolved["suppliers"]), "Supplier count matches config", checks)
    _assert(len(customers) == int(resolved["customers"]), "Customer count matches config", checks)
    _assert(len(sales_orders) == sales_order_lines["SalesOrderId"].nunique(), "Sales order header count matches line groups", checks)
    _assert(len(purchase_orders) == purchase_order_lines["PurchaseOrderId"].nunique(), "Purchase order header count matches line groups", checks)
    _assert(len(sales_order_lines) == int(resolved["sales_order_lines"]), "Sales order line count matches config", checks)
    _assert(len(purchase_order_lines) == int(resolved["purchase_order_lines"]), "Purchase order line count matches config", checks)
    _assert(len(stock_count_events) == int(resolved["stock_count_events"]), "Stock count event count matches config", checks)

    _assert(set(sales_order_lines["SalesOrderId"].astype(str)).issubset(set(sales_orders["SalesOrderId"].astype(str))), "Sales order lines map to header rows", checks)
    _assert(set(purchase_order_lines["PurchaseOrderId"].astype(str)).issubset(set(purchase_orders["PurchaseOrderId"].astype(str))), "Purchase order lines map to header rows", checks)

    if len(inventory_snapshot_daily) == 0:
        warnings.append("Inventory snapshot is empty")

    available_negative_rate = (inventory_snapshot_daily["AvailableQty"] < 0).mean() if not inventory_snapshot_daily.empty else 0.0
    if available_negative_rate > 0.25:
        warnings.append("High proportion of negative available inventory")

    delayed_share = (shipment_lines["ShipmentStatus"] == "Delayed").mean() if not shipment_lines.empty else 0.0
    if delayed_share < 0.03:
        warnings.append("Shipment delay share is lower than expected")

    part_ship_share = (sales_order_lines["Status"] == "PartShipped").mean()
    if part_ship_share < 0.05:
        warnings.append("Partial shipment rate appears low")

    return ValidationResult(ok=True, checks=checks, warnings=warnings)
