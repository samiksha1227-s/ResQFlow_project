from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Hospital
from app.schemas import HospitalResponse, HospitalCapacityUpdate

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

@router.get("", response_model=List[HospitalResponse])
def get_hospitals(db: Session = Depends(get_db)):
    return db.query(Hospital).all()

@router.patch("/{hospital_id}/capacity")
def update_hospital_capacity(
    hospital_id: int,
    cap_in: HospitalCapacityUpdate,
    db: Session = Depends(get_db)
):
    hosp = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hosp:
        raise HTTPException(status_code=404, detail="Hospital not found")

    if cap_in.available_icu_beds is not None:
        hosp.available_icu_beds = cap_in.available_icu_beds
    if cap_in.available_er_beds is not None:
        hosp.available_er_beds = cap_in.available_er_beds
    db.commit()

    return {"message": "Hospital capacity updated", "name": hosp.name}
