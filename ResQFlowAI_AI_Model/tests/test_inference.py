"""
test_inference.py
=================
Integration tests for the ResQFlowAI severity inference engine.
Tests both the ML model (if available) and the rule-based engine.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import os
import sys
import unittest

DISCLAIMER = "SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE"

# Ensure src is on the path
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TESTS_DIR)
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

from rule_engine import RuleEngine
from inference import SeverityInference


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

CRITICAL_CASE = {
    "victim_count": 4,
    "has_unconscious": 1,
    "has_bleeding": 1,
    "has_breathing_difficulty": 1,
    "has_visible_injury": 1,
    "has_critical_condition": 1,
    "age_group_critical": 1,
    "vehicle_count": 3,
}

HIGH_CASE = {
    "victim_count": 3,
    "has_unconscious": 1,
    "has_bleeding": 1,
    "has_breathing_difficulty": 0,
    "has_visible_injury": 1,
    "has_critical_condition": 0,
    "age_group_critical": 0,
    "vehicle_count": 2,
}

MEDIUM_CASE = {
    "victim_count": 2,
    "has_unconscious": 0,
    "has_bleeding": 0,
    "has_breathing_difficulty": 0,
    "has_visible_injury": 1,
    "has_critical_condition": 0,
    "age_group_critical": 0,
    "vehicle_count": 1,
}

LOW_CASE = {
    "victim_count": 1,
    "has_unconscious": 0,
    "has_bleeding": 0,
    "has_breathing_difficulty": 0,
    "has_visible_injury": 0,
    "has_critical_condition": 0,
    "age_group_critical": 0,
    "vehicle_count": 1,
}


# ---------------------------------------------------------------------------
# RuleEngine Tests
# ---------------------------------------------------------------------------

class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_critical_scenario(self):
        result = self.engine.assess(CRITICAL_CASE)
        self.assertEqual(result["severity"], "CRITICAL",
                         "Expected CRITICAL for mass casualty with unconscious/critical")
        self.assertGreaterEqual(result["confidence"], 0.85)
        self.assertEqual(result["method"], "RULE_ENGINE")
        self.assertIn("disclaimer", result)
        self.assertEqual(result["disclaimer"], DISCLAIMER)

    def test_high_scenario(self):
        result = self.engine.assess(HIGH_CASE)
        self.assertIn(result["severity"], ("CRITICAL", "HIGH"),
                      "Expected at least HIGH for mass unconscious+bleeding case")
        self.assertEqual(result["method"], "RULE_ENGINE")

    def test_medium_scenario(self):
        result = self.engine.assess(MEDIUM_CASE)
        self.assertIn(result["severity"], ("MEDIUM", "HIGH"),
                      "Expected MEDIUM or above for visible injury, conscious, few victims")
        self.assertEqual(result["method"], "RULE_ENGINE")

    def test_low_scenario(self):
        result = self.engine.assess(LOW_CASE)
        self.assertEqual(result["severity"], "LOW",
                         "Expected LOW for minor incident with no indicators")
        self.assertEqual(result["method"], "RULE_ENGINE")

    def test_rules_triggered_present(self):
        result = self.engine.assess(CRITICAL_CASE)
        self.assertIn("rules_triggered", result)
        self.assertIsInstance(result["rules_triggered"], list)
        self.assertGreater(len(result["rules_triggered"]), 0)

    def test_output_fields_complete(self):
        result = self.engine.assess(LOW_CASE)
        required_fields = {"severity", "confidence", "method", "rules_triggered", "disclaimer"}
        self.assertTrue(required_fields.issubset(set(result.keys())),
                        f"Missing fields: {required_fields - set(result.keys())}")

    def test_confidence_range(self):
        for case in [CRITICAL_CASE, HIGH_CASE, MEDIUM_CASE, LOW_CASE]:
            result = self.engine.assess(case)
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)

    def test_severity_valid_value(self):
        valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for case in [CRITICAL_CASE, HIGH_CASE, MEDIUM_CASE, LOW_CASE]:
            result = self.engine.assess(case)
            self.assertIn(result["severity"], valid_severities)

    def test_string_int_booleans(self):
        """Rule engine should accept both int(0/1) and bool fields."""
        case_with_bools = {k: bool(v) for k, v in LOW_CASE.items()}
        result = self.engine.assess(case_with_bools)
        self.assertEqual(result["severity"], "LOW")


# ---------------------------------------------------------------------------
# SeverityInference Tests
# ---------------------------------------------------------------------------

class TestSeverityInference(unittest.TestCase):

    def setUp(self):
        self.engine = SeverityInference()

    def test_predict_returns_required_fields(self):
        result = self.engine.predict(LOW_CASE)
        required = {"severity", "confidence", "method", "disclaimer", "details"}
        self.assertTrue(required.issubset(set(result.keys())),
                        f"Missing fields: {required - set(result.keys())}")

    def test_disclaimer_always_present(self):
        for case in [CRITICAL_CASE, HIGH_CASE, MEDIUM_CASE, LOW_CASE]:
            result = self.engine.predict(case)
            self.assertIn("disclaimer", result)
            self.assertEqual(result["disclaimer"], DISCLAIMER)

    def test_method_is_valid(self):
        valid_methods = {"ONNX_MODEL", "ML_MODEL", "RULE_ENGINE"}
        result = self.engine.predict(LOW_CASE)
        self.assertIn(result["method"], valid_methods)

    def test_severity_valid(self):
        valid_severities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for case in [CRITICAL_CASE, HIGH_CASE, MEDIUM_CASE, LOW_CASE]:
            result = self.engine.predict(case)
            self.assertIn(result["severity"], valid_severities)

    def test_confidence_range(self):
        for case in [CRITICAL_CASE, LOW_CASE]:
            result = self.engine.predict(case)
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)

    def test_force_rule_engine(self):
        result = self.engine.rule_assess(CRITICAL_CASE)
        self.assertEqual(result["method"], "RULE_ENGINE")
        self.assertIn("severity", result)

    def test_missing_fields_default_gracefully(self):
        """Inference should handle partially specified input."""
        partial = {"victim_count": 2, "has_unconscious": 1}
        result = self.engine.predict(partial)
        self.assertIn(result["severity"], {"CRITICAL", "HIGH", "MEDIUM", "LOW"})

    def test_active_method_property(self):
        method = self.engine.active_method
        self.assertIn(method, {"ONNX_MODEL", "ML_MODEL", "RULE_ENGINE"})


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print("ResQFlowAI – Running Test Suite\n")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestRuleEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSeverityInference))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("\n" + "=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    sys.exit(0 if result.wasSuccessful() else 1)
