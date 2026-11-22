"""
preprocessing.py
================
Shared feature preprocessing utilities for ResQFlowAI severity model.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import numpy as np

DISCLAIMER = "SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE"

# Ordered feature list – order MUST match during training and inference
FEATURE_COLUMNS = [
    "victim_count",
    "has_unconscious",
    "has_bleeding",
    "has_breathing_difficulty",
    "has_visible_injury",
    "has_critical_condition",
    "age_group_critical",
    "vehicle_count",
]

LABEL_COLUMNS = ["severity_label"]

SEVERITY_CLASSES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def extract_features(df):
    """
    Extract and validate feature matrix from a pandas DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain all columns in FEATURE_COLUMNS.

    Returns
    -------
    numpy.ndarray  shape (n_samples, n_features)
    """
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    X = df[FEATURE_COLUMNS].values.astype(np.float32)
    return X


def extract_labels(df):
    """
    Extract label vector from a pandas DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    numpy.ndarray  shape (n_samples,)  dtype str
    """
    if "severity_label" not in df.columns:
        raise ValueError("Column 'severity_label' not found in DataFrame.")
    return df["severity_label"].values


def dict_to_feature_vector(victim_data: dict) -> np.ndarray:
    """
    Convert a victim data dictionary to a (1, n_features) numpy array.

    Parameters
    ----------
    victim_data : dict

    Returns
    -------
    numpy.ndarray  shape (1, n_features) dtype float32
    """
    row = []
    for col in FEATURE_COLUMNS:
        val = victim_data.get(col, 0)
        row.append(float(int(val)))
    return np.array([row], dtype=np.float32)


def validate_victim_data(victim_data: dict) -> dict:
    """
    Validate and coerce victim_data dictionary fields.

    Parameters
    ----------
    victim_data : dict

    Returns
    -------
    dict  (cleaned copy)
    """
    cleaned = {}
    bool_fields = {
        "has_unconscious",
        "has_bleeding",
        "has_breathing_difficulty",
        "has_visible_injury",
        "has_critical_condition",
        "age_group_critical",
    }
    for col in FEATURE_COLUMNS:
        val = victim_data.get(col, 0)
        if col in bool_fields:
            cleaned[col] = int(bool(int(val)))
        else:
            cleaned[col] = max(0, int(val))
    return cleaned
