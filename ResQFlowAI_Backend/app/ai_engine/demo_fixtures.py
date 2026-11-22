from typing import List, Dict, Any

DEMO_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "scenario_highway_dedup",
        "title": "Multi-Source Highway Crash (DBSCAN Deduplication Demo)",
        "description": "Simulates 1 CCTV alert and 2 Citizen 911 reports incoming within 2 minutes for the same collision at Central Expressway. DBSCAN merges all 3 reports into a single canonical incident.",
        "primary_source": "cctv",
        "latitude": 12.9850,
        "longitude": 77.5937,
        "address": "Central Expressway Overpass, Mile Marker 4",
        "victim_count": 2,
        "vehicle_count": 3,
        "is_rollover": False,
        "has_fire": False,
        "ai_confidence": 0.89,
        "severity": "critical",
        "secondary_reports": [
            {
                "source_type": "citizen",
                "source_identifier": "+1-555-0192 (Citizen App)",
                "latitude": 12.9852,
                "longitude": 77.5939,
                "raw_text": "Huge multi-car collision on expressway! Two sedans crushed, people trapped."
            },
            {
                "source_type": "dashcam",
                "source_identifier": "Tesla-ModelY-Telemetry-ID994",
                "latitude": 12.9848,
                "longitude": 77.5935,
                "raw_text": "Sudden deceleration impact alert: Airbags deployed, 42G impact registered."
            }
        ]
    },
    {
        "id": "scenario_rollover_blockage",
        "title": "Severe Rollover Crash with Dynamic Road Blockage",
        "description": "Critical SUV rollover incident blocking Central Expressway Overpass. Demonstrates A* route calculation and instantaneous dynamic rerouting when the user clicks 'SIMULATE ROAD BLOCKAGE'.",
        "primary_source": "dashcam",
        "latitude": 12.9969,
        "longitude": 77.5937,
        "address": "North Ring Road & Tech Junction",
        "victim_count": 3,
        "vehicle_count": 2,
        "is_rollover": True,
        "has_fire": True,
        "ai_confidence": 0.94,
        "severity": "critical",
        "blocked_road_name": "Central Expressway Overpass"
    },
    {
        "id": "scenario_citizen_fender_bender",
        "title": "Citizen Reported Minor Fender-Bender",
        "description": "Citizen reports low-speed fender bender with no injuries. Rule-based severity assesses this as 'Low', matching a BLS ambulance without unnecessarily tying up Level 1 Trauma ICU beds.",
        "primary_source": "citizen",
        "latitude": 12.9650,
        "longitude": 77.5750,
        "address": "West Metro Junction & 5th Cross",
        "victim_count": 0,
        "vehicle_count": 2,
        "is_rollover": False,
        "has_fire": False,
        "ai_confidence": 0.62,
        "severity": "low"
    }
]
