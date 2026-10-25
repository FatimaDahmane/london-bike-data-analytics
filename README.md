# 🚲 London Bike Sharing — Data Analytics

Analysis of London bike-sharing trips using Python, SQL, DuckDB and Streamlit. This project covers data cleaning, data quality checks, trip patterns and station activity, with an interactive dashboard and a set of visualisations.

## Overview

The aim of this project is to explore how London's bike-sharing service was used during May 2026.

The analysis focuses on:
- Trip demand by hour and day.
- Differences between weekday and weekend journeys.
- Trip duration and its distribution.
- The most frequently used departure stations.
- Differences between station departures and arrivals.
- Trip counts by bike model.

The project also includes a data-processing pipeline that validates the raw records and saves the results in Parquet format.

## Data Source

The data was obtained from the [Transport for London (TfL) Cycling Data portal](https://cycling.data.tfl.gov.uk/).

- **Period:** May 2026
- **Input files:** `bike_trips_part1.csv` and `bike_trips_part2.csv`
- **Format:** CSV

The analysis mainly covers trips starting between 1 May and 31 May 2026. Three additional records start at midnight on 1 June 2026.

This is an independent portfolio project and is not an official TfL product. 

## Dashboard

The dashboard provides an interactive way to explore the processed trip data.

![London Bike Sharing Dashboard](docs/images/dashboard-overview.png)

## Results

### 1. Trips by hour

Demand changes throughout the day, with the highest activity during the late afternoon and morning commute.

![London Bike Trips by Hour](reports/figures/trips_by_hour.png)

The busiest hour was **5 PM, with 82,026 trips**. The next major peaks were 6 PM, with 78,704 trips, and 8 AM, with 74,678 trips.

### 2. Daily trip volume

This chart shows how the number of trips changed throughout May 2026.

![Daily London Bike Trip Volume](reports/figures/daily_trips.png)

Daily totals can help identify changes in activity during the month. This chart shows trip volume, but does not by itself explain the reasons behind those changes.

### 3. Weekday and weekend usage

The average trip duration differs between weekdays and weekends.

![Average Trip Duration: Weekday vs Weekend](reports/figures/weekday_vs_weekend.png)

| Metric | Weekdays | Weekends |
|---|---:|---:|
| Number of trips | 611,727 | 247,171 |
| Average duration | 20.49 min | 26.96 min |

Weekend trips lasted **6.47 minutes longer on average**.

The following charts provide more detail on trip duration.

![Distribution of Trip Durations](reports/figures/duration_distribution.png)

*The duration distribution includes trips between 1 and 180 minutes.*

![Trip Duration by Day of the Week](reports/figures/duration_by_weekday.png)

*The boxplots exclude displayed outliers and are limited to trips of up to 180 minutes.*

Hourly demand can also be compared between weekdays and weekends.

![Hourly Bike Demand: Weekday vs Weekend](reports/figures/hourly_weekday_weekend.png)

### 4. Departure stations

The following chart shows the ten busiest departure stations in the dataset.

![Top 10 Departure Stations](reports/figures/top_departure_stations.png)

The busiest departure stations were:

| Station | Departures |
|---|---:|
| Hyde Park Corner, Hyde Park | 5,755 |
| Waterloo Station 3, Waterloo | 4,786 |
| Black Lion Gate, Kensington Gardens | 3,744 |
| Waterloo Station 1, Waterloo | 3,693 |
| Argyle Street, Kings Cross | 3,684 |

Hyde Park Corner also ranked first for arrivals, with 5,307 trips.

### 5. Station flow imbalances

To compare station activity, the net balance is calculated as:

`Net balance = Arrivals - Departures`

![Stations with the Largest Departure Surplus](reports/figures/station_net_balance.png)

A negative balance means that more trips started at a station than ended there during the period analysed.

Waterloo Station 3 had 4,786 departures and 4,224 arrivals, giving it a net balance of **-562 trips**.

This measure describes recorded trip flows; it does not indicate the actual number of bikes available at a station at a particular time.

### 6. Trips between stations

The heatmap shows recorded trips between the ten most popular departure stations.

![Trip Flows Between the Top 10 Departure Stations](reports/figures/station_flow_heatmap.png)

It provides a closer look at how trips are distributed between these stations.

### 7. Bike model usage

This chart compares the number of trips recorded for each bike model.

![Bike Usage by Model](reports/figures/bike_model_usage.png)

Records without a known bike model are grouped under `Unknown`.

## Data Processing

The pipeline takes the raw CSV files, validates the records and saves the results for analysis.

The main steps are:

1. Load the raw trip data.
2. Check timestamps, trip durations and station information.
3. Separate rejected records from valid trips.
4. Save the processed datasets in Parquet format.
5. Use DuckDB and SQL to analyse trips and station activity.
6. Generate visualisations and dashboard outputs.

### Data quality results

The pipeline processed **863,017 raw records**.

| Metric | Result |
|---|---:|
| Raw records | 863,017 |
| Processed trips | 858,898 |
| Rejected records | 4,119 |
| Rejection rate | 0.48% |
| Retention rate | 99.52% |

The processed dataset passed the implemented checks for missing timestamps, negative durations, trips shorter than 60 seconds, inconsistent duration values and missing station names.

Repeated trip records were also examined. Identical attributes can indicate possible duplicates, but do not necessarily mean that a record is invalid.

### Generated files

The pipeline creates or updates the following files:

| File | Description |
|---|---|
| `data/processed/bike_trips.parquet` | Processed trip data |
| `data/rejected/rejected_trips.parquet` | Rejected records |
| `data/processed/bike_trips_with_destinations.parquet` | Processed trips with destination information |
| `reports/data_quality_report.json` | Data quality report |
| `reports/figures/` | Generated analysis figures |

Running the pipeline may overwrite existing outputs. Back up any files you want to keep before running it again.

## Tech Stack

- **Python** — Data processing and analysis
- **Pandas** — Data manipulation
- **DuckDB and SQL** — Analytical queries
- **PyArrow and Parquet** — Data storage
- **Matplotlib** — Charts
- **Streamlit** — Interactive dashboard
- **Pytest** — Automated tests
- **Git and GitHub** — Version control

## Project Structure

```text
london-bike-data-analytics/
├── data/
│   ├── raw/                         # Source CSV files (not committed)
│   ├── processed/                   # Cleaned Parquet datasets
│   ├── rejected/                    # Rejected trip records
│   └── analytics.duckdb             # DuckDB database
├── docs/
│   └── images/
│       └── dashboard_overview.png
├── notebooks/
│   └── exploratory_analysis.ipynb
├── reports/
│   ├── figures/
│   │   ├── bike_model_usage.png
│   │   ├── daily_trips.png
│   │   ├── duration_by_weekday.png
│   │   ├── duration_distribution.png
│   │   ├── hourly_weekday_weekend.png
│   │   ├── station_flow_heatmap.png
│   │   ├── station_net_balance.png
│   │   ├── top_departure_stations.png
│   │   ├── trips_by_hour.png
│   │   └── weekday_vs_weekend.png
│   ├── business_findings.md
│   ├── data_quality.md
│   └── data_quality_report.json
├── scripts/
│   ├── run_pipeline.py
│   ├── run_sql_analysis.py
│   ├── create_visualizations.py
│   └── __init__.py
├── sql/
│   ├── 01_final_quality_check.sql
│   ├── 02_demand_by_time.sql
│   ├── 03_station_analysis.sql
│   ├── 04_date_coverage_check.sql
│   ├── 05_duplicate_check.sql
│   └── 06_business_insights.sql
├── src/
│   ├── bike_data/
│   │   ├── export.py
│   │   ├── ingestion.py
│   │   ├── transformations.py
│   │   ├── validation.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── test_quality_checks.py
│   ├── test_transformations.py
│   └── test_validation.py
├── check_environment.py
├── dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

**Notes:**
- Raw CSV files are required to run the pipeline but are excluded from Git.
- Processed datasets, the DuckDB database and generated reports may be created locally when running the project.
- The `sql/` directory contains queries for data quality checks, demand analysis, station analysis and business insights.
- The `tests/` directory contains automated tests for data quality, transformations and validation.
- Python cache files and local test cache files are omitted from this overview.

## Getting Started

### Requirements

- Python
- Git
- The source CSV files from the TfL Cycling Data portal

### 1. Clone the repository

```bash
git clone https://github.com/FatimaDahmane/london-bike-data-analytics.git
cd london-bike-data-analytics
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Add the raw data

Place both CSV files in `data/raw/`:

```text
data/raw/
├── bike_trips_part1.csv
└── bike_trips_part2.csv
```

The raw CSV files are excluded from Git and need to be downloaded separately.

### 5. Run the pipeline

From the project root:

```powershell
python .\scripts\run_pipeline.py
```

The pipeline should create the processed datasets and data quality report.

### 6. Generate the figures

Run the script containing the ten visualisation functions. For example, if the file is named `create_visualizations.py` and is located in `scripts/`:

```powershell
python .\scripts\create_visualizations.py
```

The script should save the figures in `reports/figures/`. Adjust the command if your script has a different filename.

### 7. Launch the dashboard

```powershell
python -m streamlit run .\dashboard.py
```

Open the local URL displayed in the terminal to use the dashboard.

The dashboard currently runs locally and has not been publicly deployed.

## Tests

Run the test suite from the project root:

```bash
python -m pytest
```

The test suite previously passed with **12 tests** in the development environment. Run it again after making changes to check the current state of the project.

## Limitations

- The analysis covers one month, so it does not capture seasonal or year-round trends.
- Three records start at midnight on 1 June 2026.
- Station balances reflect trip counts, not real-time bike availability.
- Trip records do not reveal the purpose of each journey.
- Identical trip attributes are not sufficient on their own to confirm invalid duplicates.

## Author

**Fatima Dahmane**  
Computer Science Student at INSA Toulouse
