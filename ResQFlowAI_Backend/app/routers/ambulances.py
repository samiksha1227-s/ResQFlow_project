from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ambulance
from app.schemas import AmbulanceResponse, AmbulanceLocationUpdate

router = APIRouter(prefix="/ambulances", tags=["Ambulances"])

@router.get("", response_model=List[AmbulanceResponse])
def get_ambulances(db: Session = Depends(get_db)):
    return db.query(Ambulance).all()

@router.patch("/{ambulance_id}/location")
def update_ambulance_location(
    ambulance_id: int,
    loc_in: AmbulanceLocationUpdate,
    db: Session = Depends(get_db)
):
    amb = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not amb:
        raise HTTPException(status_code=404, detail="Ambulance not found")

    amb.current_latitude = loc_in.latitude
    amb.current_longitude = loc_in.longitude
    if loc_in.status:
        amb.status = loc_in.status
    db.commit()

    return {"message": "Ambulance telemetry updated", "callsign": amb.callsign}
