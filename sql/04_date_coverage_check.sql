
-- Check the temporal coverage of the dataset
SELECT
    CAST(started_at AS DATE) AS trip_date,
    COUNT(*) AS trip_count,
    MIN(started_at) AS first_trip,
    MAX(started_at) AS last_trip
FROM bike_trips
GROUP BY CAST(started_at AS DATE)
ORDER BY trip_date DESC
LIMIT 5;
