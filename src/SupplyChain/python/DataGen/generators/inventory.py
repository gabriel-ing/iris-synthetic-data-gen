from __future__ import annotations

import numpy as np
import pandas as pd


def generate_stock_count_events(
    config: dict,
    dim_date: pd.DataFrame,
    products: pd.DataFrame,
    locations: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["stock_count_events"])
    stock_locations = locations.loc[locations["LocationType"].isin(["Dc", "Store"]), "LocationId"].to_numpy()
    if len(stock_locations) == 0:
        stock_locations = locations["LocationId"].to_numpy()

    product_ids = products["ProductId"].to_numpy()
    date_ids = dim_date["DateId"].to_numpy()

    system_qty = np.maximum(0, rng.poisson(120, size=count))
    variance = rng.integers(-20, 21, size=count)
    counted_qty = np.maximum(0, system_qty + variance)

    return pd.DataFrame(
        {
            "StockCountEventId": np.arange(1, count + 1),
            "Location": rng.choice(stock_locations, size=count),
            "Product": rng.choice(product_ids, size=count),
            "CountDate": rng.choice(date_ids, size=count),
            "SystemQty": system_qty,
            "CountedQty": counted_qty,
            "VarianceQty": counted_qty - system_qty,
            "VarianceReason": rng.choice(["Shrink", "Damage", "AdminError", "MisPick"], size=count),
        }
    )


