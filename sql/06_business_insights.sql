
-- 1. Compare weekday and weekend demand.
-- DuckDB: DAYOFWEEK returns 0 for Sunday and 6 for Saturday.

SELECT
    CASE
        WHEN DAYOFWEEK(started_at) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(*) AS total_trips,
    ROUND(AVG(duration_min), 2) AS avg_duration_min
FROM bike_trips
GROUP BY day_type
ORDER BY day_type;


-- 2. Identify the busiest hours.
SELECT
    HOUR(started_at) AS hour_of_day,
    COUNT(*) AS total_trips
FROM bike_trips
GROUP BY hour_of_day
ORDER BY total_trips DESC
LIMIT 10;


-- 3. Identify stations with the largest departure imbalance.
-- A negative balance means more departures than arrivals.

WITH station_flows AS (
    SELECT start_station AS station, COUNT(*) AS departures
    FROM bike_trips
    GROUP BY start_station

    UNION ALL

    SELECT end_station AS station, -COUNT(*) AS departures
    FROM bike_trips
    GROUP BY end_station
)
SELECT
    station,
    SUM(departures) * -1 AS net_arrivals_minus_departures
FROM station_flows
GROUP BY station
ORDER BY net_arrivals_minus_departures ASC
LIMIT 10;


-- 4. Compare hourly demand on weekdays and weekends.
SELECT
    CASE
        WHEN DAYOFWEEK(started_at) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    HOUR(started_at) AS hour_of_day,
    COUNT(*) AS total_trips
FROM bike_trips
GROUP BY day_type, hour_of_day
ORDER BY day_type, hour_of_day;


