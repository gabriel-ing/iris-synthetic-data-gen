from __future__ import annotations

import argparse
import math
from typing import Iterable

import pandas as pd

from DataGen.config import load_config
from DataGen.generators.dimensions import generate_employees, generate_guests, generate_parks, generate_rides, generate_zones
from DataGen.generators.operations import generate_feedback, generate_incidents, generate_queue_snapshot, generate_tickets
from DataGen.generators.staffing import generate_ride_maintenance, generate_shifts
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


def _is_empty_delete(exc: Exception, sql: str) -> bool:
    return sql.lstrip().upper().startswith("DELETE FROM ") and getattr(exc, "sqlcode", None) == 100


def _exec_sql(iris, sql: str) -> None:
    try:
        stmt = iris.sql.prepare(sql)
        stmt.execute()
    except Exception as exc:
        if _is_empty_delete(exc, sql):
            return
        raise


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


def main(
    config_path: str,
    package: str = "ThemePark",
    clear_existing: bool = False,
    commit_every: int = 20000,
    scale_factor_override: int | None = None,
) -> dict:
    config = load_config(config_path, scale_factor_override=scale_factor_override)
    seed = int(config["seed"])

    parks = generate_parks(config, make_rng(seed, "parks"))
    zones = generate_zones(config, parks, make_rng(seed, "zones"))
    rides = generate_rides(config, parks, zones, make_rng(seed, "rides"))
    employees = generate_employees(config, parks, zones, make_rng(seed, "employees"))
    guests = generate_guests(config, make_rng(seed, "guests"))
    ride_maintenance = generate_ride_maintenance(config, rides, make_rng(seed, "ride_maintenance"))
    shifts = generate_shifts(config, parks, zones, rides, employees, make_rng(seed, "shifts"))
    tickets = generate_tickets(config, parks, guests, make_rng(seed, "tickets"))
    incidents = generate_incidents(config, parks, zones, rides, employees, tickets, make_rng(seed, "incidents"))
    queue_snapshot = generate_queue_snapshot(config, parks, zones, rides, ride_maintenance, tickets, incidents, make_rng(seed, "queue_snapshot"))
    feedback = generate_feedback(config, parks, zones, rides, tickets, incidents, make_rng(seed, "feedback"))

    validation = validate_all(config, parks, zones, rides, ride_maintenance, employees, shifts, guests, tickets, incidents, queue_snapshot, feedback)
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
        "Park": f"{package}.Parks",
        "Zone": f"{package}.Zones",
        "Ride": f"{package}.Rides",
        "RideMaintenance": f"{package}.RideMaintenance",
        "QueueSnapshot": f"{package}.QueueSnapshot",
        "Employee": f"{package}.Employees",
        "Shift": f"{package}.Shifts",
        "Guest": f"{package}.Guests",
        "Ticket": f"{package}.Tickets",
        "Incident": f"{package}.Incidents",
        "Feedback": f"{package}.Feedback",
    }

    if clear_existing:
        delete_order = [
            "Feedback",
            "Incident",
            "QueueSnapshot",
            "RideMaintenance",
            "Shift",
            "Ticket",
            "Employee",
            "Guest",
            "Ride",
            "Zone",
            "Park",
        ]
        for name in delete_order:
            _exec_sql(iris, f"TRUNCATE TABLE {tables[name]}")
            print(f"Truncated {tables[name]}")
        _exec_sql(iris, "COMMIT")

    park_cols = [
        "ParkCode",
        "ParkName",
        "Region",
        "Country",
        "ParkType",
        "OpeningDate",
        "OperatingModel",
        "DailyCapacity",
        "ActiveFlag",
    ]
    zone_cols = [
        "ZoneCode",
        "Park",
        "ZoneName",
        "Theme",
        "Environment",
        "FamilyIntensity",
        "CapacityClass",
        "IndoorFlag",
    ]
    ride_cols = [
        "RideCode",
        "Zone",
        "RideName",
        "RideType",
        "ThrillLevel",
        "HeightRequirementCm",
        "CapacityPerHour",
        "OpeningDate",
        "AccessibilitySupport",
        "Status",
    ]
    maintenance_cols = [
        "MaintenanceNumber",
        "Ride",
        "ScheduledStart",
        "ActualStart",
        "ActualEnd",
        "MaintenanceType",
        "Status",
        "Severity",
        "DowntimeHours",
        "IssueSummary",
        "VendorName",
    ]
    queue_snapshot_cols = [
        "SnapshotAt",
        "Park",
        "Ride",
        "WaitMinutes",
        "QueueLength",
        "ThroughputPerHour",
        "Status",
        "FastAccessPressure",
        "DowntimeHours",
    ]
    employee_cols = [
        "EmployeeNumber",
        "Park",
        "HomeZone",
        "EmployeeName",
        "RoleType",
        "SkillTier",
        "EmploymentType",
        "HireDate",
        "MascotQualifiedFlag",
        "ActiveFlag",
    ]
    shift_cols = [
        "ShiftNumber",
        "Employee",
        "Park",
        "Zone",
        "Ride",
        "ShiftStart",
        "ShiftEnd",
        "ShiftType",
        "AssignmentType",
        "CoverageStatus",
        "OvertimeFlag",
    ]
    guest_cols = [
        "GuestNumber",
        "HomeCountry",
        "Segment",
        "AgeBand",
        "PartySize",
        "AccessibilityNeeds",
        "LoyaltyTier",
        "VisitIntent",
    ]
    ticket_cols = [
        "TicketCode",
        "Guest",
        "Park",
        "VisitDate",
        "TicketType",
        "EntryChannel",
        "PricePaid",
        "FastAccessFlag",
        "AddOnBundle",
        "TicketStatus",
    ]
    incident_cols = [
        "IncidentNumber",
        "Park",
        "Zone",
        "Ride",
        "Ticket",
        "ReportedEmployee",
        "IncidentAt",
        "IncidentType",
        "Severity",
        "Status",
        "ImpactMinutes",
        "Description",
        "ResolutionSummary",
    ]
    feedback_cols = [
        "FeedbackNumber",
        "Ticket",
        "Park",
        "Ride",
        "SubmittedAt",
        "Channel",
        "Rating",
        "Sentiment",
        "Topic",
        "Summary",
        "RequiresFollowUp",
    ]

    inserts = {
        tables["Park"]: (park_cols, _without_object_id(parks, "ParkId")),
        tables["Zone"]: (zone_cols, _without_object_id(zones, "ZoneId")),
        tables["Ride"]: (ride_cols, _without_object_id(rides, "RideId")),
        tables["Employee"]: (employee_cols, _without_object_id(employees, "EmployeeId")),
        tables["Guest"]: (guest_cols, _without_object_id(guests, "GuestId")),
        tables["RideMaintenance"]: (maintenance_cols, _without_object_id(ride_maintenance, "RideMaintenanceId")),
        tables["QueueSnapshot"]: (queue_snapshot_cols, _without_object_id(queue_snapshot, "QueueSnapshotId")),
        tables["Shift"]: (shift_cols, _without_object_id(shifts, "ShiftId")),
        tables["Ticket"]: (ticket_cols, _without_object_id(tickets, "TicketId")),
        tables["Incident"]: (incident_cols, _without_object_id(incidents, "IncidentId")),
        tables["Feedback"]: (feedback_cols, _without_object_id(feedback, "FeedbackId")),
    }

    insert_order = [
        tables["Park"],
        tables["Zone"],
        tables["Ride"],
        tables["QueueSnapshot"],
        tables["Employee"],
        tables["Guest"],
        tables["RideMaintenance"],
        tables["Shift"],
        tables["Ticket"],
        tables["Incident"],
        tables["Feedback"],
    ]

    row_counts: dict[str, int] = {}
    for table_name in insert_order:
        columns, df = inserts[table_name]
        row_counts[table_name] = _insert_df(iris, table_name, columns, df, commit_every)
        print(f"Inserted {row_counts[table_name]} rows into {table_name}")

    return row_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Directly insert synthetic theme park data into IRIS")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--package", default="ThemePark", help="IRIS package prefix to insert into")
    parser.add_argument("--clear-existing", action="store_true", help="Truncate existing rows before insert")
    parser.add_argument("--commit-every", type=int, default=20000, help="Commit every N inserted rows")
    parser.add_argument("--scale-factor", type=int, help="Multiply configured base dataset size by this factor")
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
