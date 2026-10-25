
import pandas as pd

from scripts.run_pipeline import (
    count_exact_duplicate_rows,
    get_file_info,
)


def test_count_exact_duplicate_rows():
    df = pd.DataFrame({
        "started_at": [
            "2026-06-01 10:00:00",
            "2026-06-01 10:00:00",
            "2026-06-01 11:00:00",
        ],
        "start_station": [
            "Station A",
            "Station A",
            "Station B",
        ],
    })

    assert count_exact_duplicate_rows(df) == 1


def test_count_exact_duplicate_rows_without_duplicates():
    df = pd.DataFrame({
        "started_at": [
            "2026-06-01 10:00:00",
            "2026-06-01 11:00:00",
        ],
        "start_station": ["Station A", "Station B"],
    })

    assert count_exact_duplicate_rows(df) == 0


def test_get_file_info_for_existing_file(tmp_path):
    file_path = tmp_path / "sample.parquet"
    file_path.write_bytes(b"test data")

    info = get_file_info(file_path)

    assert info["path"] == str(file_path)
    assert info["exists"] is True
    assert info["size_bytes"] == len(b"test data")
    assert isinstance(info["last_modified"], str)
    assert info["last_modified"]


def test_get_file_info_for_missing_file(tmp_path):
    file_path = tmp_path / "missing.parquet"

    info = get_file_info(file_path)

    assert info == {
        "path": str(file_path),
        "exists": False,
    }
