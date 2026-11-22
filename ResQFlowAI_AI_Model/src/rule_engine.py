"""
rule_engine.py
==============
Pure rule-based emergency severity assessment.
No machine-learning dependencies required.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
This engine uses simplified heuristic rules for hackathon demonstration only.
It is NOT a medical diagnosis or triage tool.
"""

DISCLAIMER = "SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE"


class RuleEngine:
    """
    Deterministic rule-based severity assessor.

    All rules and confidence scores are illustrative heuristics created
    for the ResQFlowAI hackathon demo.  They do NOT constitute medical advice.

    Methods
    -------
    assess(victim_data: dict) -> dict
        Evaluate severity from victim data fields.
    """

    # Rule definitions: (name, severity, confidence, condition_fn)
    RULES = []

    def __init__(self):
        self._build_rules()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess(self, victim_data: dict) -> dict:
        """
        Assess emergency severity using rule-based logic.

        Parameters
        ----------
        victim_data : dict
            Keys:
                victim_count            (int)
                has_unconscious         (bool / int)
                has_bleeding            (bool / int)
                has_breathing_difficulty(bool / int)
                has_visible_injury      (bool / int)
                has_critical_condition  (bool / int)
                age_group_critical      (bool / int)
                vehicle_count           (int)

        Returns
        -------
        dict
            {
                severity        : str   (CRITICAL / HIGH / MEDIUM / LOW),
                confidence      : float (0-1),
                method          : str   ('RULE_ENGINE'),
                rules_triggered : list  of rule names,
                disclaimer      : str
            }
        """
        d = self._normalise(victim_data)
        triggered = []
        severity = "LOW"
        confidence = 0.60

        for rule_name, rule_severity, rule_confidence, condition_fn in self.RULES:
            if condition_fn(d):
                triggered.append(rule_name)
                # Escalate only (never downgrade)
                if self._severity_rank(rule_severity) > self._severity_rank(severity):
                    severity = rule_severity
                    confidence = rule_confidence
                elif rule_severity == severity and rule_confidence > confidence:
                    confidence = rule_confidence

        # Age-group modifier: slight confidence boost when vulnerable population
        if d["age_group_critical"] and severity in ("HIGH", "CRITICAL"):
            confidence = min(confidence + 0.03, 0.99)
            triggered.append("AGE_GROUP_MODIFIER")

        return {
            "severity": severity,
            "confidence": round(confidence, 4),
            "method": "RULE_ENGINE",
            "rules_triggered": triggered if triggered else ["DEFAULT_LOW"],
            "disclaimer": DISCLAIMER,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_rules(self):
        """Populate the RULES list with (name, severity, confidence, fn) tuples."""
        self.RULES = [
            # ── CRITICAL rules ─────────────────────────────────────────
            (
                "CRIT_UNCONSCIOUS_BREATH_CRITICAL",
                "CRITICAL",
                0.95,
                lambda d: d["has_unconscious"]
                and d["has_breathing_difficulty"]
                and d["has_critical_condition"],
            ),
            (
                "CRIT_MASS_CASUALTY_UNCONSCIOUS_BLEEDING",
                "CRITICAL",
                0.90,
                lambda d: d["victim_count"] >= 3
                and d["has_unconscious"]
                and d["has_bleeding"],
            ),
            (
                "CRIT_UNCONSCIOUS_CRITICAL_CONDITION",
                "CRITICAL",
                0.88,
                lambda d: d["has_unconscious"] and d["has_critical_condition"],
            ),
            # ── HIGH rules ─────────────────────────────────────────────
            (
                "HIGH_UNCONSCIOUS",
                "HIGH",
                0.85,
                lambda d: d["has_unconscious"],
            ),
            (
                "HIGH_BLEEDING_BREATHING",
                "HIGH",
                0.85,
                lambda d: d["has_bleeding"] and d["has_breathing_difficulty"],
            ),
            (
                "HIGH_MASS_VISIBLE_INJURY",
                "HIGH",
                0.80,
                lambda d: d["victim_count"] >= 3 and d["has_visible_injury"],
            ),
            (
                "HIGH_CRITICAL_CONDITION",
                "HIGH",
                0.82,
                lambda d: d["has_critical_condition"],
            ),
            # ── MEDIUM rules ───────────────────────────────────────────
            (
                "MED_VISIBLE_INJURY_CONSCIOUS_FEW",
                "MEDIUM",
                0.75,
                lambda d: d["has_visible_injury"]
                and not d["has_unconscious"]
                and d["victim_count"] <= 2,
            ),
            (
                "MED_BLEEDING_CONSCIOUS",
                "MEDIUM",
                0.72,
                lambda d: d["has_bleeding"]
                and not d["has_unconscious"]
                and not d["has_breathing_difficulty"],
            ),
            (
                "MED_MULTIPLE_VICTIMS_NO_CRITICAL",
                "MEDIUM",
                0.70,
                lambda d: d["victim_count"] >= 2
                and not d["has_unconscious"]
                and not d["has_critical_condition"],
            ),
        ]

    @staticmethod
    def _normalise(victim_data: dict) -> dict:
        """Normalise boolean fields to Python bool."""
        bool_fields = [
            "has_unconscious",
            "has_bleeding",
            "has_breathing_difficulty",
            "has_visible_injury",
            "has_critical_condition",
            "age_group_critical",
        ]
        d = dict(victim_data)
        for field in bool_fields:
            d[field] = bool(int(d.get(field, 0)))
        d["victim_count"] = int(d.get("victim_count", 1))
        d["vehicle_count"] = int(d.get("vehicle_count", 1))
        return d

    @staticmethod
    def _severity_rank(severity: str) -> int:
        return {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(severity, 0)


# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    engine = RuleEngine()

    test_cases = [
        {
            "label": "Mass casualty with unconscious",
            "data": {
                "victim_count": 4,
                "has_unconscious": 1,
                "has_bleeding": 1,
                "has_breathing_difficulty": 0,
                "has_visible_injury": 1,
                "has_critical_condition": 0,
                "age_group_critical": 0,
                "vehicle_count": 2,
            },
        },
        {
            "label": "Minor fender-bender",
            "data": {
                "victim_count": 1,
                "has_unconscious": 0,
                "has_bleeding": 0,
                "has_breathing_difficulty": 0,
                "has_visible_injury": 0,
                "has_critical_condition": 0,
                "age_group_critical": 0,
                "vehicle_count": 1,
            },
        },
        {
            "label": "Unconscious + breathing difficulty",
            "data": {
                "victim_count": 2,
                "has_unconscious": 1,
                "has_bleeding": 0,
                "has_breathing_difficulty": 1,
                "has_visible_injury": 1,
                "has_critical_condition": 1,
                "age_group_critical": 1,
                "vehicle_count": 1,
            },
        },
    ]

    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print("RuleEngine – Quick Test\n")
    for case in test_cases:
        result = engine.assess(case["data"])
        print(f"Scenario : {case['label']}")
        print(f"  Severity  : {result['severity']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Rules     : {result['rules_triggered']}")
        print()
