-- Q1. How long did songs stay on the Hot 100, by decade they first charted?
--
-- Tables: songs.
-- Songs still on the chart when the data ends (2021-05-29) are left out of the
-- averages, because their weeks_on_chart is not final. The count of those
-- songs is shown so you can see how many were removed. NULLIF avoids dividing
-- by zero when every song in a decade is still charting.
-- Caveat: weeks_on_chart counts weeks charted, so a holiday song that returns
-- every December keeps adding weeks.
SELECT
    decade,
    COUNT(*)                                                     AS songs,
    SUM(still_charting)                                          AS songs_still_charting,
    ROUND(CAST(AVG(CASE WHEN still_charting = 0
                        THEN weeks_on_chart END) AS NUMERIC), 1) AS avg_weeks_on_chart,
    MAX(weeks_on_chart)                                          AS max_weeks_on_chart,
    ROUND(CAST(100.0 * SUM(CASE WHEN still_charting = 0 AND weeks_on_chart >= 20
                                THEN 1 ELSE 0 END)
               / NULLIF(SUM(CASE WHEN still_charting = 0 THEN 1 ELSE 0 END), 0)
               AS NUMERIC), 1)                                   AS pct_20_plus_weeks
FROM songs
GROUP BY decade
ORDER BY decade;
