from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.generators.helpers import random_codes, weighted_choice
from DataGen.rng import normalize_weights


def generate_dim_date(config: dict) -> pd.DataFrame:
    start = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    days = int(config["resolved_counts"]["days"])
    dates = pd.date_range(start=start, periods=days, freq="D", tz="UTC")
    iso = dates.isocalendar()

    return pd.DataFrame(
        {
            "DateId": np.arange(1, days + 1),
            "DateKey": dates.strftime("%Y%m%d").astype(int),
            "CalendarDate": dates.strftime("%Y-%m-%d"),
            "Year": dates.year,
            "Quarter": dates.quarter,
            "Month": dates.month,
            "WeekOfYear": iso.week.astype(int),
            "DayOfWeek": dates.dayofweek + 1,
            "IsWeekend": (dates.dayofweek >= 5),
        }
    )


def generate_dim_product(config: dict, dim_date: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["products"])
    category_weights = config["behavior"]["product_categories"]
    categories = list(category_weights.keys())
    category = weighted_choice(rng, categories, category_weights, count)

    brand_pool = ["Atlas", "Northwind", "Harbor", "Oak", "Nimbus", "Summit", "Verde", "Orion"]
    uom_by_category = {
        "GROCERY": "EA",
        "BEVERAGE": "CASE",
        "HOUSEHOLD": "EA",
        "PERSONAL_CARE": "EA",
        "ELECTRONICS": "EA",
        "APPAREL": "EA",
        "SEASONAL": "EA",
    }
    perishable_cats = {"GROCERY", "BEVERAGE"}

    units_per_case = np.where(np.array(category) == "CASE", rng.integers(6, 25, size=count), rng.integers(1, 13, size=count))
    weight = np.round(rng.lognormal(mean=0.6, sigma=0.8, size=count), 3)
    volume = np.round(rng.lognormal(mean=-2.0, sigma=0.6, size=count), 4)
    is_perishable = np.array([cat in perishable_cats for cat in category])
    shelf_life = np.where(is_perishable, rng.integers(5, 120, size=count), np.nan)

    date_ids = dim_date["DateId"].to_numpy()
    launch_id = rng.choice(date_ids, size=count)
    discontinued = rng.random(count) < 0.06
    discontinue_offsets = rng.integers(40, 220, size=count)
    discontinue_id = np.clip(launch_id + discontinue_offsets, 1, int(date_ids.max()))
    discontinue_id = np.where(discontinued, discontinue_id, np.nan)

    base_cost = np.round(rng.lognormal(mean=2.3, sigma=0.65, size=count), 2)
    list_price = np.round(base_cost * rng.uniform(1.15, 1.8, size=count), 2)

    return pd.DataFrame(
        {
            "ProductId": np.arange(1, count + 1),
            "Sku": random_codes("SKU", count, pad=7),
            "ProductName": [f"Product {idx:06d}" for idx in range(1, count + 1)],
            "Brand": rng.choice(brand_pool, size=count),
            "Category": category,
            "Subcategory": [f"{c}_CORE" for c in category],
            "Uom": [uom_by_category[c] for c in category],
            "UnitsPerCase": units_per_case,
            "UnitWeightKg": weight,
            "UnitVolumeM3": volume,
            "TemperatureZone": np.where(is_perishable, rng.choice(["Chilled", "Ambient"], size=count, p=[0.35, 0.65]), "Ambient"),
            "IsPerishable": is_perishable,
            "ShelfLifeDays": shelf_life,
            "StandardCost": base_cost,
            "ListPrice": list_price,
            "LaunchDate": launch_id,
            "DiscontinueDate": discontinue_id,
        }
    )


def generate_dim_location(config: dict, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["locations"])
    type_weights = config["behavior"]["location_type_weights"]
    location_types = list(type_weights.keys())
    raw_types = weighted_choice(rng, location_types, type_weights, count)

    # Ensure each location type exists at least once for downstream generators.
    raw_types[: len(location_types)] = np.array(location_types)

    regions = ["NORTH", "SOUTH", "MIDLANDS", "EAST", "WEST", "SCOTLAND"]
    cities = ["London", "Birmingham", "Manchester", "Leeds", "Bristol", "Glasgow", "Liverpool", "Newcastle"]

    return pd.DataFrame(
        {
            "LocationId": np.arange(1, count + 1),
            "LocationCode": random_codes("LOC", count),
            "LocationName": [f"Node {idx:05d}" for idx in range(1, count + 1)],
            "LocationType": raw_types,
            "Country": "GB",
            "Region": rng.choice(regions, size=count),
            "City": rng.choice(cities, size=count),
            "Postcode": [f"SC{rng.integers(10, 99)} {rng.integers(1, 9)}AB" for _ in range(count)],
            "TimeZone": "Europe/London",
            "IsActive": (rng.random(count) > 0.03),
        }
    )


