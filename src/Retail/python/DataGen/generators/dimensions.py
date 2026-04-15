from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.generators.helpers import random_codes, weighted_choice


DEPARTMENT_TREE: dict[str, list[tuple[str, str]]] = {
    "GROCERY": [("PANTRY", "COOKING"), ("SNACKS", "SAVORY"), ("BREAKFAST", "CEREAL")],
    "BEVERAGE": [("SOFT_DRINKS", "SPARKLING"), ("COFFEE_TEA", "GROUND"), ("HYDRATION", "STILL_WATER")],
    "HOUSEHOLD": [("CLEANING", "SURFACES"), ("PAPER", "KITCHEN"), ("STORAGE", "ORGANIZERS")],
    "PERSONAL_CARE": [("SKINCARE", "DAILY"), ("ORAL_CARE", "TOOTHPASTE"), ("HAIRCARE", "SHAMPOO")],
    "ELECTRONICS": [("AUDIO", "HEADPHONES"), ("ACCESSORIES", "CABLES"), ("SMART_HOME", "LIGHTING")],
    "APPAREL": [("BASICS", "TEES"), ("OUTERWEAR", "LIGHT_JACKETS"), ("ACTIVE", "LEGGINGS")],
    "TOYS": [("CREATIVE", "CRAFTS"), ("OUTDOOR", "SPORTS"), ("LEARNING", "STEM")],
}

BRANDS: dict[str, list[str]] = {
    "GROCERY": ["MarketHouse", "Foundry", "Daily Table", "North Pier"],
    "BEVERAGE": ["Bright Sip", "CloudSpring", "Roastline", "Peak Pour"],
    "HOUSEHOLD": ["Oak & Iron", "Cleanroom", "HomeGrid", "Harbor Nest"],
    "PERSONAL_CARE": ["Kind Theory", "Luma", "Clearfield", "Verve Lab"],
    "ELECTRONICS": ["SignalWorks", "Blue Current", "Axis", "Nova"],
    "APPAREL": ["Threadline", "Foundry Wear", "North Coast", "Frame"],
    "TOYS": ["Little Orbit", "PlayForge", "Bright Blocks", "Launchpad"],
}

ROLE_ROWS = [
    {
        "RoleId": 1,
        "RoleName": "StoreLead",
        "AccessLevel": "PARTIAL_READ",
        "ToolTier": "BASIC",
        "CanSeeCostData": False,
        "CanSeeSupplierData": False,
        "CanSeeChainwidePricing": False,
        "CanSeeInventoryForecast": False,
    },
    {
        "RoleId": 2,
        "RoleName": "RegionalViewer",
        "AccessLevel": "PARTIAL_READ",
        "ToolTier": "BASIC",
        "CanSeeCostData": False,
        "CanSeeSupplierData": False,
        "CanSeeChainwidePricing": True,
        "CanSeeInventoryForecast": False,
    },
    {
        "RoleId": 3,
        "RoleName": "MerchandisingManager",
        "AccessLevel": "FULL_READ",
        "ToolTier": "ADVANCED",
        "CanSeeCostData": True,
        "CanSeeSupplierData": True,
        "CanSeeChainwidePricing": True,
        "CanSeeInventoryForecast": True,
    },
    {
        "RoleId": 4,
        "RoleName": "InventoryOpsManager",
        "AccessLevel": "FULL_READ",
        "ToolTier": "ADVANCED",
        "CanSeeCostData": True,
        "CanSeeSupplierData": True,
        "CanSeeChainwidePricing": True,
        "CanSeeInventoryForecast": True,
    },
]


def generate_calendar(config: dict) -> pd.DataFrame:
    start = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    days = int(config["resolved_counts"]["days"])
    dates = pd.date_range(start=start, periods=days, freq="D", tz="UTC")
    iso = dates.isocalendar()

    seasons = np.select(
        [dates.month.isin([12, 1, 2]), dates.month.isin([3, 4, 5]), dates.month.isin([6, 7, 8])],
        ["WINTER", "SPRING", "SUMMER"],
        default="AUTUMN",
    )

    retail_events = np.where(
        dates.month.isin([11, 12]),
        "HOLIDAY_PEAK",
        np.where(dates.day.isin([1, 15]), "PAYDAY", "NONE"),
    )

    return pd.DataFrame(
        {
            "CalendarId": np.arange(1, days + 1),
            "DateKey": dates.strftime("%Y%m%d").astype(int),
            "CalendarDate": dates.strftime("%Y-%m-%d"),
            "Year": dates.year,
            "Quarter": dates.quarter,
            "Month": dates.month,
            "WeekOfYear": iso.week.astype(int),
            "DayOfWeek": dates.dayofweek + 1,
            "IsWeekend": (dates.dayofweek >= 5),
            "Season": seasons,
            "FiscalPeriod": [f"{ts.year}-P{ts.month:02d}" for ts in dates],
            "RetailEvent": retail_events,
        }
    )


