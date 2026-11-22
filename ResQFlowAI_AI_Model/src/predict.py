"""
predict.py
==========
Command-line prediction tool for ResQFlowAI severity model.

Usage
-----
    python predict.py --victims 3 --unconscious 1 --bleeding 1 --breathing 1

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
"""

import argparse
import json
import os
import sys

DISCLAIMER = "⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from inference import SeverityInference

SEVERITY_COLORS = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
}

RULE_EXPLANATIONS = {
    "CRIT_UNCONSCIOUS_BREATH_CRITICAL":       "Unconscious + breathing difficulty + critical condition",
    "CRIT_MASS_CASUALTY_UNCONSCIOUS_BLEEDING": "Mass casualty (≥3 victims) + unconscious + bleeding",
    "CRIT_UNCONSCIOUS_CRITICAL_CONDITION":    "Unconscious + critical condition",
    "HIGH_UNCONSCIOUS":                       "Patient(s) unconscious",
    "HIGH_BLEEDING_BREATHING":                "Active bleeding + breathing difficulty",
    "HIGH_MASS_VISIBLE_INJURY":               "≥3 victims with visible injury",
    "HIGH_CRITICAL_CONDITION":                "Critical medical condition present",
    "MED_VISIBLE_INJURY_CONSCIOUS_FEW":       "Visible injury, conscious, ≤2 victims",
    "MED_BLEEDING_CONSCIOUS":                 "Bleeding but conscious, no breathing issues",
    "MED_MULTIPLE_VICTIMS_NO_CRITICAL":       "Multiple victims without critical indicators",
    "AGE_MODIFIER":                           "Vulnerable age group (elderly/child) – confidence boosted",
    "DEFAULT_LOW":                            "No high-risk indicators detected",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ResQFlowAI – Emergency Severity Predictor (SYNTHETIC DEMO DATA)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python predict.py --victims 3 --unconscious 1 --bleeding 1 --breathing 1
  python predict.py --victims 1 --visible-injury 1
  python predict.py --victims 5 --unconscious 1 --critical 1 --json

{DISCLAIMER}
        """,
    )
    parser.add_argument("--victims",       type=int, default=1,  help="Number of victims (default: 1)")
    parser.add_argument("--unconscious",   type=int, default=0,  choices=[0, 1], help="Has unconscious victim (0/1)")
    parser.add_argument("--bleeding",      type=int, default=0,  choices=[0, 1], help="Has bleeding (0/1)")
    parser.add_argument("--breathing",     type=int, default=0,  choices=[0, 1], help="Has breathing difficulty (0/1)")
    parser.add_argument("--visible-injury",type=int, default=0,  choices=[0, 1], dest="visible_injury", help="Has visible injury (0/1)")
    parser.add_argument("--critical",      type=int, default=0,  choices=[0, 1], help="Has critical condition (0/1)")
    parser.add_argument("--age-critical",  type=int, default=0,  choices=[0, 1], dest="age_critical", help="Elderly or child involved (0/1)")
    parser.add_argument("--vehicles",      type=int, default=1,  help="Number of vehicles involved (default: 1)")
    parser.add_argument("--json",          action="store_true",   help="Output result as JSON")
    parser.add_argument("--force-rules",   action="store_true",   help="Force rule engine (ignore ML model)")
    return parser


def print_result(result: dict, victim_data: dict):
    severity = result["severity"]
    icon = SEVERITY_COLORS.get(severity, "⚪")

    print("=" * 60)
    print(result["disclaimer"])
    print("=" * 60)
    print(f"\n  Severity   : {icon} {severity}")
    print(f"  Confidence : {result['confidence'] * 100:.1f}%")
    print(f"  Method     : {result['method']}")

    print("\n  Input Summary:")
    print(f"    Victims                : {victim_data['victim_count']}")
    print(f"    Vehicles               : {victim_data['vehicle_count']}")
    print(f"    Unconscious            : {'Yes' if victim_data['has_unconscious'] else 'No'}")
    print(f"    Bleeding               : {'Yes' if victim_data['has_bleeding'] else 'No'}")
    print(f"    Breathing Difficulty   : {'Yes' if victim_data['has_breathing_difficulty'] else 'No'}")
    print(f"    Visible Injury         : {'Yes' if victim_data['has_visible_injury'] else 'No'}")
    print(f"    Critical Condition     : {'Yes' if victim_data['has_critical_condition'] else 'No'}")
    print(f"    Vulnerable Age Group   : {'Yes' if victim_data['age_group_critical'] else 'No'}")

    details = result.get("details", {})

    if "rules_triggered" in details:
        print("\n  Rules Triggered:")
        for rule in details["rules_triggered"]:
            desc = RULE_EXPLANATIONS.get(rule, rule)
            print(f"    • {desc}")

    if "class_probabilities" in details:
        print("\n  Class Probabilities:")
        proba = details["class_probabilities"]
        for label in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if label in proba:
                bar = "█" * int(proba[label] * 20)
                print(f"    {label:8s} {proba[label]*100:5.1f}%  {bar}")

    print()
    print("=" * 60)
    print(result["disclaimer"])
    print("=" * 60)


def main():
    parser = build_parser()
    args = parser.parse_args()

    victim_data = {
        "victim_count":            args.victims,
        "has_unconscious":         args.unconscious,
        "has_bleeding":            args.bleeding,
        "has_breathing_difficulty":args.breathing,
        "has_visible_injury":      args.visible_injury,
        "has_critical_condition":  args.critical,
        "age_group_critical":      args.age_critical,
        "vehicle_count":           args.vehicles,
    }

    engine = SeverityInference()

    if args.force_rules:
        result = engine.rule_assess(victim_data)
    else:
        result = engine.predict(victim_data)

    if args.json:
        output = {**result, "input": victim_data}
        print(json.dumps(output, indent=2))
    else:
        print_result(result, victim_data)


if __name__ == "__main__":
    main()
