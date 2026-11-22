"""
inference.py
============
Python inference wrapper for the ResQFlowAI severity model.
Falls back gracefully to the rule engine if the ML model is unavailable.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import os
import sys
import warnings

import numpy as np

DISCLAIMER = "SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PKL_PATH = os.path.join(ROOT_DIR, "models", "severity_model.pkl")
ONNX_PATH = os.path.join(ROOT_DIR, "models", "severity_model.onnx")

sys.path.insert(0, SCRIPT_DIR)
from preprocessing import dict_to_feature_vector, validate_victim_data
from rule_engine import RuleEngine


class SeverityInference:
    """
    Unified severity inference interface for ResQFlowAI.

    Priority order:
        1. ONNX Runtime (fastest, portable)
        2. Scikit-Learn pickle (fallback)
        3. Rule Engine (no-ML fallback)

    All outputs include a mandatory disclaimer field.

    Parameters
    ----------
    prefer_onnx : bool
        Prefer ONNX model over sklearn pickle when both exist. Default True.

    Example
    -------
    >>> engine = SeverityInference()
    >>> result = engine.predict({
    ...     "victim_count": 3,
    ...     "has_unconscious": 1,
    ...     "has_bleeding": 1,
    ...     "has_breathing_difficulty": 0,
    ...     "has_visible_injury": 1,
    ...     "has_critical_condition": 0,
    ...     "age_group_critical": 0,
    ...     "vehicle_count": 2,
    ... })
    >>> print(result["severity"], result["method"])
    """

    def __init__(self, prefer_onnx: bool = True):
        self._rule_engine = RuleEngine()
        self._clf = None            # sklearn model
        self._onnx_sess = None      # onnxruntime.InferenceSession
        self._method = "RULE_ENGINE"

        self._load_models(prefer_onnx)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, victim_data: dict) -> dict:
        """
        Predict emergency severity for a single incident.

        Parameters
        ----------
        victim_data : dict
            victim_count, has_unconscious, has_bleeding,
            has_breathing_difficulty, has_visible_injury,
            has_critical_condition, age_group_critical, vehicle_count

        Returns
        -------
        dict
            {
                severity   : str   (CRITICAL / HIGH / MEDIUM / LOW),
                confidence : float (0.0 – 1.0),
                method     : str   ('ONNX_MODEL' | 'ML_MODEL' | 'RULE_ENGINE'),
                disclaimer : str,
                details    : dict  (label probabilities or rules triggered)
            }
        """
        cleaned = validate_victim_data(victim_data)

        if self._onnx_sess is not None:
            return self._predict_onnx(cleaned)
        elif self._clf is not None:
            return self._predict_sklearn(cleaned)
        else:
            return self._predict_rules(cleaned)

    @property
    def active_method(self) -> str:
        """Returns the currently active inference method name."""
        return self._method

    def rule_assess(self, victim_data: dict) -> dict:
        """
        Force rule-engine assessment regardless of model availability.

        Useful for cross-checking or when transparency is required.
        """
        cleaned = validate_victim_data(victim_data)
        return self._predict_rules(cleaned)

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_models(self, prefer_onnx: bool):
        """Load best available model, silently downgrading as needed."""

        # Try ONNX first
        if prefer_onnx and os.path.exists(ONNX_PATH):
            self._onnx_sess = self._try_load_onnx()
            if self._onnx_sess is not None:
                self._method = "ONNX_MODEL"
                return

        # Try sklearn pickle
        if os.path.exists(PKL_PATH):
            self._clf = self._try_load_pkl()
            if self._clf is not None:
                self._method = "ML_MODEL"
                return

        # Pure rule engine
        self._method = "RULE_ENGINE"
        warnings.warn(
            "No trained model found. Falling back to RuleEngine.\n"
            "Run src/train.py to generate a model.",
            stacklevel=2,
        )

    def _try_load_onnx(self):
        try:
            import onnxruntime as rt
            sess = rt.InferenceSession(ONNX_PATH, providers=["CPUExecutionProvider"])
            return sess
        except ImportError:
            return None
        except Exception as exc:
            warnings.warn(f"ONNX load failed: {exc}", stacklevel=3)
            return None

    def _try_load_pkl(self):
        try:
            import joblib
            return joblib.load(PKL_PATH)
        except Exception as exc:
            warnings.warn(f"Pickle load failed: {exc}", stacklevel=3)
            return None

    # ------------------------------------------------------------------
    # Inference backends
    # ------------------------------------------------------------------

    def _predict_onnx(self, cleaned: dict) -> dict:
        X = dict_to_feature_vector(cleaned)
        input_name = self._onnx_sess.get_inputs()[0].name
        label_name = self._onnx_sess.get_outputs()[0].name
        proba_name = self._onnx_sess.get_outputs()[1].name

        try:
            labels_raw, proba_raw = self._onnx_sess.run(
                [label_name, proba_name], {input_name: X}
            )
            severity = labels_raw[0]
            if isinstance(severity, bytes):
                severity = severity.decode()
            severity = str(severity)

            # proba_raw is a list of dicts from onnx
            if isinstance(proba_raw, list) and isinstance(proba_raw[0], dict):
                proba_dict = {
                    k.decode() if isinstance(k, bytes) else str(k): float(v)
                    for k, v in proba_raw[0].items()
                }
            else:
                proba_dict = {}

            confidence = float(proba_dict.get(severity, 0.0))

            return {
                "severity": severity,
                "confidence": round(confidence, 4),
                "method": "ONNX_MODEL",
                "disclaimer": DISCLAIMER,
                "details": {"class_probabilities": proba_dict},
            }
        except Exception as exc:
            warnings.warn(f"ONNX inference failed ({exc}), falling back.", stacklevel=2)
            self._onnx_sess = None
            return self._predict_sklearn(cleaned) if self._clf else self._predict_rules(cleaned)

    def _predict_sklearn(self, cleaned: dict) -> dict:
        X = dict_to_feature_vector(cleaned)
        severity = self._clf.predict(X)[0]
        proba = self._clf.predict_proba(X)[0]
        classes = list(self._clf.classes_)
        proba_dict = {cls: round(float(p), 4) for cls, p in zip(classes, proba)}
        confidence = proba_dict.get(severity, 0.0)

        return {
            "severity": str(severity),
            "confidence": round(confidence, 4),
            "method": "ML_MODEL",
            "disclaimer": DISCLAIMER,
            "details": {"class_probabilities": proba_dict},
        }

    def _predict_rules(self, cleaned: dict) -> dict:
        result = self._rule_engine.assess(cleaned)
        return {
            "severity": result["severity"],
            "confidence": result["confidence"],
            "method": "RULE_ENGINE",
            "disclaimer": DISCLAIMER,
            "details": {"rules_triggered": result["rules_triggered"]},
        }


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print("SeverityInference – Quick Demo\n")

    engine = SeverityInference()
    print(f"Active method: {engine.active_method}\n")

    scenarios = [
        {
            "desc": "Critical mass casualty",
            "data": {
                "victim_count": 5, "has_unconscious": 1, "has_bleeding": 1,
                "has_breathing_difficulty": 1, "has_visible_injury": 1,
                "has_critical_condition": 1, "age_group_critical": 1, "vehicle_count": 3,
            },
        },
        {
            "desc": "Minor fender-bender",
            "data": {
                "victim_count": 1, "has_unconscious": 0, "has_bleeding": 0,
                "has_breathing_difficulty": 0, "has_visible_injury": 0,
                "has_critical_condition": 0, "age_group_critical": 0, "vehicle_count": 1,
            },
        },
    ]

    for scenario in scenarios:
        result = engine.predict(scenario["data"])
        print(f"Scenario  : {scenario['desc']}")
        print(f"  Severity  : {result['severity']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Method    : {result['method']}")
        print(f"  Disclaimer: {result['disclaimer']}")
        print()
