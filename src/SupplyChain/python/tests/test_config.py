from __future__ import annotations

from DataGen.config import load_config
from conftest import write_config


def test_explicit_counts_are_resolved(tmp_path):
    cfg = {
        "time": {"start_date": "2026-01-01", "days": 30, "timezone": "UTC"},
        "scale": {
            "mode": "explicit",
            "counts": {
                "products": 10,
                "locations": 11,
                "suppliers": 12,
                "customers": 13,
                "product_suppliers": 14,
                "sales_order_lines": 15,
                "purchase_order_lines": 16,
                "stock_count_events": 17,
            },
        },
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["products"] == 10
    assert resolved["locations"] == 11
    assert resolved["suppliers"] == 12
    assert resolved["customers"] == 13
    assert resolved["product_suppliers"] == 14
    assert resolved["sales_order_lines"] == 15
    assert resolved["purchase_order_lines"] == 16
    assert resolved["stock_count_events"] == 17


def test_factor_counts_are_resolved(tmp_path):
    cfg = {
        "scale": {
            "mode": "factor",
            "factor": 3,
            "base_counts": {
                "products": 2,
                "locations": 3,
                "suppliers": 4,
                "customers": 5,
                "product_suppliers": 6,
                "sales_order_lines": 7,
                "purchase_order_lines": 8,
                "stock_count_events": 9,
            },
        }
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["products"] == 6
    assert resolved["locations"] == 9
    assert resolved["suppliers"] == 12
    assert resolved["customers"] == 15
    assert resolved["product_suppliers"] == 18
    assert resolved["sales_order_lines"] == 21
    assert resolved["purchase_order_lines"] == 24
    assert resolved["stock_count_events"] == 27
