
SELECT
    start_station_number,
    end_station_number,
    started_at,
    ended_at,
    bike_model,
    COUNT(*) AS occurrences
FROM bike_trips
GROUP BY
    start_station_number,
    end_station_number,
    started_at,
    ended_at,
    bike_model
HAVING COUNT(*) > 1
ORDER BY occurrences DESC
LIMIT 20;
