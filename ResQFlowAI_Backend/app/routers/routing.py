import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, Ambulance, Hospital, Route, ActivityLog
from app.schemas import BlockageSimulationRequest
from app.algorithms import city_road_graph

router = APIRouter(prefix="/routing", tags=["Routing & Dynamic Rerouting"])

@router.post("/simulate-blockage")
def simulate_road_blockage(request: BlockageSimulationRequest, db: Session = Depends(get_db)):
    """
    Simulate Road Blockage Endpoint:
    1. Blocks designated road segment (e.g. Central Expressway Overpass).
    2. Runs A* algorithm to dynamically find an alternate obstacle-free route.
    3. Calculates new distance, updated ETA, and delta.
    4. Records event into the operational Activity Timeline.
    5. Returns both original and alternative polylines for high-impact UI comparison.
    """
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
    hosp = db.query(Hospital).filter(Hospital.id == incident.recommended_hospital_id).first()

    if not amb or not hosp:
        raise HTTPException(status_code=400, detail="Incident does not have both an assigned ambulance and hospital")

    existing_route = db.query(Route).filter(Route.incident_id == incident.id).first()
    if not existing_route:
        raise HTTPException(status_code=404, detail="No active route found for this incident")

    blocked_name = request.blocked_segment_name or "Central Expressway Overpass"

    # Step 1: Set blockage in the A* road graph
    city_road_graph.set_road_blockage(blocked_name, blocked=True)

    # Step 2: Rerun A* dynamic reroute
    reroute_data = city_road_graph.plan_full_emergency_route(
        amb.current_latitude,
        amb.current_longitude,
        incident.latitude,
        incident.longitude,
        hosp.latitude,
        hosp.longitude
    )

    # Preserve original route for visual comparison on Leaflet map
    if not existing_route.original_route_geojson:
        existing_route.original_route_geojson = existing_route.polyline_geojson
        existing_route.original_eta_minutes = existing_route.eta_minutes

    existing_route.polyline_geojson = json.dumps(reroute_data["polyline"])
    existing_route.distance_km = reroute_data["distance_km"]
    old_eta = existing_route.eta_minutes
    existing_route.eta_minutes = reroute_data["eta_minutes"]
    existing_route.has_blockage = True
    existing_route.blocked_segment = blocked_name

    eta_delta = round(existing_route.eta_minutes - (existing_route.original_eta_minutes or old_eta), 1)

    # Step 3: Append high-priority event to Activity Timeline
    log = ActivityLog(
        incident_id=incident.id,
        event_type="REROUTED",
        message=f"⚠️ CRITICAL ROAD BLOCKAGE: {blocked_name} impassable! A* dynamic reroute computed via East Valley Parkway / Green Arterial. ETA adjusted: {existing_route.eta_minutes} mins (+{eta_delta} mins).",
        severity="danger"
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "incident_id": incident.id,
        "blocked_segment": blocked_name,
        "has_blockage": True,
        "distance_km": existing_route.distance_km,
        "new_eta_minutes": existing_route.eta_minutes,
        "original_eta_minutes": existing_route.original_eta_minutes,
        "eta_delta_minutes": eta_delta,
        "polyline": reroute_data["polyline"],
        "original_polyline": json.loads(existing_route.original_route_geojson) if existing_route.original_route_geojson else [],
        "message": f"Dynamic rerouting completed via A*. Obstacle on {blocked_name} avoided."
    }

@router.post("/clear-blockage/{incident_id}")
def clear_road_blockage(incident_id: int, db: Session = Depends(get_db)):
    """Resets the road blockage and restores the primary route."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
    hosp = db.query(Hospital).filter(Hospital.id == incident.recommended_hospital_id).first()
    existing_route = db.query(Route).filter(Route.incident_id == incident.id).first()

    # Clear graph blockages
    city_road_graph.clear_all_blockages()

    if amb and hosp and existing_route:
        fresh_route = city_road_graph.plan_full_emergency_route(
            amb.current_latitude,
            amb.current_longitude,
            incident.latitude,
            incident.longitude,
            hosp.latitude,
            hosp.longitude
        )
        existing_route.polyline_geojson = json.dumps(fresh_route["polyline"])
        existing_route.distance_km = fresh_route["distance_km"]
        existing_route.eta_minutes = fresh_route["eta_minutes"]
        existing_route.has_blockage = False
        existing_route.blocked_segment = None

        log = ActivityLog(
            incident_id=incident.id,
            event_type="REROUTED",
            message=f"Road blockage cleared. Restored primary A* route. ETA: {existing_route.eta_minutes} mins.",
            severity="info"
        )
        db.add(log)
        db.commit()

    return {"success": True, "message": "Road blockage cleared and route normalized."}

@router.get("/active/{incident_id}")
def get_active_route(incident_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.incident_id == incident_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return {
        "id": route.id,
        "incident_id": route.incident_id,
        "ambulance_id": route.ambulance_id,
        "hospital_id": route.hospital_id,
        "distance_km": route.distance_km,
        "eta_minutes": route.eta_minutes,
        "has_blockage": route.has_blockage,
        "blocked_segment": route.blocked_segment,
        "polyline": json.loads(route.polyline_geojson) if route.polyline_geojson else [],
        "original_polyline": json.loads(route.original_route_geojson) if route.original_route_geojson else None,
        "original_eta_minutes": route.original_eta_minutes
    }
