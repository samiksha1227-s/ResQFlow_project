# ResQFlow AI — Source-Agnostic Emergency Response and Coordination System

> **20-Hour Hackathon Prototype**  
> An AI-assisted multi-source emergency detection, verification, deduplication, triage, and dynamic routing system.

---

## 🌟 Key Features

1. **Source-Agnostic Ingestion Layer**:
   - Ingests emergency telemetry from 4 distinct channels:
     - 📹 **CCTV / Traffic Surveillance Video**
     - 📱 **Citizen Mobile SOS App**
     - 🚗 **Vehicle Telemetry / Dashcam Impact Alerts**
     - 🏛️ **Traffic Authority & Municipal Sensor Feeds**

2. **AI Verification & Collision Confidence Layer**:
   - Combines object detection with a prototype event heuristic layer.
   - Evaluates bounding box geometric intersection (IoU), abnormal orientation/rollover aspect ratios, and pedestrian-to-hazard proximity.
   - Clearly labeled for hackathon prototype evaluation with Demo Mode indicators.

3. **Spatio-Temporal Duplicate Detection (DBSCAN)**:
   - Uses spatial epsilon ($\le 250$m) and time window ($\le 15$m) clustering.
   - Merges multiple incoming reports of the same accident into a single canonical incident, preventing redundant fleet dispatch.

4. **Multi-Factor Rule-Based Severity Assessment**:
   - Evaluates casualty count, vehicle count, rollover inversion, fire hazard, and road speed limits to classify priority (`Critical`, `High`, `Medium`, `Low`).

5. **Resource Optimization Engines**:
   - **Ambulance Matching**: Weighted scoring factoring in Haversine distance, ALS (Advanced Life Support) vs. BLS capability matching, and fleet readiness.
   - **Hospital Matching**: Multi-criteria scoring prioritizing Level 1 Trauma centers and real-time open ICU/ER bed capacity for severe injuries.

6. **A* Route Planning & Dynamic Rerouting**:
   - Computes optimal emergency routes across an urban road network graph.
   - **"SIMULATE ROAD BLOCKAGE"**: When triggered, marks designated road segments impassable, instantly re-executes A* to find alternative detours, updates ETA, and logs the event to the operational timeline.

7. **Four Unified Operational Views**:
   - 👮 **Operator / Police Command Dashboard**: Full tactical Leaflet map, active incidents queue, AI inspection cards, blockage simulator, and live timeline.
   - 👥 **Citizen SOS Portal**: Quick 1-click incident reporting with location presets and live status ticket tracking.
   - 🚑 **Ambulance Driver HUD**: Turn-by-turn navigation guidance, dynamic blockage alert banners, and driver status progression controls.
   - 🏥 **Hospital Trauma Desk**: Inbound ambulance tracking, patient triage summary, live ICU/ER bed management, and intake confirmation.

---

## 🚀 Quick Start Instructions

### 1. Launch Backend (FastAPI)
```powershell
# From project root
.\run_backend.bat
```
*Or manually via PowerShell:*
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python run.py
```
- **Backend URL**: `http://localhost:8000`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`

### 2. Launch Frontend (React + Vite)
```powershell
# In a second terminal from project root
.\run_frontend.bat
```
*Or manually:*
```powershell
cd frontend
npm run dev
```
- **Frontend Dashboard**: `http://localhost:5173`

---

## 🎬 3-Minute Hackathon Demo Script

1. **Scene 1: Multi-Source Ingestion & DBSCAN Deduplication (0:00 - 0:45)**
   - Open the **Operator Dashboard** at `http://localhost:5173`.
   - Switch to **Citizen SOS** view in another tab and submit a report near *Central Expressway Overpass*.
   - Return to Operator Center: Note how **DBSCAN** recognized the spatial proximity ($\le 250$m) and merged the report into the active incident without dispatching redundant fleets.
   - Point out the `2 Linked (DBSCAN)` badge on the incident card.

2. **Scene 2: Automated Dispatch & Hospital Matching (0:45 - 1:30)**
   - Click on the active incident in the queue.
   - Show that the system automatically matched:
     - **Ambulance**: `MEDIC-101 (ALS)` (closest available unit with Advanced Life Support equipment).
     - **Hospital**: `Metro Comprehensive Trauma Center` (Level 1 Trauma facility with available ICU beds).
   - Point out the active blue route on the Leaflet map and ETA of ~6.5 mins.

3. **Scene 3: Dynamic Rerouting ("SIMULATE ROAD BLOCKAGE") (1:30 - 2:15)**
   - In the right-hand panel, click the prominent **"SIMULATE ROAD BLOCKAGE"** button.
   - A hazard barrier appears on the map over *Central Expressway Overpass*.
   - A* immediately calculates an alternate route (shown in green/amber), updates the ETA, and logs a high-priority alert to the Live Operations Audit Timeline.
   - Switch to **Ambulance HUD** tab to show the driver's screen receiving the instant reroute warning!

4. **Scene 4: Human Operator Override (2:15 - 2:45)**
   - In the Operator Dashboard, click **"Operator Override"**.
   - Show how the dispatcher can manually adjust severity, reassign the ambulance, or redirect the hospital destination, with immediate route recalculation.

5. **Scene 5: Hospital Intake & Incident Closure (2:45 - 3:00)**
   - Switch to the **Hospital Desk** tab.
   - Review the incoming ambulance tracking board.
   - Click **"Admit Patient & Close"** to admit the casualty, update available ICU bed capacity, and mark the emergency closed.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, Leaflet, React-Leaflet, Lucide React, Axios |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, SQLite, Pydantic |
| **AI & Vision** | YOLOv8 object detector integration, Geometric Bounding Box IoU heuristic, Aspect ratio roll detection |
| **Algorithms** | Haversine Geodesic Distance, DBSCAN Spatio-temporal Clustering, Rule-based Multi-factor Severity Scoring, Multi-criteria Decision Analysis (MCDA), A* Shortest Path Graph Router |

---

*Note: Built for hackathon demonstration. Features simulated ambulance and hospital telemetry.*
