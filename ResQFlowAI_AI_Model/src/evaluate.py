"""
evaluate.py
===========
Load the trained severity model and evaluate it on the test split.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DISCLAIMER = "⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_CSV = os.path.join(ROOT_DIR, "data", "synthetic_emergency_data.csv")
PKL_PATH = os.path.join(ROOT_DIR, "models", "severity_model.pkl")
ONNX_PATH = os.path.join(ROOT_DIR, "models", "severity_model.onnx")

sys.path.insert(0, SCRIPT_DIR)
from preprocessing import extract_features, extract_labels, SEVERITY_CLASSES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_model_pkl():
    if not os.path.exists(PKL_PATH):
        raise FileNotFoundError(
            f"Model not found at {PKL_PATH}. Run train.py first."
        )
    return joblib.load(PKL_PATH)


def load_data():
    if not os.path.exists(DATA_CSV):
        raise FileNotFoundError(
            f"Dataset not found at {DATA_CSV}. Run generate_synthetic_data.py first."
        )
    return pd.read_csv(DATA_CSV)


def print_separator(char="=", width=60):
    print(char * width)


def evaluate_sklearn(clf, X_test, y_test):
    y_pred = clf.predict(X_test)
    proba = clf.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=clf.classes_)

    print("\n[evaluate] ── Scikit-Learn Model ──")
    print(f"Accuracy : {acc:.4f}")
    print("\nClassification Report:")
    print(report)
    print("Confusion Matrix (rows=actual, cols=predicted):")
    print(f"{'':10s}", end="")
    for cls in clf.classes_:
        print(f"{cls:>10s}", end="")
    print()
    for i, row_label in enumerate(clf.classes_):
        print(f"{row_label:10s}", end="")
        for val in cm[i]:
            print(f"{val:>10d}", end="")
        print()
    return acc


def evaluate_onnx(X_test, y_test):
    """Evaluate using the ONNX Runtime if model and library are available."""
    if not os.path.exists(ONNX_PATH):
        print("\n[evaluate] ONNX model not found – skipping ONNX evaluation.")
        return

    try:
        import onnxruntime as rt

        sess = rt.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        proba_name = sess.get_outputs()[1].name

        pred_labels_raw = sess.run([label_name], {input_name: X_test.astype(np.float32)})[0]
        # onnx may return bytes
        y_pred_onnx = [
            p.decode() if isinstance(p, bytes) else str(p) for p in pred_labels_raw
        ]

        acc = accuracy_score(y_test, y_pred_onnx)
        report = classification_report(y_test, y_pred_onnx, zero_division=0)

        print("\n[evaluate] ── ONNX Runtime Model ──")
        print(f"Accuracy : {acc:.4f}")
        print("\nClassification Report:")
        print(report)

    except ImportError:
        print("\n[evaluate] onnxruntime not installed – skipping ONNX evaluation.")
    except Exception as exc:
        print(f"\n[evaluate] ONNX evaluation error: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print_separator()
    print(DISCLAIMER)
    print_separator()
    print("[evaluate] ResQFlowAI – Model Evaluation\n")

    df = load_data()
    X = extract_features(df)
    y = extract_labels(df)

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = load_model_pkl()
    evaluate_sklearn(clf, X_test, y_test)
    evaluate_onnx(X_test, y_test)

    print()
    print_separator()
    print(DISCLAIMER)
    print_separator()


if __name__ == "__main__":
    main()