def generate_dim_supplier(config: dict, locations: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["suppliers"])
    supplier_sites = locations.loc[locations["LocationType"] == "SupplierSite", "LocationId"].to_numpy()
    if len(supplier_sites) == 0:
        supplier_sites = locations["LocationId"].to_numpy()

    risk = np.clip(rng.normal(44, 18, size=count), 0, 100).astype(int)
    return pd.DataFrame(
        {
            "SupplierId": np.arange(1, count + 1),
            "SupplierCode": random_codes("SUP", count),
            "SupplierName": [f"Supplier {idx:05d}" for idx in range(1, count + 1)],
            "SupplierTier": rng.choice([1, 2, 3], size=count, p=[0.25, 0.50, 0.25]),
            "Country": rng.choice(["GB", "DE", "FR", "NL", "IE"], size=count, p=[0.58, 0.15, 0.12, 0.08, 0.07]),
            "PreferredFlag": rng.random(count) < 0.4,
            "PaymentTermsDays": rng.choice([15, 30, 45, 60], size=count, p=[0.1, 0.55, 0.25, 0.10]),
            "RiskScore": risk,
            "DefaultShipFromLocation": rng.choice(supplier_sites, size=count),
        }
    )


def generate_dim_customer(config: dict, locations: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["customers"])
    segment_weights = config["behavior"]["customer_segment_weights"]
    segments = list(segment_weights.keys())
    segment = weighted_choice(rng, segments, segment_weights, count)
    customer_sites = locations.loc[locations["LocationType"] == "CustomerSite", "LocationId"].to_numpy()
    if len(customer_sites) == 0:
        customer_sites = locations["LocationId"].to_numpy()

    return pd.DataFrame(
        {
            "CustomerId": np.arange(1, count + 1),
            "CustomerNumber": random_codes("CUS", count),
            "CustomerName": [f"Customer {idx:06d}" for idx in range(1, count + 1)],
            "CustomerType": rng.choice(["Consumer", "B2B"], size=count, p=[0.75, 0.25]),
            "Segment": segment,
            "Country": "GB",
            "Region": rng.choice(["NORTH", "SOUTH", "MIDLANDS", "EAST", "WEST", "SCOTLAND"], size=count),
            "ServiceLevelTargetPct": np.round(rng.uniform(92.0, 99.5, size=count), 2),
            "DefaultShipToLocation": rng.choice(customer_sites, size=count),
        }
    )


def generate_product_supplier(
    config: dict,
    products: pd.DataFrame,
    suppliers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    target = int(config["resolved_counts"]["product_suppliers"])
    product_ids = products["ProductId"].to_numpy()
    supplier_ids = suppliers["SupplierId"].to_numpy()

    pairs: set[tuple[int, int]] = set()
    rows: list[dict[str, object]] = []

    # Guarantee every product has at least one sourcing path.
    for pid in product_ids:
        sid = int(rng.choice(supplier_ids))
        pairs.add((int(pid), sid))

    while len(pairs) < target:
        pairs.add((int(rng.choice(product_ids)), int(rng.choice(supplier_ids))))

    for idx, (pid, sid) in enumerate(sorted(pairs), start=1):
        moq = int(rng.choice([10, 20, 40, 60, 100], p=normalize_weights([0.18, 0.34, 0.24, 0.14, 0.10])))
        multiple = int(rng.choice([1, 2, 4, 5, 10], p=normalize_weights([0.25, 0.25, 0.20, 0.15, 0.15])))
        rows.append(
            {
                "ProductSupplierId": idx,
                "Product": pid,
                "Supplier": sid,
                "IsPrimarySupplier": bool(rng.random() < 0.35),
                "MinOrderQty": moq,
                "OrderMultipleQty": multiple,
                "PackSize": max(1, multiple),
                "PlannedLeadTimeDays": int(rng.integers(2, 22)),
                "UnitPurchaseCost": float(np.round(rng.lognormal(mean=2.0, sigma=0.5), 2)),
                "Incoterm": str(rng.choice(["EXW", "FCA", "DAP", "DDP"])),
                "ShipMode": str(rng.choice(["Road", "Air", "Ocean"], p=[0.78, 0.10, 0.12])),
            }
        )

    out = pd.DataFrame(rows)
    out = out.sort_values("ProductSupplierId", ignore_index=True)
    out["IsPrimarySupplier"] = out.groupby("Product")["IsPrimarySupplier"].transform(lambda s: s | (s.index == s.index.min()))
    return out
