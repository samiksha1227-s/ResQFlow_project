from pydantic import BaseModel
from typing import Optional

class AmbulanceResponse(BaseModel):
    id: int
    callsign: str
    type: str # ALS, BLS
    status: str # available, dispatched, busy, maintenance
    current_latitude: float
    current_longitude: float
    base_station: Optional[str]
    speed_kmh: float
    contact_number: Optional[str]
    current_incident_id: Optional[int]

    class Config:
        from_attributes = True

class AmbulanceLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    status: Optional[str] = None
