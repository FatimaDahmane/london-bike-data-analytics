
-- 1. Number of trips by hour of the day
SELECT
    EXTRACT(HOUR FROM started_at) AS hour_of_day,
    COUNT(*) AS trip_count
FROM bike_trips
WHERE started_at IS NOT NULL
GROUP BY hour_of_day
ORDER BY hour_of_day;


-- 2. Number of trips by day of the week
-- DuckDB: Sunday = 0, Monday = 1, ..., Saturday = 6
SELECT
    DAYOFWEEK(started_at) AS day_of_week,
    COUNT(*) AS trip_count
FROM bike_trips
WHERE started_at IS NOT NULL
GROUP BY day_of_week
ORDER BY day_of_week;


-- 3. Number of trips by date
SELECT
    CAST(started_at AS DATE) AS trip_date,
    COUNT(*) AS trip_count
FROM bike_trips
WHERE CAST(started_at AS DATE) < DATE '2026-06-01'
GROUP BY trip_date
ORDER BY trip_date;
