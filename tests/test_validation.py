
import pandas as pd
import pytest

from src.bike_data.validation import validate_required_columns


def test_required_columns_present():
    df = pd.DataFrame({
        "started_at": ["2026-01-01"],
        "station": ["Station A"],
    })

    # No exception should be raised.
    validate_required_columns(
        df,
        ["started_at", "station"],
    )


def test_missing_required_column_raises_error():
    df = pd.DataFrame({
        "station": ["Station A"],
    })

    with pytest.raises(ValueError, match="started_at"):
        validate_required_columns(
            df,
            ["started_at"],
        )
