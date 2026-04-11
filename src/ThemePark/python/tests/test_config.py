from __future__ import annotations

from DataGen.config import load_config
from conftest import write_config


def test_explicit_counts_are_resolved(tmp_path):
    cfg = {
        "scale": {
            "mode": "explicit",
            "counts": {
                "parks": 10,
                "zones": 11,
                "rides": 12,
                "ride_maintenance": 13,
                "employees": 14,
                "shifts": 15,
                "guests": 16,
                "tickets": 17,
                "incidents": 18,
                "feedback": 19,
            },
        }
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["parks"] == 10
    assert resolved["zones"] == 11
    assert resolved["rides"] == 12
    assert resolved["ride_maintenance"] == 13
    assert resolved["employees"] == 14
    assert resolved["shifts"] == 15
    assert resolved["guests"] == 16
    assert resolved["tickets"] == 17
    assert resolved["incidents"] == 18
    assert resolved["feedback"] == 19


def test_factor_counts_are_resolved(tmp_path):
    cfg = {
        "scale": {
            "mode": "factor",
            "factor": 3,
            "base_counts": {
                "parks": 2,
                "zones": 3,
                "rides": 4,
                "ride_maintenance": 5,
                "employees": 6,
                "shifts": 7,
                "guests": 8,
                "tickets": 9,
                "incidents": 10,
                "feedback": 11,
            },
        }
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["parks"] == 6
    assert resolved["zones"] == 9
    assert resolved["rides"] == 12
    assert resolved["ride_maintenance"] == 15
    assert resolved["employees"] == 18
    assert resolved["shifts"] == 21
    assert resolved["guests"] == 24
    assert resolved["tickets"] == 27
    assert resolved["incidents"] == 30
    assert resolved["feedback"] == 33


def test_scale_factor_override_multiplies_configured_counts(tmp_path):
    cfg = {
        "scale": {
            "mode": "explicit",
            "counts": {
                "parks": 10,
                "zones": 11,
                "rides": 12,
                "ride_maintenance": 13,
                "employees": 14,
                "shifts": 15,
                "guests": 16,
                "tickets": 17,
                "incidents": 18,
                "feedback": 19,
            },
        },
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path, scale_factor_override=2)

    resolved = loaded["resolved_counts"]
    assert resolved["parks"] == 20
    assert resolved["zones"] == 22
    assert resolved["rides"] == 24
    assert resolved["ride_maintenance"] == 26
    assert resolved["employees"] == 28
    assert resolved["shifts"] == 30
    assert resolved["guests"] == 32
    assert resolved["tickets"] == 34
    assert resolved["incidents"] == 36
    assert resolved["feedback"] == 38