def generate_roles() -> pd.DataFrame:
    return pd.DataFrame(ROLE_ROWS)


def generate_stores(config: dict, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["stores"])
    format_weights = config["behavior"]["stores"]["format_weights"]
    store_formats = list(format_weights.keys())
    formats = weighted_choice(rng, store_formats, format_weights, count)
    formats[: len(store_formats)] = np.array(store_formats)

    region_map = {
        "WEST": [("CA", "Los Angeles"), ("WA", "Seattle"), ("AZ", "Phoenix")],
        "MIDWEST": [("IL", "Chicago"), ("OH", "Columbus"), ("MN", "Minneapolis")],
        "SOUTH": [("TX", "Dallas"), ("GA", "Atlanta"), ("FL", "Tampa")],
        "EAST": [("NY", "Albany"), ("MA", "Boston"), ("PA", "Philadelphia")],
    }
    regions = list(region_map.keys())
    region = rng.choice(regions, size=count, p=[0.24, 0.23, 0.29, 0.24])

    states: list[str] = []
    cities: list[str] = []
    districts: list[str] = []
    open_dates: list[str] = []
    base_open = pd.Timestamp(config["time"]["start_date"], tz="UTC") - pd.Timedelta(days=900)

    for idx, current_region in enumerate(region, start=1):
        state, city = region_map[current_region][int(rng.integers(0, len(region_map[current_region])))]
        states.append(state)
        cities.append(city)
        districts.append(f"{current_region[:2]}-{int(rng.integers(1, 10)):02d}")
        opened_at = base_open + pd.Timedelta(days=int(rng.integers(0, 860)))
        open_dates.append(opened_at.strftime("%Y-%m-%dT%H:%M:%SZ"))

    square_feet = np.select(
        [formats == "FLAGSHIP", formats == "SUBURBAN", formats == "URBAN"],
        [rng.integers(42000, 78000, size=count), rng.integers(26000, 52000, size=count), rng.integers(14000, 26000, size=count)],
        default=rng.integers(10000, 22000, size=count),
    )

    return pd.DataFrame(
        {
            "StoreId": np.arange(1, count + 1),
            "StoreCode": random_codes("STR", count),
            "StoreName": [f"Store {idx:04d}" for idx in range(1, count + 1)],
            "StoreFormat": formats,
            "Region": region,
            "District": districts,
            "City": cities,
            "State": states,
            "OpenDate": open_dates,
            "SquareFeet": square_feet,
            "ActiveFlag": (rng.random(count) > 0.03),
        }
    )


