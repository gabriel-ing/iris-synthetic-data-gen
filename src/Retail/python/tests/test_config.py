from __future__ import annotations

from DataGen.config import load_config
from conftest import write_config


def test_explicit_counts_are_resolved(tmp_path):
    cfg = {
        "scale": {
            "mode": "explicit",
            "counts": {
                "users": 10,
                "stores": 11,
                "products": 12,
                "supplier_products": 13,
                "promotions": 14,
                "purchase_orders": 15,
                "stock_transfers": 16,
                "sales_transactions": 17,
                "inventory_snapshots": 18,
            },
        }
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["users"] == 10
    assert resolved["stores"] == 11
    assert resolved["products"] == 12
    assert resolved["supplier_products"] == 13
    assert resolved["promotions"] == 14
    assert resolved["purchase_orders"] == 15
    assert resolved["stock_transfers"] == 16
    assert resolved["sales_transactions"] == 17
    assert resolved["inventory_snapshots"] == 18
    assert resolved["roles"] == 4


def test_factor_counts_are_resolved(tmp_path):
    cfg = {
        "scale": {
            "mode": "factor",
            "factor": 3,
            "base_counts": {
                "users": 2,
                "stores": 3,
                "products": 4,
                "supplier_products": 5,
                "promotions": 6,
                "purchase_orders": 7,
                "stock_transfers": 8,
                "sales_transactions": 9,
                "inventory_snapshots": 10,
            },
        }
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path)

    resolved = loaded["resolved_counts"]
    assert resolved["users"] == 6
    assert resolved["stores"] == 9
    assert resolved["products"] == 12
    assert resolved["supplier_products"] == 15
    assert resolved["promotions"] == 18
    assert resolved["purchase_orders"] == 21
    assert resolved["stock_transfers"] == 24
    assert resolved["sales_transactions"] == 27
    assert resolved["inventory_snapshots"] == 30


def test_scale_factor_override_multiplies_configured_counts(tmp_path):
    cfg = {
        "scale": {
            "mode": "explicit",
            "counts": {
                "users": 10,
                "stores": 11,
                "products": 12,
                "supplier_products": 13,
                "promotions": 14,
                "purchase_orders": 15,
                "stock_transfers": 16,
                "sales_transactions": 17,
                "inventory_snapshots": 18,
            },
        },
    }
    path = write_config(tmp_path, cfg)
    loaded = load_config(path, scale_factor_override=2)

    resolved = loaded["resolved_counts"]
    assert resolved["users"] == 20
    assert resolved["stores"] == 22
    assert resolved["products"] == 24
    assert resolved["supplier_products"] == 26
    assert resolved["promotions"] == 28
    assert resolved["purchase_orders"] == 30
    assert resolved["stock_transfers"] == 32
    assert resolved["sales_transactions"] == 34
    assert resolved["inventory_snapshots"] == 36
