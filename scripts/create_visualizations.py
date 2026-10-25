
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "bike_trips.parquet"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures"

plt.rcParams["figure.dpi"] = 120
plt.rcParams["axes.titleweight"] = "bold"


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    """Connect to DuckDB and load the processed Parquet dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Run the data pipeline first."
        )

    connection = duckdb.connect()
    parquet_path = str(DATA_PATH).replace("\\", "/").replace("'", "''")

    connection.execute(
        f"""
        CREATE VIEW bike_trips AS
        SELECT *
        FROM read_parquet('{parquet_path}')
        """
    )

    return connection


# --------------------------------------------------
# 1. Number of trips by hour
# --------------------------------------------------

def plot_trips_by_hour(connection):
    df = connection.execute("""
        SELECT
            EXTRACT(HOUR FROM started_at) AS hour,
            COUNT(*) AS trip_count
        FROM bike_trips
        GROUP BY hour
        ORDER BY hour
    """).fetchdf()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["hour"], df["trip_count"])

    ax.set(
        title="London Bike Trips by Hour",
        xlabel="Hour of Day",
        ylabel="Number of Trips",
        xticks=range(24),
    )
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "trips_by_hour.png")
    plt.close(fig)


# --------------------------------------------------
# 2. Average duration: weekday vs weekend
# --------------------------------------------------

def plot_weekday_vs_weekend(connection):
    df = connection.execute("""
        SELECT
            CASE
                WHEN DAYOFWEEK(started_at) IN (0, 6)
                    THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            AVG(duration_min) AS avg_duration
        FROM bike_trips
        GROUP BY day_type
        ORDER BY CASE
            WHEN day_type = 'Weekday' THEN 1
            ELSE 2
        END
    """).fetchdf()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df["day_type"], df["avg_duration"])

    ax.set(
        title="Average Trip Duration: Weekday vs Weekend",
        xlabel="Day Type",
        ylabel="Average Duration (minutes)",
    )
    ax.bar_label(bars, fmt="%.2f min", padding=4)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "weekday_vs_weekend.png")
    plt.close(fig)


# --------------------------------------------------
# 3. Stations with the largest departure surplus
# --------------------------------------------------

def plot_station_net_balance(connection):
    df = connection.execute("""
        WITH departures AS (
            SELECT
                start_station_number AS station_id,
                MAX(start_station) AS station_name,
                COUNT(*) AS departure_count
            FROM bike_trips
            GROUP BY station_id
        ),
        arrivals AS (
            SELECT
                end_station_number AS station_id,
                COUNT(*) AS arrival_count
            FROM bike_trips
            GROUP BY station_id
        )
        SELECT
            d.station_name,
            d.departure_count,
            COALESCE(a.arrival_count, 0) AS arrival_count,
            COALESCE(a.arrival_count, 0)
                - d.departure_count AS net_balance
        FROM departures d
        LEFT JOIN arrivals a USING (station_id)
        ORDER BY net_balance ASC
        LIMIT 10
    """).fetchdf()

    df = df.sort_values("net_balance")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["station_name"], df["net_balance"])

    ax.set(
        title="Stations with the Largest Departure Surplus",
        xlabel="Arrivals Minus Departures",
        ylabel="Station",
    )
    ax.axvline(0, linewidth=0.8)
    ax.bar_label(bars, padding=3, fmt="%d")
    ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "station_net_balance.png")
    plt.close(fig)


# --------------------------------------------------
# 4. Daily trip volume
# --------------------------------------------------

def plot_daily_trips(connection):
    df = connection.execute("""
        SELECT
            CAST(started_at AS DATE) AS trip_date,
            COUNT(*) AS trip_count
        FROM bike_trips
        WHERE CAST(started_at AS DATE) < DATE '2026-06-01'
        GROUP BY trip_date
        ORDER BY trip_date
    """).fetchdf()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["trip_date"], df["trip_count"], linewidth=1.2)

    ax.set(
        title="Daily London Bike Trip Volume",
        xlabel="Date",
        ylabel="Number of Trips",
    )
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "daily_trips.png")
    plt.close(fig)


# --------------------------------------------------
# 5. Hourly demand: weekday vs weekend
# --------------------------------------------------

def plot_hourly_weekday_weekend(connection):
    df = connection.execute("""
        SELECT
            EXTRACT(HOUR FROM started_at) AS hour,
            CASE
                WHEN DAYOFWEEK(started_at) IN (0, 6)
                    THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            COUNT(*) AS trip_count
        FROM bike_trips
        GROUP BY hour, day_type
        ORDER BY hour
    """).fetchdf()

    pivot = df.pivot(
        index="hour",
        columns="day_type",
        values="trip_count",
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(11, 5))

    for day_type in ["Weekday", "Weekend"]:
        if day_type in pivot.columns:
            ax.plot(
                pivot.index,
                pivot[day_type],
                marker="o",
                markersize=3,
                label=day_type,
            )

    ax.set(
        title="Hourly Bike Demand: Weekday vs Weekend",
        xlabel="Hour of Day",
        ylabel="Number of Trips",
        xticks=range(24),
    )
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "hourly_weekday_weekend.png")
    plt.close(fig)


# --------------------------------------------------
# 6. Trip duration distribution
# --------------------------------------------------

def plot_duration_distribution(connection):
    # Limit to 180 minutes to make the main distribution readable.
    df = connection.execute("""
        SELECT duration_min
        FROM bike_trips
        WHERE duration_min BETWEEN 1 AND 180
    """).fetchdf()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["duration_min"], bins=60)

    ax.set(
        title="Distribution of Trip Durations",
        xlabel="Trip Duration (minutes)",
        ylabel="Number of Trips",
    )
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "duration_distribution.png")
    plt.close(fig)


# --------------------------------------------------
# 7. Trip duration by day of the week
# --------------------------------------------------

def plot_duration_by_weekday(connection):
    df = connection.execute("""
        SELECT
            DAYOFWEEK(started_at) AS weekday_num,
            CASE DAYOFWEEK(started_at)
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
                WHEN 0 THEN 'Sunday'
            END AS weekday,
            duration_min
        FROM bike_trips
        WHERE duration_min <= 180
    """).fetchdf()

    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday",
    ]

    values = [
        df.loc[df["weekday"] == day, "duration_min"].to_numpy()
        for day in weekday_order
    ]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.boxplot(values, tick_labels=weekday_order, showfliers=False)

    ax.set(
        title="Trip Duration by Day of the Week",
        xlabel="Day of the Week",
        ylabel="Trip Duration (minutes)",
    )
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "duration_by_weekday.png")
    plt.close(fig)


# --------------------------------------------------
# 8. Top 10 departure stations
# --------------------------------------------------

def plot_top_departure_stations(connection):
    df = connection.execute("""
        SELECT
            start_station AS station_name,
            COUNT(*) AS departure_count
        FROM bike_trips
        GROUP BY start_station
        ORDER BY departure_count DESC
        LIMIT 10
    """).fetchdf()

    df = df.sort_values("departure_count")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df["station_name"], df["departure_count"])

    ax.set(
        title="Top 10 Departure Stations",
        xlabel="Number of Departures",
        ylabel="Station",
    )
    ax.bar_label(bars, padding=3, fmt="%d")
    ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "top_departure_stations.png")
    plt.close(fig)


# --------------------------------------------------
# 9. Number of trips by bike model
# --------------------------------------------------

def plot_bike_model_usage(connection):
    df = connection.execute("""
        SELECT
            COALESCE(bike_model, 'Unknown') AS bike_model,
            COUNT(*) AS trip_count
        FROM bike_trips
        GROUP BY bike_model
        ORDER BY trip_count DESC
    """).fetchdf()

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(df["bike_model"], df["trip_count"])

    ax.set(
        title="Bike Usage by Model",
        xlabel="Bike Model",
        ylabel="Number of Trips",
    )
    ax.bar_label(bars, padding=3, fmt="%.0f")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "bike_model_usage.png")
    plt.close(fig)


# --------------------------------------------------
# 10. Heatmap of flows between top stations
# --------------------------------------------------

def plot_station_flow_heatmap(connection):
    # Select the 10 most popular departure stations.
    top_stations = connection.execute("""
        SELECT start_station AS station_name
        FROM bike_trips
        GROUP BY start_station
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """).fetchdf()["station_name"].tolist()

    if not top_stations:
        print("No stations available for the flow heatmap.")
        return

    df = connection.execute("""
        SELECT
            start_station,
            end_station,
            COUNT(*) AS trip_count
        FROM bike_trips
        WHERE start_station IN (
            SELECT start_station
            FROM bike_trips
            GROUP BY start_station
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        AND end_station IN (
            SELECT start_station
            FROM bike_trips
            GROUP BY start_station
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        GROUP BY start_station, end_station
    """).fetchdf()

    matrix = df.pivot(
        index="start_station",
        columns="end_station",
        values="trip_count",
    ).fillna(0)

    # Use the same station order on both axes.
    matrix = matrix.reindex(
        index=top_stations,
        columns=top_stations,
        fill_value=0,
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(matrix.to_numpy(), aspect="auto")

    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=90, fontsize=7)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=7)

    ax.set(
        title="Trip Flows Between the Top 10 Departure Stations",
        xlabel="Arrival Station",
        ylabel="Departure Station",
    )

    fig.colorbar(image, ax=ax, label="Number of Trips")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "station_flow_heatmap.png")
    plt.close(fig)


# --------------------------------------------------
# Main execution
# --------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    connection = get_connection()

    plots = [
        ("Trips by hour", plot_trips_by_hour),
        ("Weekday vs weekend duration", plot_weekday_vs_weekend),
        ("Station net balance", plot_station_net_balance),
        ("Daily trips", plot_daily_trips),
        ("Hourly weekday vs weekend", plot_hourly_weekday_weekend),
        ("Duration distribution", plot_duration_distribution),
        ("Duration by weekday", plot_duration_by_weekday),
        ("Top departure stations", plot_top_departure_stations),
        ("Bike model usage", plot_bike_model_usage),
        ("Station flow heatmap", plot_station_flow_heatmap),
    ]

    try:
        for name, plot_function in plots:
            try:
                plot_function(connection)
                print(f"[OK] {name}")
            except Exception as error:
                print(f"[ERROR] {name}: {error}")
                raise
    finally:
        connection.close()

    print(f"\nAll 10 visualizations saved to:\n{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
