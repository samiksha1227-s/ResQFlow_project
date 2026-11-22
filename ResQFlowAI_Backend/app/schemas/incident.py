from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class IncidentReportCreate(BaseModel):
    source_type: str = Field(..., description="cctv, citizen, dashcam, authority")
    source_identifier: Optional[str] = Field(None, description="Camera ID, caller phone, vehicle ID")
    latitude: float
    longitude: float
    address: Optional[str] = None
    raw_text: Optional[str] = None
    media_url: Optional[str] = None
    victim_count: Optional[int] = 1
    vehicle_count: Optional[int] = 2
    is_rollover: Optional[bool] = False
    has_fire: Optional[bool] = False

class IncidentOverrideRequest(BaseModel):
    action: Optional[str] = Field(None, description="confirm, reject, override")
    status: Optional[str] = None
    severity: Optional[str] = None # low, medium, high, critical
    assigned_ambulance_id: Optional[int] = None
    recommended_hospital_id: Optional[int] = None
    notes: Optional[str] = None

class IncidentStatusUpdate(BaseModel):
    status: str # reported, verified, dispatched, on_scene, transporting, arrived, closed, rejected

class IncidentReportResponse(BaseModel):
    id: int
    source_type: str
    source_identifier: Optional[str]
    latitude: float
    longitude: float
    raw_text: Optional[str]
    reported_at: Optional[datetime]

    class Config:
        from_attributes = True

class IncidentResponse(BaseModel):
    id: int
    incident_code: str
    latitude: float
    longitude: float
    address: Optional[str]
    primary_source: str
    status: str
    severity: str
    ai_confidence: float
    ai_verified: bool
    is_demo_mode: bool
    victim_count: int
    vehicle_count: int
    description: Optional[str]
    media_url: Optional[str]
    assigned_ambulance_id: Optional[int]
    recommended_hospital_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    report_count: Optional[int] = 1

    class Config:
        from_attributes = True