def generate_inventory_movements(
    config: dict,
    dim_date: pd.DataFrame,
    products: pd.DataFrame,
    locations: pd.DataFrame,
    purchase_order_lines: pd.DataFrame,
    shipment_lines: pd.DataFrame,
    stock_count_events: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    movement_id = 1

    stock_locations = locations.loc[locations["LocationType"].isin(["Dc", "Store"]), "LocationId"].to_numpy()
    if len(stock_locations) == 0:
        stock_locations = locations["LocationId"].to_numpy()

    product_ids = products["ProductId"].to_numpy()

    # Seed initial stock to avoid unrealistic empty-network shipping.
    initial_pairs = int(max(1, len(stock_locations) * len(product_ids) * 0.08))
    chosen_products = rng.choice(product_ids, size=initial_pairs)
    chosen_locations = rng.choice(stock_locations, size=initial_pairs)
    initial_qty = rng.integers(
        int(config["behavior"]["inventory"]["initial_stock_min"]),
        int(config["behavior"]["inventory"]["initial_stock_max"]),
        size=initial_pairs,
    )

    for pid, lid, qty in zip(chosen_products, chosen_locations, initial_qty):
        rows.append(
            {
                "InventoryMovementId": movement_id,
                "Product": int(pid),
                "FromLocation": np.nan,
                "ToLocation": int(lid),
                "MovementDate": 1,
                "MovementTimestamp": "2026-01-01T00:00:00Z",
                "MovementType": "Adjustment",
                "ReferenceType": "InitialLoad",
                "ReferenceId": "INIT",
                "Qty": int(qty),
                "UnitCost": np.nan,
                "ReasonCode": "SystemCorrection",
            }
        )
        movement_id += 1

    for _, row in purchase_order_lines.iterrows():
        received = int(row["ReceivedQty"])
        receipt_date = row["ReceiptDate"]
        if received <= 0 or pd.isna(receipt_date):
            continue

        rows.append(
            {
                "InventoryMovementId": movement_id,
                "Product": int(row["Product"]),
                "FromLocation": int(row["ShipFromLocation"]),
                "ToLocation": int(row["DeliverToLocation"]),
                "MovementDate": int(receipt_date),
                "MovementTimestamp": f"{dim_date.loc[dim_date['DateId'] == int(receipt_date), 'CalendarDate'].iloc[0]}T07:30:00Z",
                "MovementType": "Receipt",
                "ReferenceType": "PurchaseOrder",
                "ReferenceId": str(int(row["PurchaseOrderId"])),
                "Qty": received,
                "UnitCost": float(row["UnitPurchaseCost"]),
                "ReasonCode": None,
            }
        )
        movement_id += 1

    for _, row in shipment_lines.iterrows():
        qty = int(row["ShippedQty"])
        if qty <= 0:
            continue
        ship_date = int(row["ShipDate"])
        rows.append(
            {
                "InventoryMovementId": movement_id,
                "Product": int(row["Product"]),
                "FromLocation": int(row["OriginLocation"]),
                "ToLocation": int(row["DestinationLocation"]),
                "MovementDate": ship_date,
                "MovementTimestamp": f"{dim_date.loc[dim_date['DateId'] == ship_date, 'CalendarDate'].iloc[0]}T12:15:00Z",
                "MovementType": "Ship",
                "ReferenceType": "Shipment",
                "ReferenceId": str(int(row["ShipmentId"])),
                "Qty": -qty,
                "UnitCost": np.nan,
                "ReasonCode": None,
            }
        )
        movement_id += 1

    for _, row in stock_count_events.iterrows():
        variance = int(row["VarianceQty"])
        if variance == 0:
            continue
        count_date = int(row["CountDate"])
        rows.append(
            {
                "InventoryMovementId": movement_id,
                "Product": int(row["Product"]),
                "FromLocation": np.nan,
                "ToLocation": int(row["Location"]),
                "MovementDate": count_date,
                "MovementTimestamp": f"{dim_date.loc[dim_date['DateId'] == count_date, 'CalendarDate'].iloc[0]}T20:00:00Z",
                "MovementType": "Adjustment",
                "ReferenceType": "StockCount",
                "ReferenceId": str(int(row["StockCountEventId"])),
                "Qty": variance,
                "UnitCost": np.nan,
                "ReasonCode": str(row["VarianceReason"]),
            }
        )
        movement_id += 1

    out = pd.DataFrame(rows)
    out = out.sort_values(["MovementDate", "InventoryMovementId"], ignore_index=True)
    return out


def _build_running_events(events: pd.DataFrame, max_date: int) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["Product", "Location", "DateId", "Qty"])

    grouped = events.groupby(["Product", "Location", "DateId"], as_index=False)["Qty"].sum()
    out_frames: list[pd.DataFrame] = []
    for (product, location), chunk in grouped.groupby(["Product", "Location"]):
        s = chunk.set_index("DateId")["Qty"].sort_index()
        s = s.reindex(np.arange(1, max_date + 1), fill_value=0).cumsum()
        out_frames.append(
            pd.DataFrame(
                {
                    "Product": int(product),
                    "Location": int(location),
                    "DateId": s.index.to_numpy(dtype=int),
                    "Qty": s.to_numpy(dtype=float),
                }
            )
        )
    return pd.concat(out_frames, ignore_index=True)


