-- Q8. How common were explicit lyrics among charting songs, and how much did
-- the share change from one decade to the next?
--
-- Tables: songs JOIN audio_features (the explicit flag comes from Spotify).
-- Step 1 (CTE "by_decade"): share of songs flagged explicit.
-- Step 2: LAG() fetches the previous decade's share so we can subtract.
-- Caveat: Spotify's flag reflects the version on Spotify today; older songs
-- were rarely flagged, and a clean radio edit may have been the charting version.
WITH by_decade AS (
    SELECT
        s.decade,
        COUNT(a.explicit)                          AS songs_with_flag,
        100.0 * SUM(a.explicit) / COUNT(a.explicit) AS pct_explicit
    FROM songs AS s
    JOIN audio_features AS a ON a.song_key = s.song_key
    GROUP BY s.decade
)
SELECT
    decade,
    songs_with_flag,
    ROUND(CAST(pct_explicit AS NUMERIC), 1)                                    AS pct_explicit,
    ROUND(CAST(pct_explicit - LAG(pct_explicit) OVER (ORDER BY decade)
               AS NUMERIC), 1)                                                 AS change_from_prev_decade
FROM by_decade
ORDER BY decade;
