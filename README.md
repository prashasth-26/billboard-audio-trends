# Billboard Hot 100 + Spotify Audio Features (SQL / Tableau)

Relational database and SQL analysis of Billboard Hot 100 chart history joined
with Spotify audio features, plus Tableau views of the results.

Status: setup. The schema and queries will be written after the data has been inspected.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/00_download.py   # downloads the dataset into data/raw/
python src/01_inspect.py    # prints files, columns, null rates, date ranges
```

Kaggle dataset: `luthfimuthathohirin/billboard-hot-100-spotify-audio-features`

## Planned questions

1. How long do songs stay on the Hot 100, and has that changed across eras?
2. How concentrated is the chart in a few artists per decade?
3. Have charting songs become more danceable, louder, or more upbeat over time?
4. (Optional) Do Grammy-nominated songs chart differently from non-nominated ones?

## Layout

```
src/    download, inspection, and load scripts
sql/    schema and analysis queries (to be added)
data/   raw and derived data (git-ignored)
```