def generate_products(config: dict, calendar: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["products"])
    department_weights = config["behavior"]["products"]["department_weights"]
    departments = list(department_weights.keys())
    department = weighted_choice(rng, departments, department_weights, count)

    category: list[str] = []
    subcategory: list[str] = []
    brands: list[str] = []
    seasonality: list[str] = []
    unit_size: list[str] = []
    base_cost: list[float] = []
    base_price: list[float] = []

    season_choices = {
        "GROCERY": ["EVERGREEN", "SUMMER", "HOLIDAY"],
        "BEVERAGE": ["EVERGREEN", "SUMMER"],
        "HOUSEHOLD": ["EVERGREEN", "SPRING"],
        "PERSONAL_CARE": ["EVERGREEN", "SUMMER"],
        "ELECTRONICS": ["EVERGREEN", "HOLIDAY", "BACK_TO_SCHOOL"],
        "APPAREL": ["SPRING", "SUMMER", "AUTUMN", "HOLIDAY"],
        "TOYS": ["HOLIDAY", "SUMMER", "BACK_TO_SCHOOL"],
    }
    unit_size_choices = {
        "GROCERY": ["8 OZ", "12 OZ", "18 OZ", "24 OZ"],
        "BEVERAGE": ["12 PK", "6 PK", "1 L", "500 ML"],
        "HOUSEHOLD": ["EA", "2 PK", "4 PK"],
        "PERSONAL_CARE": ["EA", "150 ML", "250 ML"],
        "ELECTRONICS": ["EA", "KIT"],
        "APPAREL": ["S", "M", "L", "XL"],
        "TOYS": ["EA", "SET"],
    }
    cost_ranges = {
        "GROCERY": (1.2, 7.5),
        "BEVERAGE": (1.0, 12.0),
        "HOUSEHOLD": (2.0, 18.0),
        "PERSONAL_CARE": (2.2, 16.0),
        "ELECTRONICS": (8.0, 80.0),
        "APPAREL": (4.0, 28.0),
        "TOYS": (3.0, 35.0),
    }
    margin_ranges = {
        "GROCERY": (1.18, 1.42),
        "BEVERAGE": (1.2, 1.55),
        "HOUSEHOLD": (1.35, 1.75),
        "PERSONAL_CARE": (1.45, 1.95),
        "ELECTRONICS": (1.18, 1.45),
        "APPAREL": (1.55, 2.35),
        "TOYS": (1.4, 2.0),
    }

    for current_department in department:
        selected_category, selected_subcategory = DEPARTMENT_TREE[str(current_department)][int(rng.integers(0, len(DEPARTMENT_TREE[str(current_department)])))]
        category.append(selected_category)
        subcategory.append(selected_subcategory)
        brands.append(str(rng.choice(BRANDS[str(current_department)])))
        seasonality.append(str(rng.choice(season_choices[str(current_department)])))
        unit_size.append(str(rng.choice(unit_size_choices[str(current_department)])))
        low_cost, high_cost = cost_ranges[str(current_department)]
        unit_cost = float(np.round(rng.uniform(low_cost, high_cost), 2))
        low_margin, high_margin = margin_ranges[str(current_department)]
        unit_price = float(np.round(unit_cost * rng.uniform(low_margin, high_margin), 2))
        base_cost.append(unit_cost)
        base_price.append(max(unit_price, unit_cost + 0.5))

    calendar_ids = calendar["CalendarId"].to_numpy()
    launch_date = rng.choice(calendar_ids[: max(5, int(len(calendar_ids) * 0.55))], size=count)
    discontinued = rng.random(count) < 0.05
    discontinue_offset = rng.integers(10, 45, size=count)
    discontinue_date = np.clip(launch_date + discontinue_offset, 1, int(calendar_ids.max()))
    discontinue_date = np.where(discontinued, discontinue_date, np.nan)

    return pd.DataFrame(
        {
            "ProductId": np.arange(1, count + 1),
            "Sku": random_codes("SKU", count, pad=7),
            "ProductName": [f"Product {idx:06d}" for idx in range(1, count + 1)],
            "Department": department,
            "Category": category,
            "Subcategory": subcategory,
            "Brand": brands,
            "PrivateLabelFlag": (rng.random(count) < float(config["behavior"]["products"]["private_label_share"])),
            "Seasonality": seasonality,
            "UnitSize": unit_size,
            "BaseUnitCost": np.round(base_cost, 2),
            "BaseRegularPrice": np.round(base_price, 2),
            "LaunchDate": launch_date,
            "DiscontinueDate": discontinue_date,
        }
    )


def generate_customers(config: dict, stores: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["customers"])
    store_ids = stores["StoreId"].to_numpy()
    store_weights = np.where(stores["ActiveFlag"], 1.0, 0.45).astype(float)
    store_weights = store_weights / store_weights.sum()
    channels = list(config["behavior"]["sales"]["channel_weights"].keys())

    segments = np.array(["BUDGET", "MAINSTREAM", "PREMIUM", "OCCASIONAL"], dtype=object)
    segment_weights = np.array([0.28, 0.44, 0.16, 0.12], dtype=float)
    loyalty_tiers = np.array(["NONE", "MEMBER", "PLUS", "VIP"], dtype=object)
    loyalty_weights = {
        "BUDGET": [0.52, 0.32, 0.12, 0.04],
        "MAINSTREAM": [0.30, 0.42, 0.20, 0.08],
        "PREMIUM": [0.12, 0.30, 0.34, 0.24],
        "OCCASIONAL": [0.68, 0.22, 0.08, 0.02],
    }
    preferred_channel_weights = {
        "BUDGET": [0.72, 0.08, 0.10, 0.10],
        "MAINSTREAM": [0.62, 0.14, 0.14, 0.10],
        "PREMIUM": [0.34, 0.22, 0.20, 0.24],
        "OCCASIONAL": [0.78, 0.06, 0.08, 0.08],
    }
    start = pd.Timestamp(config["time"]["start_date"], tz="UTC")

    chosen_segments = rng.choice(segments, size=count, p=segment_weights)
    rows: list[dict[str, object]] = []
    for customer_id in range(1, count + 1):
        segment = str(chosen_segments[customer_id - 1])
        join_at = start - pd.Timedelta(days=int(rng.integers(30, 960))) + pd.Timedelta(hours=int(rng.integers(0, 24)))
        rows.append(
            {
                "CustomerId": customer_id,
                "CustomerNumber": f"CUS{customer_id:08d}",
                "Segment": segment,
                "LoyaltyTier": str(rng.choice(loyalty_tiers, p=loyalty_weights[segment])),
                "HomeStore": int(rng.choice(store_ids, p=store_weights)),
                "PreferredChannel": str(rng.choice(channels, p=preferred_channel_weights[segment])),
                "JoinDate": join_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ActiveFlag": bool(rng.random() > 0.04),
            }
        )

    return pd.DataFrame(rows)


