"""
generate_synthetic_data.py
==========================
Generates synthetic emergency scenario data for training the ResQFlowAI severity model.

⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️
This data is entirely fabricated for hackathon demonstration purposes only.
It does NOT represent real medical or emergency scenarios.
"""

import random
import csv
import os

DISCLAIMER = "⚠️  SYNTHETIC DEMO DATA – NOT FOR MEDICAL USE  ⚠️"

FEATURES = [
    "victim_count",
    "has_unconscious",
    "has_bleeding",
    "has_breathing_difficulty",
    "has_visible_injury",
    "has_critical_condition",
    "age_group_critical",
    "vehicle_count",
    "severity_label",
]


def assign_label(row: dict) -> str:
    """
    Deterministic labelling rules for synthetic samples.
    These rules are simplified heuristics for demo purposes only.
    """
    vc = row["victim_count"]
    uncon = row["has_unconscious"]
    bleed = row["has_bleeding"]
    breath = row["has_breathing_difficulty"]
    crit = row["has_critical_condition"]
    visible = row["has_visible_injury"]

    # CRITICAL
    if uncon and (breath or crit) and vc >= 2:
        return "CRITICAL"

    # HIGH
    if uncon or (bleed and breath) or (vc >= 3 and bleed):
        return "HIGH"

    # MEDIUM
    if visible and not uncon and vc <= 2:
        return "MEDIUM"

    # LOW (default)
    return "LOW"


def generate_sample(seed_idx: int) -> dict:
    """Generate a single synthetic emergency sample."""
    random.seed(seed_idx * 7 + 13)  # Reproducible per index

    victim_count = random.randint(1, 10)
    vehicle_count = random.randint(1, 5)

    # Inject some correlation so labels are realistic
    severity_roll = random.random()

    if severity_roll < 0.15:  # ~15% truly critical
        has_unconscious = True
        has_breathing_difficulty = random.random() < 0.75
        has_critical_condition = random.random() < 0.65
        has_bleeding = random.random() < 0.70
        has_visible_injury = True
        age_group_critical = random.random() < 0.45
        victim_count = max(victim_count, random.randint(2, 10))
    elif severity_roll < 0.40:  # ~25% high
        has_unconscious = random.random() < 0.55
        has_breathing_difficulty = random.random() < 0.50
        has_critical_condition = random.random() < 0.35
        has_bleeding = random.random() < 0.60
        has_visible_injury = True
        age_group_critical = random.random() < 0.30
    elif severity_roll < 0.70:  # ~30% medium
        has_unconscious = False
        has_breathing_difficulty = random.random() < 0.15
        has_critical_condition = False
        has_bleeding = random.random() < 0.30
        has_visible_injury = random.random() < 0.80
        age_group_critical = random.random() < 0.20
        victim_count = min(victim_count, 2)
    else:  # ~30% low
        has_unconscious = False
        has_breathing_difficulty = False
        has_critical_condition = False
        has_bleeding = random.random() < 0.10
        has_visible_injury = random.random() < 0.40
        age_group_critical = random.random() < 0.10
        victim_count = 1

    row = {
        "victim_count": victim_count,
        "has_unconscious": int(has_unconscious),
        "has_bleeding": int(has_bleeding),
        "has_breathing_difficulty": int(has_breathing_difficulty),
        "has_visible_injury": int(has_visible_injury),
        "has_critical_condition": int(has_critical_condition),
        "age_group_critical": int(age_group_critical),
        "vehicle_count": vehicle_count,
    }

    row["severity_label"] = assign_label(row)
    return row


def generate_dataset(n_samples: int = 1200, output_path: str = None) -> list:
    """
    Generate n_samples synthetic emergency records and save to CSV.

    Parameters
    ----------
    n_samples : int
        Number of synthetic records to generate.
    output_path : str
        Path to save the CSV file. Defaults to data/synthetic_emergency_data.csv.

    Returns
    -------
    list of dict
    """
    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    print(f"Generating {n_samples} synthetic emergency samples...")

    samples = [generate_sample(i) for i in range(n_samples)]

    # Compute label distribution
    from collections import Counter
    dist = Counter(s["severity_label"] for s in samples)
    print("\nLabel distribution:")
    for label in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        print(f"  {label:8s}: {dist.get(label, 0):5d} ({dist.get(label, 0)/n_samples*100:.1f}%)")

    if output_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "synthetic_emergency_data.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FEATURES)
        writer.writeheader()
        writer.writerows(samples)

    print(f"\nDataset saved to: {output_path}")
    print(f"Total samples   : {n_samples}")
    print("=" * 60)
    print(DISCLAIMER)
    print("=" * 60)
    return samples


if __name__ == "__main__":
    generate_dataset(n_samples=1200)
