# Building the Tableau Public dashboard

Tableau Public reads files, not databases, so the dashboard is built from the
CSVs that `python3 src/04_export_results.py` writes to `data/exports/`.

## 1. Set up

1. Download Tableau Public (free) from public.tableau.com and create an account.
2. Open it, choose **Connect > To a File > Text file**, and pick
   `data/exports/02_audio_features_by_decade.csv`.
3. Add the other CSVs you need as separate data sources (**Data > New Data Source**):
   `01_longevity_by_decade.csv`, `08_explicit_share_by_decade.csv`, `07_artist_concentration.csv`.
4. On each source, make sure `decade` is a **Dimension** shown as discrete
   (right-click > Convert to Discrete), so decades appear as labels, not a sum.

## 2. View 1: "How the sound of hits changed" (main view)

Source: `02_audio_features_by_decade.csv`.

1. Drag `decade` to **Columns**.
2. Drag `Measure Values` to **Rows**, then keep only `avg_danceability`, `avg_energy`,
   `avg_valence` and `avg_acousticness` in the Measure Values card (all are 0-1).
3. Drag `Measure Names` to **Color**. Change the mark type to **Line**.
4. Drag `songs_with_audio` and `pct_missing_audio` to **Tooltip**, so hovering shows
   how many songs each point rests on.
5. Title it: "Hits got more danceable and less acoustic, 1958-2021".

## 3. View 2: "Explicit songs by decade" or "Weeks on chart by decade"

Source: `08_explicit_share_by_decade.csv` (bar chart of `pct_explicit` by `decade`), or
`01_longevity_by_decade.csv` (bar chart of `avg_weeks_on_chart` by `decade`).
Put `songs_with_flag` or `songs` on Tooltip.

## 4. Dashboard

1. **Dashboard > New Dashboard**, size **Automatic**.
2. Drag in View 1 on top and View 2 below it.
3. Add a **Text** object with:
   "Source: Billboard Hot 100 + Spotify audio features (Kaggle, CC0), 29,383 songs,
   Aug 1958 to May 2021. Audio features are missing for 35% of 1950s, 24% of 1960s
   and 36% of 2020-21 songs."
4. **File > Save to Tableau Public**. Copy the link, open it in a private window to
   check it loads while logged out, and paste it into the README under "Dashboard".
5. Take a screenshot, save it as `docs/dashboard.png`, and reference it in the README.

## 5. Check

Pick two numbers on the dashboard (for example 1960s danceability 0.531 and 2010s
explicit share 38.3%) and confirm they match the CSVs.
