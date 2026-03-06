from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import small_config_dict, write_config


def test_cli_generates_expected_csv_outputs(tmp_path):
    cfg = small_config_dict(tmp_path, seed=99, partition="none")
    config_path = write_config(tmp_path, cfg)

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "synthetic_data_gen.main", "--config", str(config_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    out_dir = tmp_path / "out"
    assert (out_dir / "customers.csv").exists()
    assert (out_dir / "cards.csv").exists()
    assert (out_dir / "merchants.csv").exists()
    assert (out_dir / "transactions.csv").exists()
    assert (out_dir / "disputes.csv").exists()
    assert "Validation checks passed" in result.stdout
