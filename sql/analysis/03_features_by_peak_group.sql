-- Q3. Do songs that reached the top 5 sound different from songs that peaked lower?
--
-- Tables: songs JOIN audio_features (inner join: only songs with features).
-- Groups: #1, #2-5 (together these are "top 5"), and #6-100.
-- Caveat: every song here charted, so this compares bigger hits with smaller
-- hits, not hits with songs that never charted. Differences are associations.
SELECT
    CASE
        WHEN s.peak_position = 1  THEN '1: #1'
        WHEN s.peak_position <= 5 THEN '2: #2-5'
        ELSE                           '3: #6-100'
    END                                                AS peak_group,
    COUNT(*)                                           AS songs,
    ROUND(CAST(AVG(a.danceability) AS NUMERIC), 3)     AS avg_danceability,
    ROUND(CAST(AVG(a.energy) AS NUMERIC), 3)           AS avg_energy,
    ROUND(CAST(AVG(a.valence) AS NUMERIC), 3)          AS avg_valence,
    ROUND(CAST(AVG(a.acousticness) AS NUMERIC), 3)     AS avg_acousticness,
    ROUND(CAST(AVG(a.speechiness) AS NUMERIC), 3)      AS avg_speechiness,
    ROUND(CAST(AVG(a.loudness) AS NUMERIC), 2)         AS avg_loudness_db,
    ROUND(CAST(AVG(a.tempo) AS NUMERIC), 1)            AS avg_tempo_bpm
FROM songs AS s
JOIN audio_features AS a ON a.song_key = s.song_key
GROUP BY 1
ORDER BY 1;
