from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO_ROOT / ".pytest_artifacts"
CONTAINER_REPO_ROOT = "/home/irisowner/dev"


def _run(command: list[str], *, cwd: Path | None = None, input_text: str | None = None, timeout: int = 1200) -> str:
    result = subprocess.run(
        command,
        cwd=cwd or REPO_ROOT,
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Command failed: {' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def _docker_compose(*args: str, timeout: int = 1200) -> str:
    return _run(["docker-compose", *args], timeout=timeout)


def _iris_session(script: str, *, timeout: int = 1200) -> str:
    return _run(
        ["docker-compose", "exec", "-T", "iris", "iris", "session", "iris"],
        input_text=script,
        timeout=timeout,
    )


def _wait_for_iris(timeout: int = 300) -> None:
    deadline = time.monotonic() + timeout
    last_error = "IRIS did not become ready"
    while time.monotonic() < deadline:
        try:
            _iris_session('halt', timeout=30)
            return
        except AssertionError as exc:
            last_error = str(exc)
            time.sleep(5)
    raise AssertionError(last_error)


def _extract_marker(output: str, marker: str) -> str:
    match = re.search(rf"{re.escape(marker)}=(.*)", output)
    if not match:
        raise AssertionError(f"Marker {marker}=... not found in output:\n{output}")
    return match.group(1).strip()


def _write_financial_test_config() -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    host_path = ARTIFACT_DIR / "financial_loader_small.yaml"
    data = {
        "seed": 7,
        "currency": "USD",
        "time": {
            "start_date": "2026-01-01",
            "days": 14,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "customers": 12,
                "merchants": 8,
                "cards": 16,
                "transactions": 80,
                "disputes": 4,
            },
        },
        "output": {
            "format": "csv",
            "path": str(ARTIFACT_DIR / "financial_out"),
            "partition_transactions_by": "none",
            "overwrite": True,
        },
        "edge_cases": {
            "enable": True,
            "customers_with_no_cards": 1,
            "cards_with_only_declines": 1,
            "blocked_cards_mid_window": 1,
            "fraud_bursts": {
                "count_cards": 1,
                "txns_per_card": 4,
                "burst_hours": 2,
                "amount_range": [1.0, 10.0],
            },
        },
    }
    host_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return f"{CONTAINER_REPO_ROOT}/.pytest_artifacts/{host_path.name}"


def _write_retail_test_config() -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    host_path = ARTIFACT_DIR / "retail_loader_small.yaml"
    data = {
        "seed": 11,
        "currency": "USD",
        "time": {
            "start_date": "2026-01-01",
            "days": 21,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "users": 10,
                "stores": 6,
                "products": 18,
                "supplier_products": 28,
                "promotions": 8,
                "purchase_orders": 24,
                "stock_transfers": 10,
                "sales_transactions": 120,
                "inventory_snapshots": 72,
            },
        },
        "output": {
            "path": str(ARTIFACT_DIR / "retail_out"),
            "overwrite": True,
        },
    }
    host_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return f"{CONTAINER_REPO_ROOT}/.pytest_artifacts/{host_path.name}"


def _write_themepark_test_config() -> str:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    host_path = ARTIFACT_DIR / "themepark_loader_small.yaml"
    data = {
        "seed": 13,
        "currency": "USD",
        "time": {
            "start_date": "2026-05-01",
            "days": 30,
            "timezone": "UTC",
        },
        "scale": {
            "mode": "explicit",
            "counts": {
                "parks": 4,
                "zones": 12,
                "rides": 24,
                "ride_maintenance": 36,
                "employees": 48,
                "shifts": 160,
                "guests": 120,
                "tickets": 180,
                "incidents": 24,
                "feedback": 72,
            },
        },
        "output": {
            "path": str(ARTIFACT_DIR / "themepark_out"),
            "overwrite": True,
        },
    }
    host_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return f"{CONTAINER_REPO_ROOT}/.pytest_artifacts/{host_path.name}"


