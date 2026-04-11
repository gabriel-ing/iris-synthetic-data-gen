from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.generators.catalog import INCIDENT_DESCRIPTIONS, ROLE_DEFINITIONS
from DataGen.rng import normalize_weights


def generate_ride_maintenance(config: dict, rides: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["ride_maintenance"])
    ride_ids = rides["RideId"].to_numpy()
    ride_lookup = rides.set_index("RideId")
    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    total_days = int(config["resolved_counts"]["days"])
    maintenance_types = ["INSPECTION", "EMERGENCY_REPAIR", "COSMETIC", "SENSOR_CALIBRATION", "RESTRAINT_TEST"]
    type_weights = normalize_weights([0.28, 0.20, 0.14, 0.20, 0.18])
    statuses = ["COMPLETED", "SCHEDULED", "IN_PROGRESS", "DELAYED"]
    status_weights = normalize_weights([0.58, 0.14, 0.12, 0.16])
    severity_map = {
        "INSPECTION": ["LOW", "MEDIUM"],
        "EMERGENCY_REPAIR": ["HIGH", "CRITICAL"],
        "COSMETIC": ["LOW", "MEDIUM"],
        "SENSOR_CALIBRATION": ["MEDIUM", "HIGH"],
        "RESTRAINT_TEST": ["MEDIUM", "HIGH"],
    }
    vendors = ["LiftWorks", "ParkTech", "MotionLab", "Apex Systems", "TrackLine"]

    rows: list[dict[str, object]] = []
    for maintenance_id in range(1, count + 1):
        ride_id = int(rng.choice(ride_ids))
        ride_row = ride_lookup.loc[ride_id]
        maintenance_type = str(rng.choice(maintenance_types, p=type_weights))
        status = str(rng.choice(statuses, p=status_weights))
        severity = str(rng.choice(severity_map[maintenance_type]))
        scheduled_start = start_date + timedelta(days=int(rng.integers(0, total_days)), hours=int(rng.integers(0, 23)))
        actual_start = scheduled_start + timedelta(hours=int(rng.integers(0, 10)))
        if status == "SCHEDULED":
            actual_start_value = pd.NA
            actual_end_value = pd.NA
            downtime_hours = float(np.round(rng.uniform(1.5, 5.5), 2))
        elif status == "IN_PROGRESS":
            actual_start_value = actual_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            actual_end_value = pd.NA
            downtime_hours = float(np.round(rng.uniform(2.0, 8.0), 2))
        else:
            downtime_hours = float(np.round(rng.uniform(1.0, 6.0) * (1.45 if severity in {"HIGH", "CRITICAL"} else 1.0), 2))
            actual_start_value = actual_start.strftime("%Y-%m-%dT%H:%M:%SZ")
            extra_delay = 2 if status == "DELAYED" else 0
            actual_end = actual_start + timedelta(hours=float(downtime_hours) + extra_delay)
            actual_end_value = actual_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        issue_pool = INCIDENT_DESCRIPTIONS["RIDE_OUTAGE"] if maintenance_type in {"EMERGENCY_REPAIR", "SENSOR_CALIBRATION", "RESTRAINT_TEST"} else INCIDENT_DESCRIPTIONS["QUEUE_DISRUPTION"]
        rows.append(
            {
                "RideMaintenanceId": maintenance_id,
                "MaintenanceNumber": f"MNT{maintenance_id:07d}",
                "Ride": ride_id,
                "ScheduledStart": scheduled_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ActualStart": actual_start_value,
                "ActualEnd": actual_end_value,
                "MaintenanceType": maintenance_type,
                "Status": status,
                "Severity": severity,
                "DowntimeHours": downtime_hours,
                "IssueSummary": str(rng.choice(issue_pool)),
                "VendorName": str(rng.choice(vendors)) if str(ride_row["RideType"]) != "FAMILY_FLAT" else "InHouseOps",
            }
        )

    return pd.DataFrame(rows)


def generate_shifts(
    config: dict,
    parks: pd.DataFrame,
    zones: pd.DataFrame,
    rides: pd.DataFrame,
    employees: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["shifts"])
    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    total_days = int(config["resolved_counts"]["days"])
    short_handed_rate = float(config["behavior"]["staffing"]["short_handed_rate"])
    overtime_rate = float(config["behavior"]["staffing"]["overtime_rate"])
    role_lookup = {row["role"]: row for row in ROLE_DEFINITIONS}
    employee_ids = employees["EmployeeId"].to_numpy()
    employee_lookup = employees.set_index("EmployeeId")
    zone_lookup = zones.set_index("ZoneId")
    rides_by_zone = {zone_id: frame["RideId"].to_numpy() for zone_id, frame in rides.groupby("Zone", sort=False)}

    shift_blocks = {
        "OPEN": (8, 8),
        "MID": (11, 8),
        "CLOSE": (15, 8),
        "OVERNIGHT": (22, 7),
    }
    block_names = list(shift_blocks.keys())

    rows: list[dict[str, object]] = []
    for shift_id in range(1, count + 1):
        employee_id = int(rng.choice(employee_ids))
        employee_row = employee_lookup.loc[employee_id]
        park_id = int(employee_row["Park"])
        zone_id = int(employee_row["HomeZone"])
        if rng.random() < 0.28:
            candidate_zones = zones.loc[zones["Park"] == park_id, "ZoneId"].to_numpy()
            zone_id = int(rng.choice(candidate_zones))

        shift_type = str(rng.choice(block_names, p=normalize_weights([0.28, 0.36, 0.28, 0.08])))
        start_hour, duration_hours = shift_blocks[shift_type]
        shift_start = start_date + timedelta(days=int(rng.integers(0, total_days)), hours=start_hour, minutes=int(rng.integers(0, 30)) * 2)
        overtime = bool(rng.random() < overtime_rate)
        shift_end = shift_start + timedelta(hours=duration_hours + (1.5 if overtime else 0.0))

        role = str(employee_row["RoleType"])
        assignment_type = str(role_lookup[role]["assignment"])
        ride_value: int | pd._libs.missing.NAType = pd.NA
        if bool(role_lookup[role]["ride_eligible"]) and zone_id in rides_by_zone and len(rides_by_zone[zone_id]):
            ride_value = int(rng.choice(rides_by_zone[zone_id]))

        coverage_status = "SHORT_HANDED" if rng.random() < short_handed_rate else str(rng.choice(["STAFFED", "CALL_OUT_COVERED", "REDEPLOYED"], p=[0.76, 0.14, 0.10]))
        rows.append(
            {
                "ShiftId": shift_id,
                "ShiftNumber": f"SFT{shift_id:07d}",
                "Employee": employee_id,
                "Park": park_id,
                "Zone": zone_id,
                "Ride": ride_value,
                "ShiftStart": shift_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ShiftEnd": shift_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ShiftType": shift_type,
                "AssignmentType": assignment_type,
                "CoverageStatus": coverage_status,
                "OvertimeFlag": overtime,
            }
        )

    return pd.DataFrame(rows)
