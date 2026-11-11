-- Q6. What were the five most common genres among charting songs in each decade?
--
-- Tables: songs JOIN song_genres (one row per song-genre pair).
-- Step 1 (CTE "genre_counts"): how many songs carry each genre, per decade.
-- Step 2 (CTE "ranked"): RANK() within each decade (PARTITION BY decade).
-- Step 3: keep ranks 1-5. Ties can return more than five rows.
-- Caveat: Spotify tags artists, not songs, with genres, and with today's labels;
-- a 1960s artist may carry a label invented later.
WITH genre_counts AS (
    SELECT s.decade, g.genre, COUNT(*) AS songs
    FROM songs AS s
    JOIN song_genres AS g ON g.song_key = s.song_key
    GROUP BY s.decade, g.genre
),
ranked AS (
    SELECT
        decade, genre, songs,
        RANK() OVER (PARTITION BY decade ORDER BY songs DESC) AS genre_rank
    FROM genre_counts
)
SELECT decade, genre_rank, genre, songs
FROM ranked
WHERE genre_rank <= 5
ORDER BY decade, genre_rank, genre;
