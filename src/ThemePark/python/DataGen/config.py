from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Counts:
    parks: int
    zones: int
    rides: int
    ride_maintenance: int
    employees: int
    shifts: int
    guests: int
    tickets: int
    incidents: int
    feedback: int


def _default_config() -> dict[str, Any]:
    return {
        "seed": 42,
        "currency": "USD",
        "time": {
            "start_date": "2026-05-01",
            "days": 120,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "factor": 1,
            "base_counts": {
                "parks": 6,
                "zones": 30,
                "rides": 112,
                "ride_maintenance": 260,
                "employees": 420,
                "shifts": 1600,
                "guests": 2800,
                "tickets": 4200,
                "incidents": 260,
                "feedback": 1100,
            },
            "counts": {
                "parks": 6,
                "zones": 30,
                "rides": 112,
                "ride_maintenance": 260,
                "employees": 420,
                "shifts": 1600,
                "guests": 2800,
                "tickets": 4200,
                "incidents": 260,
                "feedback": 1100,
            },
        },
        "output": {
            "path": "./out_theme_park",
            "overwrite": True,
        },
        "behavior": {
            "parks": {
                "region_weights": {
                    "SOUTHEAST": 0.28,
                    "WEST": 0.24,
                    "MIDWEST": 0.18,
                    "NORTHEAST": 0.16,
                    "INTERNATIONAL": 0.14,
                },
                "park_type_weights": {
                    "DESTINATION": 0.34,
                    "CITY": 0.26,
                    "RESORT": 0.22,
                    "WATER": 0.18,
                },
            },
            "rides": {
                "type_weights": {
                    "COASTER": 0.18,
                    "DARK_RIDE": 0.16,
                    "DROP_TOWER": 0.10,
                    "FAMILY_FLAT": 0.22,
                    "LOG_FLUME": 0.12,
                    "SIMULATOR": 0.12,
                    "WATER_RIDE": 0.10,
                },
                "operating_share": 0.90,
            },
            "staffing": {
                "role_weights": {
                    "RIDE_OPERATOR": 0.34,
                    "MECHANIC": 0.12,
                    "GUEST_SERVICES": 0.20,
                    "SAFETY_COORDINATOR": 0.10,
                    "ENTERTAINMENT_HOST": 0.12,
                    "AREA_SUPERVISOR": 0.12,
                },
                "overtime_rate": 0.11,
                "short_handed_rate": 0.08,
            },
            "tickets": {
                "type_weights": {
                    "DAY_PASS": 0.42,
                    "MULTI_DAY": 0.18,
                    "ANNUAL_PASS": 0.16,
                    "FAST_ACCESS": 0.14,
                    "VIP": 0.10,
                },
                "channel_weights": {
                    "MOBILE_APP": 0.38,
                    "WEBSITE": 0.27,
                    "ON_SITE": 0.17,
                    "HOTEL_DESK": 0.08,
                    "TRAVEL_AGENT": 0.10,
                },
                "fast_access_share": 0.24,
                "cancelled_share": 0.04,
            },
            "incidents": {
                "type_weights": {
                    "RIDE_OUTAGE": 0.24,
                    "GUEST_MEDICAL": 0.15,
                    "LOST_CHILD": 0.09,
                    "WEATHER_DELAY": 0.10,
                    "QUEUE_DISRUPTION": 0.15,
                    "COSTUME_MALFUNCTION": 0.08,
                    "SECURITY_ESCALATION": 0.08,
                    "FOOD_SPILL": 0.11,
                },
                "severity_weights": {
                    "LOW": 0.36,
                    "MEDIUM": 0.34,
                    "HIGH": 0.20,
                    "CRITICAL": 0.10,
                },
                "ticket_link_share": 0.46,
            },
            "feedback": {
                "channel_weights": {
                    "MOBILE_SURVEY": 0.42,
                    "EMAIL": 0.22,
                    "KIOSK": 0.18,
                    "SMS": 0.10,
                    "CHATBOT": 0.08,
                },
                "follow_up_threshold": 2,
                "negative_share": 0.24,
            },
        },
    }


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _selected_base_counts(scale: dict[str, Any]) -> dict[str, int]:
    source = scale["counts"] if scale["mode"] == "explicit" else scale["base_counts"]
    return {key: int(value) for key, value in source.items()}


def _apply_scale_factor_override(config: dict[str, Any], scale_factor_override: int | None) -> dict[str, Any]:
    if scale_factor_override is None:
        return config

    factor = int(scale_factor_override)
    if factor <= 0:
        raise ValueError("scale_factor_override must be a positive integer")

    scale = dict(config["scale"])
    scale["mode"] = "factor"
    scale["factor"] = factor
    scale["base_counts"] = _selected_base_counts(config["scale"])
    config["scale"] = scale
    return config


def _derive_counts(config: dict[str, Any]) -> Counts:
    scale = config["scale"]
    mode = scale["mode"]
    if mode == "explicit":
        counts = scale["counts"]
    elif mode == "factor":
        factor = int(scale.get("factor", 1))
        base_counts = scale["base_counts"]
        counts = {key: int(value * factor) for key, value in base_counts.items()}
    else:
        raise ValueError(f"Unsupported scale.mode: {mode}")

    return Counts(
        parks=int(counts["parks"]),
        zones=int(counts["zones"]),
        rides=int(counts["rides"]),
        ride_maintenance=int(counts["ride_maintenance"]),
        employees=int(counts["employees"]),
        shifts=int(counts["shifts"]),
        guests=int(counts["guests"]),
        tickets=int(counts["tickets"]),
        incidents=int(counts["incidents"]),
        feedback=int(counts["feedback"]),
    )


def load_config(config_path: str | Path, scale_factor_override: int | None = None) -> dict[str, Any]:
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as handle:
        user_cfg = yaml.safe_load(handle) or {}

    merged = _deep_merge(_default_config(), user_cfg)
    merged = _apply_scale_factor_override(merged, scale_factor_override)
    counts = _derive_counts(merged)
    merged["resolved_counts"] = {
        "days": int(merged["time"]["days"]),
        "parks": counts.parks,
        "zones": counts.zones,
        "rides": counts.rides,
        "ride_maintenance": counts.ride_maintenance,
        "employees": counts.employees,
        "shifts": counts.shifts,
        "guests": counts.guests,
        "tickets": counts.tickets,
        "incidents": counts.incidents,
        "feedback": counts.feedback,
    }
    return merged
