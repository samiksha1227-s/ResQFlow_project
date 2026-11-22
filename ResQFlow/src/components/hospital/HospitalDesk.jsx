import React, { useState } from 'react';
import { 
  Building2, 
  Truck, 
  Activity, 
  CheckCircle, 
  Bed, 
  AlertCircle, 
  Clock, 
  Plus, 
  Minus,
  ShieldAlert
} from 'lucide-react';
import { api } from '../../services/api';
import { getSeverityStyle } from '../../utils/formatters';

export default function HospitalDesk({ 
  hospitals = [], 
  incidents = [], 
  ambulances = [], 
  onRefresh 
}) {
  const [selectedHospId, setSelectedHospId] = useState(hospitals[0]?.id || '');
  const currentHosp = hospitals.find(h => h.id === parseInt(selectedHospId)) || hospitals[0];

  // Incidents assigned to this hospital
  const inboundIncidents = incidents.filter(i => 
    i.recommended_hospital_id === currentHosp?.id && !['closed', 'rejected'].includes(i.status)
  );

  const handleAdjustBed = async (type, delta) => {
    if (!currentHosp) return;
    try {
      const newIcu = type === 'icu' ? Math.max(0, currentHosp.available_icu_beds + delta) : currentHosp.available_icu_beds;
      const newEr = type === 'er' ? Math.max(0, currentHosp.available_er_beds + delta) : currentHosp.available_er_beds;
      
      await api.updateHospitalCapacity(currentHosp.id, {
        available_icu_beds: newIcu,
        available_er_beds: newEr
      });
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Error updating capacity: ' + e.message);
    }
  };

  const handleAdmitAndClose = async (incidentId) => {
    try {
      await api.updateIncidentStatus(incidentId, 'closed');
      // Decrement 1 ICU bed
      if (currentHosp && currentHosp.available_icu_beds > 0) {
        await api.updateHospitalCapacity(currentHosp.id, {
          available_icu_beds: currentHosp.available_icu_beds - 1
        });
      }
      if (onRefresh) onRefresh();
    } catch (e) {
      alert('Failed to admit patient: ' + e.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-4">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-600/20 text-emerald-400 border border-emerald-500/30">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-black text-white">
              Hospital Emergency Intake & Trauma Command
            </h2>
            <p className="text-xs text-slate-400">
              Live Patient Telemetry, Bed Allocation & Inbound Fleet Coordination
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <label className="text-slate-400 font-bold">Select Facility:</label>
          <select
            value={selectedHospId}
            onChange={(e) => setSelectedHospId(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-bold focus:ring-2 focus:ring-emerald-500 focus:outline-none"
          >
            {hospitals.map((hosp) => (
              <option key={hosp.id} value={hosp.id}>
                {hosp.name} (Level {hosp.trauma_level})
              </option>
            ))}
          </select>
        </div>
      </div>

      {currentHosp && (
        <div className="space-y-4">
          
          {/* Facility Status & Bed Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            
            {/* Trauma Level Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-400">Trauma Designation</div>
                <div className="text-xl font-black text-white mt-1">
                  Level {currentHosp.trauma_level} Trauma Center
                </div>
                <div className="text-[11px] text-emerald-400 font-semibold mt-0.5">
                  Comprehensive 24/7 Surgical Readiness
                </div>
              </div>
              <div className="h-10 w-10 rounded-lg bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400 font-black text-base">
                L{currentHosp.trauma_level}
              </div>
            </div>

            {/* ICU Beds Card with Increment/Decrement Controls */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-400">Available ICU Beds</div>
                <div className="text-2xl font-black text-emerald-400 mt-1 flex items-baseline gap-1.5">
                  {currentHosp.available_icu_beds}
                  <span className="text-xs text-slate-400 font-normal">/ {currentHosp.total_icu_beds}</span>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleAdjustBed('icu', -1)}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
                >
                  <Minus className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => handleAdjustBed('icu', 1)}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            {/* ER Beds Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-400">Available ER Beds</div>
                <div className="text-2xl font-black text-blue-400 mt-1 flex items-baseline gap-1.5">
                  {currentHosp.available_er_beds}
                  <span className="text-xs text-slate-400 font-normal">/ {currentHosp.total_er_beds}</span>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleAdjustBed('er', -1)}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
                >
                  <Minus className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => handleAdjustBed('er', 1)}
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

          </div>

          {/* Inbound Ambulances & Patient Triage Queue */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-black text-white flex items-center gap-2">
                <Truck className="h-4 w-4 text-blue-400" />
                <span>Inbound Emergency Fleet & Patient Pre-Arrival Brief</span>
              </h3>
              <span className="text-xs text-slate-400 font-semibold">
                {inboundIncidents.length} Inbound Ambulance(s)
              </span>
            </div>

            {inboundIncidents.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs">
                No inbound emergency patients en route to {currentHosp.name} at this moment.
              </div>
            ) : (
              <div className="space-y-3">
                {inboundIncidents.map((inc) => {
                  const amb = ambulances.find(a => a.id === inc.assigned_ambulance_id);
                  const sevStyle = getSeverityStyle(inc.severity);

                  return (
                    <div
                      key={inc.id}
                      className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-black text-white tracking-wider">
                            {inc.incident_code}
                          </span>
                          <span className={`text-[10px] uppercase font-black px-2 py-0.5 rounded ${sevStyle.badge}`}>
                            {inc.severity}
                          </span>
                          <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">
                            Unit: {amb?.callsign || 'Assigned'}
                          </span>
                        </div>

                        <div className="text-xs text-slate-300 font-medium">
                          Location: {inc.address}
                        </div>

                        <div className="text-[11px] text-slate-400">
                          Victims: <strong className="text-red-400">{inc.victim_count}</strong> | AI Confidence: <strong className="text-emerald-400">{Math.round((inc.ai_confidence || 0.85) * 100)}%</strong>
                        </div>
                      </div>

                      {/* Admit Patient & Close Action */}
                      <div className="flex sm:flex-col items-end gap-2 shrink-0">
                        <div className="text-right">
                          <span className="text-[10px] text-slate-400 uppercase font-bold">Estimated Arrival</span>
                          <div className="text-xl font-black text-emerald-400 flex items-center justify-end gap-1">
                            <Clock className="h-4 w-4 text-emerald-400" />
                            <span>5.8 mins</span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleAdmitAndClose(inc.id)}
                          className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-3 py-2 rounded-lg shadow-md shadow-emerald-900/40 transition"
                        >
                          <CheckCircle className="h-4 w-4" />
                          <span>Admit Patient & Close</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
