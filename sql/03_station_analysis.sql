
-- 1. Top 10 departure stations
SELECT
    start_station,
    COUNT(*) AS departure_count
FROM bike_trips
WHERE start_station IS NOT NULL
GROUP BY start_station
ORDER BY departure_count DESC
LIMIT 10;


-- 2. Top 10 arrival stations
SELECT
    end_station,
    COUNT(*) AS arrival_count
FROM bike_trips
WHERE end_station IS NOT NULL
GROUP BY end_station
ORDER BY arrival_count DESC
LIMIT 10;


-- 3. Departure and arrival balance by station
WITH departures AS (
    SELECT
        start_station AS station_name,
        COUNT(*) AS departure_count
    FROM bike_trips
    WHERE start_station IS NOT NULL
    GROUP BY start_station
),
arrivals AS (
    SELECT
        end_station AS station_name,
        COUNT(*) AS arrival_count
    FROM bike_trips
    WHERE end_station IS NOT NULL
    GROUP BY end_station
)
SELECT
    COALESCE(d.station_name, a.station_name) AS station_name,
    COALESCE(d.departure_count, 0) AS departure_count,
    COALESCE(a.arrival_count, 0) AS arrival_count,
    COALESCE(a.arrival_count, 0)
        - COALESCE(d.departure_count, 0) AS net_trip_balance
FROM departures d
FULL OUTER JOIN arrivals a
    ON d.station_name = a.station_name
ORDER BY net_trip_balance ASC
LIMIT 15;
