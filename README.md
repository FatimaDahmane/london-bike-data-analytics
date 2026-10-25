# London Bike Data Analytics 🚲

## About the project

This project looks at bike-sharing trips in London. The goal is to build an ETL pipeline, check data quality and explore how people use the bikes.

I used Python and Pandas to process the data, DuckDB and SQL for the analysis, and Streamlit to build an interactive dashboard.

The analysis focuses on **May 2026**.

## Tools used

- **Python & Pandas** — data cleaning and processing
- **DuckDB & SQL** — data analysis
- **Parquet** — storing processed data
- **Streamlit** — dashboard
- **Pytest** — automated tests
- **Git & GitHub** — version control

## Project structure

```text
london-bike-data-analytics/
├── data/          # Raw and processed data
├── notebooks/     # Data exploration
├── reports/       # Analysis reports and outputs
├── scripts/       # Scripts to run the pipeline and analysis
├── sql/           # SQL queries
├── src/           # Main Python code
├── tests/         # Automated tests
├── dashboard.py   # Streamlit dashboard
├── requirements.txt
├── check_environment.py
├── .gitignore
└── README.md
```

## Data pipeline

The project follows three main steps:

1. **Extract:** load the raw bike-sharing data.
2. **Transform:** clean the data, apply validation rules and separate valid records from rejected ones.
3. **Load:** save the processed data for analysis.

The processed data is then used for SQL queries and dashboard visualisations.

## Data quality

The pipeline processed the following number of records:

| Metric | Result |
|---|---:|
| Raw records | 863,017 |
| Processed records | 858,898 |
| Rejected records | 4,119 |
| Rejection rate | 0.48% |
| Tests passing | 12 |

The rejection rate is calculated by dividing the number of rejected records by the total number of raw records.

## Dashboard

The dashboard is built with Streamlit and covers several aspects of the dataset:

- **Overview:** key figures for the selected period.
- **Data quality:** processed and rejected records.
- **Time analysis:** trip activity by day, hour and day of the week.
- **Trip duration:** distribution of journey durations.
- **Station analysis:** comparison of station activity.
- **Business insights:** observations based on the data.

It also provides access to available data exports.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/FatimaDahmane/london-bike-data-analytics.git
cd london-bike-data-analytics
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the tests

```bash
python -m pytest -v
```

The current test suite contains 12 passing tests.

### 5. Launch the dashboard

```bash
streamlit run dashboard.py
```

## What I learned

Through this project, I worked on building a data pipeline, handling invalid records, writing SQL queries with DuckDB and presenting analytical results in a dashboard.

I also used automated tests to check that the data processing works as expected.

## Author

**Fatima Dahmane**

[GitHub profile](https://github.com/FatimaDahmane)
