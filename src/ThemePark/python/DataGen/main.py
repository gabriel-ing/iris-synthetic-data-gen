from __future__ import annotations

import argparse

from DataGen.config import load_config
from DataGen.generators.dimensions import generate_employees, generate_guests, generate_parks, generate_rides, generate_zones
from DataGen.generators.operations import generate_feedback, generate_incidents, generate_tickets
from DataGen.generators.staffing import generate_ride_maintenance, generate_shifts
from DataGen.rng import make_rng
from DataGen.validate import validate_all
from DataGen.writer import prepare_output_dir, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic theme park management dataset generator")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--scale-factor", type=int, help="Multiply the configured base dataset size by this factor")
    return parser.parse_args()


def _summary(shifts, tickets, incidents, feedback) -> dict:
    incident_rate = float((incidents["IncidentType"] == "RIDE_OUTAGE").mean())
    follow_up_rate = float(feedback["RequiresFollowUp"].mean())
    fast_access_rate = float(tickets["FastAccessFlag"].mean())
    short_handed_rate = float((shifts["CoverageStatus"] == "SHORT_HANDED").mean())

    top_incident_types = incidents.groupby("IncidentType", observed=True).size().sort_values(ascending=False).head(5).to_dict()
    top_feedback_topics = feedback.groupby("Topic", observed=True).size().sort_values(ascending=False).head(5).to_dict()

    return {
        "counts": {
            "parks": len(shifts["Park"].drop_duplicates()),
            "tickets": len(tickets),
            "incidents": len(incidents),
            "feedback": len(feedback),
        },
        "rates": {
            "ride_outage_share": round(incident_rate, 4),
            "follow_up_share": round(follow_up_rate, 4),
            "fast_access_share": round(fast_access_rate, 4),
            "short_handed_shift_share": round(short_handed_rate, 4),
        },
        "top_incident_types": top_incident_types,
        "top_feedback_topics": top_feedback_topics,
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config, scale_factor_override=args.scale_factor)
    seed = int(config["seed"])

    out_dir = prepare_output_dir(config["output"]["path"], config["output"].get("overwrite", True))

    parks = generate_parks(config, make_rng(seed, "parks"))
    zones = generate_zones(config, parks, make_rng(seed, "zones"))
    rides = generate_rides(config, parks, zones, make_rng(seed, "rides"))
    employees = generate_employees(config, parks, zones, make_rng(seed, "employees"))
    guests = generate_guests(config, make_rng(seed, "guests"))
    ride_maintenance = generate_ride_maintenance(config, rides, make_rng(seed, "ride_maintenance"))
    shifts = generate_shifts(config, parks, zones, rides, employees, make_rng(seed, "shifts"))
    tickets = generate_tickets(config, parks, guests, make_rng(seed, "tickets"))
    incidents = generate_incidents(config, parks, zones, rides, employees, tickets, make_rng(seed, "incidents"))
    feedback = generate_feedback(config, parks, zones, rides, tickets, incidents, make_rng(seed, "feedback"))

    tables = {
        "parks": parks,
        "zones": zones,
        "rides": rides,
        "ride_maintenance": ride_maintenance,
        "employees": employees,
        "shifts": shifts,
        "guests": guests,
        "tickets": tickets,
        "incidents": incidents,
        "feedback": feedback,
    }
    for name, frame in tables.items():
        write_csv(frame, out_dir, name)

    validation = validate_all(config, parks, zones, rides, ride_maintenance, employees, shifts, guests, tickets, incidents, feedback)
    summary = _summary(shifts, tickets, incidents, feedback)

    print("Validation checks passed:", len(validation.checks))
    if validation.warnings:
        print("Validation warnings:")
        for warning in validation.warnings:
            print(" -", warning)
    print("Run summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
