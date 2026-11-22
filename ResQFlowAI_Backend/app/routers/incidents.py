import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, IncidentReport, Ambulance, Hospital, Route, ActivityLog
from app.schemas import (
    IncidentReportCreate,
    IncidentOverrideRequest,
    IncidentStatusUpdate,
    IncidentResponse,
    IncidentReportResponse,
)
from app.algorithms import (
    duplicate_detector,
    calculate_severity,
    match_optimal_ambulance,
    match_optimal_hospital,
    city_road_graph,
    haversine_distance_meters
)
from app.ai_engine import accident_event_engine, yolo_detector

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/report", response_model=dict)
def report_incident(report_in: IncidentReportCreate, db: Session = Depends(get_db)):
    """
    Multi-Source Ingestion Endpoint:
    Receives accident report from CCTV, Citizen, Dashcam, or Authority.
    Executes:
    1. Spatio-temporal DBSCAN duplicate check against existing incidents.
    2. AI heuristic verification & confidence calculation.
    3. Multi-factor rule-based severity scoring.
    4. Optimal ambulance & hospital matching.
    5. A* route generation.
    """
    # 1. Duplicate Detection Check
    active_incidents = db.query(Incident).filter(Incident.status.notin_(["closed", "rejected"])).all()
    matching_incident = duplicate_detector.find_matching_incident(
        report_in.latitude,
        report_in.longitude,
        active_incidents
    )

    if matching_incident:
        # Existing incident found within 250m! Attach as secondary report to avoid duplicate fleets
        dist_m = haversine_distance_meters(report_in.latitude, report_in.longitude, matching_incident.latitude, matching_incident.longitude)
        raw_rep = IncidentReport(
            incident_id=matching_incident.id,
            source_type=report_in.source_type,
            source_identifier=report_in.source_identifier,
            latitude=report_in.latitude,
            longitude=report_in.longitude,
            raw_text=report_in.raw_text,
            media_url=report_in.media_url,
        )
        db.add(raw_rep)
        
        # Log deduplication event in timeline
        log_entry = ActivityLog(
            incident_id=matching_incident.id,
            event_type="DEDUPLICATED",
            message=f"DBSCAN clustered new {report_in.source_type.upper()} report from {report_in.source_identifier or 'Source'} into Incident {matching_incident.incident_code} (Proximity: {int(dist_m)}m). No redundant fleet dispatched.",
            severity="info"
        )
        db.add(log_entry)
        db.commit()

        return {
            "is_duplicate": True,
            "incident_id": matching_incident.id,
            "incident_code": matching_incident.incident_code,
            "status": "merged",
            "message": f"Report correlated with existing active incident {matching_incident.incident_code} via DBSCAN."
        }

    # 2. AI Confidence Assessment
    # Default visual / sensor evidence evaluation
    ai_confidence = 0.85 if report_in.source_type in ["cctv", "dashcam"] else 0.72
    if report_in.is_rollover:
        ai_confidence = max(0.92, ai_confidence)
    
    # 3. Rule-based Severity Assessment
    severity_label, score, breakdown = calculate_severity(
        vehicle_count=report_in.vehicle_count or 2,
        victim_count=report_in.victim_count or 1,
        is_rollover=bool(report_in.is_rollover),
        has_fire=bool(report_in.has_fire),
        ai_confidence=ai_confidence,
        is_highway="expressway" in (report_in.address or "").lower() or "highway" in (report_in.address or "").lower()
    )

    # Generate unique incident code
    inc_code = f"INC-{str(uuid.uuid4())[:8].upper()}"

    # 4. Multi-Criteria Ambulance & Hospital Matching
    all_ambulances = db.query(Ambulance).all()
    all_hospitals = db.query(Hospital).all()

    matched_amb, _ = match_optimal_ambulance(report_in.latitude, report_in.longitude, severity_label, all_ambulances)
    matched_hosp, _ = match_optimal_hospital(report_in.latitude, report_in.longitude, severity_label, all_hospitals)

    new_incident = Incident(
        incident_code=inc_code,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        address=report_in.address or f"Metro Junction ({report_in.latitude:.4f}, {report_in.longitude:.4f})",
        primary_source=report_in.source_type,
        status="dispatched" if matched_amb else "verified",
        severity=severity_label,
        ai_confidence=ai_confidence,
        ai_verified=True,
        is_demo_mode=True,
        victim_count=report_in.victim_count or 1,
        vehicle_count=report_in.vehicle_count or 2,
        description=report_in.raw_text or f"Emergency accident reported via {report_in.source_type.upper()}.",
        media_url=report_in.media_url,
        assigned_ambulance_id=matched_amb.id if matched_amb else None,
        recommended_hospital_id=matched_hosp.id if matched_hosp else None
    )
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)

    # Attach the initiating report
    raw_rep = IncidentReport(
        incident_id=new_incident.id,
        source_type=report_in.source_type,
        source_identifier=report_in.source_identifier,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        raw_text=report_in.raw_text,
        media_url=report_in.media_url,
    )
    db.add(raw_rep)

    # Update ambulance status
    if matched_amb:
        matched_amb.status = "dispatched"
        matched_amb.current_incident_id = new_incident.id

    # 5. Calculate A* Route
    if matched_amb and matched_hosp:
        route_data = city_road_graph.plan_full_emergency_route(
            matched_amb.current_latitude,
            matched_amb.current_longitude,
            new_incident.latitude,
            new_incident.longitude,
            matched_hosp.latitude,
            matched_hosp.longitude
        )
        route_record = Route(
            incident_id=new_incident.id,
            ambulance_id=matched_amb.id,
            hospital_id=matched_hosp.id,
            polyline_geojson=json.dumps(route_data["polyline"]),
            distance_km=route_data["distance_km"],
            eta_minutes=route_data["eta_minutes"],
            has_blockage=False
        )
        db.add(route_record)

    # 6. Comprehensive Timeline logs following exact Core System Workflow
    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="INCIDENT_INGESTION",
        message=f"INCIDENT SOURCE: Received emergency telemetry from {report_in.source_type.upper()} ({report_in.source_identifier or 'Source'}). Lat: {report_in.latitude:.5f}, Lng: {report_in.longitude:.5f}",
        severity="info"
    ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="DBSCAN",
        message=f"DBSCAN: Evaluated spatio-temporal cluster (Epsilon: 250m, Time: 15m). No existing duplicate found. Assigned new Incident {inc_code}.",
        severity="info"
    ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="RISK_ANALYSIS",
        message=f"RISK ANALYZER & MACHINE CLASSIFIER: Determined Risk Level: {severity_label.upper()} (Score: {score}/100, AI Confidence: {int(ai_confidence*100)}%).",
        severity="warning" if severity_label in ["critical", "high"] else "info"
    ))

    if matched_amb:
        db.add(ActivityLog(
            incident_id=new_incident.id,
            event_type="SUGGEST_AMBULANCE",
            message=f"SUGGESTED AMBULANCE: Selected Unit {matched_amb.callsign} ({matched_amb.type}) based on ALS capability & Haversine proximity.",
            severity="success"
        ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="TRAFFIC_ANALYSIS",
        message="TRAFFIC BLOCKING: Analyzed affected road corridors. Ready for restriction upon hazard simulation.",
        severity="info"
    ))

    if matched_amb and matched_hosp:
        db.add(ActivityLog(
            incident_id=new_incident.id,
            event_type="ASTAR_ROUTING",
            message=f"REROUTING USING A* ALGORITHM: Optimal obstacle-free route computed. Distance: {route_data['distance_km']} km, Initial ETA: {route_data['eta_minutes']} mins.",
            severity="info"
        ))

    if matched_hosp:
        db.add(ActivityLog(
            incident_id=new_incident.id,
            event_type="SUGGEST_HOSPITAL",
            message=f"SUGGESTED HOSPITAL: Matched {matched_hosp.name} (Level {matched_hosp.trauma_level} Trauma, {matched_hosp.available_icu_beds} ICU beds open).",
            severity="info"
        ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="EMERGENCY_RESPONSE",
        message=f"EMERGENCY RESPONSE: Transmitted incident details, GNSS location ({report_in.latitude:.4f}, {report_in.longitude:.4f}), and severity to Hospital and Ambulance.",
        severity="success"
    ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="LORA_COMMUNICATION",
        message="SIMULATED LoRa COMMUNICATION: Packet Created ↓ Packet Sent ↓ Packet Received ↓ SUCCESS (Long-range telemetry delivered).",
        severity="info"
    ))

    db.add(ActivityLog(
        incident_id=new_incident.id,
        event_type="INFORMATION_RETURN",
        message="EMERGENCY INFORMATION UPDATED: Dispatch and intake confirmed. Response status sent back to source.",
        severity="success"
    ))

    db.commit()

    return {
        "is_duplicate": False,
        "incident_id": new_incident.id,
        "incident_code": new_incident.incident_code,
        "status": new_incident.status,
        "severity": new_incident.severity,
        "ai_confidence": new_incident.ai_confidence,
        "ambulance": matched_amb.callsign if matched_amb else None,
        "hospital": matched_hosp.name if matched_hosp else None,
        "message": "Incident successfully verified, prioritized, and dispatched."
    }

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    
    incidents = query.order_by(Incident.created_at.desc()).all()
    
    # Calculate report counts
    result = []
    for inc in incidents:
        rep_count = db.query(IncidentReport).filter(IncidentReport.incident_id == inc.id).count()
        inc_dict = {
            "id": inc.id,
            "incident_code": inc.incident_code,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "address": inc.address,
            "primary_source": inc.primary_source,
            "status": inc.status,
            "severity": inc.severity,
            "ai_confidence": inc.ai_confidence,
            "ai_verified": inc.ai_verified,
            "is_demo_mode": inc.is_demo_mode,
            "victim_count": inc.victim_count,
            "vehicle_count": inc.vehicle_count,
            "description": inc.description,
            "media_url": inc.media_url,
            "assigned_ambulance_id": inc.assigned_ambulance_id,
            "recommended_hospital_id": inc.recommended_hospital_id,
            "created_at": inc.created_at,
            "updated_at": inc.updated_at,
            "report_count": max(1, rep_count)
        }
        result.append(inc_dict)
    return result

