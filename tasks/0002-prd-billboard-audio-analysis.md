# PRD: Billboard Hot 100 + Spotify Audio Features Analysis

## 1. Introduction / Overview

This project loads a Kaggle dataset that combines per-song Billboard Hot 100 chart summaries (peak position, weeks on chart) with Spotify audio features into a small SQL database, answers a set of questions about how charting songs have changed over time using SQL, visualizes the results in Tableau, and fits a simple model to see which audio features are associated with a song reaching a high chart position.

**Primary goal:** A small, finishable portfolio project that demonstrates SQL (joins, CTEs, window functions), a relational schema, automated tests (pytest), a Tableau dashboard, and a simple, honestly-evaluated prediction model, with a README an interviewer can read in a few minutes.

**Secondary goal:** Connect the analysis to the author's interest in how people respond to music (a cognitive-science angle), without making claims the data cannot support.

**Source dataset:** Kaggle, `luthfimuthathohirin/billboard-hot-100-spotify-audio-features`. Inspected on 2026-11-09 with `src/01_inspect.py`. Findings:

- One file, `billboard_hot_100_spotify_audio_features_enriched.csv`: 32,503 rows x 33 columns, **one row per song**, not per chart week.
- **The last 3,000 rows (file rows 29,504-32,503) are unreliable and are excluded.** The dataset's version 3 note (October 2026) says it grew from 29,503 to 32,503 rows by adding chart issues from 2021-06-05 to 2026-10-23, which matches the cut: 29,500 real-looking rows plus the 3 corrupted ones are the earlier 29,503. The added rows fail checks the earlier rows pass (found with `src/02b_check_duplicates.py`): (1) Billboard issue dates are Saturdays (charts are published on Tuesdays but dated the Saturday of the issue); all 29,500 earlier rows start on a Saturday, the added rows on all seven weekdays (about 14% each); (2) many titles carry labels such as "Kill Bill (Version 1057)"; (3) some songs appear twice with conflicting peaks and dates ("Deja Vu" at #8 in 2021 and #1 in 2024), and all 20 shared IDs whose chart fields differed pair a real row with an added one; (4) none is missing audio features, against 17.5% of the earlier rows; (5) 28% reach the top 5, against 10%. It is not known whether the rows were generated or real data scrambled during assembly. The project uses the 29,500 earlier rows, covering chart weeks from 1958-08-02 to 2021-05-29. The README must say so.
- **There is no weekly chart history.** Chart information is limited to `peak_position`, `weeks_on_chart`, `first_week` and `last_week`.
- 3 rows (file rows 29,501-29,503) have no chart data and look corrupted: one has a song title stored as the number 37623 (a date conversion of "1/2/03"), one has a performer recorded as "4", and one has a garbled character in its ID. They are dropped.
- Figures below are for the 29,500 kept rows.
- `song_id` is the song title and performer joined with no separator, and it is not unique: 117 IDs are shared by 234 rows (every shared ID has exactly 2 rows). 24 pairs are identical in every column; 93 pairs have identical chart fields and differ only in Spotify or generated columns (usually `spotify_track_popularity`). No pair differs in chart fields.
- 5,167 rows (17.5%) have no Spotify audio features. By decade of `first_week`: 1950s 34.6% (of 926), 1960s 23.8% (6,852), 1970s 20.6% (5,299), 1980s 14.8% (4,114), 1990s 18.1% (3,423), 2000s 8.6% (3,419), 2010s 6.0% (4,552), 2020-21 36.4% (915).
- The final chart week is 2021-05-29 (a Saturday). 99 songs have that `last_week`, close to the 100 songs on one Hot 100 chart, so they are the songs still charting when the data ends; their `weeks_on_chart` is incomplete (right-censored). Within 14, 28 and 56 days of it: 131, 154 and 205 songs.
- `weeks_on_chart` counts weeks charted, not the span between `first_week` and `last_week`: seasonal songs return year after year (for example "A Holly Jolly Christmas" has 19 weeks across a four-year span).
- **`weeks_on_chart` checked against Billboard:** "Radioactive" has 87 weeks in the file and 87 on Billboard; "Blinding Lights" has 76, which is right for the data's end date of 2021-05-29 (it debuted 2019-12-14 and missed one chart week, reaching 88 weeks on the chart dated 2021-08-21). The data card's 88 refers to a later date. The column is treated as accurate up to 2021-05-29.
- `spotify_genre` is a list stored as text (for example `['pop', 'dance pop']`); some are null.
- Seven columns appear to be generated from the other columns rather than observed: `chart_success_tier`, `hit_longevity_profile`, `acoustic_mood_cluster`, `musical_era`, `evidence_span`, `cot_rationale` and `confidence_score`. The two text columns restate the numeric columns in templated sentences. The Kaggle data card describes them as enrichment labels, with "Chain-of-Thought" rationale text and a "Bayesian" confidence score. They are derived from the chart and audio columns, not independent measurements; they are not loaded, not used as model inputs and not treated as evidence.
- `spotify_track_popularity` is a 0-100 Spotify score that depends on when the data was pulled and may reflect a song's chart success and recency. It is excluded from model inputs.
- **License:** CC0 Public Domain, per the Kaggle page (checked 2026-11-09).
- **Peak position:** 1,133 songs peaked at #1 (3.8%), 3,042 at #5 or better (10.3%), 5,019 at #10 or better (17.0%), 8,008 at #20 or better (27.1%). These counts include both rows of each shared ID; the loader's counts after removing duplicates are reported in the README.

