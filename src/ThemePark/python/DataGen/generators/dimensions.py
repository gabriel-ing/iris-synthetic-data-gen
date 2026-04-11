from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.generators.catalog import ROLE_DEFINITIONS, RIDE_TYPE_DEFINITIONS, ZONE_THEMES
from DataGen.generators.helpers import random_codes, weighted_choice


COUNTRY_BY_REGION = {
    "SOUTHEAST": [("US", "Orlando"), ("US", "Tampa"), ("US", "Atlanta")],
    "WEST": [("US", "Anaheim"), ("US", "San Diego"), ("US", "Las Vegas")],
    "MIDWEST": [("US", "Chicago"), ("US", "Branson"), ("US", "Columbus")],
    "NORTHEAST": [("US", "Hershey"), ("US", "Boston"), ("CA", "Toronto")],
    "INTERNATIONAL": [("JP", "Osaka"), ("FR", "Paris"), ("AE", "Abu Dhabi")],
}

GUEST_SEGMENTS = {
    "FAMILY": (1, 6),
    "THRILL_SEEKER": (1, 3),
    "TOUR_GROUP": (4, 12),
    "LOCAL_MEMBER": (1, 4),
    "SCHOOL_TRIP": (10, 24),
    "VIP_TRAVELER": (1, 4),
}


def generate_parks(config: dict, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["parks"])
    region_weights = config["behavior"]["parks"]["region_weights"]
    type_weights = config["behavior"]["parks"]["park_type_weights"]
    regions = list(region_weights.keys())
    park_types = list(type_weights.keys())
    chosen_regions = weighted_choice(rng, regions, region_weights, count)
    chosen_types = weighted_choice(rng, park_types, type_weights, count)
    chosen_regions[: min(len(regions), count)] = np.array(regions[: min(len(regions), count)])
    chosen_types[: min(len(park_types), count)] = np.array(park_types[: min(len(park_types), count)])

    base_open = pd.Timestamp(config["time"]["start_date"], tz="UTC") - pd.Timedelta(days=3650)
    capacities = {
        "DESTINATION": (18000, 42000),
        "CITY": (9000, 22000),
        "RESORT": (22000, 52000),
        "WATER": (8000, 18000),
    }
    operating_models = {
        "DESTINATION": ["YEAR_ROUND", "EXTENDED_HOURS"],
        "CITY": ["YEAR_ROUND", "WEEKEND_HEAVY"],
        "RESORT": ["YEAR_ROUND", "HOTEL_INTEGRATED"],
        "WATER": ["SEASONAL_PEAK", "SUMMER_EXTENDED"],
    }

    rows: list[dict[str, object]] = []
    for park_id in range(1, count + 1):
        region = str(chosen_regions[park_id - 1])
        park_type = str(chosen_types[park_id - 1])
        country, city = COUNTRY_BY_REGION[region][int(rng.integers(0, len(COUNTRY_BY_REGION[region])))]
        opened_at = base_open + pd.Timedelta(days=int(rng.integers(0, 3000)))
        capacity_low, capacity_high = capacities[park_type]
        rows.append(
            {
                "ParkId": park_id,
                "ParkCode": f"PRK{park_id:04d}",
                "ParkName": f"{city} {park_type.title()} Park",
                "Region": region,
                "Country": country,
                "ParkType": park_type,
                "OpeningDate": opened_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "OperatingModel": str(rng.choice(operating_models[park_type])),
                "DailyCapacity": int(rng.integers(capacity_low, capacity_high)),
                "ActiveFlag": bool(rng.random() > 0.02),
            }
        )

    return pd.DataFrame(rows)


