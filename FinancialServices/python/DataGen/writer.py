from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


def prepare_output_dir(path: str, overwrite: bool) -> Path:
    out = Path(path)
    if out.exists() and overwrite:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_csv(df: pd.DataFrame, out_dir: Path, name: str) -> Path:
    target = out_dir / f"{name}.csv"
    df.to_csv(target, index=False)
    return target


def write_transactions(
    transaction_frames: list[pd.DataFrame],
    out_dir: Path,
    partition_by: str,
) -> list[Path]:
    paths: list[Path] = []
    if partition_by == "day":
        tx_dir = out_dir / "transactions"
        tx_dir.mkdir(parents=True, exist_ok=True)
        for frame in transaction_frames:
            day = pd.to_datetime(frame["AuthAt"].iloc[0]).strftime("%Y-%m-%d")
            path = tx_dir / f"transactions_{day}.csv"
            frame.to_csv(path, index=False)
            paths.append(path)
    else:
        combined = pd.concat(transaction_frames, ignore_index=True)
        paths.append(write_csv(combined, out_dir, "transactions"))
    return paths