**Who uses it:** The author (to learn and to put on a resume), and recruiters or interviewers reading the repository, queries, README and dashboard.

**Scope note:** The author wants this finished in roughly a weekend. Requirements are therefore labeled **Must**, **Should** or **Could**. If time runs short, cut from the bottom (Could, then Should). The prediction model is Could-level work and must not delay the Must items.

## 2. Git Worktree and Git Branch Name

- **Worktree name:** `billboard-audio-analysis-wt`
- **Branch name:** `feature/billboard-audio-analysis`

(A git worktree is a second working folder attached to the same repository and checked out on its own branch.)

## 3. Goals

1. Load the dataset into a documented relational schema in a local SQL database.
2. Answer at least three questions about chart history and audio features using SQL, with at least 8 documented queries in total using joins, CTEs and window functions (including `LAG` and `RANK`).
3. Verify data loading and query logic with pytest.
4. Produce a Tableau Public dashboard with 1-3 views from exported aggregate results.
5. Fit a simple, honestly-evaluated model relating audio features to peak chart position, and report what it can and cannot show.
6. Publish a public GitHub repository with a README covering question, method, results and limitations.

## 4. User Stories

- As the **author**, I want one command to download and load the data, so that I can rebuild the database from scratch at any time.
- As the **author**, I want each analysis question answered by a named SQL file with a comment explaining it, so that I can explain every query in an interview.
- As a **recruiter**, I want a README that states the questions, the method, the findings and the limitations, so that I can judge the work in a few minutes.
- As an **interviewer**, I want to read the SQL and tests, so that I can check the author understands them.
- As a **viewer of the dashboard**, I want to see how chart longevity and audio features changed by decade, so that I get the main findings without running any code.

## 5. Functional Requirements

### Setup and inspection (Must)

1. The repository must contain `src/00_download.py`, which downloads the dataset with `kagglehub` into `data/raw/`. (Already created.)
2. The repository must contain `src/01_inspect.py`, which prints each file's rows, columns, types, null rates, distinct counts, sample rows and date ranges. (Already created.)
3. Inspection is complete (Section 1). The README must record those findings. No requirement may assume a column name the inspection did not confirm.
4. Inspection showed there is no weekly chart history. Requirements that needed it (a weekly chart table, week-over-week rank movement) have been replaced as noted below, and the README must state this limitation.

### Schema and loading (Must)

