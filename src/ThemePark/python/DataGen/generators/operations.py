from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from DataGen.generators.catalog import FEEDBACK_SNIPPETS, INCIDENT_DESCRIPTIONS, INCIDENT_RESOLUTIONS
from DataGen.rng import normalize_weights


def generate_tickets(config: dict, parks: pd.DataFrame, guests: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    count = int(config["resolved_counts"]["tickets"])
    ticket_cfg = config["behavior"]["tickets"]
    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC")
    total_days = int(config["resolved_counts"]["days"])
    park_ids = parks["ParkId"].to_numpy()
    park_weights = parks["DailyCapacity"].to_numpy(dtype=float)
    park_weights = park_weights / park_weights.sum()
    guest_ids = guests["GuestId"].to_numpy()
    guest_lookup = guests.set_index("GuestId")
    type_weights = ticket_cfg["type_weights"]
    channel_weights = ticket_cfg["channel_weights"]
    ticket_types = list(type_weights.keys())
    channels = list(channel_weights.keys())
    cancelled_share = float(ticket_cfg["cancelled_share"])
    fast_access_share = float(ticket_cfg["fast_access_share"])
    price_bands = {
        "DAY_PASS": (89, 149),
        "MULTI_DAY": (160, 340),
        "ANNUAL_PASS": (260, 520),
        "FAST_ACCESS": (145, 240),
        "VIP": (260, 520),
    }
    bundle_options = ["NONE", "DINING_PHOTO", "CHARACTER_MEET", "RAINY_DAY_CREDIT", "PARKING_PLUS"]

    rows: list[dict[str, object]] = []
    for ticket_id in range(1, count + 1):
        park_id = int(rng.choice(park_ids, p=park_weights))
        guest_id = int(rng.choice(guest_ids))
        guest_row = guest_lookup.loc[guest_id]
        visit_date = start_date + timedelta(days=int(rng.integers(0, total_days)), hours=int(rng.integers(8, 18)), minutes=int(rng.integers(0, 4)) * 15)
        ticket_type = str(rng.choice(ticket_types, p=normalize_weights([type_weights[item] for item in ticket_types])))
        channel = str(rng.choice(channels, p=normalize_weights([channel_weights[item] for item in channels])))
        status_roll = float(rng.random())
        if status_roll < cancelled_share:
            status = "CANCELLED"
        elif status_roll < cancelled_share + 0.03:
            status = "NO_SHOW"
        elif status_roll < cancelled_share + 0.11:
            status = "UPGRADED"
        else:
            status = "USED"

        price_low, price_high = price_bands[ticket_type]
        base_price = float(np.round(rng.uniform(price_low, price_high), 2))
        party_size = int(guest_row["PartySize"])
        loyalty_tier = str(guest_row["LoyaltyTier"])
        price_multiplier = 0.86 if loyalty_tier == "ANNUAL_PASS" and ticket_type == "DAY_PASS" else 1.0
        fast_access_flag = bool(ticket_type in {"FAST_ACCESS", "VIP"} or rng.random() < fast_access_share)
        rows.append(
            {
                "TicketId": ticket_id,
                "TicketCode": f"TKT{ticket_id:08d}",
                "Guest": guest_id,
                "Park": park_id,
                "VisitDate": visit_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "TicketType": ticket_type,
                "EntryChannel": channel,
                "PricePaid": float(np.round(base_price * price_multiplier * max(1.0, min(1.8, party_size / 2.0)), 2)),
                "FastAccessFlag": fast_access_flag,
                "AddOnBundle": "FAST_ACCESS" if fast_access_flag else str(rng.choice(bundle_options, p=normalize_weights([0.36, 0.20, 0.16, 0.12, 0.16]))),
                "TicketStatus": status,
            }
        )

    return pd.DataFrame(rows)


def generate_incidents(
    config: dict,
    parks: pd.DataFrame,
    zones: pd.DataFrame,
    rides: pd.DataFrame,
    employees: pd.DataFrame,
    tickets: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["incidents"])
    incident_cfg = config["behavior"]["incidents"]
    types = list(incident_cfg["type_weights"].keys())
    severities = list(incident_cfg["severity_weights"].keys())
    ticket_link_share = float(incident_cfg["ticket_link_share"])
    tickets_by_park = {park_id: frame["TicketId"].to_numpy() for park_id, frame in tickets.groupby("Park", sort=False)}
    employees_by_park = {park_id: frame["EmployeeId"].to_numpy() for park_id, frame in employees.groupby("Park", sort=False)}
    zones_by_park = {park_id: frame["ZoneId"].to_numpy() for park_id, frame in zones.groupby("Park", sort=False)}
    rides_by_zone = {zone_id: frame["RideId"].to_numpy() for zone_id, frame in rides.groupby("Zone", sort=False)}
    ride_lookup = rides.set_index("RideId")
    zone_lookup = zones.set_index("ZoneId")
    ticket_lookup = tickets.set_index("TicketId")
    park_ids = parks["ParkId"].to_numpy()

    rows: list[dict[str, object]] = []
    for incident_id in range(1, count + 1):
        incident_type = str(rng.choice(types, p=normalize_weights([incident_cfg["type_weights"][item] for item in types])))
        severity = str(rng.choice(severities, p=normalize_weights([incident_cfg["severity_weights"][item] for item in severities])))
        park_id = int(rng.choice(park_ids))
        zone_id = int(rng.choice(zones_by_park[park_id]))
        ride_value: int | pd._libs.missing.NAType = pd.NA
        if incident_type in {"RIDE_OUTAGE", "QUEUE_DISRUPTION", "WEATHER_DELAY"} and zone_id in rides_by_zone and len(rides_by_zone[zone_id]):
            ride_value = int(rng.choice(rides_by_zone[zone_id]))
        if incident_type == "RIDE_OUTAGE" and ride_value is pd.NA:
            ride_id = int(rng.choice(rides["RideId"].to_numpy()))
            ride_value = ride_id
            zone_id = int(ride_lookup.loc[ride_id, "Zone"])
            park_id = int(zone_lookup.loc[zone_id, "Park"])

        ticket_value: int | pd._libs.missing.NAType = pd.NA
        if rng.random() < ticket_link_share and park_id in tickets_by_park and len(tickets_by_park[park_id]):
            ticket_value = int(rng.choice(tickets_by_park[park_id]))
            ticket_row = ticket_lookup.loc[ticket_value]
            park_id = int(ticket_row["Park"])
        employee_value: int | pd._libs.missing.NAType = pd.NA
        if park_id in employees_by_park and len(employees_by_park[park_id]):
            employee_value = int(rng.choice(employees_by_park[park_id]))

        visit_ts = pd.Timestamp(ticket_lookup.loc[ticket_value, "VisitDate"], tz="UTC") if ticket_value is not pd.NA else pd.Timestamp(config["time"]["start_date"], tz="UTC") + timedelta(days=int(rng.integers(0, int(config["resolved_counts"]["days"]))), hours=int(rng.integers(8, 23)))
        incident_at = visit_ts + timedelta(minutes=int(rng.integers(0, 720)))
        impact_minutes = {
            "LOW": int(rng.integers(8, 25)),
            "MEDIUM": int(rng.integers(18, 55)),
            "HIGH": int(rng.integers(35, 120)),
            "CRITICAL": int(rng.integers(80, 240)),
        }[severity]
        status = "RESOLVED" if severity != "CRITICAL" or rng.random() < 0.76 else str(rng.choice(["UNDER_REVIEW", "ESCALATED", "CLOSED_WITH_FOLLOWUP"], p=[0.40, 0.22, 0.38]))

        rows.append(
            {
                "IncidentId": incident_id,
                "IncidentNumber": f"INC{incident_id:07d}",
                "Park": park_id,
                "Zone": zone_id,
                "Ride": ride_value,
                "Ticket": ticket_value,
                "ReportedEmployee": employee_value,
                "IncidentAt": incident_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "IncidentType": incident_type,
                "Severity": severity,
                "Status": status,
                "ImpactMinutes": impact_minutes,
                "Description": str(rng.choice(INCIDENT_DESCRIPTIONS[incident_type])),
                "ResolutionSummary": str(rng.choice(INCIDENT_RESOLUTIONS[incident_type])),
            }
        )

    return pd.DataFrame(rows)


def generate_queue_snapshot(
    config: dict,
    parks: pd.DataFrame,
    zones: pd.DataFrame,
    rides: pd.DataFrame,
    ride_maintenance: pd.DataFrame,
    tickets: pd.DataFrame,
    incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    start_date = pd.Timestamp(config["time"]["start_date"], tz="UTC").normalize()
    days = int(config["resolved_counts"]["days"])
    visit_days = pd.date_range(start=start_date, periods=days, freq="D", tz="UTC")

    zone_parks = zones.set_index("ZoneId")["Park"].to_dict()
    ride_frame = rides[["RideId", "Zone", "CapacityPerHour", "Status", "ThrillLevel", "RideType"]].copy()
    ride_frame["Park"] = ride_frame["Zone"].map(zone_parks)

    active_tickets = tickets.loc[tickets["TicketStatus"].isin(["USED", "UPGRADED"])].copy()
    active_tickets["VisitDay"] = pd.to_datetime(active_tickets["VisitDate"], utc=True).dt.strftime("%Y-%m-%d")
    park_day_volume = active_tickets.groupby(["Park", "VisitDay"], observed=True).size().to_dict()
    park_day_fast_access = active_tickets.groupby(["Park", "VisitDay"], observed=True)["FastAccessFlag"].mean().to_dict()

    maintenance_events = ride_maintenance.copy()
    maintenance_day = pd.to_datetime(
        maintenance_events["ActualStart"].fillna(maintenance_events["ScheduledStart"]),
        utc=True,
    ).dt.strftime("%Y-%m-%d")
    maintenance_events["QueueDay"] = maintenance_day
    maintenance_hours = maintenance_events.groupby(["Ride", "QueueDay"], observed=True)["DowntimeHours"].sum().to_dict()

    incident_events = incidents.loc[incidents["Ride"].notna()].copy()
    incident_events["QueueDay"] = pd.to_datetime(incident_events["IncidentAt"], utc=True).dt.strftime("%Y-%m-%d")
    incident_minutes = incident_events.groupby(["Ride", "QueueDay"], observed=True)["ImpactMinutes"].sum().to_dict()
    disruption_events = incident_events.groupby(["Ride", "QueueDay"], observed=True).size().to_dict()

    ride_type_boost = {
        "COASTER": 1.18,
        "DARK_RIDE": 0.92,
        "DROP_TOWER": 1.05,
        "FAMILY_FLAT": 0.88,
        "LOG_FLUME": 1.04,
        "SIMULATOR": 0.96,
        "WATER_RIDE": 1.10,
    }

    rows: list[dict[str, object]] = []
    queue_snapshot_id = 1
    for ride in ride_frame.itertuples(index=False):
        thrill_boost = 0.78 + (float(ride.ThrillLevel) * 0.08)
        type_boost = ride_type_boost.get(str(ride.RideType), 1.0)
        base_popularity = thrill_boost * type_boost
        for day in visit_days:
            day_key = day.strftime("%Y-%m-%d")
            park_id = int(ride.Park)
            park_volume = float(park_day_volume.get((park_id, day_key), 0))
            fast_access_pressure = float(park_day_fast_access.get((park_id, day_key), 0.0))
            downtime_hours = float(maintenance_hours.get((int(ride.RideId), day_key), 0.0))
            downtime_hours += float(incident_minutes.get((int(ride.RideId), day_key), 0.0)) / 60.0
            disruptions = int(disruption_events.get((int(ride.RideId), day_key), 0))

            if str(ride.Status) in {"SEASONAL", "STANDBY"} and day.month not in {5, 6, 7, 8, 9}:
                status = "CLOSED"
            elif downtime_hours >= 9.0:
                status = "CLOSED"
            elif str(ride.Status) == "LIMITED_HOURS" or downtime_hours >= 1.5 or disruptions > 0:
                status = "DELAYED"
            else:
                status = "OPERATING"

            operating_hours = 0.0 if status == "CLOSED" else max(2.0, 10.0 - min(downtime_hours, 8.0))
            demand = park_volume * base_popularity * rng.uniform(0.012, 0.035)
            demand *= 1.0 + min(0.35, fast_access_pressure * 0.40)
            hourly_capacity = float(ride.CapacityPerHour) * (0.82 if status == "DELAYED" else 1.0)
            throughput_per_hour = 0 if status == "CLOSED" else int(max(0.0, min(hourly_capacity, demand / max(1.0, operating_hours))))
            if status == "CLOSED":
                wait_minutes = 0
                queue_length = 0
            else:
                congestion = 0.0 if hourly_capacity <= 0 else max(0.0, demand / max(1.0, operating_hours) / hourly_capacity)
                wait_minutes = int(np.clip(8 + congestion * 70 + fast_access_pressure * 20 + disruptions * 9, 5, 240))
                queue_length = int(max(0, round(throughput_per_hour * wait_minutes / 60)))

            rows.append(
                {
                    "QueueSnapshotId": queue_snapshot_id,
                    "SnapshotAt": (day + pd.Timedelta(hours=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "Park": park_id,
                    "Ride": int(ride.RideId),
                    "WaitMinutes": wait_minutes,
                    "QueueLength": queue_length,
                    "ThroughputPerHour": throughput_per_hour,
                    "Status": status,
                    "FastAccessPressure": round(min(0.95, max(0.0, fast_access_pressure)), 4),
                    "DowntimeHours": round(downtime_hours, 2),
                }
            )
            queue_snapshot_id += 1

    return pd.DataFrame(rows)


def generate_feedback(
    config: dict,
    parks: pd.DataFrame,
    zones: pd.DataFrame,
    rides: pd.DataFrame,
    tickets: pd.DataFrame,
    incidents: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    count = int(config["resolved_counts"]["feedback"])
    feedback_cfg = config["behavior"]["feedback"]
    channels = list(feedback_cfg["channel_weights"].keys())
    follow_up_threshold = int(feedback_cfg["follow_up_threshold"])
    negative_share = float(feedback_cfg["negative_share"])
    ticket_ids = tickets["TicketId"].to_numpy()
    ticket_lookup = tickets.set_index("TicketId")
    rides_by_park = {
        park_id: rides.loc[rides["Zone"].isin(frame["ZoneId"]), "RideId"].to_numpy()
        for park_id, frame in zones.groupby("Park", sort=False)
    }
    incident_counts = incidents.groupby("Ticket", observed=True).size().to_dict() if "Ticket" in incidents else {}
    topics = list(FEEDBACK_SNIPPETS.keys())

    rows: list[dict[str, object]] = []
    for feedback_id in range(1, count + 1):
        ticket_id = int(rng.choice(ticket_ids))
        ticket_row = ticket_lookup.loc[ticket_id]
        park_id = int(ticket_row["Park"])
        visit_date = pd.Timestamp(ticket_row["VisitDate"], tz="UTC")
        topic = str(rng.choice(topics))
        incident_pressure = int(incident_counts.get(ticket_id, 0))
        negative = rng.random() < (negative_share + min(0.30, incident_pressure * 0.10))
        if topic == "RIDE_DOWNTIME":
            negative = negative or incident_pressure > 0
        sentiment = "NEGATIVE" if negative else str(rng.choice(["POSITIVE", "NEUTRAL"], p=[0.78, 0.22]))
        rating = int(rng.choice([1, 2, 3], p=[0.22, 0.46, 0.32])) if sentiment == "NEGATIVE" else int(rng.choice([3, 4, 5], p=[0.18, 0.38, 0.44]))
        ride_value: int | pd._libs.missing.NAType = pd.NA
        available_rides = rides_by_park.get(park_id, np.array([], dtype=int))
        if topic in {"RIDE_DOWNTIME", "WAIT_TIME", "ACCESSIBILITY", "MASCOT_EXPERIENCE"} and len(available_rides):
            ride_value = int(rng.choice(available_rides))
        polarity = "negative" if sentiment == "NEGATIVE" else "positive"
        summary = str(rng.choice(FEEDBACK_SNIPPETS[topic][polarity]))
        submitted_at = visit_date + timedelta(hours=int(rng.integers(1, 36)), minutes=int(rng.integers(0, 4)) * 15)
        rows.append(
            {
                "FeedbackId": feedback_id,
                "FeedbackNumber": f"FDB{feedback_id:07d}",
                "Ticket": ticket_id,
                "Park": park_id,
                "Ride": ride_value,
                "SubmittedAt": submitted_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Channel": str(rng.choice(channels, p=normalize_weights([feedback_cfg["channel_weights"][item] for item in channels]))),
                "Rating": rating,
                "Sentiment": sentiment,
                "Topic": topic,
                "Summary": summary,
                "RequiresFollowUp": bool(rating <= follow_up_threshold or (sentiment == "NEGATIVE" and topic in {"RIDE_DOWNTIME", "ACCESSIBILITY", "VALUE"})),
            }
        )

    return pd.DataFrame(rows)
