from __future__ import annotations

import numpy as np
import pandas as pd

from DataGen.rng import normalize_weights


def _doc_and_line_ids(count: int, base: int, new_doc_probability: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    doc_ids = np.empty(count, dtype=int)
    line_no = np.empty(count, dtype=int)
    current_doc = base
    current_line = 1
    for i in range(count):
        if i == 0 or rng.random() < new_doc_probability:
            current_doc += 1
            current_line = 1
        doc_ids[i] = current_doc
        line_no[i] = current_line
        current_line += 1
    return doc_ids, line_no


def _sample_order_dates(dim_date: pd.DataFrame, size: int, rng: np.random.Generator) -> np.ndarray:
    weekend = dim_date["IsWeekend"].to_numpy(dtype=bool)
    weights = np.where(weekend, 1.1, 0.95).astype(float)
    month = dim_date["Month"].to_numpy(dtype=int)
    # Create a mild holiday peak around November/December.
    weights = weights * np.where(np.isin(month, [11, 12]), 1.25, 1.0)
    probs = normalize_weights(weights)
    return rng.choice(dim_date["DateId"].to_numpy(), size=size, p=probs)


def _clamp_date_id(values: np.ndarray, max_date_id: int) -> np.ndarray:
    return np.clip(values, 1, max_date_id)


def _first_present(series: pd.Series):
    present = series.dropna()
    if len(present):
        return present.iloc[0]
    return pd.NA


def generate_sales_order_lines(
    config: dict,
    dim_date: pd.DataFrame,
    products: pd.DataFrame,
    locations: pd.DataFrame,
    customers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["sales_order_lines"])
    max_date_id = int(dim_date["DateId"].max())

    channels = list(config["behavior"]["sales"]["channel_weights"].keys())
    channel_probs = normalize_weights(list(config["behavior"]["sales"]["channel_weights"].values()))

    product_ids = products["ProductId"].to_numpy()
    category = products.set_index("ProductId")["Category"].to_dict()
    list_price = products.set_index("ProductId")["ListPrice"].to_dict()
    customer_ids = customers["CustomerId"].to_numpy()
    segment = customers.set_index("CustomerId")["Segment"].to_dict()

    dc_ids = locations.loc[locations["LocationType"] == "Dc", "LocationId"].to_numpy()
    store_ids = locations.loc[locations["LocationType"] == "Store", "LocationId"].to_numpy()
    customer_site_ids = locations.loc[locations["LocationType"] == "CustomerSite", "LocationId"].to_numpy()
    if len(dc_ids) == 0:
        dc_ids = locations["LocationId"].to_numpy()
    if len(store_ids) == 0:
        store_ids = locations["LocationId"].to_numpy()
    if len(customer_site_ids) == 0:
        customer_site_ids = locations["LocationId"].to_numpy()

    sales_order_id, line_number = _doc_and_line_ids(count, base=100000, new_doc_probability=0.58, rng=rng)
    order_date = _sample_order_dates(dim_date, count, rng)

    chosen_product = rng.choice(product_ids, size=count)
    chosen_customer = rng.choice(customer_ids, size=count)
    channel = rng.choice(channels, size=count, p=channel_probs)
    ship_from = rng.choice(dc_ids, size=count)

    ship_to = np.where(
        channel == "Store",
        rng.choice(store_ids, size=count),
        rng.choice(customer_site_ids, size=count),
    )

    category_factor = {
        "GROCERY": 1.8,
        "BEVERAGE": 1.4,
        "HOUSEHOLD": 1.2,
        "PERSONAL_CARE": 1.0,
        "ELECTRONICS": 0.55,
        "APPAREL": 0.9,
        "SEASONAL": 1.15,
    }
    qty_lambda = np.array([category_factor[category[int(p)]] for p in chosen_product])
    ordered_qty = np.maximum(1, rng.poisson(qty_lambda) + 1)

    cancel_rate = float(config["behavior"]["sales"]["cancel_rate"])
    partial_rate = float(config["behavior"]["sales"]["partial_ship_rate"])
    cancelled = rng.random(count) < cancel_rate
    partial = (rng.random(count) < partial_rate) & (~cancelled)

    alloc_ratio = np.where(partial, rng.uniform(0.35, 0.85, size=count), rng.uniform(0.90, 1.00, size=count))
    allocated_qty = np.where(cancelled, 0, np.floor(ordered_qty * alloc_ratio).astype(int))
    allocated_qty = np.minimum(allocated_qty, ordered_qty)

    shipped_ratio = np.where(partial, rng.uniform(0.45, 0.95, size=count), rng.uniform(0.95, 1.0, size=count))
    shipped_qty = np.where(cancelled, 0, np.floor(allocated_qty * shipped_ratio).astype(int))
    shipped_qty = np.minimum(shipped_qty, allocated_qty)

    requested_ship_date = _clamp_date_id(order_date + rng.integers(1, 5, size=count), max_date_id)
    promised_delivery_date = _clamp_date_id(requested_ship_date + rng.integers(1, 8, size=count), max_date_id)

    delivered_mask = (shipped_qty > 0) & (rng.random(count) < 0.88)
    actual_delivery_date = np.where(
        delivered_mask,
        _clamp_date_id(promised_delivery_date + rng.integers(-1, 4, size=count), max_date_id),
        np.nan,
    )

    backordered_qty = np.maximum(ordered_qty - shipped_qty, 0)

    status = np.full(count, "Open", dtype=object)
    status[cancelled] = "Cancelled"
    status[(~cancelled) & (shipped_qty == 0) & (allocated_qty > 0)] = "Open"
    status[(~cancelled) & (shipped_qty > 0) & (shipped_qty < ordered_qty)] = "PartShipped"
    status[(~cancelled) & (shipped_qty >= ordered_qty)] = "Shipped"
    status[(~cancelled) & delivered_mask & (shipped_qty > 0)] = "Delivered"

    seg_discount = {
        "Value": 0.07,
        "Standard": 0.03,
        "Premium": 0.10,
    }
    discount = np.array([seg_discount[segment[int(c)]] for c in chosen_customer])
    unit_price = np.array([list_price[int(pid)] for pid in chosen_product])
    unit_sell_price = np.round(unit_price * (1 - discount) * rng.uniform(0.98, 1.03, size=count), 2)

    return pd.DataFrame(
        {
            "SalesOrderLineId": np.arange(1, count + 1),
            "SalesOrderId": sales_order_id,
            "LineNumber": line_number,
            "Customer": chosen_customer,
            "Product": chosen_product,
            "ShipFromLocation": ship_from,
            "ShipToLocation": ship_to,
            "OrderDate": order_date,
            "RequestedShipDate": requested_ship_date,
            "PromisedDeliveryDate": promised_delivery_date,
            "ActualDeliveryDate": actual_delivery_date,
            "OrderedQty": ordered_qty,
            "AllocatedQty": allocated_qty,
            "ShippedQty": shipped_qty,
            "BackorderedQty": backordered_qty,
            "UnitSellPrice": unit_sell_price,
            "Status": status,
            "Channel": channel,
        }
    )


def generate_purchase_order_lines(
    config: dict,
    dim_date: pd.DataFrame,
    product_supplier: pd.DataFrame,
    suppliers: pd.DataFrame,
    locations: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["purchase_order_lines"])
    max_date_id = int(dim_date["DateId"].max())
    po_cfg = config["behavior"]["purchase_orders"]

    dc_ids = locations.loc[locations["LocationType"] == "Dc", "LocationId"].to_numpy()
    if len(dc_ids) == 0:
        dc_ids = locations["LocationId"].to_numpy()

    supplier_ship_from = suppliers.set_index("SupplierId")["DefaultShipFromLocation"].to_dict()

    sampled = product_supplier.sample(n=count, replace=True, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    po_id, line_number = _doc_and_line_ids(count, base=200000, new_doc_probability=0.62, rng=rng)
    order_date = _sample_order_dates(dim_date, count, rng)

    cancel = rng.random(count) < float(po_cfg["cancel_rate"])
    partial = (rng.random(count) < float(po_cfg["partial_receipt_rate"])) & (~cancel)

    moq = sampled["MinOrderQty"].to_numpy(dtype=int)
    multiple = sampled["OrderMultipleQty"].to_numpy(dtype=int)
    ordered_base = moq + multiple * rng.integers(1, 7, size=count)
    ordered_qty = np.maximum(ordered_base, moq)

    planned_lead = sampled["PlannedLeadTimeDays"].to_numpy(dtype=int)
    expected_receipt = _clamp_date_id(order_date + planned_lead, max_date_id)

    late = (rng.random(count) < float(po_cfg["late_receipt_rate"])) & (~cancel)
    lead_variance = rng.integers(-1, 3, size=count) + np.where(late, rng.integers(3, 10, size=count), 0)
    receipt_date = _clamp_date_id(expected_receipt + lead_variance, max_date_id)

    received_ratio = np.where(partial, rng.uniform(0.45, 0.9, size=count), rng.uniform(0.95, 1.0, size=count))
    received_qty = np.where(cancel, 0, np.floor(ordered_qty * received_ratio).astype(int))
    received_qty = np.minimum(received_qty, ordered_qty)

    open_mask = (~cancel) & (received_qty == 0)
    part_mask = (~cancel) & (received_qty > 0) & (received_qty < ordered_qty)
    closed_mask = (~cancel) & (received_qty >= ordered_qty)

    status = np.full(count, "Open", dtype=object)
    status[cancel] = "Cancelled"
    status[part_mask] = "PartReceived"
    status[closed_mask] = "Closed"
    receipt_date = np.where(status == "Open", np.nan, receipt_date)
    receipt_date = np.where(status == "Cancelled", np.nan, receipt_date)

    supplier_id = sampled["Supplier"].to_numpy(dtype=int)

    return pd.DataFrame(
        {
            "PurchaseOrderLineId": np.arange(1, count + 1),
            "PurchaseOrderId": po_id,
            "LineNumber": line_number,
            "Supplier": supplier_id,
            "Product": sampled["Product"].to_numpy(dtype=int),
            "ShipFromLocation": np.array([supplier_ship_from[int(sid)] for sid in supplier_id]),
            "DeliverToLocation": rng.choice(dc_ids, size=count),
            "OrderDate": order_date,
            "ExpectedReceiptDate": expected_receipt,
            "ReceiptDate": receipt_date,
            "OrderedQty": ordered_qty,
            "ReceivedQty": received_qty,
            "UnitPurchaseCost": np.round(sampled["UnitPurchaseCost"].to_numpy(dtype=float) * rng.uniform(0.97, 1.05, size=count), 2),
            "Status": status,
            "CancelReason": np.where(cancel, rng.choice(["SupplierIssue", "DemandDrop", "DataError"], size=count), None),
            "PlannedLeadTimeDays": planned_lead,
            "ActualLeadTimeDays": np.where(np.isnan(receipt_date), np.nan, np.maximum(0, receipt_date - order_date)),
        }
    )


def generate_sales_orders(sales_order_lines: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sales_order_id, frame in sales_order_lines.groupby("SalesOrderId", sort=True):
        ordered_total = float(frame["OrderedQty"].sum())
        shipped_total = float(frame["ShippedQty"].sum())
        backordered_total = float(frame["BackorderedQty"].sum())
        delivered_count = int(frame["ActualDeliveryDate"].notna().sum())
        if frame["Status"].eq("Cancelled").all():
            header_status = "Cancelled"
        elif delivered_count == len(frame) and backordered_total <= 0:
            header_status = "Delivered"
        elif shipped_total >= ordered_total and delivered_count == 0:
            header_status = "Shipped"
        elif shipped_total > 0:
            header_status = "PartShipped"
        else:
            header_status = "Open"

        rows.append(
            {
                "SalesOrderId": str(sales_order_id),
                "Customer": int(frame["Customer"].iloc[0]),
                "ShipFromLocation": int(frame["ShipFromLocation"].iloc[0]),
                "ShipToLocation": int(frame["ShipToLocation"].iloc[0]),
                "OrderDate": int(frame["OrderDate"].min()),
                "RequestedShipDate": int(frame["RequestedShipDate"].min()),
                "PromisedDeliveryDate": int(frame["PromisedDeliveryDate"].max()),
                "ActualDeliveryDate": _first_present(frame["ActualDeliveryDate"].sort_values(ascending=False)),
                "Status": header_status,
                "Channel": str(frame["Channel"].iloc[0]),
                "OrderLineCount": int(len(frame)),
                "OrderedQtyTotal": round(ordered_total, 2),
                "ShippedQtyTotal": round(shipped_total, 2),
                "BackorderedQtyTotal": round(backordered_total, 2),
                "OrderValue": round(float((frame["OrderedQty"] * frame["UnitSellPrice"]).sum()), 2),
            }
        )

    return pd.DataFrame(rows)


def generate_purchase_orders(purchase_order_lines: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for purchase_order_id, frame in purchase_order_lines.groupby("PurchaseOrderId", sort=True):
        ordered_total = float(frame["OrderedQty"].sum())
        received_total = float(frame["ReceivedQty"].sum())
        if frame["Status"].eq("Cancelled").all():
            header_status = "Cancelled"
        elif received_total >= ordered_total and frame["ReceiptDate"].notna().all():
            header_status = "Received"
        elif received_total > 0:
            header_status = "PartReceived"
        else:
            header_status = "Open"

        expected_receipt = int(frame["ExpectedReceiptDate"].max())
        receipt_date = _first_present(frame["ReceiptDate"].sort_values(ascending=False))
        late_receipt = bool(pd.notna(receipt_date) and int(receipt_date) > expected_receipt)
        rows.append(
            {
                "PurchaseOrderId": str(purchase_order_id),
                "Supplier": int(frame["Supplier"].iloc[0]),
                "ShipFromLocation": int(frame["ShipFromLocation"].iloc[0]),
                "DeliverToLocation": int(frame["DeliverToLocation"].iloc[0]),
                "OrderDate": int(frame["OrderDate"].min()),
                "ExpectedReceiptDate": expected_receipt,
                "ReceiptDate": receipt_date,
                "Status": header_status,
                "OrderLineCount": int(len(frame)),
                "OrderedQtyTotal": round(ordered_total, 2),
                "ReceivedQtyTotal": round(received_total, 2),
                "OrderValue": round(float((frame["OrderedQty"] * frame["UnitPurchaseCost"]).sum()), 2),
                "LateReceiptFlag": late_receipt,
            }
        )

    return pd.DataFrame(rows)


def _split_qty(total_qty: int, pieces: int, rng: np.random.Generator) -> np.ndarray:
    if pieces <= 1 or total_qty <= 1:
        return np.array([total_qty], dtype=int)
    cuts = sorted(rng.choice(np.arange(1, total_qty), size=pieces - 1, replace=False).tolist())
    points = [0] + cuts + [total_qty]
    return np.diff(points)


def generate_shipment_lines(
    config: dict,
    dim_date: pd.DataFrame,
    sales_order_lines: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    ship_cfg = config["behavior"]["shipments"]
    shippable = sales_order_lines.loc[sales_order_lines["ShippedQty"] > 0].copy()
    if shippable.empty:
        return pd.DataFrame(
            columns=[
                "ShipmentLineId",
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
        )

    rows: list[dict[str, object]] = []
    shipment_id = 500000
    for _, so in shippable.iterrows():
        qty = int(so["ShippedQty"])
        split = bool(rng.random() < float(ship_cfg["split_shipment_rate"]) and qty >= 2)
        pieces = int(rng.integers(2, min(4, qty + 1))) if split else 1
        piece_qty = _split_qty(qty, pieces, rng)

        for line_no, sqty in enumerate(piece_qty, start=1):
            shipment_id += 1
            ship_date = int(max(so["OrderDate"], so["RequestedShipDate"] - rng.integers(0, 2)))
            service = str(rng.choice(["Ground", "Express", "Economy"], p=[0.6, 0.25, 0.15]))
            planned = int(rng.integers(1, 6))
            delayed = bool(rng.random() < float(ship_cfg["delay_rate"]))
            actual = planned + int(rng.integers(1, 5)) if delayed else max(1, planned + int(rng.integers(-1, 2)))
            delivery = int(min(dim_date["DateId"].max(), ship_date + actual))

            status = "Delivered"
            if delayed and rng.random() < 0.06:
                status = "Lost"
            elif delayed and delivery >= int(dim_date["DateId"].max()):
                status = "InTransit"
            elif delayed:
                status = "Delayed"

            rows.append(
                {
                    "ShipmentLineId": len(rows) + 1,
                    "ShipmentId": shipment_id,
                    "LineNumber": line_no,
                    "SalesOrderLine": int(so["SalesOrderLineId"]),
                    "Product": int(so["Product"]),
                    "OriginLocation": int(so["ShipFromLocation"]),
                    "DestinationLocation": int(so["ShipToLocation"]),
                    "ShipDate": ship_date,
                    "DeliveryDate": delivery if status != "InTransit" else np.nan,
                    "ShippedQty": int(sqty),
                    "CarrierName": str(rng.choice(["ParcelEx", "BlueRoad", "NorthCarrier", "LineHaulOne"])),
                    "ServiceLevel": service,
                    "PlannedTransitDays": planned,
                    "ActualTransitDays": actual if status != "InTransit" else np.nan,
                    "FreightCost": float(np.round(max(4.0, sqty * rng.uniform(0.6, 2.2)), 2)),
                    "ShipmentStatus": status,
                    "DelayReason": None if status in {"Delivered", "InTransit"} else str(rng.choice(["Weather", "Capacity", "Customs", "HubCongestion"])),
                }
            )

    return pd.DataFrame(rows)