5. The system must load the data into a SQLite database file at `data/billboard.db` (see Technical Considerations for why SQLite).
6. The schema must be defined in `sql/schema.sql`, with primary keys and foreign keys. The source is one flat table, so the schema is built by splitting it. Working proposal: `songs` (ID, title, performer, peak position, weeks on chart, first and last week, still-charting flag), `audio_features` (one row per song that has Spotify data), `song_genres` (one row per song-genre pair, built by parsing the text list in `spotify_genre`), and optionally `artists` (primary artist parsed from `performer`). The genre split is the clearest reason to normalize, because it is a real one-to-many relationship. The choice must be explained in the README.
7. Loading must be safe to re-run: running it twice must not create duplicate rows.
8. The loader must report: row counts per table, and the count of songs with no audio features.
   - 8a. Before anything else, the loader must keep only rows whose `last_week` is on or before 2021-05-29, which drops the 3,000 unreliable rows (Section 1). It must then keep one row per `song_id`: of the 117 shared IDs, 24 pairs are identical, and 93 differ only in Spotify or generated columns; for those it keeps the row that has audio features, and otherwise the first row in file order. The README must state these counts and the rule.
   - Because `song_id` is not unique and joins title to performer without a separator, the loader must create its own integer key.
   - 8b. The loader must drop the 3 corrupted rows with no chart data, and the README must say so.
   - 8c. The loader must add a `still_charting` flag: a song is flagged if its `last_week` equals the final chart week, 2021-05-29 (99 songs). The README must report this count.

### Analysis questions (Must unless marked)

9. **Chart longevity (Must).** Use the provided `weeks_on_chart` (weeks charted, not the span between first and last week) and summarize by decade of `first_week`. Songs still charting at the end of the data have incomplete counts and must be flagged or excluded, with the choice stated.
10. **Chart concentration (Should).** For each decade, compute the share of songs (or of total weeks on chart) held by the top 10 primary artists. This needs a primary artist parsed from `performer`, which lists collaborations as free text (for example "X Featuring Y"). The parsing rule must be documented and its limits stated.
11. **Audio features over time (Must).** Compute the average of each Spotify audio feature (danceability, energy, loudness, valence, acousticness, speechiness, tempo and so on) by decade of `first_week`, using only songs that have audio features, and report the share of songs missing features in each decade. Missing features are concentrated in older decades (Section 1), so early-decade averages rest on fewer and possibly unrepresentative songs; say so wherever they are shown.
12. **Features and chart peak (Must for the SQL half).** Compare average audio features of songs that reached #1 or the top 10 against songs whose peak was lower.
13. The `sql/` folder must contain at least 8 queries, each in its own file with a short comment on what it finds. Collectively they must use joins, CTEs, and window functions including `LAG` and `RANK`. Because there is no weekly data, `LAG` is applied to ordered yearly or decade aggregates (for example year-over-year change in average danceability), not to weekly ranks.
14. Any decade-level result must also report how many songs it is based on, so thin groups are visible.

### Testing (Must)

15. The project must include pytest tests covering: the loader (row counts, no duplicate primary keys, no orphaned foreign keys), idempotent re-loading, and each analysis query against a small hand-built fixture where the correct answer is known in advance.
16. Tests must run with a single command (`pytest`) and pass on a fresh checkout after setup.

### Visualization (Should)

17. Each analysis query that feeds the dashboard must export its result to CSV in `data/exports/`.
18. A Tableau Public workbook with 1-3 views must be built from those CSVs. The README must link to it. Tableau Public connects to files rather than databases, so the CSV export is required, not optional.
19. If time runs short, one good view is acceptable; skipping Tableau is acceptable only if the README states so.

### Prediction model (Could)

20. Define the prediction target from `peak_position`, for example "reached the top 10" versus "peaked lower". The threshold is the top 5 (about 10% of songs; chosen by the author); it must be a named constant, and the class balance must be reported. Because roughly 90% of songs fall in the "peaked lower" class, a model that always guesses "lower" is right about 90% of the time, so ROC AUC is the main metric and accuracy is secondary.
21. Fit a baseline logistic regression and one tree-based model (random forest or gradient boosting) using only the Spotify audio features (danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time signature) and, optionally, duration and the explicit flag. The model must NOT use `chart_success_tier`, `hit_longevity_profile`, `acoustic_mood_cluster`, `musical_era`, `evidence_span`, `cot_rationale`, `confidence_score`, `spotify_track_popularity`, `weeks_on_chart`, or any other column derived from chart results, because they leak the outcome. Rows without audio features are excluded and the count reported.
22. Split train and test sets **by time** (older songs train, newer songs test), not randomly, so the test reflects predicting newer songs. Because the newest songs may still be on the chart, their peak positions can still change; the README must state how songs still charting at the end of the data were handled (for example, excluded from the test set).
23. Report accuracy alongside a baseline that always predicts the majority class, plus ROC AUC. A model that does not beat the majority-class baseline must be reported as such.
24. Report which features matter most (logistic coefficients and permutation importance), described as association, not cause.
25. The README must state the key limitation: the dataset contains only songs that charted, so the model compares higher-charting songs with lower-charting songs, not hits with non-hits.