def generate_inventory_snapshot_daily(
    dim_date: pd.DataFrame,
    inventory_movements: pd.DataFrame,
    sales_order_lines: pd.DataFrame,
    purchase_order_lines: pd.DataFrame,
    shipment_lines: pd.DataFrame,
) -> pd.DataFrame:
    max_date = int(dim_date["DateId"].max())

    move_events: list[dict[str, int | float]] = []
    for _, row in inventory_movements.iterrows():
        qty = float(row["Qty"])
        if pd.notna(row["ToLocation"]):
            move_events.append({"Product": int(row["Product"]), "Location": int(row["ToLocation"]), "DateId": int(row["MovementDate"]), "Qty": qty})
        if pd.notna(row["FromLocation"]):
            # For transfer-like rows with negative qty on from-location, keep sign as recorded.
            if qty < 0:
                move_events.append({"Product": int(row["Product"]), "Location": int(row["FromLocation"]), "DateId": int(row["MovementDate"]), "Qty": qty})

    onhand_events = pd.DataFrame(move_events)
    onhand = _build_running_events(onhand_events, max_date)

    alloc_events: list[dict[str, int | float]] = []
    for _, row in sales_order_lines.iterrows():
        back = float(row["BackorderedQty"])
        if back <= 0:
            continue
        start = int(row["OrderDate"])
        end = int(row["ActualDeliveryDate"]) if pd.notna(row["ActualDeliveryDate"]) else min(max_date, int(row["PromisedDeliveryDate"]) + 7)
        alloc_events.append({"Product": int(row["Product"]), "Location": int(row["ShipFromLocation"]), "DateId": start, "Qty": back})
        if end + 1 <= max_date:
            alloc_events.append({"Product": int(row["Product"]), "Location": int(row["ShipFromLocation"]), "DateId": end + 1, "Qty": -back})

    allocated = _build_running_events(pd.DataFrame(alloc_events), max_date)

    on_order_events: list[dict[str, int | float]] = []
    for _, row in purchase_order_lines.iterrows():
        open_qty = float(max(0, int(row["OrderedQty"]) - int(row["ReceivedQty"])))
        if open_qty <= 0:
            continue
        start = int(row["OrderDate"])
        end = int(row["ReceiptDate"]) if pd.notna(row["ReceiptDate"]) else max_date
        on_order_events.append({"Product": int(row["Product"]), "Location": int(row["DeliverToLocation"]), "DateId": start, "Qty": open_qty})
        if end + 1 <= max_date:
            on_order_events.append({"Product": int(row["Product"]), "Location": int(row["DeliverToLocation"]), "DateId": end + 1, "Qty": -open_qty})

    on_order = _build_running_events(pd.DataFrame(on_order_events), max_date)

    in_transit_events: list[dict[str, int | float]] = []
    for _, row in shipment_lines.iterrows():
        qty = float(row["ShippedQty"])
        start = int(row["ShipDate"])
        end = int(row["DeliveryDate"]) if pd.notna(row["DeliveryDate"]) else max_date
        in_transit_events.append({"Product": int(row["Product"]), "Location": int(row["DestinationLocation"]), "DateId": start, "Qty": qty})
        if end + 1 <= max_date:
            in_transit_events.append({"Product": int(row["Product"]), "Location": int(row["DestinationLocation"]), "DateId": end + 1, "Qty": -qty})

    in_transit = _build_running_events(pd.DataFrame(in_transit_events), max_date)

    frames = []
    for name, frame in [
        ("OnHandQty", onhand),
        ("AllocatedQty", allocated),
        ("OnOrderQty", on_order),
        ("InTransitQty", in_transit),
    ]:
        if frame.empty:
            continue
        temp = frame.rename(columns={"Qty": name})
        frames.append(temp)

    if not frames:
        return pd.DataFrame(columns=["InventorySnapshotDailyId", "SnapshotDate", "Product", "Location", "OnHandQty", "AllocatedQty", "AvailableQty", "InTransitQty", "SafetyStockQty", "OnOrderQty", "InventoryValue"])

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on=["Product", "Location", "DateId"], how="outer")

    merged = merged.fillna(0)
    merged["OnHandQty"] = merged.get("OnHandQty", 0)
    merged["AllocatedQty"] = merged.get("AllocatedQty", 0)
    merged["OnOrderQty"] = merged.get("OnOrderQty", 0)
    merged["InTransitQty"] = merged.get("InTransitQty", 0)
    merged["SafetyStockQty"] = np.maximum(5, np.round(merged["OnHandQty"] * 0.15).astype(int))
    merged["AvailableQty"] = merged["OnHandQty"] - merged["AllocatedQty"]
    merged["InventoryValue"] = np.round(merged["OnHandQty"] * 4.25, 2)

    merged = merged.sort_values(["DateId", "Location", "Product"], ignore_index=True)
    merged.insert(0, "InventorySnapshotDailyId", np.arange(1, len(merged) + 1))
    merged = merged.rename(columns={"DateId": "SnapshotDate"})
    return merged[
        [
            "InventorySnapshotDailyId",
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
    ]
