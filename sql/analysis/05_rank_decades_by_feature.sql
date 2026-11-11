-- Q5. Which decades had the most danceable, energetic and positive-sounding hits?
--
-- Tables: songs JOIN audio_features.
-- Step 1 (CTE "by_decade"): one row per decade with the averages.
-- Step 2: RANK() orders the decades separately for each feature (1 = highest).
-- RANK gives tied decades the same rank and skips the next number.
WITH by_decade AS (
    SELECT
        s.decade,
        COUNT(*)              AS songs_with_audio,
        AVG(a.danceability)   AS danceability,
        AVG(a.energy)         AS energy,
        AVG(a.valence)        AS valence
    FROM songs AS s
    JOIN audio_features AS a ON a.song_key = s.song_key
    GROUP BY s.decade
)
SELECT
    decade,
    songs_with_audio,
    ROUND(CAST(danceability AS NUMERIC), 3)            AS avg_danceability,
    RANK() OVER (ORDER BY danceability DESC)           AS danceability_rank,
    ROUND(CAST(energy AS NUMERIC), 3)                  AS avg_energy,
    RANK() OVER (ORDER BY energy DESC)                 AS energy_rank,
    ROUND(CAST(valence AS NUMERIC), 3)                 AS avg_valence,
    RANK() OVER (ORDER BY valence DESC)                AS valence_rank
FROM by_decade
ORDER BY decade;
