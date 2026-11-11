"""Fit and evaluate the top-5 model, then print and save the results.

Compares three models on newer songs (2010-2021) after training on older ones
(1958-2009):
  - a baseline that always guesses "not top 5"
  - logistic regression (scaled features, a straight-line model)
  - random forest (many decision trees, can capture non-linear patterns)

ROC AUC is the main score: 0.5 is a coin flip, 1.0 is perfect ranking.
Accuracy is shown too, but about 90% of songs are "not top 5", so the
always-"no" baseline already gets about 90% accuracy.

Run from the project root (after src/03_load_db.py):  python3 src/05_model.py
Results are also written to docs/model_results.txt.
"""
import io
from contextlib import redirect_stdout

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from db import DB_PATH, ROOT, connect
from model import FEATURES, MODEL_QUERY, SPLIT_YEAR, TOP_N, add_target, time_split

SEED = 0


def run() -> None:
    con = connect(DB_PATH)
    df = pd.read_sql_query(MODEL_QUERY, con)
    n_songs = con.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    con.close()

    df = add_target(df.dropna(subset=FEATURES))
    train, test, n_dropped = time_split(df)
    target = "top_n_hit"

    print(f"Target: peaked at #{TOP_N} or better")
    print(f"Songs in database: {n_songs:,}; with complete audio features: {len(df):,} "
          f"({n_songs - len(df):,} excluded)")
    print(f"Train: first charted {train.first_year.min()}-{SPLIT_YEAR - 1}, "
          f"{len(train):,} songs, {train[target].mean():.1%} top {TOP_N}")
    print(f"Test:  first charted {SPLIT_YEAR}-{test.first_year.max()}, "
          f"{len(test):,} songs, {test[target].mean():.1%} top {TOP_N} "
          f"({n_dropped} still-charting songs left out)\n")

    models = {
        "Baseline (always 'no')": DummyClassifier(strategy="most_frequent"),
        "Logistic regression": make_pipeline(
            StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=1000)),
        "Random forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=20, class_weight="balanced",
            random_state=SEED, n_jobs=-1),
    }

    X_train, y_train = train[FEATURES], train[target]
    X_test, y_test = test[FEATURES], test[target]

    print(f"{'Model':26s} {'Accuracy':>9s} {'ROC AUC':>8s}")
    for name, model in models.items():
        model.fit(X_train, y_train)
        acc = accuracy_score(y_test, model.predict(X_test))
        auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
        print(f"{name:26s} {acc:9.3f} {auc:8.3f}")
    print("(The two real models are trained to weigh top-5 songs more heavily, so they\n"
          " flag more songs as hits and score lower accuracy than the baseline by design.)\n")

    logit = models["Logistic regression"][-1]
    coefs = pd.Series(logit.coef_[0], index=FEATURES).sort_values(key=abs, ascending=False)
    print("Logistic regression coefficients (per 1 standard deviation; + = more likely top 5):")
    for f, c in coefs.items():
        print(f"  {f:18s} {c:+.3f}")

    print("\nPermutation importance on the test set (drop in ROC AUC when a feature is shuffled):")
    for name in ("Logistic regression", "Random forest"):
        imp = permutation_importance(models[name], X_test, y_test, scoring="roc_auc",
                                     n_repeats=10, random_state=SEED, n_jobs=-1)
        s = pd.Series(imp.importances_mean, index=FEATURES).sort_values(ascending=False)
        print(f"  {name}: " + ", ".join(f"{f} {v:+.3f}" for f, v in s.head(5).items()))

    print("\nThese are associations among songs that charted, not causes, and not a way to\n"
          "pick hits from all released music.")


def main() -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        run()
    text = buf.getvalue()
    print(text)
    out = ROOT / "docs" / "model_results.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    print(f"Saved to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
