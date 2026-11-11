-- Q4. Year over year, how much did average danceability move?
--
-- Tables: songs JOIN audio_features.
-- Step 1 (CTE "yearly"): average danceability for songs that first charted each year.
-- Step 2: LAG() looks back one row (the previous year) so we can subtract.
-- Caveat: 1958 is a partial year (the chart started in August) and so is 2021
-- (data ends in May); years with few songs swing more.
WITH yearly AS (
    SELECT
        s.first_year                 AS year,
        COUNT(*)                     AS songs_with_audio,
        AVG(a.danceability)          AS avg_danceability
    FROM songs AS s
    JOIN audio_features AS a ON a.song_key = s.song_key
    GROUP BY s.first_year
)
SELECT
    year,
    songs_with_audio,
    ROUND(CAST(avg_danceability AS NUMERIC), 3)                                AS avg_danceability,
    ROUND(CAST(avg_danceability - LAG(avg_danceability) OVER (ORDER BY year)
               AS NUMERIC), 3)                                                 AS change_from_prev_year
FROM yearly
ORDER BY year;
