# Data Quality and Rejection Rules

## Purpose

The pipeline applies explicit data quality rules, preserves rejected records, and produces a report that explains how input data was processed.

## General processing rules

| Rule | Action | Reason |
|---|---|---|
| Invalid start date | Reject | The trip cannot be placed reliably in time |
| Invalid end date | Reject | The trip duration cannot be calculated reliably |
| Duration below 60 seconds | Reject | The trip does not meet the current duration threshold |
| Missing start station | Retain in the general dataset; exclude from station analysis | Temporal analysis may still be possible |
| Missing end station | Retain in the general dataset; exclude from destination analysis | Destination analysis requires a usable destination |

## Rejection reasons

Each rejected record receives one primary `rejection_reason`:

- `invalid_start_date`
- `invalid_end_date`
- `duration_below_60_seconds`

When a record violates multiple rules, the pipeline assigns the first applicable reason in the order defined by the transformation function.

This makes rejection counts mutually exclusive and ensures that each rejected row is counted once.

## Analytical datasets

### General temporal dataset

`data/processed/bike_trips.parquet`

Contains records with valid start and end dates and a duration of at least 60 seconds. It can be used for general temporal analysis.

### Destination analysis dataset

`data/processed/bike_trips_with_destinations.parquet`

Contains records from the general dataset with both start and end stations available.

### Rejected records

`data/rejected/rejected_trips.parquet`

Contains rejected records and their primary rejection reason. These records are retained for inspection and quality monitoring.

## Quality report

`reports/data_quality_report.json` records:

- `input_rows`: number of input records.
- `retained_rows`: number of records in the general processed dataset.
- `rejected_rows`: number of rejected records.
- `modified_rows`: retained records enriched with derived duration fields.
- `destination_analysis_rows`: number of records usable for destination analysis.
- `rejection_reasons`: count for each primary rejection reason.

The modified row count can overlap with the retained row count. It is not an additional category of records.

The pipeline checks the following accounting invariant:

`input_rows = retained_rows + rejected_rows`

## Additional quality checks

- **Negative durations:** count trips for which the end timestamp precedes the start timestamp. These records should be investigated as temporal inconsistencies.
- **Exact duplicate input rows:** count repeated input rows using all original columns. This is a diagnostic metric; duplicates are not automatically removed.
- **Output file metadata:** record each output file's path, existence, size in bytes and last-modified timestamp.

## Duration threshold

Trips shorter than 60 seconds are rejected; trips lasting exactly 60 seconds are retained. This is a configurable project rule used to exclude very short trips from the analysis. It should not be interpreted as proof that every short trip is invalid. The threshold may be revised after examining the source data and the project's analytical requirements.

Quality anomalies are counted and reported. No arbitrary global percentage threshold is used to stop the pipeline at this stage.

## Current limitations

- The 60-second threshold is a configurable business rule and should be reviewed against the source data documentation.
- Missing station values are excluded from station analysis, but other station-quality issues may require additional validation.
- Exact duplicate detection has not yet been implemented.
- The modified row count measures enrichment with derived fields, not every possible source-value correction.
