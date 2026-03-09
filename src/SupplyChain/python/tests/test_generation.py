from __future__ import annotations

from pandas.testing import assert_frame_equal

from conftest import build_dataset, load_small_config
from DataGen.validate import validate_all


def test_generation_is_deterministic_for_same_seed(tmp_path):
    cfg_a = load_small_config(tmp_path / "a", seed=123)
    a = build_dataset(cfg_a)

    cfg_b = load_small_config(tmp_path / "b", seed=123)
    b = build_dataset(cfg_b)

    for key in a:
        assert_frame_equal(a[key], b[key], check_like=False)


def test_generation_passes_core_validation(tmp_path):
    cfg = load_small_config(tmp_path)
    ds = build_dataset(cfg)

    result = validate_all(
        cfg,
        ds["dim_date"],
        ds["dim_product"],
        ds["dim_location"],
        ds["dim_supplier"],
        ds["dim_customer"],
        ds["product_supplier"],
        ds["sales_order_line"],
        ds["purchase_order_line"],
        ds["shipment_line"],
        ds["inventory_movement"],
        ds["inventory_snapshot_daily"],
        ds["stock_count_event"],
    )

    assert result.ok is True
    assert len(result.checks) >= 20
    assert len(ds["dim_date"]) == cfg["resolved_counts"]["days"]
    assert len(ds["dim_product"]) == cfg["resolved_counts"]["products"]
    assert len(ds["sales_order_line"]) == cfg["resolved_counts"]["sales_order_lines"]
