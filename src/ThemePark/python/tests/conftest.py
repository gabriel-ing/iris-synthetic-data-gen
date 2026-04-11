from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from DataGen.config import load_config
from DataGen.generators.dimensions import generate_employees, generate_guests, generate_parks, generate_rides, generate_zones
from DataGen.generators.operations import generate_feedback, generate_incidents, generate_tickets
from DataGen.generators.staffing import generate_ride_maintenance, generate_shifts
from DataGen.rng import make_rng


def build_dataset(config: dict) -> dict[str, pd.DataFrame]:
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
    feedback = generate_feedback(config, parks, zones, rides, tickets, incidents, make_rng(seed, "feedback"))

    return {
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


def write_config(tmp_path: Path, data: dict) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return config_path


def small_config_dict(tmp_path: Path, seed: int = 42) -> dict:
    return {
        "seed": seed,
        "currency": "USD",
        "time": {
            "start_date": "2026-05-01",
            "days": 45,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "parks": 3,
                "zones": 12,
                "rides": 30,
                "ride_maintenance": 42,
                "employees": 60,
                "shifts": 200,
                "guests": 160,
                "tickets": 240,
                "incidents": 36,
                "feedback": 96,
            },
        },
        "output": {
            "path": str(tmp_path / "out_theme_park"),
            "overwrite": True,
        },
    }


def load_small_config(tmp_path: Path, seed: int = 42) -> dict:
    cfg = small_config_dict(tmp_path, seed=seed)
    path = write_config(tmp_path, cfg)
    return load_config(path)
