import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Truck, 
  Building2, 
  Navigation, 
  AlertOctagon, 
  Sliders, 
  CheckCircle, 
  XCircle, 
  Layers, 
  Clock, 
  Users, 
  AlertTriangle,
  RotateCcw
} from 'lucide-react';
import { getSeverityStyle, getStatusStyle } from '../../utils/formatters';
import { api } from '../../services/api';

export default function IncidentDetail({ 
  incidentDetail, 
  onRefresh, 
  onOpenOverride 
}) {
  const [blocking, setBlocking] = useState(false);

  if (!incidentDetail || !incidentDetail.incident) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center text-center h-full text-slate-500">
        <Navigation className="h-10 w-10 text-slate-600 mb-2 animate-pulse" />
        <p className="text-sm font-semibold">Select an incident from the queue to view full AI triage and dispatch intelligence.</p>
      </div>
    );
  }

  const { incident, ambulance, hospital, route, reports } = incidentDetail;
  const sevStyle = getSeverityStyle(incident.severity);
  const statusClass = getStatusStyle(incident.status);

  const handleSimulateBlockage = async () => {
    try {
      setBlocking(true);
      await api.simulateRoadBlockage(incident.id, "Central Expressway Overpass");
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Error simulating blockage: ' + e.message);
    } finally {
      setBlocking(false);
    }
  };

  const handleClearBlockage = async () => {
    try {
      setBlocking(true);
      await api.clearRoadBlockage(incident.id);
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Error clearing blockage: ' + e.message);
    } finally {
      setBlocking(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    try {
      await api.updateIncidentStatus(incident.id, newStatus);
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Failed to update status: ' + e.message);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col gap-4 overflow-y-auto max-h-[720px]">
      
      {/* Top Banner: Incident Header & Quick Actions */}
      <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-black text-white tracking-wide">
              {incident.incident_code}
            </h2>
            <span className={`text-[10px] uppercase font-black px-2 py-0.5 rounded ${sevStyle.badge}`}>
              {incident.severity}
            </span>
            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${statusClass}`}>
              {incident.status}
            </span>
          </div>
          <p className="text-xs text-slate-300 font-medium mt-1">
            {incident.address}
          </p>
        </div>

        {/* Human Override Button */}
        <button
          onClick={onOpenOverride}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-700 transition shadow-sm"
        >
          <Sliders className="h-3.5 w-3.5 text-blue-400" />
          <span>Operator Override</span>
        </button>
      </div>

      {/* 1. Mandated Core Workflow Stage Bar */}
      <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-center space-y-1">
        <div className="text-[10px] font-extrabold text-blue-400 uppercase tracking-widest">
          PRIMARY EMERGENCY PROCESSING FLOW
        </div>
        <div className="flex flex-wrap items-center justify-center gap-1.5 text-[10px] font-black text-white">
          <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">SOURCE</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">DBSCAN</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">RISK ANALYZER</span>
          <span>&rarr;</span>
          <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">MACHINE CLASSIFIER</span>
        </div>
      </div>

      {/* 2. Dynamic Routing & Blockage Action Center */}
      <div className={`p-3 rounded-xl border transition-all ${
        route?.has_blockage 
          ? 'bg-amber-950/40 border-amber-500/80 ring-1 ring-amber-500/50' 
          : 'bg-slate-950/60 border-slate-800'
      }`}>
        <div className="flex items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-black text-emerald-400 uppercase tracking-wide">
              <Navigation className="h-4 w-4 text-emerald-400" />
              <span>REROUTING USING A* ALGORITHM</span>
              {route?.has_blockage && (
                <span className="text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-red-600 text-white animate-pulse">
                  TRAFFIC BLOCKED / RESTRICTED
                </span>
              )}
            </div>
            <div className="text-lg font-black text-white mt-1 flex items-baseline gap-2">
              <span className={route?.has_blockage ? 'text-amber-400' : 'text-blue-400'}>
                {route?.eta_minutes || '--'} mins
              </span>
              <span className="text-xs text-slate-400 font-normal">
                ({route?.distance_km || '--'} km)
              </span>
              {route?.has_blockage && route.original_eta_minutes && (
                <span className="text-[11px] text-red-400 font-semibold">
                  (+{(route.eta_minutes - route.original_eta_minutes).toFixed(1)}m delay)
                </span>
              )}
            </div>
          </div>

          {/* DYNAMIC ROAD BLOCKAGE TRIGGER BUTTON */}
          {!route?.has_blockage ? (
            <button
              onClick={handleSimulateBlockage}
              disabled={blocking}
              className="flex items-center gap-1.5 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white font-extrabold text-xs px-3.5 py-2.5 rounded-lg shadow-lg shadow-red-900/40 border border-red-500/40 transition active:scale-95"
            >
              <AlertOctagon className="h-4 w-4 text-white animate-pulse" />
              <span>SIMULATE ROAD BLOCKAGE</span>
            </button>
          ) : (
            <button
              onClick={handleClearBlockage}
              disabled={blocking}
              className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 font-semibold text-xs px-3 py-2 rounded-lg border border-slate-700 transition"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Clear Roadblock</span>
            </button>
          )}
        </div>

        {/* Detailed A* Route Breakdown */}
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-[11px] font-bold text-slate-300">
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Current Ambulance Location:</span>
            <span className="text-blue-300">{ambulance ? `${ambulance.callsign} (${ambulance.base_station})` : 'Base Station'}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Accident Location:</span>
            <span className="text-red-300">{incident.address}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Blocked Road Segment:</span>
            <span className={route?.has_blockage ? 'text-amber-400' : 'text-slate-400'}>
              {route?.has_blockage ? (route.blocked_segment || 'Central Expressway Overpass') : 'None (Open Corridor)'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Alternative Detour Road:</span>
            <span className="text-emerald-300">{route?.has_blockage ? 'East Valley Parkway Detour' : 'Primary Expressway Direct'}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Destination Hospital:</span>
            <span className="text-emerald-300">{hospital ? hospital.name : 'Trauma Center'}</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[9px] uppercase">Distance & Travel Time:</span>
            <span className="text-white">{route?.distance_km || '--'} km | {route?.eta_minutes || '--'} mins</span>
          </div>
        </div>
      </div>

      {/* 3. GNSS & Telemetry Card */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3 space-y-1 text-xs">
        <div className="flex items-center justify-between text-blue-400 font-extrabold uppercase text-[11px]">
          <span>GNSS LOCATION</span>
          <span className="text-slate-400 text-[10px] font-mono">Timestamp: {new Date(incident.created_at || Date.now()).toLocaleTimeString()}</span>
        </div>
        <div className="font-mono text-slate-200 text-[11px]">
          Latitude: <strong className="text-emerald-400">{incident.latitude.toFixed(5)}</strong> | Longitude: <strong className="text-emerald-400">{incident.longitude.toFixed(5)}</strong>
        </div>
      </div>

      {/* 4. Matched Ambulance & Recommended Hospital Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Ambulance Card */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
          <div className="flex items-center justify-between text-xs font-black text-blue-400 uppercase mb-2">
            <span className="flex items-center gap-1.5">
              <Truck className="h-4 w-4" />
              <span>SUGGESTED AMBULANCE</span>
            </span>
            <span className="text-[9px] bg-blue-950 text-blue-300 px-1.5 py-0.5 rounded font-bold border border-blue-800">
              {ambulance?.type || 'ALS'}
            </span>
          </div>

          {ambulance ? (
            <div>
              <div className="text-sm font-black text-white">{ambulance.callsign}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                Base: <span className="text-slate-300">{ambulance.base_station}</span>
              </div>
              <div className="text-[11px] text-emerald-400 font-semibold mt-1">
                Status: {ambulance.status.toUpperCase()}
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-500">No ambulance assigned</div>
          )}
        </div>

        {/* Hospital Card */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
          <div className="flex items-center justify-between text-xs font-black text-emerald-400 uppercase mb-2">
            <span className="flex items-center gap-1.5">
              <Building2 className="h-4 w-4" />
              <span>SUGGESTED HOSPITAL</span>
            </span>
            <span className="text-[9px] bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded font-bold border border-emerald-800">
              Level {hospital?.trauma_level || 1}
            </span>
          </div>

          {hospital ? (
            <div>
              <div className="text-sm font-black text-white line-clamp-1">{hospital.name}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                ICU Beds: <span className="text-emerald-400 font-bold">{hospital.available_icu_beds}</span> open
              </div>
              <div className="text-[11px] text-slate-400">
                ER Beds: <span className="text-blue-400 font-bold">{hospital.available_er_beds}</span> open
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-500">No hospital matched</div>
          )}
        </div>
      </div>

      {/* 4. Multi-Source Reports Feed (DBSCAN Evidence) */}
      <div className="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3">
        <div className="flex items-center justify-between text-xs font-bold text-slate-300 mb-2">
          <span className="flex items-center gap-1.5">
            <Layers className="h-4 w-4 text-purple-400" />
            <span>Correlated Ingestion Reports ({reports?.length || 1})</span>
          </span>
          <span className="text-[9px] bg-purple-950 text-purple-300 px-1.5 py-0.5 rounded border border-purple-800">
            DBSCAN Clustered
          </span>
        </div>

        <div className="space-y-1.5 max-h-32 overflow-y-auto text-[11px]">
          {reports && reports.map((rep) => (
            <div key={rep.id} className="bg-slate-900/80 p-2 rounded border border-slate-800/80">
              <div className="flex items-center justify-between">
                <span className="font-bold text-purple-300 uppercase text-[10px]">
                  {rep.source_type} • {rep.source_identifier || 'Unknown'}
                </span>
                <span className="text-[9px] text-slate-400">
                  {new Date(rep.reported_at).toLocaleTimeString()}
                </span>
              </div>
              <div className="text-slate-300 mt-1">{rep.raw_text}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 5. Status Transition Workflow Buttons */}
      <div className="pt-2 border-t border-slate-800 flex items-center justify-between gap-2">
        <span className="text-[11px] text-slate-400 font-medium">Quick Status:</span>
        <div className="flex items-center gap-1.5">
          {incident.status === 'reported' && (
            <button
              onClick={() => handleUpdateStatus('verified')}
              className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-xs font-bold"
            >
              Verify
            </button>
          )}
          {incident.status === 'verified' && (
            <button
              onClick={() => handleUpdateStatus('dispatched')}
              className="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold"
            >
              Dispatch Fleet
            </button>
          )}
          {incident.status === 'dispatched' && (
            <button
              onClick={() => handleUpdateStatus('on_scene')}
              className="px-2.5 py-1 bg-amber-600 hover:bg-amber-500 text-slate-950 rounded text-xs font-bold"
            >
              Mark On Scene
            </button>
          )}
          {incident.status === 'on_scene' && (
            <button
              onClick={() => handleUpdateStatus('transporting')}
              className="px-2.5 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-bold"
            >
              Transporting
            </button>
          )}
          {incident.status === 'transporting' && (
            <button
              onClick={() => handleUpdateStatus('arrived')}
              className="px-2.5 py-1 bg-teal-600 hover:bg-teal-500 text-white rounded text-xs font-bold"
            >
              Hospital Arrival
            </button>
          )}
          {incident.status === 'arrived' && (
            <button
              onClick={() => handleUpdateStatus('closed')}
              className="px-2.5 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs font-bold flex items-center gap-1"
            >
              <CheckCircle className="h-3 w-3 text-emerald-400" />
              Close Incident
            </button>
          )}
        </div>
      </div>

    </div>
  );
}