### Repository (Must)

26. `requirements.txt` must pin library versions once the code works.
27. The README must cover question, method, results, limitations, and setup steps.
28. `data/` must stay in `.gitignore`. Raw data is not committed.

## 6. Non-Goals (Out of Scope)

- No Grammy data or Grammy-based analysis in this version (see Open Question 2).
- No lyrics, no audio processing, no calls to the Spotify API.
- No use of the generated text columns (`evidence_span`, `cot_rationale`) as evidence; they are not independent observations.
- No causal claims about why songs succeed.
- No web app, dashboard hosting beyond Tableau Public, or user accounts.
- No deep learning or hyperparameter-tuning marathon; the model is a baseline comparison.
- No claim that the model can predict future hits.

## 7. Design Considerations

- Every finding in the README or dashboard must show how many songs it rests on.
- Query comments and README text should use plain language (for example "weeks on chart"), not database jargon.
- The dashboard should lead with the clearest finding, not the most complex chart.

## 8. Technical Considerations

- **Language and libraries:** Python, pandas, SQLite (via Python's built-in `sqlite3`), scikit-learn for the model, pytest, Tableau Public.
- **Why SQLite (decided):** It needs no server, runs on any machine, and supports CTEs and window functions (`LAG`, `RANK`) since version 3.25, so it covers every keyword this project needs. SQLite is not the most common database in job listings (PostgreSQL, MySQL and SQL Server are), but most postings ask for "SQL" in general, and the queries here will be written in standard SQL that also runs on PostgreSQL. The README and resume should say "SQL (SQLite)" and not claim PostgreSQL experience. PostgreSQL would add installation work that conflicts with the weekend budget. DuckDB was used in PRD 0001 and also works, but is less commonly listed by employers.
- **Schema considerations:** The source is one flat table. Splitting it (songs, audio features, song genres, optionally artists) lets you demonstrate joins and keys, and the genre list is a genuine one-to-many relationship. The cost is extra loading code, and artist names are free text (collaborations are written out in one string) that needs cleaning to make clean keys. Keeping a single table is faster but shows less.
- **Missing audio features:** About 17.5% of songs have no audio features. The loader must report coverage by decade, and the README must state this.
- **Repository layout:** `src/` (scripts), `sql/` (schema and queries), `tests/`, `data/` (git-ignored), `tasks/` (PRD and task list), `README.md`.
- **Authorship:** The analysis questions, SQL queries and model choices must be explainable by the author. Scaffolding (repo layout, loader, test setup, README skeleton) may be generated.
- **Licensing:** The Kaggle page lists the license as CC0 Public Domain. The repository still does not include the raw data; the README links to the Kaggle page.

## 9. Success Metrics

1. `python3 src/00_download.py` followed by the loader builds the database from scratch without errors.
2. At least 8 documented SQL queries exist using joins, CTEs and window functions.
3. `pytest` passes on a fresh checkout.
4. The README states the match rate between chart songs and audio features, and every decade-level finding shows its sample size.
5. A Tableau Public view is live and linked (or the README states it was skipped).
6. If the model is built, it is compared against the majority-class baseline using a time-based split, and the README states the limitation in requirement 25.
7. The repository is public with a README and the raw data excluded.

## 10. Open Questions

1. **Dataset contents:** Answered; see Section 1, including the 3,000 unreliable rows and the duplicate groups.
2. **Grammys:** The author leaned toward leaving them out. Revisit only if the core work finishes early and a clean Grammy dataset is found.
3. **Schema:** Decided: split the flat table into songs, audio features and song genres (requirement 6), with the artists table optional. The author deferred to the recommendation.
4. **Database:** Decided: SQLite (see Section 8).
5. **Model target:** Decided: top 5 (about 10% of songs after the unreliable rows are removed), chosen by the author.
6. **Dataset license:** Resolved: CC0 Public Domain. Credit the source in the README anyway.
7. **Scope:** If the weekend runs out, the working plan is to drop the model first, then Tableau, and keep SQL, tests and README.
8. **`weeks_on_chart` accuracy:** Resolved: matches Billboard for the songs checked, as of 2021-05-29 (Section 1).
