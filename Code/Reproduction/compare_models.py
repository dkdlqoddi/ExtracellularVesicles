"""Compare the random forest models and the scaler in Models/ with those of another git revision.

By default the reference is 0ddfa23, the authors' last commit before the Linux re-run. Run it with
python from the pinned environment in RESULTS.md (scikit-learn 1.0.1 is needed to unpickle the
models), from anywhere in the repository:
    python Code/Reproduction/compare_models.py [--ref 0ddfa23]

For each of the six models it checks the feature order, whether all trees are identical (split
features, children, leaf values), the largest split-threshold difference and the largest difference
in predicted EV probability on the full training dataset. The exit code is 0 only if every model has
the same features and identical trees. It takes about half a minute.
"""
import argparse
import gc
import gzip
import pickle
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATASETS = {
    "no_filter": "training_data_no_filter.csv",
    "MS_filter": "training_data_MS_filter.csv",
    "MS_iso_filter": "training_data_MS_iso_filter.csv",
}


def git_blob(ref, path):
    return subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{path}"], capture_output=True, check=True).stdout


def same_trees(old, new):
    """Return (all trees identical, largest split-threshold difference)."""
    if len(old.estimators_) != len(new.estimators_):
        return False, float("nan")
    largest = 0.0
    for a, b in zip(old.estimators_, new.estimators_):
        ta, tb = a.tree_, b.tree_
        if (ta.node_count != tb.node_count
                or not np.array_equal(ta.feature, tb.feature)
                or not np.array_equal(ta.children_left, tb.children_left)
                or not np.array_equal(ta.children_right, tb.children_right)
                or not np.array_equal(ta.value, tb.value)):
            return False, float("nan")
        largest = max(largest, float(np.abs(ta.threshold - tb.threshold).max()))
    return True, largest


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ref", default="0ddfa23", help="git revision to compare with (default: 0ddfa23)")
    ref = parser.parse_args().ref
    all_same = True

    old_scaler = pickle.loads(git_blob(ref, "Models/EV_scaler_MS_iso_filter.pkl"))
    new_scaler = pickle.loads((REPO / "Models" / "EV_scaler_MS_iso_filter.pkl").read_bytes())
    same_features = list(old_scaler.feature_names_in_) == list(new_scaler.feature_names_in_)
    print(f"{'EV_scaler_MS_iso_filter.pkl':36s} same features {same_features} | "
          f"max centre diff {np.abs(old_scaler.center_ - new_scaler.center_).max():.1e} | "
          f"max scale diff {np.abs(old_scaler.scale_ - new_scaler.scale_).max():.1e}")
    all_same &= same_features

    for key, csv in DATASETS.items():
        data = pd.read_csv(REPO / "Data" / "Training" / csv)
        for suffix in ("", "_seq"):
            name = f"EV_RF_model_{key}{suffix}.pkl"
            old = pickle.loads(gzip.decompress(git_blob(ref, f"Models/{name}")))
            with gzip.open(REPO / "Models" / name, "rb") as f:
                new = pickle.load(f)
            same_features = list(old.feature_names_in_) == list(new.feature_names_in_)
            trees, threshold_diff = same_trees(old, new)
            # both models see the same (unscaled) rows, which is enough to compare them with each other
            rows = data[list(old.feature_names_in_)]
            probability_diff = np.abs(old.predict_proba(rows)[:, 1] - new.predict_proba(rows)[:, 1]).max()
            print(f"{name:36s} same features {same_features} | trees identical {trees} | "
                  f"max threshold diff {threshold_diff:.1e} | max probability diff {probability_diff:.1e}")
            all_same &= same_features and trees
            del old, new
            gc.collect()
    raise SystemExit(0 if all_same else 1)


if __name__ == "__main__":
    main()
