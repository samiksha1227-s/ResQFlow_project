from typing import List, Tuple, Optional, Any
from app.algorithms.distance import haversine_distance_km

def match_optimal_ambulance(
    incident_lat: float,
    incident_lng: float,
    severity: str,
    ambulances: List[Any]
) -> Tuple[Optional[Any], List[dict]]:
    """
    Weighted scoring algorithm for ambulance selection.
    Considers proximity, capability (ALS/BLS), and availability.
    """
    if not ambulances:
        return None, []

    candidates = [a for a in ambulances if a.status == "available"]
    if not candidates:
        # Fallback to any active ambulance if none available
        candidates = ambulances

    scored_list = []
    max_radius_km = 30.0 # Normalization baseline

    for amb in candidates:
        dist_km = haversine_distance_km(incident_lat, incident_lng, amb.current_latitude, amb.current_longitude)
        
        # 1. Proximity Score (0 to 1, higher is closer)
        proximity_score = max(0.0, 1.0 - (dist_km / max_radius_km))
        
        # 2. Capability Score (ALS vs BLS match to incident severity)
        is_critical = severity in ["critical", "high"]
        if is_critical:
            capability_score = 1.0 if amb.type == "ALS" else 0.45
        else:
            capability_score = 1.0 if amb.type == "BLS" else 0.85
        
        # 3. Readiness Score
        readiness_score = 1.0 if amb.status == "available" else 0.3

        # Composite Weighted Score
        w_dist = 0.55
        w_cap = 0.30
        w_ready = 0.15
        
        composite_score = (w_dist * proximity_score) + (w_cap * capability_score) + (w_ready * readiness_score)
        total_score_100 = round(composite_score * 100.0, 1)

        scored_list.append({
            "ambulance": amb,
            "distance_km": round(dist_km, 2),
            "score": total_score_100,
            "type": amb.type,
            "callsign": amb.callsign
        })

    # Sort descending by score
    scored_list.sort(key=lambda x: x["score"], reverse=True)
    best_match = scored_list[0]["ambulance"] if scored_list else None
    
    return best_match, scored_list
