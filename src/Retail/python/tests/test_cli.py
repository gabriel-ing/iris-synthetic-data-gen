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
    out_dir = tmp_path / "out_retail"
    assert (out_dir / "calendar.csv").exists()
    assert (out_dir / "roles.csv").exists()
    assert (out_dir / "users.csv").exists()
    assert (out_dir / "user_store_access.csv").exists()
    assert (out_dir / "stores.csv").exists()
    assert (out_dir / "products.csv").exists()
    assert (out_dir / "supplier_product.csv").exists()
    assert (out_dir / "promotions.csv").exists()
    assert (out_dir / "purchase_orders.csv").exists()
    assert (out_dir / "stock_transfers.csv").exists()
    assert (out_dir / "sales_transactions.csv").exists()
    assert (out_dir / "inventory_snapshot.csv").exists()
    assert "Validation checks passed" in result.stdout
