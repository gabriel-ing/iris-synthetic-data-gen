from __future__ import annotations

import pandas as pd

from conftest import load_small_config
from synthetic_data_gen.writer import prepare_output_dir, write_transactions


def test_write_transactions_day_partition(tmp_path):
    cfg = load_small_config(tmp_path, partition="day")
    out_dir = prepare_output_dir(cfg["output"]["path"], overwrite=True)

    frames = [
        pd.DataFrame(
            {
                "TransactionId": [1, 2],
                "Card": [10, 11],
                "Merchant": [100, 101],
                "AuthAt": ["2026-01-01T01:00:00Z", "2026-01-01T02:00:00Z"],
                "PostedAt": ["2026-01-01T01:05:00Z", "2026-01-01T02:05:00Z"],
            }
        ),
        pd.DataFrame(
            {
                "TransactionId": [3],
                "Card": [12],
                "Merchant": [102],
                "AuthAt": ["2026-01-02T08:00:00Z"],
                "PostedAt": ["2026-01-02T08:03:00Z"],
            }
        ),
    ]

    paths = write_transactions(frames, out_dir, partition_by="day")
    assert len(paths) == 2
    assert all(path.exists() for path in paths)
