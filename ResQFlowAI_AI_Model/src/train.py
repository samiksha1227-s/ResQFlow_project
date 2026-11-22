"""
train.py
========
Train a RandomForestClassifier on synthetic emergency data
and export the model as both .pkl and .onnx.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import os
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

DISCLAIMER = "⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_CSV = os.path.join(ROOT_DIR, "data", "synthetic_emergency_data.csv")
MODELS_DIR = os.path.join(ROOT_DIR, "models")
PKL_PATH = os.path.join(MODELS_DIR, "severity_model.pkl")
ONNX_PATH = os.path.join(MODELS_DIR, "severity_model.onnx")

# Ensure src is importable
sys.path.insert(0, SCRIPT_DIR)
from preprocessing import (
    FEATURE_COLUMNS,
    SEVERITY_CLASSES,
    extract_features,
    extract_labels,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_data_exists():
    """Auto-generate dataset if it doesn't exist yet."""
    if not os.path.exists(DATA_CSV):
        print(f"[train] Dataset not found at {DATA_CSV}")
        print("[train] Running generate_synthetic_data.py ...")
        data_script = os.path.join(ROOT_DIR, "data", "generate_synthetic_data.py")
        import subprocess
        subprocess.run([sys.executable, data_script], check=True)


def load_data():
    ensure_data_exists()
    df = pd.read_csv(DATA_CSV)
    print(f"[train] Loaded {len(df)} samples from {DATA_CSV}")
    return df


def train_model(df: pd.DataFrame):
    X = extract_features(df)
    y = extract_labels(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, zero_division=0)

    print("\n[train] Classification Report (test set):")
    print(report)

    return clf, X_test, y_test


def save_pickle(clf):
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(clf, PKL_PATH)
    print(f"[train] Model saved  → {PKL_PATH}")


def export_onnx(clf):
    """Export to ONNX if skl2onnx is available; silently skip otherwise."""
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType

        n_features = len(FEATURE_COLUMNS)
        initial_type = [("float_input", FloatTensorType([None, n_features]))]
        onnx_model = convert_sklearn(
            clf,
            initial_types=initial_type,
            target_opset=15,
        )
        os.makedirs(MODELS_DIR, exist_ok=True)
        with open(ONNX_PATH, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"[train] ONNX model saved → {ONNX_PATH}")
    except ImportError:
        warnings.warn(
            "skl2onnx not installed – skipping ONNX export. "
            "Install with: pip install skl2onnx",
            stacklevel=2,
        )
    except Exception as exc:
        warnings.warn(f"ONNX export failed: {exc}", stacklevel=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print("[train] ResQFlowAI – Severity Model Training")
    print("[train] Using RandomForestClassifier on SYNTHETIC data.\n")

    df = load_data()
    clf, X_test, y_test = train_model(df)
    save_pickle(clf)
    export_onnx(clf)

    print("\n" + "=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print("[train] Training complete.\n")


if __name__ == "__main__":
    main()
