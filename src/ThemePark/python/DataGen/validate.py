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
        raise AssertionError(message)
    checks.append(message)


def validate_all(
    config: dict,
    parks: pd.DataFrame,
    zones: pd.DataFrame,
    rides: pd.DataFrame,
    ride_maintenance: pd.DataFrame,
    employees: pd.DataFrame,
    shifts: pd.DataFrame,
    guests: pd.DataFrame,
    tickets: pd.DataFrame,
    incidents: pd.DataFrame,
    feedback: pd.DataFrame,
) -> ValidationResult:
    checks: list[str] = []
    warnings: list[str] = []
    counts = config["resolved_counts"]

    _assert(len(parks) == counts["parks"], "park row count matches configuration", checks)
    _assert(len(zones) == counts["zones"], "zone row count matches configuration", checks)
    _assert(len(rides) == counts["rides"], "ride row count matches configuration", checks)
    _assert(len(ride_maintenance) == counts["ride_maintenance"], "ride maintenance row count matches configuration", checks)
    _assert(len(employees) == counts["employees"], "employee row count matches configuration", checks)
    _assert(len(shifts) == counts["shifts"], "shift row count matches configuration", checks)
    _assert(len(guests) == counts["guests"], "guest row count matches configuration", checks)
    _assert(len(tickets) == counts["tickets"], "ticket row count matches configuration", checks)
    _assert(len(incidents) == counts["incidents"], "incident row count matches configuration", checks)
    _assert(len(feedback) == counts["feedback"], "feedback row count matches configuration", checks)

    park_ids = set(parks["ParkId"].tolist())
    zone_ids = set(zones["ZoneId"].tolist())
    ride_ids = set(rides["RideId"].tolist())
    employee_ids = set(employees["EmployeeId"].tolist())
    guest_ids = set(guests["GuestId"].tolist())
    ticket_ids = set(tickets["TicketId"].tolist())

    _assert(set(zones["Park"]).issubset(park_ids), "zones reference valid parks", checks)
    _assert(set(rides["Zone"]).issubset(zone_ids), "rides reference valid zones", checks)
    _assert(set(ride_maintenance["Ride"]).issubset(ride_ids), "ride maintenance references valid rides", checks)
    _assert(set(employees["Park"]).issubset(park_ids), "employees reference valid parks", checks)
    _assert(set(employees["HomeZone"]).issubset(zone_ids), "employees reference valid home zones", checks)
    _assert(set(shifts["Employee"]).issubset(employee_ids), "shifts reference valid employees", checks)
    _assert(set(shifts["Park"]).issubset(park_ids), "shifts reference valid parks", checks)
    _assert(set(shifts["Zone"]).issubset(zone_ids), "shifts reference valid zones", checks)
    ride_shift = shifts["Ride"]
    _assert(ride_shift[ride_shift.notna()].isin(rides["RideId"]).all(), "shifts reference valid rides when assigned", checks)
    _assert(set(tickets["Guest"]).issubset(guest_ids), "tickets reference valid guests", checks)
    _assert(set(tickets["Park"]).issubset(park_ids), "tickets reference valid parks", checks)
    _assert(set(incidents["Park"]).issubset(park_ids), "incidents reference valid parks", checks)
    incident_zone = incidents["Zone"]
    _assert(incident_zone[incident_zone.notna()].isin(zones["ZoneId"]).all(), "incidents reference valid zones when present", checks)
    incident_ride = incidents["Ride"]
    _assert(incident_ride[incident_ride.notna()].isin(rides["RideId"]).all(), "incidents reference valid rides when present", checks)
    incident_ticket = incidents["Ticket"]
    _assert(incident_ticket[incident_ticket.notna()].isin(tickets["TicketId"]).all(), "incidents reference valid tickets when present", checks)
    incident_employee = incidents["ReportedEmployee"]
    _assert(incident_employee[incident_employee.notna()].isin(employees["EmployeeId"]).all(), "incidents reference valid employees when present", checks)
    _assert(set(feedback["Ticket"]).issubset(ticket_ids), "feedback references valid tickets", checks)
    _assert(set(feedback["Park"]).issubset(park_ids), "feedback references valid parks", checks)
    feedback_ride = feedback["Ride"]
    _assert(feedback_ride[feedback_ride.notna()].isin(rides["RideId"]).all(), "feedback references valid rides when present", checks)

    zone_parks = zones.set_index("ZoneId")["Park"].to_dict()
    ride_zones = rides.set_index("RideId")["Zone"].to_dict()
    employee_parks = employees.set_index("EmployeeId")["Park"].to_dict()
    ticket_parks = tickets.set_index("TicketId")["Park"].to_dict()

    _assert((employees["HomeZone"].map(zone_parks) == employees["Park"]).all(), "employee home zones belong to the employee park", checks)
    _assert((rides["Zone"].map(zone_parks).isin(parks["ParkId"])).all(), "rides belong to zones with valid parks", checks)
    _assert((shifts["Zone"].map(zone_parks) == shifts["Park"]).all(), "shift zones belong to the shift park", checks)
    _assert((shifts["Employee"].map(employee_parks) == shifts["Park"]).all(), "shift employees belong to the shift park", checks)
    shift_with_ride = shifts.loc[shifts["Ride"].notna()].copy()
    if len(shift_with_ride):
        _assert((shift_with_ride["Ride"].map(ride_zones) == shift_with_ride["Zone"]).all(), "shift rides stay within the assigned zone", checks)

    maintenance_start = pd.to_datetime(ride_maintenance["ScheduledStart"], utc=True)
    maintenance_actual_start = pd.to_datetime(ride_maintenance["ActualStart"], utc=True, errors="coerce")
    maintenance_actual_end = pd.to_datetime(ride_maintenance["ActualEnd"], utc=True, errors="coerce")
    _assert((maintenance_actual_start.dropna() >= maintenance_start.loc[maintenance_actual_start.dropna().index]).all(), "maintenance actual start is not before scheduled start", checks)
    completed_mask = maintenance_actual_end.notna() & maintenance_actual_start.notna()
    _assert((maintenance_actual_end.loc[completed_mask] >= maintenance_actual_start.loc[completed_mask]).all(), "maintenance actual end is not before actual start", checks)
    _assert((ride_maintenance["DowntimeHours"] >= 0).all(), "maintenance downtime hours are non-negative", checks)

    shift_start = pd.to_datetime(shifts["ShiftStart"], utc=True)
    shift_end = pd.to_datetime(shifts["ShiftEnd"], utc=True)
    _assert((shift_end > shift_start).all(), "shift end timestamps are after shift start", checks)

    ticket_visit = pd.to_datetime(tickets["VisitDate"], utc=True)
    _assert((tickets["PricePaid"] > 0).all(), "ticket prices are positive", checks)
    _assert(tickets["TicketStatus"].isin(["USED", "CANCELLED", "NO_SHOW", "UPGRADED"]).all(), "ticket status values stay within the supported set", checks)

    ride_park_map = {ride_id: zone_parks[zone_id] for ride_id, zone_id in ride_zones.items()}
    incident_with_zone = incidents.loc[incidents["Zone"].notna()].copy()
    if len(incident_with_zone):
        _assert((incident_with_zone["Zone"].map(zone_parks) == incident_with_zone["Park"]).all(), "incident zones belong to the incident park", checks)
    incident_with_ride = incidents.loc[incidents["Ride"].notna()].copy()
    if len(incident_with_ride):
        _assert((incident_with_ride["Ride"].map(ride_park_map) == incident_with_ride["Park"]).all(), "incident rides belong to the incident park", checks)
    incident_with_ticket = incidents.loc[incidents["Ticket"].notna()].copy()
    if len(incident_with_ticket):
        _assert((incident_with_ticket["Ticket"].map(ticket_parks) == incident_with_ticket["Park"]).all(), "incident tickets belong to the incident park", checks)
    incident_with_employee = incidents.loc[incidents["ReportedEmployee"].notna()].copy()
    if len(incident_with_employee):
        _assert((incident_with_employee["ReportedEmployee"].map(employee_parks) == incident_with_employee["Park"]).all(), "incident reporting employees belong to the incident park", checks)

    incident_at = pd.to_datetime(incidents["IncidentAt"], utc=True)
    _assert((incidents["ImpactMinutes"] > 0).all(), "incident impact minutes are positive", checks)
    _assert((incident_at >= pd.Timestamp(config["time"]["start_date"], tz="UTC") - pd.Timedelta(days=1)).all(), "incident timestamps stay within the configured run horizon", checks)

    feedback_submitted = pd.to_datetime(feedback["SubmittedAt"], utc=True)
    _assert(feedback["Rating"].between(1, 5).all(), "feedback ratings stay within 1-5", checks)
    _assert(feedback["Sentiment"].isin(["POSITIVE", "NEUTRAL", "NEGATIVE"]).all(), "feedback sentiment values stay within the supported set", checks)
    feedback_ticket_visit = pd.to_datetime(feedback["Ticket"].map(tickets.set_index("TicketId")["VisitDate"]), utc=True)
    _assert((feedback_submitted >= feedback_ticket_visit).all(), "feedback is submitted after the ticket visit date", checks)
    feedback_with_ride = feedback.loc[feedback["Ride"].notna()].copy()
    if len(feedback_with_ride):
        _assert((feedback_with_ride["Ride"].map(ride_park_map) == feedback_with_ride["Park"]).all(), "feedback rides belong to the feedback park", checks)
    low_rating = feedback["Rating"] <= int(config["behavior"]["feedback"]["follow_up_threshold"])
    _assert((feedback.loc[low_rating, "RequiresFollowUp"]).all(), "low-rating feedback requires follow-up", checks)

    if float((incidents["IncidentType"] == "RIDE_OUTAGE").mean()) < 0.12:
        warnings.append("Ride-outage incidents are relatively sparse; outage-triage demos may look too easy.")
    if float((feedback["Sentiment"] == "NEGATIVE").mean()) < 0.08:
        warnings.append("Negative feedback is sparse; complaint-triage workflows may lack edge cases.")
    if float((shifts["CoverageStatus"] == "SHORT_HANDED").mean()) < 0.04:
        warnings.append("Short-handed shift coverage is limited; staffing-assistant demos may feel thin.")

    return ValidationResult(ok=True, checks=checks, warnings=warnings)