def test_zpm_install_persists_root_and_defers_dataset_compile():
    rebuild = os.environ.get("SYNTHETICDATAGEN_REBUILD_DOCKER", "1") != "0"
    if rebuild:
        _docker_compose("down", "-v", "--remove-orphans", timeout=1200)
        _docker_compose("up", "-d", "--build", timeout=1800)
    else:
        _docker_compose("up", "-d", timeout=1200)

    _wait_for_iris(timeout=300)

    install_output = _iris_session(
        "\n".join(
            [
                'ZN "USER"',
                'zpm "load /home/irisowner/dev -v"',
                'write "INSTALLROOT=",$get(^SyntheticDataGen("InstallRoot")),!',
                'write "FINANCE_EXISTS=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","Finance.Customers"),!',
                'write "SUPPLY_EXISTS=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","SupplyChain.DimCustomer"),!',
                'write "RETAIL_EXISTS=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","Retail.Stores"),!',
                'write "THEME_EXISTS=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","ThemePark.Parks"),!',
                'halt',
            ]
        ),
        timeout=1800,
    )

    install_root = _extract_marker(install_output, "INSTALLROOT")
    finance_exists_before = _extract_marker(install_output, "FINANCE_EXISTS")
    supply_exists_before = _extract_marker(install_output, "SUPPLY_EXISTS")
    retail_exists_before = _extract_marker(install_output, "RETAIL_EXISTS")
    theme_exists_before = _extract_marker(install_output, "THEME_EXISTS")

    assert install_root.endswith("/lib/SyntheticDataGen/")
    assert finance_exists_before == "0"
    assert supply_exists_before == "0"
    assert retail_exists_before == "0"
    assert theme_exists_before == "0"

    financial_config_path = _write_financial_test_config()
    load_output = _iris_session(
        "\n".join(
            [
                'ZN "USER"',
                f'do ##class(SyntheticDataGen.DataLoader).LoadData("FinancialServices","","{financial_config_path}",1)',
                'write "INSTALLROOT_AFTER=",$get(^SyntheticDataGen("InstallRoot")),!',
                'write "FINANCE_EXISTS_AFTER=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","Finance.Customers"),!',
                'write "SUPPLY_EXISTS_AFTER=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","SupplyChain.DimCustomer"),!',
                'write "RETAIL_EXISTS_AFTER=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","Retail.Stores"),!',
                'write "CUSTOMER_ROWS=",##class(Finance.Customers).%ExtentSize(),!',
                'halt',
            ]
        ),
        timeout=1800,
    )

    assert _extract_marker(load_output, "INSTALLROOT_AFTER") == install_root
    assert _extract_marker(load_output, "FINANCE_EXISTS_AFTER") == "1"
    assert _extract_marker(load_output, "SUPPLY_EXISTS_AFTER") == "0"
    assert _extract_marker(load_output, "RETAIL_EXISTS_AFTER") == "0"
    assert _extract_marker(load_output, "CUSTOMER_ROWS") == "12"

    retail_config_path = _write_retail_test_config()
    retail_load_output = _iris_session(
        "\n".join(
            [
                'ZN "USER"',
                f'do ##class(SyntheticDataGen.DataLoader).LoadData("Retail",2,"{retail_config_path}",1)',
                'set rs=##class(%SQL.Statement).%ExecDirect(,"SELECT COUNT(*) AS Cnt FROM Retail.Stores")',
                'if rs.%Next() { write "STORE_ROWS=",rs.%Get("Cnt"),! }',
                'write "RETAIL_EXISTS_FINAL=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","Retail.Stores"),!',
                'halt',
            ]
        ),
        timeout=1800,
    )

    assert _extract_marker(retail_load_output, "RETAIL_EXISTS_FINAL") == "1"
    assert _extract_marker(retail_load_output, "STORE_ROWS") == "12"

    themepark_config_path = _write_themepark_test_config()
    themepark_load_output = _iris_session(
        "\n".join(
            [
                'ZN "USER"',
                f'do ##class(SyntheticDataGen.DataLoader).LoadData("ThemePark",2,"{themepark_config_path}",1)',
                'set rs=##class(%SQL.Statement).%ExecDirect(,"SELECT COUNT(*) AS Cnt FROM ThemePark.Parks")',
                'if rs.%Next() { write "PARK_ROWS=",rs.%Get("Cnt"),! }',
                'write "THEME_EXISTS_FINAL=",$classmethod("%Dictionary.ClassDefinition","%ExistsId","ThemePark.Parks"),!',
                'halt',
            ]
        ),
        timeout=1800,
    )

    assert _extract_marker(themepark_load_output, "THEME_EXISTS_FINAL") == "1"
    assert _extract_marker(themepark_load_output, "PARK_ROWS") == "8"