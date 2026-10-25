import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_trips(df: pd.DataFrame,) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """
    Clean bike trips and preserve rejected records with their reasons.

    Returns:
        processed: trips suitable for general temporal analysis.
        rejected: rejected trips with a rejection_reason column.
        modified_count: number of retained rows with derived fields added.
    """
    cleaned = df.copy()

    # Normalize column names.
    cleaned.columns = [
        col.strip().lower().replace(" ", "_")
        for col in cleaned.columns
    ]

    # Remove the redundant human-readable duration column.
    if "total_duration" in cleaned.columns:
        cleaned = cleaned.drop(columns=["total_duration"])

    # Parse dates. Invalid dates become NaT.
    if "start_date" not in cleaned.columns:
        raise ValueError("Required column 'start_date' is missing.")

    if "end_date" not in cleaned.columns:
        raise ValueError("Required column 'end_date' is missing.")

    cleaned["started_at"] = pd.to_datetime(
        cleaned["start_date"], errors="coerce"
    )
    cleaned["ended_at"] = pd.to_datetime(
        cleaned["end_date"], errors="coerce"
    )

    invalid_start_dates = cleaned["started_at"].isna().sum()
    invalid_end_dates = cleaned["ended_at"].isna().sum()

    if invalid_start_dates:
        logger.warning(
            "%s rows have invalid start dates",
            invalid_start_dates,
        )

    if invalid_end_dates:
        logger.warning(
            "%s rows have invalid end dates",
            invalid_end_dates,
        )

    # Assign one primary rejection reason to each rejected row.
    rejection_reason = pd.Series(
        pd.NA, index=cleaned.index, dtype="string"
    )

    invalid_start = cleaned["started_at"].isna()
    rejection_reason.loc[invalid_start] = "invalid_start_date"

    invalid_end = (
        cleaned["ended_at"].isna() & rejection_reason.isna()
    )
    rejection_reason.loc[invalid_end] = "invalid_end_date"

    # Calculate duration only when both dates are valid.
    cleaned["duration_seconds"] = (
        cleaned["ended_at"] - cleaned["started_at"]
    ).dt.total_seconds()

    # Assign rejection reasons for invalid durations.
    valid_dates = rejection_reason.isna()

    negative_duration = (
        valid_dates & (cleaned["duration_seconds"] < 0)
    )
    rejection_reason.loc[negative_duration] = "negative_duration"

    too_short = (
        valid_dates
        & (cleaned["duration_seconds"] >= 0)
        & (cleaned["duration_seconds"] < 60)
    )
    rejection_reason.loc[too_short] = "duration_below_60_seconds"

    # Keep rejected rows, including their original fields.
    rejected_mask = rejection_reason.notna()
    rejected = cleaned.loc[rejected_mask].copy()
    rejected["rejection_reason"] = rejection_reason.loc[rejected_mask]

    # Keep rows that pass the general temporal quality rules.
    processed = cleaned.loc[~rejected_mask].copy()

    
    # Derive duration in minutes from the timestamp-based duration.
    processed["duration_min"] = processed["duration_seconds"] / 60


    # Count retained rows enriched with derived duration fields.
    modified_count = len(processed)


        
    # Keep only columns needed for the analytical dataset.
    analytical_columns = [
        "start_station_number",
        "start_station",
        "end_station_number",
        "end_station",
        "bike_model",
        "started_at",
        "ended_at",
        "duration_seconds",
        "duration_min",
    ]

    # Keep the full rejected dataset for troubleshooting.
    processed = processed[
        [column for column in analytical_columns if column in processed.columns]
    ].copy()

    return processed, rejected, modified_count