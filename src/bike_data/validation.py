import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_required_columns(df, required_columns):
    """Raise an error when required columns are missing."""
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    logger.info("Required columns validated successfully")