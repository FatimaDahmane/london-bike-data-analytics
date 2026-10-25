import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import logging
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.bike_data.validation import validate_required_columns
from src.bike_data.ingestion import load_csv
from src.bike_data.transformations import clean_trips

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def write_parquet_safely(df: pd.DataFrame, path: Path) -> None:
    """Create the output directory and write a Parquet file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
    except (OSError, ImportError, ValueError) as exc:
        logger.error("Could not write Parquet file '%s': %s", path, exc)
        raise RuntimeError(
            f"Failed to write Parquet file '{path}': {exc}"
        ) from exc


def get_file_info(path: Path) -> dict:
    """Return basic metadata for an existing output file."""
    path = Path(path)

    if not path.is_file():
        return {
            "path": str(path),
            "exists": False,
        }

    stat = path.stat()

    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(
            stat.st_mtime
        ).astimezone().isoformat(),
    }



def count_exact_duplicate_rows(df: pd.DataFrame) -> int:
    """Count exact duplicate rows after their first occurrence."""
    return int(df.duplicated().sum())



def run_pipeline(input_paths: list, output_path: str) -> pd.DataFrame:
    """Run the ETL pipeline and save quality outputs."""

    root = Path(__file__).resolve().parent.parent
    output_path = Path(output_path)

    rejected_path = root / "data" / "rejected" / "rejected_trips.parquet"
    report_path = root / "reports" / "data_quality_report.json"
    destination_path = (
        root / "data" / "processed" / "bike_trips_with_destinations.parquet"
    )

    required_columns = [
        "Start date",
        "End date",
        "Start station",
        "End station",
    ]

    logger.info("1. LOADING AND COMBINING DATA...")
    dataframes = [load_csv(path) for path in input_paths]
    raw_df = pd.concat(dataframes, ignore_index=True)
    input_rows = len(raw_df)

    logger.info("Loaded %s input rows", input_rows)

    logger.info("2. VALIDATING STRUCTURE...")
    validate_required_columns(raw_df, required_columns)

    logger.info("3. CLEANING AND TRANSFORMING DATA...")
    processed_df, rejected_df, modified_count = clean_trips(raw_df)

    
    # Count negative durations across all rows, including rejected trips.
    if "duration_seconds" in rejected_df.columns:
        all_durations = pd.concat(
            [
                processed_df["duration_seconds"],
                rejected_df["duration_seconds"],
            ],
            ignore_index=True,
        )

        negative_duration_count = int(
            (all_durations < 0).sum()
        )
    else:
        negative_duration_count = 0

    # Count exact duplicate input records after the first occurrence.
    duplicate_count = count_exact_duplicate_rows(raw_df)

    logger.info(
        "Negative durations detected: %s",
        negative_duration_count,
    )
    logger.info(
        "Exact duplicate input rows detected: %s",
        duplicate_count,
    )


    if processed_df.empty:
        logger.error(
            "Cleaning produced an empty dataset: "
            "%s input rows, %s rejected rows",
            len(raw_df),
            len(rejected_df),
        )
        raise ValueError(
            "The pipeline stopped because no valid rows remain "
            "after cleaning."
        )

    logger.info(
        "Cleaning completed: %s retained, %s rejected",
        len(processed_df),
        len(rejected_df),
    )

    # Count the primary rejection reason assigned to each rejected row.
    rejection_counts = (
        rejected_df["rejection_reason"]
        .value_counts()
        .to_dict()
    )

    # Create a separate view for destination analysis.
    # Trips without a usable start or end station are excluded only here.
    station_columns = ["start_station", "end_station"]
    available_station_columns = [
        col for col in station_columns if col in processed_df.columns
    ]

    if len(available_station_columns) == 2:
        destination_df = processed_df.dropna(
            subset=available_station_columns
        ).copy()
        destination_df = destination_df[
            destination_df["start_station"].astype(str).str.strip().ne("")
            & destination_df["end_station"].astype(str).str.strip().ne("")
        ].copy()
    else:
        destination_df = processed_df.iloc[0:0].copy()

    
    logger.info("4. SAVING PROCESSED DATA...")

    write_parquet_safely(processed_df, Path(output_path))
    write_parquet_safely(rejected_df, rejected_path)
    write_parquet_safely(destination_df, destination_path)


    report = {
        "input_rows": input_rows,
        "retained_rows": len(processed_df),
        "rejected_rows": len(rejected_df),
        "modified_rows": modified_count,
        "destination_analysis_rows": len(destination_df),
        "rejection_reasons": rejection_counts,
        "modified_rows_definition": (
            "Retained rows enriched with derived duration fields; "
            "this count can overlap with retained_rows."
        ),
        "negative_duration_rows": negative_duration_count,
        "exact_duplicate_input_rows": duplicate_count,
        "output_files": {
            "processed": get_file_info(Path(output_path)),
            "rejected": get_file_info(rejected_path),
            "destination_analysis": get_file_info(destination_path),
        },
    }

        
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with report_path.open("w", encoding="utf-8") as report_file:
            json.dump(report, report_file, indent=2)

    except (OSError, TypeError, ValueError) as exc:
        logger.error(
            "Could not write data quality report '%s': %s",
            report_path,
            exc,
        )
        raise RuntimeError(
            f"Failed to write data quality report '{report_path}': {exc}"
        ) from exc


    print("\nData quality summary")
    print("--------------------")
    print(f"Input rows:                 {input_rows}")
    print(f"Retained rows:              {len(processed_df)}")
    print(f"Rejected rows:              {len(rejected_df)}")
    print(f"Retained rows enriched:     {modified_count}")
    print(f"Rows for destination study: {len(destination_df)}")
    print(f"Rejection reasons:          {rejection_counts}")

    # Every input row should be either retained or rejected.
    assert input_rows == len(processed_df) + len(rejected_df), (
        "Data quality accounting error: input rows do not match "
        "retained + rejected rows."
    )

    logger.info("PIPELINE EXECUTED SUCCESSFULLY!")

    return processed_df



if __name__ == "__main__":
    ROOT = Path(__file__).resolve().parent.parent

    inputs = [
        ROOT / "data" / "raw" / "bike_trips_part1.csv",
        ROOT / "data" / "raw" / "bike_trips_part2.csv",
    ]

    output = ROOT / "data" / "processed" / "bike_trips.parquet"

    run_pipeline(inputs, output)
