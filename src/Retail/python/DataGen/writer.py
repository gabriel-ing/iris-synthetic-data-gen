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
