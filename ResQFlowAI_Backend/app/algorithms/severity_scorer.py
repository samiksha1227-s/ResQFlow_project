from typing import Dict, Any, Tuple

def calculate_severity(
    vehicle_count: int = 1,
    victim_count: int = 0,
    is_rollover: bool = False,
    has_fire: bool = False,
    ai_confidence: float = 0.5,
    is_highway: bool = False
) -> Tuple[str, float, Dict[str, Any]]:
    """
    Rule-based multi-factor severity scoring algorithm.
    Returns: (severity_label, score_0_to_100, factor_breakdown)
    """
    score = 0.0
    breakdown = {}

    # 1. Casualty Impact (up to 60 pts)
    casualty_score = min(60.0, victim_count * 25.0)
    score += casualty_score
    breakdown["casualties"] = {"count": victim_count, "points": casualty_score}

    # 2. Vehicle involvement (up to 30 pts)
    vehicle_score = min(30.0, vehicle_count * 12.0)
    score += vehicle_score
    breakdown["vehicles"] = {"count": vehicle_count, "points": vehicle_score}

    # 3. Rollover / Inversion Hazard
    if is_rollover:
        score += 25.0
        breakdown["rollover"] = 25.0

    # 4. Fire / Smoke hazard
    if has_fire:
        score += 20.0
        breakdown["fire_hazard"] = 20.0

    # 5. Speed environment
    if is_highway:
        score += 15.0
        breakdown["highway_speed"] = 15.0

    # 6. AI Confidence adjustment
    ai_factor = round(ai_confidence * 10.0, 1)
    score += ai_factor
    breakdown["ai_confidence_factor"] = ai_factor

    # Cap score at 100
    score = min(100.0, max(10.0, score))

    if score >= 80.0:
        label = "critical"
    elif score >= 55.0:
        label = "high"
    elif score >= 30.0:
        label = "medium"
    else:
        label = "low"

    return label, score, breakdown
