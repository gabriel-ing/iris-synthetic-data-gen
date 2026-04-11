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
        ds["parks"],
        ds["zones"],
        ds["rides"],
        ds["ride_maintenance"],
        ds["employees"],
        ds["shifts"],
        ds["guests"],
        ds["tickets"],
        ds["incidents"],
        ds["feedback"],
    )

    assert result.ok is True
    assert len(result.checks) >= 30
    assert len(ds["parks"]) == cfg["resolved_counts"]["parks"]
    assert len(ds["rides"]) == cfg["resolved_counts"]["rides"]
    assert len(ds["tickets"]) == cfg["resolved_counts"]["tickets"]
    assert len(ds["feedback"]) == cfg["resolved_counts"]["feedback"]