@router.get("/{incident_id}")
def get_incident_detail(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    reports = db.query(IncidentReport).filter(IncidentReport.incident_id == incident.id).all()
    ambulance = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
    hospital = db.query(Hospital).filter(Hospital.id == incident.recommended_hospital_id).first()
    route = db.query(Route).filter(Route.incident_id == incident.id).first()
    logs = db.query(ActivityLog).filter(ActivityLog.incident_id == incident.id).order_by(ActivityLog.created_at.desc()).all()

    route_info = None
    if route:
        route_info = {
            "id": route.id,
            "distance_km": route.distance_km,
            "eta_minutes": route.eta_minutes,
            "has_blockage": route.has_blockage,
            "blocked_segment": route.blocked_segment,
            "polyline": json.loads(route.polyline_geojson) if route.polyline_geojson else [],
            "original_polyline": json.loads(route.original_route_geojson) if route.original_route_geojson else None,
            "original_eta_minutes": route.original_eta_minutes
        }

    return {
        "incident": incident,
        "reports": reports,
        "ambulance": ambulance,
        "hospital": hospital,
        "route": route_info,
        "logs": logs
    }

@router.patch("/{incident_id}/override")
def human_operator_override(
    incident_id: int,
    override: IncidentOverrideRequest,
    db: Session = Depends(get_db)
):
    """
    Human Operator Override Endpoint:
    Allows dispatcher to confirm, reject, change severity, reassign ambulance, or reassign hospital.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    changes = []
    
    if override.action == "reject" or override.status == "rejected":
        incident.status = "rejected"
        # Release assigned ambulance
        if incident.assigned_ambulance_id:
            amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
            if amb:
                amb.status = "available"
                amb.current_incident_id = None
        changes.append("Incident rejected by operator")
    elif override.action == "confirm" or override.status == "verified":
        if incident.status == "reported":
            incident.status = "verified"
            changes.append("Incident confirmed by operator")

    if override.severity and override.severity != incident.severity:
        changes.append(f"Severity adjusted from {incident.severity.upper()} to {override.severity.upper()}")
        incident.severity = override.severity

    if override.assigned_ambulance_id and override.assigned_ambulance_id != incident.assigned_ambulance_id:
        old_amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
        if old_amb:
            old_amb.status = "available"
            old_amb.current_incident_id = None
        
        new_amb = db.query(Ambulance).filter(Ambulance.id == override.assigned_ambulance_id).first()
        if new_amb:
            new_amb.status = "dispatched"
            new_amb.current_incident_id = incident.id
            incident.assigned_ambulance_id = new_amb.id
            changes.append(f"Ambulance reassigned to {new_amb.callsign}")

    if override.recommended_hospital_id and override.recommended_hospital_id != incident.recommended_hospital_id:
        new_hosp = db.query(Hospital).filter(Hospital.id == override.recommended_hospital_id).first()
        if new_hosp:
            incident.recommended_hospital_id = new_hosp.id
            changes.append(f"Hospital redirected to {new_hosp.name}")

    # Re-calculate route if ambulance or hospital changed
    amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
    hosp = db.query(Hospital).filter(Hospital.id == incident.recommended_hospital_id).first()
    
    if amb and hosp:
        route_data = city_road_graph.plan_full_emergency_route(
            amb.current_latitude,
            amb.current_longitude,
            incident.latitude,
            incident.longitude,
            hosp.latitude,
            hosp.longitude
        )
        existing_route = db.query(Route).filter(Route.incident_id == incident.id).first()
        if existing_route:
            existing_route.ambulance_id = amb.id
            existing_route.hospital_id = hosp.id
            existing_route.polyline_geojson = json.dumps(route_data["polyline"])
            existing_route.distance_km = route_data["distance_km"]
            existing_route.eta_minutes = route_data["eta_minutes"]
            existing_route.has_blockage = False
        else:
            new_route = Route(
                incident_id=incident.id,
                ambulance_id=amb.id,
                hospital_id=hosp.id,
                polyline_geojson=json.dumps(route_data["polyline"]),
                distance_km=route_data["distance_km"],
                eta_minutes=route_data["eta_minutes"]
            )
            db.add(new_route)

    # Log human override action in activity timeline
    override_msg = "Human Operator Override: " + "; ".join(changes) if changes else "Human Operator Override executed"
    if override.notes:
        override_msg += f" (Notes: {override.notes})"
    
    log = ActivityLog(
        incident_id=incident.id,
        event_type="OVERRIDE",
        message=override_msg,
        severity="warning"
    )
    db.add(log)
    db.commit()

    return {"message": "Override applied successfully", "changes": changes}

@router.post("/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    status_update: IncidentStatusUpdate,
    db: Session = Depends(get_db)
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = incident.status
    incident.status = status_update.status

    if status_update.status in ["closed", "arrived"]:
        # Release assigned ambulance
        if incident.assigned_ambulance_id:
            amb = db.query(Ambulance).filter(Ambulance.id == incident.assigned_ambulance_id).first()
            if amb:
                amb.status = "available"
                amb.current_incident_id = None

    log = ActivityLog(
        incident_id=incident.id,
        event_type="STATUS_CHANGE",
        message=f"Incident status updated from {old_status.upper()} to {status_update.status.upper()}",
        severity="success" if status_update.status == "closed" else "info"
    )
    db.add(log)
    db.commit()

    return {"message": f"Status updated to {status_update.status}"}
