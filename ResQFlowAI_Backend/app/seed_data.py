import os
import sys
import json

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import Ambulance, Hospital, Incident, IncidentReport, Route, ActivityLog
from app.algorithms import calculate_severity, match_optimal_ambulance, match_optimal_hospital, city_road_graph


def seed_database(db: Session):
    """
    Cleans and seeds the database with initial ambulances, hospitals,
    and a baseline active incident for instant hackathon demonstration.
    """
    # Delete existing data
    db.query(ActivityLog).delete()
    db.query(Route).delete()
    db.query(IncidentReport).delete()
    db.query(Incident).delete()
    db.query(Ambulance).delete()
    db.query(Hospital).delete()
    db.commit()

    # 1. Seed Ambulances
    ambulances_data = [
        {"callsign": "MEDIC-101 (ALS)", "type": "ALS", "status": "available", "current_latitude": 12.9820, "current_longitude": 77.5850, "base_station": "North Station"},
        {"callsign": "MEDIC-102 (ALS)", "type": "ALS", "status": "available", "current_latitude": 12.9600, "current_longitude": 77.6100, "base_station": "East Central Station"},
        {"callsign": "MEDIC-103 (BLS)", "type": "BLS", "status": "available", "current_latitude": 12.9950, "current_longitude": 77.6000, "base_station": "Outer North Post"},
        {"callsign": "MEDIC-104 (BLS)", "type": "BLS", "status": "available", "current_latitude": 12.9550, "current_longitude": 77.5750, "base_station": "Southwest Base"},
        {"callsign": "MEDIC-105 (ALS)", "type": "ALS", "status": "dispatched", "current_latitude": 12.9750, "current_longitude": 77.5950, "base_station": "City Center Post"},
        {"callsign": "MEDIC-106 (BLS)", "type": "BLS", "status": "available", "current_latitude": 12.9680, "current_longitude": 77.6250, "base_station": "Tech Corridor Post"},
    ]
    amb_objects = []
    for d in ambulances_data:
        amb = Ambulance(**d)
        db.add(amb)
        amb_objects.append(amb)
    db.commit()

    # 2. Seed Hospitals
    hospitals_data = [
        {
            "name": "Metro Comprehensive Trauma Center",
            "latitude": 12.9469,
            "longitude": 77.5987,
            "trauma_level": 1,
            "total_icu_beds": 25,
            "available_icu_beds": 7,
            "total_er_beds": 50,
            "available_er_beds": 16,
            "specialties": json.dumps(["Trauma Surgery", "Neurosurgery", "Cardiac Cath", "Burn Unit"])
        },
        {
            "name": "St. Jude Regional Emergency Hospital",
            "latitude": 12.9969,
            "longitude": 77.5920,
            "trauma_level": 2,
            "total_icu_beds": 16,
            "available_icu_beds": 4,
            "total_er_beds": 35,
            "available_er_beds": 11,
            "specialties": json.dumps(["Emergency Surgery", "Orthopedics", "Cardiology"])
        },
        {
            "name": "Tech City Memorial Hospital",
            "latitude": 12.9720,
            "longitude": 77.6320,
            "trauma_level": 2,
            "total_icu_beds": 12,
            "available_icu_beds": 3,
            "total_er_beds": 28,
            "available_er_beds": 8,
            "specialties": json.dumps(["General Emergency", "Internal Medicine"])
        },
        {
            "name": "Westside Community Health & ER",
            "latitude": 12.9680,
            "longitude": 77.5580,
            "trauma_level": 3,
            "total_icu_beds": 6,
            "available_icu_beds": 2,
            "total_er_beds": 15,
            "available_er_beds": 7,
            "specialties": json.dumps(["Minor Trauma", "Urgent Care"])
        }
    ]
    hosp_objects = []
    for d in hospitals_data:
        hosp = Hospital(**d)
        db.add(hosp)
        hosp_objects.append(hosp)
    db.commit()

    # 3. Create initial verified showcase incident: Highway Multi-Vehicle Collision
    inc_lat = 12.9850
    inc_lng = 77.5937
    severity_label, score, _ = calculate_severity(vehicle_count=2, victim_count=2, is_rollover=False, ai_confidence=0.88)
    
    # Match ambulance and hospital
    matched_amb, _ = match_optimal_ambulance(inc_lat, inc_lng, severity_label, amb_objects)
    matched_hosp, _ = match_optimal_hospital(inc_lat, inc_lng, severity_label, hosp_objects)

    incident = Incident(
        incident_code="INC-2026-001",
        latitude=inc_lat,
        longitude=inc_lng,
        address="Central Expressway Overpass, Mile Marker 4",
        primary_source="cctv",
        status="dispatched",
        severity=severity_label,
        ai_confidence=0.88,
        ai_verified=True,
        is_demo_mode=True,
        victim_count=2,
        vehicle_count=2,
        description="Two-vehicle high-speed collision detected on CCTV stream with vehicle overlap and traffic halt.",
        assigned_ambulance_id=matched_amb.id if matched_amb else None,
        recommended_hospital_id=matched_hosp.id if matched_hosp else None
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    if matched_amb:
        matched_amb.status = "dispatched"
        matched_amb.current_incident_id = incident.id
        db.commit()

    # Add raw reports from CCTV and Citizen to demonstrate multi-source deduplication
    rep1 = IncidentReport(
        incident_id=incident.id,
        source_type="cctv",
        source_identifier="CCTV-EXP-CAM-08",
        latitude=inc_lat,
        longitude=inc_lng,
        raw_text="Automated vision alert: Vehicle overlap detected. Confidence: 88%."
    )
    rep2 = IncidentReport(
        incident_id=incident.id,
        source_type="citizen",
        source_identifier="+1-555-0144 (Citizen SOS)",
        latitude=inc_lat + 0.0002,
        longitude=inc_lng - 0.0001,
        raw_text="Citizen 911 report: Head-on collision on Central Expressway Overpass, two victims injured."
    )
    db.add_all([rep1, rep2])
    db.commit()

    # Plan initial route
    if matched_amb and matched_hosp:
        route_data = city_road_graph.plan_full_emergency_route(
            matched_amb.current_latitude,
            matched_amb.current_longitude,
            inc_lat,
            inc_lng,
            matched_hosp.latitude,
            matched_hosp.longitude
        )
        route = Route(
            incident_id=incident.id,
            ambulance_id=matched_amb.id,
            hospital_id=matched_hosp.id,
            polyline_geojson=json.dumps(route_data["polyline"]),
            distance_km=route_data["distance_km"],
            eta_minutes=route_data["eta_minutes"],
            has_blockage=False
        )
        db.add(route)
        db.commit()

    # Activity Timeline initial entries
    logs = [
        ActivityLog(
            incident_id=incident.id,
            event_type="AI_VERIFIED",
            message="CCTV-EXP-CAM-08: Vision model detected multi-vehicle overlap (AI Confidence: 88%)",
            severity="warning"
        ),
        ActivityLog(
            incident_id=incident.id,
            event_type="DEDUPLICATED",
            message="DBSCAN Spatio-temporal cluster merged Citizen SOS call #555-0144 into canonical Incident INC-2026-001 (Distance: 24m)",
            severity="info"
        ),
        ActivityLog(
            incident_id=incident.id,
            event_type="DISPATCHED",
            message=f"Optimal Ambulance {matched_amb.callsign} assigned (Proximity: 2.1km, ALS Capability Match)",
            severity="success"
        ),
        ActivityLog(
            incident_id=incident.id,
            event_type="HOSPITAL_MATCH",
            message=f"Patient assigned to {matched_hosp.name} (Level 1 Trauma Center, 7 ICU Beds Open)",
            severity="info"
        ),
    ]
    db.add_all(logs)
    db.commit()

    print("Database successfully seeded with ambulances, hospitals, and demo incident!")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        seed_database(db_session)
    finally:
        db_session.close()