def generate_zones(config: dict, parks: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["zones"])
    park_ids = parks["ParkId"].to_numpy()
    min_per_park = max(1, min(3, count // max(1, len(park_ids))))
    assignments: list[int] = []
    for park_id in park_ids:
        assignments.extend([int(park_id)] * min_per_park)
    while len(assignments) < count:
        capacities = parks.set_index("ParkId")["DailyCapacity"]
        weights = capacities.loc[park_ids].to_numpy(dtype=float)
        weights = weights / weights.sum()
        assignments.append(int(rng.choice(park_ids, p=weights)))

    rng.shuffle(assignments)

    rows: list[dict[str, object]] = []
    for zone_id in range(1, count + 1):
        theme_row = ZONE_THEMES[(zone_id - 1) % len(ZONE_THEMES)]
        park_id = assignments[zone_id - 1]
        rows.append(
            {
                "ZoneId": zone_id,
                "ZoneCode": f"ZON{zone_id:05d}",
                "Park": park_id,
                "ZoneName": theme_row["theme"].replace("_", " ").title(),
                "Theme": theme_row["theme"],
                "Environment": theme_row["environment"],
                "FamilyIntensity": theme_row["intensity"],
                "CapacityClass": str(rng.choice(["SMALL", "MEDIUM", "LARGE"], p=[0.24, 0.48, 0.28])),
                "IndoorFlag": theme_row["environment"] == "INDOOR",
            }
        )

    return pd.DataFrame(rows)


def _ride_name(ride_type: str, rng: np.random.Generator) -> str:
    prefixes, suffixes = RIDE_TYPE_DEFINITIONS[ride_type]["name_parts"]
    return f"{rng.choice(prefixes)} {rng.choice(suffixes)}"


def generate_rides(config: dict, parks: pd.DataFrame, zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["rides"])
    ride_weights = config["behavior"]["rides"]["type_weights"]
    ride_types = list(ride_weights.keys())
    chosen_types = weighted_choice(rng, ride_types, ride_weights, count)
    zones_by_park = {park_id: frame["ZoneId"].to_numpy() for park_id, frame in zones.groupby("Park", sort=False)}
    park_ids = parks["ParkId"].to_numpy()
    park_capacity = parks.set_index("ParkId")["DailyCapacity"].to_numpy(dtype=float)
    park_weights = park_capacity / park_capacity.sum()
    base_open = pd.Timestamp(config["time"]["start_date"], tz="UTC") - pd.Timedelta(days=1600)
    operating_share = float(config["behavior"]["rides"]["operating_share"])

    rows: list[dict[str, object]] = []
    for ride_id in range(1, count + 1):
        park_id = int(rng.choice(park_ids, p=park_weights))
        zone_id = int(rng.choice(zones_by_park[park_id]))
        ride_type = str(chosen_types[ride_id - 1])
        definition = RIDE_TYPE_DEFINITIONS[ride_type]
        height_low, height_high = definition["height_range"]
        capacity_low, capacity_high = definition["capacity_range"]
        opened_at = base_open + pd.Timedelta(days=int(rng.integers(0, 1400)))
        status = "OPERATING" if rng.random() < operating_share else str(rng.choice(["SEASONAL", "STANDBY", "LIMITED_HOURS"], p=[0.44, 0.26, 0.30]))
        rows.append(
            {
                "RideId": ride_id,
                "RideCode": f"RID{ride_id:05d}",
                "Zone": zone_id,
                "RideName": _ride_name(ride_type, rng),
                "RideType": ride_type,
                "ThrillLevel": int(rng.choice(definition["thrill_levels"])),
                "HeightRequirementCm": int(rng.integers(height_low, height_high + 1)),
                "CapacityPerHour": int(rng.integers(capacity_low, capacity_high)),
                "OpeningDate": opened_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "AccessibilitySupport": str(rng.choice(definition["supports"])),
                "Status": status,
            }
        )

    return pd.DataFrame(rows)


def generate_employees(config: dict, parks: pd.DataFrame, zones: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["employees"])
    role_weights = config["behavior"]["staffing"]["role_weights"]
    roles = list(role_weights.keys())
    chosen_roles = weighted_choice(rng, roles, role_weights, count)
    role_lookup = {row["role"]: row for row in ROLE_DEFINITIONS}
    park_ids = parks["ParkId"].to_numpy()
    park_weights = parks["DailyCapacity"].to_numpy(dtype=float)
    park_weights = park_weights / park_weights.sum()
    zones_by_park = {park_id: frame["ZoneId"].to_numpy() for park_id, frame in zones.groupby("Park", sort=False)}
    base_date = pd.Timestamp(config["time"]["start_date"], tz="UTC") - pd.Timedelta(days=1100)

    rows: list[dict[str, object]] = []
    for employee_id in range(1, count + 1):
        role = str(chosen_roles[employee_id - 1])
        role_data = role_lookup[role]
        park_id = int(rng.choice(park_ids, p=park_weights))
        home_zone = int(rng.choice(zones_by_park[park_id]))
        hire_date = base_date + timedelta(days=int(rng.integers(0, 980))) + timedelta(hours=int(rng.integers(0, 18)))
        rows.append(
            {
                "EmployeeId": employee_id,
                "EmployeeNumber": f"EMP{employee_id:06d}",
                "Park": park_id,
                "HomeZone": home_zone,
                "EmployeeName": f"Employee {employee_id:05d}",
                "RoleType": role,
                "SkillTier": str(rng.choice(role_data["skill_tiers"])),
                "EmploymentType": str(rng.choice(["FULL_TIME", "PART_TIME", "SEASONAL"], p=[0.56, 0.24, 0.20])),
                "HireDate": hire_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "MascotQualifiedFlag": bool(rng.random() < float(role_data["mascot_share"])),
                "ActiveFlag": bool(rng.random() > 0.03),
            }
        )

    return pd.DataFrame(rows)


def generate_guests(config: dict, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["guests"])
    segments = list(GUEST_SEGMENTS.keys())
    segment_weights = np.array([0.34, 0.18, 0.10, 0.16, 0.12, 0.10], dtype=float)
    segment_weights = segment_weights / segment_weights.sum()
    countries = ["US", "CA", "MX", "BR", "GB", "JP", "FR", "DE", "AE"]
    country_weights = np.array([0.60, 0.10, 0.08, 0.05, 0.05, 0.04, 0.03, 0.03, 0.02], dtype=float)
    age_bands = ["CHILD", "TEEN", "ADULT", "SENIOR"]
    loyalty = ["NONE", "ANNUAL_PASS", "HOTEL_GUEST", "VIP_CLUB"]
    accessibility = ["NONE", "MOBILITY", "SENSORY", "HEARING", "DIETARY"]

    rows: list[dict[str, object]] = []
    for guest_id in range(1, count + 1):
        segment = str(rng.choice(segments, p=segment_weights))
        party_low, party_high = GUEST_SEGMENTS[segment]
        rows.append(
            {
                "GuestId": guest_id,
                "GuestNumber": f"GST{guest_id:07d}",
                "HomeCountry": str(rng.choice(countries, p=country_weights)),
                "Segment": segment,
                "AgeBand": str(rng.choice(age_bands, p=[0.18, 0.16, 0.56, 0.10])),
                "PartySize": int(rng.integers(party_low, party_high + 1)),
                "AccessibilityNeeds": str(rng.choice(accessibility, p=[0.74, 0.08, 0.06, 0.04, 0.08])),
                "LoyaltyTier": str(rng.choice(loyalty, p=[0.56, 0.20, 0.16, 0.08])),
                "VisitIntent": str(rng.choice(["RIDE_DAY", "FAMILY_DAY", "VACATION", "EVENT_NIGHT", "WATER_PARK"], p=[0.30, 0.26, 0.22, 0.10, 0.12])),
            }
        )

    return pd.DataFrame(rows)
