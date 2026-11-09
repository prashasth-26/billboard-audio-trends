"""Download the Billboard Hot 100 + Spotify audio features dataset into data/raw/.

Run from the project root:  python src/00_download.py
"""
import shutil
from pathlib import Path

import kagglehub

SLUG = "luthfimuthathohirin/billboard-hot-100-spotify-audio-features"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main() -> None:
    cache_path = Path(kagglehub.dataset_download(SLUG))
    print(f"kagglehub cache: {cache_path}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for f in cache_path.rglob("*"):
        if f.is_file():
            dest = RAW_DIR / f.relative_to(cache_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            print(f"copied {f.name} -> {dest}")


if __name__ == "__main__":
    main()
