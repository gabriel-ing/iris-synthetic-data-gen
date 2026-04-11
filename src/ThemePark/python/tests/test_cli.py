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
    out_dir = tmp_path / "out_theme_park"
    assert (out_dir / "parks.csv").exists()
    assert (out_dir / "zones.csv").exists()
    assert (out_dir / "rides.csv").exists()
    assert (out_dir / "ride_maintenance.csv").exists()
    assert (out_dir / "employees.csv").exists()
    assert (out_dir / "shifts.csv").exists()
    assert (out_dir / "guests.csv").exists()
    assert (out_dir / "tickets.csv").exists()
    assert (out_dir / "incidents.csv").exists()
    assert (out_dir / "feedback.csv").exists()
    assert "Validation checks passed" in result.stdout
