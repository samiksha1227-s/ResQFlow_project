import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, IncidentReport, Ambulance, Hospital, Route, ActivityLog
from app.seed_data import seed_database
from app.ai_engine.demo_fixtures import DEMO_SCENARIOS
from app.algorithms import (
    calculate_severity,
    match_optimal_ambulance,
    match_optimal_hospital,
    city_road_graph
)

router = APIRouter(prefix="/simulation", tags=["Simulation & Demo Scenarios"])

@router.get("/scenarios")
def list_scenarios():
    return DEMO_SCENARIOS

@router.post("/reset")
def reset_system_simulation(db: Session = Depends(get_db)):
    """Resets the database back to clean initial state with seeded fleet and base incident."""
    seed_database(db)
    city_road_graph.clear_all_blockages()
    return {"success": True, "message": "ResQFlow AI system reset to default initial state."}

@router.post("/trigger/{scenario_id}")
def trigger_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Triggers one of the pre-configured hackathon demo scenarios."""
    scenario = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    all_ambs = db.query(Ambulance).all()
    all_hosps = db.query(Hospital).all()

    matched_amb, _ = match_optimal_ambulance(scenario["latitude"], scenario["longitude"], scenario["severity"], all_ambs)
    matched_hosp, _ = match_optimal_hospital(scenario["latitude"], scenario["longitude"], scenario["severity"], all_hosps)

    # Create canonical incident
    new_inc = Incident(
        incident_code=f"INC-{scenario_id[:6].upper()}-99",
        latitude=scenario["latitude"],
        longitude=scenario["longitude"],
        address=scenario["address"],
        primary_source=scenario["primary_source"],
        status="dispatched" if matched_amb else "verified",
        severity=scenario["severity"],
        ai_confidence=scenario["ai_confidence"],
        ai_verified=True,
        is_demo_mode=True,
        victim_count=scenario["victim_count"],
        vehicle_count=scenario["vehicle_count"],
        description=scenario["description"],
        assigned_ambulance_id=matched_amb.id if matched_amb else None,
        recommended_hospital_id=matched_hosp.id if matched_hosp else None
    )
    db.add(new_inc)
    db.commit()
    db.refresh(new_inc)

    if matched_amb:
        matched_amb.status = "dispatched"
        matched_amb.current_incident_id = new_inc.id

    # Add primary report
    rep1 = IncidentReport(
        incident_id=new_inc.id,
        source_type=scenario["primary_source"],
        source_identifier="SIM-SOURCE-PRIMARY",
        latitude=scenario["latitude"],
        longitude=scenario["longitude"],
        raw_text=scenario["description"]
    )
    db.add(rep1)

    # If scenario has secondary reports (demonstrates DBSCAN deduplication)
    for sec in scenario.get("secondary_reports", []):
        rep_sec = IncidentReport(
            incident_id=new_inc.id,
            source_type=sec["source_type"],
            source_identifier=sec["source_identifier"],
            latitude=sec["latitude"],
            longitude=sec["longitude"],
            raw_text=sec["raw_text"]
        )
        db.add(rep_sec)

        # Log deduplication
        db.add(ActivityLog(
            incident_id=new_inc.id,
            event_type="DEDUPLICATED",
            message=f"DBSCAN duplicate filter merged {sec['source_type'].upper()} ({sec['source_identifier']}) into Incident {new_inc.incident_code}. Redundant dispatch prevented.",
            severity="info"
        ))

    # Calculate route
    if matched_amb and matched_hosp:
        route_data = city_road_graph.plan_full_emergency_route(
            matched_amb.current_latitude,
            matched_amb.current_longitude,
            new_inc.latitude,
            new_inc.longitude,
            matched_hosp.latitude,
            matched_hosp.longitude
        )
        route_rec = Route(
            incident_id=new_inc.id,
            ambulance_id=matched_amb.id,
            hospital_id=matched_hosp.id,
            polyline_geojson=json.dumps(route_data["polyline"]),
            distance_km=route_data["distance_km"],
            eta_minutes=route_data["eta_minutes"],
            has_blockage=False
        )
        db.add(route_rec)

    # Activity log
    db.add(ActivityLog(
        incident_id=new_inc.id,
        event_type="AI_VERIFIED",
        message=f"Demo Scenario Injected: {scenario['title']} ({int(scenario['ai_confidence']*100)}% Confidence, Severity: {scenario['severity'].upper()})",
        severity="warning"
    ))

    db.commit()

    return {
        "success": True,
        "incident_id": new_inc.id,
        "incident_code": new_inc.incident_code,
        "title": scenario["title"],
        "message": "Scenario successfully activated."
    }
