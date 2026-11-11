"""Build data/billboard.db from the raw Kaggle CSV and print a short report.

Safe to re-run: every run drops and rebuilds the tables.

Run from the project root:  python3 src/03_load_db.py
"""
from db import DB_PATH, build_database


def main() -> None:
    report = build_database()
    print(f"Built {DB_PATH}\n")
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"    {k}s: {v}%")
        else:
            print(f"{key:40s} {value:>8,}")


if __name__ == "__main__":
    main()
