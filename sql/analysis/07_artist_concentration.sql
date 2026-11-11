-- Q7. How concentrated were the charts? Share of each decade's charting songs
-- that belong to that decade's 10 busiest artists.
--
-- Tables: songs JOIN artists.
-- Step 1 (CTE "artist_songs"): songs per primary artist per decade.
-- Step 2 (CTE "ranked"): ROW_NUMBER() numbers artists within each decade from
-- most songs to fewest (ties broken alphabetically, so exactly 10 are kept).
-- Step 3: add up the top 10 and divide by the decade's total.
-- Caveat: "primary artist" is the first act in the credit (before "Featuring"
-- or "With"); guest appearances are not counted.
WITH artist_songs AS (
    SELECT s.decade, ar.name AS artist, COUNT(*) AS songs
    FROM songs AS s
    JOIN artists AS ar ON ar.artist_key = s.artist_key
    GROUP BY s.decade, ar.name
),
ranked AS (
    SELECT
        decade, artist, songs,
        ROW_NUMBER() OVER (PARTITION BY decade ORDER BY songs DESC, artist) AS artist_rank,
        SUM(songs)   OVER (PARTITION BY decade)                            AS decade_songs
    FROM artist_songs
)
SELECT
    decade,
    MAX(decade_songs)                                                    AS songs,
    COUNT(*)                                                             AS top_artists_counted,
    SUM(songs)                                                           AS songs_by_top_10,
    ROUND(CAST(100.0 * SUM(songs) / MAX(decade_songs) AS NUMERIC), 1)    AS pct_songs_by_top_10,
    MAX(CASE WHEN artist_rank = 1 THEN artist END)                       AS busiest_artist,
    MAX(CASE WHEN artist_rank = 1 THEN songs END)                        AS busiest_artist_songs
FROM ranked
WHERE artist_rank <= 10
GROUP BY decade
ORDER BY decade;