def generate_users(config: dict, roles: pd.DataFrame, stores: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["users"])
    role_weights = config["behavior"]["access"]["role_weights"]
    role_names = list(role_weights.keys())
    chosen_roles = weighted_choice(rng, role_names, role_weights, count)
    role_lookup = roles.set_index("RoleName").to_dict(orient="index")
    store_rows = stores.set_index("StoreId")
    store_ids = stores["StoreId"].to_numpy()
    departments = list(config["behavior"]["products"]["department_weights"].keys())
    start = pd.Timestamp(config["time"]["start_date"], tz="UTC")

    rows: list[dict[str, object]] = []
    for user_id in range(1, count + 1):
        role_name = str(chosen_roles[user_id - 1])
        role_data = role_lookup[role_name]
        primary_store = int(rng.choice(store_ids))
        region = str(store_rows.loc[primary_store, "Region"])
        access_scope = "FULL" if str(role_data["AccessLevel"]) == "FULL_READ" else "PARTIAL"
        category_scope = "ALL" if access_scope == "FULL" else str(rng.choice(departments))
        created_at = start - pd.Timedelta(days=int(rng.integers(45, 600))) + timedelta(hours=int(rng.integers(0, 24)))
        rows.append(
            {
                "UserId": user_id,
                "UserName": f"user{user_id:04d}",
                "FullName": f"User {user_id:04d}",
                "Email": f"user{user_id:04d}@synthetic-retail.demo",
                "RoleRef": int(role_data["RoleId"]),
                "AccessScope": access_scope,
                "ToolTier": str(role_data["ToolTier"]),
                "CategoryScope": category_scope,
                "Region": region,
                "PrimaryStore": primary_store,
                "CreatedAt": created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ActiveFlag": bool(rng.random() > 0.05),
            }
        )

    return pd.DataFrame(rows)


def generate_user_store_access(config: dict, users: pd.DataFrame, stores: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    min_partial = int(config["behavior"]["access"]["partial_store_min"])
    max_partial = int(config["behavior"]["access"]["partial_store_max"])
    stores_by_region = {
        region: frame["StoreId"].to_numpy()
        for region, frame in stores.groupby("Region", sort=False)
    }
    all_store_ids = stores["StoreId"].to_numpy()

    rows: list[dict[str, object]] = []
    access_id = 1
    for user in users.itertuples(index=False):
        primary_store = int(user.PrimaryStore)
        if user.AccessScope == "FULL":
            scoped_store_ids = all_store_ids
            access_type = "FULL"
        else:
            regional_store_ids = stores_by_region.get(str(user.Region), all_store_ids)
            scoped_count = min(len(regional_store_ids), int(rng.integers(min_partial, max_partial + 1)))
            picked = set(rng.choice(regional_store_ids, size=scoped_count, replace=False).tolist()) if len(regional_store_ids) >= scoped_count else set(regional_store_ids.tolist())
            picked.add(primary_store)
            scoped_store_ids = np.array(sorted(picked))
            access_type = "ASSIGNED"

        for store_id in scoped_store_ids:
            rows.append(
                {
                    "UserStoreAccessId": access_id,
                    "UserRef": int(user.UserId),
                    "Store": int(store_id),
                    "AccessType": "PRIMARY" if int(store_id) == primary_store else access_type,
                }
            )
            access_id += 1

    return pd.DataFrame(rows)
