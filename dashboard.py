
from pathlib import Path
import json

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="London Bike | Data Quality & Business Insights",
    page_icon="🚲",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent

PROCESSED_CANDIDATES = [
    ROOT / "data" / "processed" / "bike_trips.parquet",
]

REJECTED_CANDIDATES = [
    ROOT / "data" / "rejected" / "rejected_trips.parquet",
    ROOT / "data" / "rejected" / "rejected_trips.csv",
    ROOT / "data" / "rejected" / "rejection_report.csv",
    ROOT / "data" / "rejected" / "rejected_rows.csv",
]

REPORT_CANDIDATES = [
    ROOT / "reports" / "data_quality_report.json",
    ROOT / "data" / "rejected" / "data_quality_report.json",
]


# ============================================================
# HELPERS
# ============================================================
def first_existing(paths):
    return next((path for path in paths if path.exists()), None)


def read_table(path):
    if path is None:
        return pd.DataFrame()

    suffix = path.suffix.lower()

    if suffix == ".parquet":
        return pd.read_parquet(path)

    if suffix == ".csv":
        return pd.read_csv(path)

    return pd.DataFrame()


def read_json(path):
    if path is None:
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}


def find_column(df, candidates):
    """Find a column without depending on capitalization."""
    lookup = {str(col).lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    return None


def as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metric_count(value):
    return f"{int(value):,}".replace(",", " ")


def get_json_value(data, keys):
    """Find common metric aliases in a nested JSON report."""
    if not isinstance(data, dict):
        return None

    for key in keys:
        if key in data and not isinstance(data[key], (dict, list)):
            value = as_number(data[key])
            if value is not None:
                return value

    for value in data.values():
        if isinstance(value, dict):
            result = get_json_value(value, keys)
            if result is not None:
                return result

    return None


def add_date_parts(data):
    """Create dashboard date attributes on a copy of the data."""
    out = data.copy()

    date_col = find_column(
        out,
        [
            "started_at",
            "start_time",
            "start_date",
            "start_datetime",
            "started",
            "date",
        ],
    )

    if date_col:
        out[date_col] = pd.to_datetime(
            out[date_col],
            errors="coerce",
        )

        out["_dashboard_date"] = out[date_col]
        out["_dashboard_hour"] = out[date_col].dt.hour
        out["_dashboard_weekday"] = out[date_col].dt.day_name()
        out["_dashboard_month"] = (
            out[date_col].dt.to_period("M").astype(str)
        )

    return out, date_col



# ============================================================
# LOAD DATA
# ============================================================
st.title("🚲 London Bike Data Analytics")

st.markdown("""
This dashboard provides an overview of London's bike-sharing data
for the period from **May 1 to May 31, 2026**. It aims to understand
usage patterns, trip duration, station performance, and data quality.
Key performance indicators and visual analyses help identify daily
and weekly trends, understand usage patterns throughout the day,
and highlight the busiest departure stations. The dashboard also
summarizes the ETL pipeline results, including data retention,
rejected records, and data quality checks, to support reliable and
consistent analysis.
""")

st.caption(
    "ETL monitoring · Data quality · Temporal analysis · "
    "Station performance · Business insights"
)

st.divider()

processed_path = first_existing(PROCESSED_CANDIDATES)

if processed_path is None:
    st.error(
        "Processed Parquet file not found. Expected: "
        "`data/processed/bike_trips.parquet`. "
        "Run your pipeline before opening the dashboard."
    )
    st.stop()

try:
    df_processed = read_table(processed_path)
except Exception as exc:
    st.error(f"Could not read the processed dataset: {exc}")
    st.stop()

if df_processed.empty:
    st.error("The processed dataset is empty.")
    st.stop()

rejected_path = first_existing(REJECTED_CANDIDATES)
report_path = first_existing(REPORT_CANDIDATES)

try:
    df_rejected = read_table(rejected_path)
except Exception as exc:
    df_rejected = pd.DataFrame()
    st.warning(f"Could not read rejection file: {exc}")

quality_report = read_json(report_path)

df, date_col = add_date_parts(df_processed)

# Find relevant columns using the original processed schema.
station_col = find_column(
    df,
    [
        "start_station",
        "start_station_name",
        "start_station_id",
        "start_station_id_name",
    ],
)

end_station_col = find_column(
    df,
    [
        "end_station",
        "end_station_name",
        "end_station_id",
    ],
)

duration_col = find_column(
    df,
    [
        "duration_min",
        "duration_minutes",
        "trip_duration_min",
        "duration",
    ],
)

if duration_col:
    df[duration_col] = pd.to_numeric(
        df[duration_col],
        errors="coerce",
    )

# Discover a raw input file if one exists.
RAW_CANDIDATES = [
    ROOT / "data" / "raw" / "bike_trips.csv",
    ROOT / "data" / "raw" / "bike_trips.parquet",
    ROOT / "data" / "raw" / "trips.csv",
    ROOT / "data" / "raw" / "trips.parquet",
]

raw_path = first_existing(RAW_CANDIDATES)
raw_rows = None

if raw_path is not None:
    try:
        raw_rows = len(read_table(raw_path))
    except Exception:
        pass


# ============================================================
# ETL COUNTS AND DATA QUALITY
# ============================================================
report_raw = as_number(
    get_json_value(
        quality_report,
        ["raw_rows", "total_input_rows", "input_rows", "rows_read"],
    )
)

report_kept = as_number(
    get_json_value(
        quality_report,
        ["processed_rows", "kept_rows", "valid_rows", "rows_kept"],
    )
)

report_rejected = as_number(
    get_json_value(
        quality_report,
        ["rejected_rows", "invalid_rows", "rows_rejected", "total_rejected"],
    )
)

kept_rows = len(df_processed)

rejected_rows_file = (
    len(df_rejected) if not df_rejected.empty else None
)

if report_rejected is not None:
    rejected_rows = int(report_rejected)
    rejection_source = "Pipeline JSON report"
elif (
    rejected_rows_file is not None
    and rejected_path.name != "rejection_report.csv"
):
    rejected_rows = rejected_rows_file
    rejection_source = f"Rows in {rejected_path.name}"
else:
    rejected_rows = None
    rejection_source = "No authoritative rejection count found"

if report_kept is not None and int(report_kept) != kept_rows:
    st.warning(
        f"The JSON report says {int(report_kept):,} processed rows, "
        f"but the Parquet contains {kept_rows:,}. "
        "Check whether both artifacts come from the same pipeline run."
    )

if report_raw is not None:
    total_raw = int(report_raw)
    raw_source = "Pipeline JSON report"
elif raw_rows is not None:
    total_raw = raw_rows
    raw_source = f"Raw file: {raw_path.name}"
elif rejected_rows is not None:
    total_raw = kept_rows + rejected_rows
    raw_source = "Computed from processed + rejected rows"
else:
    total_raw = None
    raw_source = "Unknown"

counts_consistent = (
    total_raw is not None
    and rejected_rows is not None
    and total_raw == kept_rows + rejected_rows
)

if (
    total_raw is not None
    and rejected_rows is not None
    and total_raw != kept_rows + rejected_rows
):
    st.warning(
        "Raw, processed and rejected counts do not reconcile. "
        "Check that all files belong to the same pipeline execution."
    )


# ============================================================
# SECTION 1: EXECUTIVE SUMMARY
# ============================================================
st.header("1. Executive summary")

valid_durations = pd.Series(dtype=float)

if duration_col:
    valid_durations = df[duration_col].dropna()
    valid_durations = valid_durations[valid_durations > 0]

avg_duration = (
    valid_durations.mean()
    if not valid_durations.empty
    else None
)

median_duration = (
    valid_durations.median()
    if not valid_durations.empty
    else None
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Processed trips", metric_count(kept_rows))

col2.metric(
    "Raw input rows",
    metric_count(total_raw) if total_raw is not None else "Unknown",
)

col3.metric(
    "Rejected rows",
    metric_count(rejected_rows)
    if rejected_rows is not None
    else "Unknown",
)

col4.metric(
    "Rejection rate",
    f"{100 * rejected_rows / total_raw:.2f}%"
    if total_raw is not None
    and total_raw > 0
    and rejected_rows is not None
    else "Unknown",
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Retention rate",
    f"{100 * kept_rows / total_raw:.2f}%"
    if total_raw is not None and total_raw > 0
    else "Unknown",
)

col2.metric(
    "Mean trip duration",
    f"{avg_duration:.1f} min"
    if avg_duration is not None
    else "N/A",
)

col3.metric(
    "Median trip duration",
    f"{median_duration:.1f} min"
    if median_duration is not None
    else "N/A",
)

col4.metric(
    "Unique departure stations",
    metric_count(df[station_col].nunique())
    if station_col
    else "N/A",
)

if rejected_rows is None:
    st.warning(
        "The rejection count could not be verified. "
        "The dashboard will not assume that zero rows were rejected. "
        "Check the rejection artifact or the pipeline JSON report."
    )


# ============================================================
# SECTION 2: ETL PIPELINE AND DATA QUALITY
# ============================================================
st.header("2. ETL pipeline and data quality")

if not df_rejected.empty:
    st.subheader("Rejected rows preview")
    st.dataframe(
        df_rejected.head(100),
        use_container_width=True,
    )

    reason_col = find_column(
        df_rejected,
        [
            "rejection_reason",
            "reject_reason",
            "reason",
            "error_reason",
            "rule",
        ],
    )

    if reason_col:
        reasons = (
            df_rejected[reason_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Rejection reason")
            .reset_index(name="Rows")
        )

        reasons["Share of rejection file (%)"] = (
            reasons["Rows"] / max(1, len(df_rejected)) * 100
        ).round(2)

        col1, col2 = st.columns([3, 2])

        with col1:
            st.subheader("Rejection reasons")
            st.bar_chart(
                reasons.set_index("Rejection reason")["Rows"]
            )

        with col2:
            st.subheader("Reason breakdown")
            st.dataframe(
                reasons,
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info(
            "No recognizable rejection-reason column was found."
        )
else:
    st.warning(
        "No rejected-row file was found or the file is empty. "
        "An empty report does not prove that zero rows were rejected."
    )

if quality_report:
    with st.expander("Full pipeline quality report (JSON)"):
        st.json(quality_report)

quality_summary = pd.DataFrame({
    "column": df_processed.columns,
    "missing_values": [
        df_processed[col].isna().sum()
        for col in df_processed.columns
    ],
    "missing_pct": [
        round(df_processed[col].isna().mean() * 100, 3)
        for col in df_processed.columns
    ],
    "distinct_values": [
        df_processed[col].nunique(dropna=True)
        for col in df_processed.columns
    ],
})

st.subheader("Processed dataset completeness")

st.dataframe(
    quality_summary,
    use_container_width=True,
    hide_index=True,
)

duplicate_count = int(df_processed.duplicated().sum())

st.metric(
    "Exact duplicate rows in processed dataset",
    metric_count(duplicate_count),
)

st.markdown("---")


# ============================================================
# SECTION 3: TEMPORAL ANALYSIS
# ============================================================
st.header("3. Temporal analysis")

if date_col and df["_dashboard_date"].notna().any():
    valid_dates = df.dropna(subset=["_dashboard_date"]).copy()
    valid_dates["_trip_count"] = 1

    daily = (
        valid_dates.set_index("_dashboard_date")
        .resample("D")["_trip_count"]
        .sum()
        .rename("trips")
        .reset_index()
    )

    weekly = (
        valid_dates.set_index("_dashboard_date")
        .resample("W-MON")["_trip_count"]
        .sum()
        .rename("trips")
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Trips per day")
        st.line_chart(
            daily.set_index("_dashboard_date")["trips"]
        )

    with col2:
        st.subheader("Trips per week")
        st.bar_chart(
            weekly.set_index("_dashboard_date")["trips"]
        )

    if "_dashboard_hour" in df.columns:
        hourly = (
            df["_dashboard_hour"]
            .dropna()
            .astype(int)
            .value_counts()
            .reindex(range(24), fill_value=0)
            .sort_index()
        )

        st.subheader("Trip volume by hour")
        st.bar_chart(hourly.rename_axis("Hour").rename("Trips"))

    if "_dashboard_weekday" in df.columns:
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        weekday_counts = (
            df["_dashboard_weekday"]
            .value_counts()
            .reindex(weekday_order, fill_value=0)
        )

        st.subheader("Trip volume by day of week")
        st.bar_chart(weekday_counts.rename("Trips"))


else:
    st.info(
        "No usable start-date column was detected for temporal analysis."
    )

st.markdown("---")


# ============================================================
# SECTION 4: DURATION ANALYSIS
# ============================================================
st.header("4. Trip duration and usage patterns")

if duration_col:
    duration_data = df[duration_col].dropna()
    duration_data = duration_data[duration_data > 0]

    if not duration_data.empty:
        p99 = duration_data.quantile(0.99)
        visible_durations = duration_data[duration_data <= p99]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Valid positive durations",
            metric_count(len(duration_data)),
        )

        col2.metric(
            "Median duration",
            f"{duration_data.median():.1f} min",
        )

        col3.metric(
            "95th percentile",
            f"{duration_data.quantile(0.95):.1f} min",
        )

        st.subheader("Duration distribution (up to 99th percentile)")

        histogram_counts = pd.cut(
            visible_durations,
            bins=30,
        ).value_counts().sort_index()

        histogram_counts.index = histogram_counts.index.astype(str)

        st.bar_chart(histogram_counts.rename("Trips"))

        st.caption(
            "The chart excludes durations above the 99th percentile "
            "for readability. These trips are not automatically invalid."
        )
    else:
        st.info("No positive trip durations are available.")
else:
    st.info(
        "No recognized duration column found. Expected one of: "
        "`duration_min`, `duration_minutes`, `trip_duration_min`, `duration`."
    )

st.markdown("---")


# ============================================================
# SECTION 5: STATION ANALYSIS
# ============================================================
st.header("5. Station performance")

if station_col:
    departures = (
        df[station_col]
        .fillna("Unknown")
        .astype(str)
        .value_counts()
        .head(15)
        .rename_axis("Station")
        .rename("Departures")
    )

    st.subheader("Top departure stations")
    st.bar_chart(departures)

    if end_station_col:
        arrivals = (
            df[end_station_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .head(15)
            .rename_axis("Station")
            .rename("Arrivals")
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top departures")
            st.bar_chart(departures)

        with col2:
            st.subheader("Top arrivals")
            st.bar_chart(arrivals)

        dep = (
            df[station_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        arr = (
            df[end_station_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
        )

        balance = pd.concat(
            [
                dep.rename("departures"),
                arr.rename("arrivals"),
            ],
            axis=1,
        ).fillna(0)

        balance["net_flow"] = (
            balance["arrivals"] - balance["departures"]
        )

        balance = balance.sort_values("net_flow")

        st.subheader("Station flow proxy")

        st.caption(
            "Net flow = recorded arrivals minus departures. "
            "This indicates usage patterns; it does not directly measure "
            "bike availability or shortages."
        )

        st.dataframe(
            balance.head(20),
            use_container_width=True,
        )

else:
    st.info("No recognized departure-station column was found.")

st.markdown("---")


# ============================================================
# SECTION 6: BUSINESS INSIGHTS
# ============================================================
st.header("6. Business insights")

insights = []

if date_col and df["_dashboard_date"].notna().any():
    temp = df.dropna(subset=["_dashboard_date"]).copy()

    weekday_counts = temp["_dashboard_weekday"].value_counts()

    if not weekday_counts.empty:
        busiest = weekday_counts.idxmax()
        quietest = weekday_counts.idxmin()

        insights.append(
            f"**Weekly pattern:** {busiest} has the most recorded trips, "
            f"while {quietest} has the fewest in this dataset. "
            "This may inform staffing and rebalancing hypotheses."
        )

    hourly_counts = temp["_dashboard_hour"].value_counts()

    if not hourly_counts.empty:
        busiest_hour = int(hourly_counts.idxmax())

        insights.append(
            f"**Peak hour:** {busiest_hour:02d}:00 has the highest "
            "recorded trip volume in this period."
        )

if duration_col and not valid_durations.empty:
    insights.append(
        f"**Trip duration:** median duration is "
        f"{valid_durations.median():.1f} minutes and the 95th percentile is "
        f"{valid_durations.quantile(0.95):.1f} minutes. "
        "Investigate unusually long trips before defining operational thresholds."
    )

if station_col:
    top_station = df[station_col].mode(dropna=True)

    if not top_station.empty:
        station_name = str(top_station.iloc[0])

        station_share = (
            df[station_col]
            .eq(top_station.iloc[0])
            .mean()
            * 100
        )

        insights.append(
            f"**Demand concentration:** `{station_name}` is the most "
            f"frequent departure station, accounting for {station_share:.1f}% "
            "of rows with the current station field."
        )

if rejected_rows is not None and total_raw is not None and total_raw > 0:
    insights.append(
        f"**Data quality:** reported rejection rate is "
        f"{100 * rejected_rows / total_raw:.2f}%. "
        "Monitor this rate across pipeline runs."
    )

if insights:
    for insight in insights:
        st.markdown(f"- {insight}")
else:
    st.info(
        "Not enough recognized columns to generate business insights. "
        "Check the dataset schema and column aliases."
    )

st.warning(
    "These insights are descriptive. They do not establish causality, "
    "financial impact, bike shortages or ROI without additional data."
)

st.markdown("---")


# ============================================================
# SECTION 7: EXPORTS
# ============================================================
st.header("7. Export data")

col1, col2 = st.columns(2)

with col1:
    export_df = df.drop(
        columns=[
            "_dashboard_date",
            "_dashboard_hour",
            "_dashboard_weekday",
            "_dashboard_month",
        ],
        errors="ignore",
    )

    st.download_button(
        "Download processed trips (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="bike_trips_processed.csv",
        mime="text/csv",
    )

with col2:
    if not df_rejected.empty:
        st.download_button(
            "Download rejection data (CSV)",
            data=df_rejected.to_csv(index=False).encode("utf-8"),
            file_name="rejected_trips.csv",
            mime="text/csv",
        )

st.caption(
    "Dashboard built from local pipeline artifacts. "
    "For trustworthy monitoring, ensure raw, processed, rejected and "
    "quality-report files all belong to the same pipeline execution."
)
