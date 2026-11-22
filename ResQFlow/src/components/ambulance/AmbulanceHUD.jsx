import React, { useState } from 'react';
import { 
  Truck, 
  Navigation, 
  AlertTriangle, 
  MapPin, 
  Building2, 
  CheckCircle2, 
  Clock, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';
import { api } from '../../services/api';

export default function AmbulanceHUD({ 
  ambulances = [], 
  incidents = [], 
  activeRoute = null, 
  onRefresh 
}) {
  const [selectedAmbId, setSelectedAmbId] = useState(
    ambulances.find(a => a.status === 'dispatched')?.id || ambulances[0]?.id || ''
  );

  const currentAmb = ambulances.find(a => a.id === parseInt(selectedAmbId)) || ambulances[0];
  const assignedIncident = incidents.find(i => i.assigned_ambulance_id === currentAmb?.id && !['closed', 'rejected'].includes(i.status));

  const handleUpdateDriverStatus = async (status) => {
    if (!assignedIncident) return;
    try {
      await api.updateIncidentStatus(assignedIncident.id, status);
      if (status === 'arrived') {
        await api.updateAmbulanceLocation(currentAmb.id, {
          latitude: currentAmb.current_latitude,
          longitude: currentAmb.current_longitude,
          status: 'available'
        });
      }
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Failed to update driver status: ' + e.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-4">
      {/* Unit Selector Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Truck className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-black text-white">
              Ambulance Driver HUD & Navigation Terminal
            </h2>
            <p className="text-xs text-slate-400">
              In-Vehicle Tactical Telemetry & Dynamic Rerouting System
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <label className="text-slate-400 font-bold">Select Unit:</label>
          <select
            value={selectedAmbId}
            onChange={(e) => setSelectedAmbId(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-bold focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            {ambulances.map((amb) => (
              <option key={amb.id} value={amb.id}>
                {amb.callsign} ({amb.type}) — {amb.status.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main HUD Dashboard */}
      {!assignedIncident ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-12 text-center text-slate-500 space-y-3">
          <Truck className="h-12 w-12 mx-auto text-slate-600 animate-pulse" />
          <div className="text-sm font-bold text-slate-300">
            Unit {currentAmb?.callsign || 'Fleet'} is on STANDBY
          </div>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Ready for dispatch. No active emergency assigned to this unit currently.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          
          {/* Dynamic Road Blockage Alert Banner */}
          {activeRoute?.has_blockage && (
            <div className="bg-amber-950/80 border-2 border-amber-500 rounded-2xl p-4 shadow-2xl animate-pulse">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-7 w-7 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-black text-amber-300 uppercase tracking-wide">
                    ⚠️ TACTICAL REROUTE ALERT: ROAD OBSTRUCTION AHEAD
                  </div>
                  <div className="text-xs text-slate-200 mt-1">
                    <strong>{activeRoute.blocked_segment}</strong> is blocked. A* dynamic path recalculation complete. Follow highlighted alternate route.
                  </div>
                  <div className="text-xs font-bold text-amber-400 mt-1">
                    New ETA: {activeRoute.eta_minutes} mins (+{(activeRoute.eta_minutes - (activeRoute.original_eta_minutes || 0)).toFixed(1)}m delay)
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Active Mission Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
            
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                  {assignedIncident.severity} PRIORITY
                </span>
                <h3 className="text-lg font-black text-white mt-1">
                  Incident {assignedIncident.incident_code}
                </h3>
              </div>

              <div className="text-right">
                <div className="text-xs text-slate-400 font-semibold">Estimated Arrival</div>
                <div className="text-2xl font-black text-blue-400">
                  {activeRoute?.eta_minutes || 6.5} <span className="text-xs text-slate-300">MINS</span>
                </div>
              </div>
            </div>

            {/* Destination & Pick-up points */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <div className="flex items-center gap-2 text-slate-400 font-bold mb-1">
                  <MapPin className="h-4 w-4 text-red-500" />
                  <span>Scene Location</span>
                </div>
                <div className="text-sm font-black text-white">{assignedIncident.address}</div>
                <div className="text-slate-400 mt-1">
                  Casualties: <strong className="text-red-400">{assignedIncident.victim_count}</strong> | Vehicles: <strong>{assignedIncident.vehicle_count}</strong>
                </div>
              </div>

              <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                <div className="flex items-center gap-2 text-slate-400 font-bold mb-1">
                  <Building2 className="h-4 w-4 text-emerald-400" />
                  <span>Designated Trauma Center</span>
                </div>
                <div className="text-sm font-black text-white">Apollo Metro Trauma Center</div>
                <div className="text-slate-400 mt-1">
                  Trauma Bay Ready • Direct ICU Admission
                </div>
              </div>
            </div>

            {/* Turn-by-Turn Guidance Preview */}
            <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800 text-xs">
              <div className="font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Navigation className="h-4 w-4 text-blue-400" />
                <span>Turn-by-Turn Waypoint Guidance</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-3 p-2 bg-slate-900 rounded-lg border border-slate-800">
                  <span className="h-6 w-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">1</span>
                  <div className="flex-1">
                    <span className="font-bold text-slate-200">Depart North Station via West Arterial</span>
                    <span className="text-[11px] text-slate-400 block">Continue 1.4 km straight</span>
                  </div>
                </div>

                <div className={`flex items-center gap-3 p-2 rounded-lg border ${
                  activeRoute?.has_blockage ? 'bg-amber-950/40 border-amber-600 text-amber-200' : 'bg-slate-900 border-slate-800 text-slate-200'
                }`}>
                  <span className={`h-6 w-6 rounded-full flex items-center justify-center font-bold text-xs ${
                    activeRoute?.has_blockage ? 'bg-amber-500 text-slate-950' : 'bg-blue-600 text-white'
                  }`}>2</span>
                  <div className="flex-1">
                    <span className="font-bold">
                      {activeRoute?.has_blockage ? 'Turn right onto East Valley Parkway (DETOUR)' : 'Merge onto Central Expressway Overpass'}
                    </span>
                    <span className="text-[11px] text-slate-400 block">
                      {activeRoute?.has_blockage ? 'Avoid blocked Central Expressway' : 'Speed Limit 70 km/h • Siren Priority'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-2 bg-slate-900 rounded-lg border border-slate-800">
                  <span className="h-6 w-6 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs">3</span>
                  <div className="flex-1">
                    <span className="font-bold text-slate-200">Arrive at Accident Scene</span>
                    <span className="text-[11px] text-slate-400 block">Deploy ALS trauma kit</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Tactical Driver Action Progression Buttons */}
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                Driver Mission Progression Controls:
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <button
                  type="button"
                  onClick={() => handleUpdateDriverStatus('dispatched')}
                  className={`py-3 rounded-xl font-black text-xs transition border ${
                    assignedIncident.status === 'dispatched'
                      ? 'bg-blue-600 text-white border-blue-400 shadow-lg shadow-blue-900/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  1. Dispatched
                </button>

                <button
                  type="button"
                  onClick={() => handleUpdateDriverStatus('on_scene')}
                  className={`py-3 rounded-xl font-black text-xs transition border ${
                    assignedIncident.status === 'on_scene'
                      ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-lg shadow-amber-900/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  2. On Scene
                </button>

                <button
                  type="button"
                  onClick={() => handleUpdateDriverStatus('transporting')}
                  className={`py-3 rounded-xl font-black text-xs transition border ${
                    assignedIncident.status === 'transporting'
                      ? 'bg-cyan-600 text-white border-cyan-400 shadow-lg shadow-cyan-900/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  3. Transporting
                </button>

                <button
                  type="button"
                  onClick={() => handleUpdateDriverStatus('arrived')}
                  className={`py-3 rounded-xl font-black text-xs transition border ${
                    assignedIncident.status === 'arrived'
                      ? 'bg-emerald-600 text-white border-emerald-400 shadow-lg shadow-emerald-900/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  4. Arrived at ER
                </button>
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
