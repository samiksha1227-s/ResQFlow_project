from pydantic import BaseModel
from typing import Optional

class HospitalResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    trauma_level: int
    total_icu_beds: int
    available_icu_beds: int
    total_er_beds: int
    available_er_beds: int
    specialties: Optional[str]
    contact_number: Optional[str]

    class Config:
        from_attributes = True

class HospitalCapacityUpdate(BaseModel):
    available_icu_beds: Optional[int] = None
    available_er_beds: Optional[int] = None
