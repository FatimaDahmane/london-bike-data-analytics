
SELECT
    COUNT(*) AS total_trips,

    COUNT(*) FILTER (
        WHERE started_at IS NULL
    ) AS missing_start_dates,

    COUNT(*) FILTER (
        WHERE ended_at IS NULL
    ) AS missing_end_dates,

    COUNT(*) FILTER (
        WHERE ended_at < started_at
    ) AS negative_duration_trips,

    COUNT(*) FILTER (
        WHERE duration_seconds < 60
    ) AS trips_below_60_seconds,

    COUNT(*) FILTER (
        WHERE ABS(
            duration_min - duration_seconds / 60.0
        ) > 0.000001
    ) AS inconsistent_duration_rows,

    COUNT(*) FILTER (
        WHERE start_station IS NULL
           OR TRIM(start_station) = ''
    ) AS missing_start_stations,

    COUNT(*) FILTER (
        WHERE end_station IS NULL
           OR TRIM(end_station) = ''
    ) AS missing_end_stations

FROM bike_trips;
