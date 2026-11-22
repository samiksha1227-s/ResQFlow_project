from pydantic import BaseModel
from typing import List, Optional

class RoutePlanResponse(BaseModel):
    id: Optional[int] = None
    incident_id: int
    ambulance_id: int
    hospital_id: int
    polyline: List[List[float]] # [[lat, lng], ...]
    distance_km: float
    eta_minutes: float
    has_blockage: bool = False
    blocked_segment: Optional[str] = None
    original_polyline: Optional[List[List[float]]] = None
    original_eta_minutes: Optional[float] = None
    alternative_reason: Optional[str] = None

class BlockageSimulationRequest(BaseModel):
    incident_id: int
    blocked_segment_name: Optional[str] = "Central Expressway Overpass"

class ActivityLogResponse(BaseModel):
    id: int
    incident_id: Optional[int]
    event_type: str
    message: str
    severity: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
