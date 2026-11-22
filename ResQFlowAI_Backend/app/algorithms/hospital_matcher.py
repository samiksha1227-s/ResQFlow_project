from typing import List, Tuple, Optional, Any
from app.algorithms.distance import haversine_distance_km

def match_optimal_hospital(
    incident_lat: float,
    incident_lng: float,
    severity: str,
    hospitals: List[Any]
) -> Tuple[Optional[Any], List[dict]]:
    """
    Weighted scoring algorithm for hospital selection.
    Considers proximity, trauma tier capability, and ICU/ER bed availability.
    """
    if not hospitals:
        return None, []

    scored_list = []
    max_radius_km = 30.0

    for hosp in hospitals:
        dist_km = haversine_distance_km(incident_lat, incident_lng, hosp.latitude, hosp.longitude)
        
        # 1. Proximity score (0 to 1)
        proximity_score = max(0.0, 1.0 - (dist_km / max_radius_km))

        # 2. Bed Capacity Score (ICU beds prioritized for critical, ER beds for others)
        is_critical = severity in ["critical", "high"]
        if is_critical and hosp.total_icu_beds > 0:
            capacity_score = max(0.0, hosp.available_icu_beds / hosp.total_icu_beds)
        elif hosp.total_er_beds > 0:
            capacity_score = max(0.0, hosp.available_er_beds / hosp.total_er_beds)
        else:
            capacity_score = 0.2

        # 3. Trauma Level Suitability
        # Level 1 = Comprehensive (best for Critical/High)
        # Level 2 = Major Trauma
        # Level 3 = General Hospital
        if severity == "critical":
            trauma_score = 1.0 if hosp.trauma_level == 1 else (0.6 if hosp.trauma_level == 2 else 0.2)
        elif severity == "high":
            trauma_score = 1.0 if hosp.trauma_level in [1, 2] else 0.5
        else:
            trauma_score = 1.0 # Any hospital is fine for low/medium

        # Penalize if critical patient and 0 ICU beds available
        if is_critical and hosp.available_icu_beds == 0:
            capacity_score *= 0.1

        # Composite Weighted Score
        w_dist = 0.45
        w_cap = 0.30
        w_trauma = 0.25

        composite_score = (w_dist * proximity_score) + (w_cap * capacity_score) + (w_trauma * trauma_score)
        total_score_100 = round(composite_score * 100.0, 1)

        scored_list.append({
            "hospital": hosp,
            "name": hosp.name,
            "distance_km": round(dist_km, 2),
            "score": total_score_100,
            "trauma_level": hosp.trauma_level,
            "available_icu": hosp.available_icu_beds,
            "available_er": hosp.available_er_beds
        })

    # Sort descending by score
    scored_list.sort(key=lambda x: x["score"], reverse=True)
    best_match = scored_list[0]["hospital"] if scored_list else None

    return best_match, scored_list
