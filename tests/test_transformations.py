
import pandas as pd
import pytest

from src.bike_data.transformations import clean_trips


def make_trip(start_date, end_date):
    """Create one raw trip using the original CSV column names."""
    return {
        "Start date": start_date,
        "End date": end_date,
        "Start station": "Station A",
        "End station": "Station B",
    }


def test_invalid_start_date_is_rejected():
    df = pd.DataFrame([
        make_trip("not-a-date", "2026-06-01 10:05:00")
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) == 0
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == "invalid_start_date"


def test_invalid_end_date_is_rejected():
    df = pd.DataFrame([
        make_trip("2026-06-01 10:00:00", "not-a-date")
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) == 0
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == "invalid_end_date"


def test_trip_shorter_than_60_seconds_is_rejected():
    df = pd.DataFrame([
        make_trip("2026-06-01 10:00:00", "2026-06-01 10:00:30")
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) == 0
    assert len(rejected) == 1
    assert (
        rejected.iloc[0]["rejection_reason"]
        == "duration_below_60_seconds"
    )


def test_valid_trip_is_retained():
    df = pd.DataFrame([
        make_trip("2026-06-01 10:00:00", "2026-06-01 10:05:00")
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) == 1
    assert len(rejected) == 0
    assert processed.iloc[0]["duration_seconds"] == 300
    assert processed.iloc[0]["duration_min"] == pytest.approx(5.0)


def test_all_rows_are_accounted_for():
    df = pd.DataFrame([
        make_trip("2026-06-01 10:00:00", "2026-06-01 10:05:00"),
        make_trip("not-a-date", "2026-06-01 10:05:00"),
        make_trip("2026-06-01 10:00:00", "2026-06-01 10:00:30"),
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) + len(rejected) == len(df)
    assert len(processed) == 1
    assert len(rejected) == 2

def test_trip_of_exactly_60_seconds_is_retained():
    df = pd.DataFrame([
        make_trip(
            "2026-06-01 10:00:00",
            "2026-06-01 10:01:00",
        )
    ])

    processed, rejected, _ = clean_trips(df)

    assert len(processed) == 1
    assert len(rejected) == 0
    assert processed.iloc[0]["duration_seconds"] == 60