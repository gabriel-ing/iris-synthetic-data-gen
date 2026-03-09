from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import small_config_dict, write_config


def test_cli_generates_expected_csv_outputs(tmp_path):
    cfg = small_config_dict(tmp_path, seed=99)
    config_path = write_config(tmp_path, cfg)

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "DataGen.main", "--config", str(config_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    out_dir = tmp_path / "out_supply_chain"
    assert (out_dir / "dim_date.csv").exists()
    assert (out_dir / "dim_product.csv").exists()
    assert (out_dir / "dim_location.csv").exists()
    assert (out_dir / "dim_supplier.csv").exists()
    assert (out_dir / "dim_customer.csv").exists()
    assert (out_dir / "product_supplier.csv").exists()
    assert (out_dir / "sales_order_line.csv").exists()
    assert (out_dir / "purchase_order_line.csv").exists()
    assert (out_dir / "shipment_line.csv").exists()
    assert (out_dir / "inventory_movement.csv").exists()
    assert (out_dir / "inventory_snapshot_daily.csv").exists()
    assert (out_dir / "stock_count_event.csv").exists()
    assert "Validation checks passed" in result.stdout
