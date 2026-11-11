-- Q2. How did the sound of charting songs change, decade by decade?
--
-- Tables: songs LEFT JOIN audio_features. The LEFT JOIN keeps songs that have
-- no audio features, so we can report how many are missing in each decade.
-- AVG ignores the missing (NULL) values, so averages use only songs with features.
-- Caveat: about 35% of 1950s songs and 24% of 1960s songs have no features,
-- so early averages rest on fewer, possibly unrepresentative, songs.
SELECT
    s.decade,
    COUNT(*)                                                      AS songs,
    COUNT(a.song_key)                                             AS songs_with_audio,
    ROUND(CAST(100.0 * (COUNT(*) - COUNT(a.song_key)) / COUNT(*)
               AS NUMERIC), 1)                                    AS pct_missing_audio,
    ROUND(CAST(AVG(a.danceability) AS NUMERIC), 3)                AS avg_danceability,
    ROUND(CAST(AVG(a.energy) AS NUMERIC), 3)                      AS avg_energy,
    ROUND(CAST(AVG(a.valence) AS NUMERIC), 3)                     AS avg_valence,
    ROUND(CAST(AVG(a.acousticness) AS NUMERIC), 3)                AS avg_acousticness,
    ROUND(CAST(AVG(a.speechiness) AS NUMERIC), 3)                 AS avg_speechiness,
    ROUND(CAST(AVG(a.loudness) AS NUMERIC), 2)                    AS avg_loudness_db,
    ROUND(CAST(AVG(a.tempo) AS NUMERIC), 1)                       AS avg_tempo_bpm,
    ROUND(CAST(AVG(a.duration_ms) / 60000.0 AS NUMERIC), 2)       AS avg_minutes
FROM songs AS s
LEFT JOIN audio_features AS a ON a.song_key = s.song_key
GROUP BY s.decade
ORDER BY s.decade;
