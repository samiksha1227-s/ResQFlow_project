import React from 'react';
import { AlertTriangle, Flame, Truck, Hospital as HospIcon, Clock } from 'lucide-react';

export default function MetricCards({ incidents = [], ambulances = [], hospitals = [] }) {
  const activeIncidents = incidents.filter(i => !['closed', 'rejected'].includes(i.status));
  const criticalIncidents = activeIncidents.filter(i => i.severity === 'critical');
  const availableAmbulances = ambulances.filter(a => a.status === 'available');
  
  const totalIcuAvailable = hospitals.reduce((sum, h) => sum + (h.available_icu_beds || 0), 0);
  const totalIcuCapacity = hospitals.reduce((sum, h) => sum + (h.total_icu_beds || 0), 0);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* 1. Active Incidents */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-400">Active Emergencies</div>
          <div className="text-2xl font-black text-white mt-0.5 flex items-baseline gap-2">
            {activeIncidents.length}
            {criticalIncidents.length > 0 && (
              <span className="text-xs font-bold text-red-400 bg-red-950/80 px-2 py-0.5 rounded-md border border-red-800/60 flex items-center gap-1">
                <Flame className="h-3 w-3 text-red-500 animate-pulse" />
                {criticalIncidents.length} Critical
              </span>
            )}
          </div>
        </div>
        <div className="h-10 w-10 rounded-lg bg-red-950/60 border border-red-800/40 flex items-center justify-center text-red-400">
          <AlertTriangle className="h-5 w-5" />
        </div>
      </div>

      {/* 2. Available Ambulances */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-400">Ambulance Fleet</div>
          <div className="text-2xl font-black text-white mt-0.5 flex items-baseline gap-1.5">
            <span className="text-emerald-400">{availableAmbulances.length}</span>
            <span className="text-sm text-slate-400 font-medium">/ {ambulances.length} ready</span>
          </div>
        </div>
        <div className="h-10 w-10 rounded-lg bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center text-emerald-400">
          <Truck className="h-5 w-5" />
        </div>
      </div>

      {/* 3. Hospital Beds */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-400">Trauma ICU Beds</div>
          <div className="text-2xl font-black text-white mt-0.5 flex items-baseline gap-1.5">
            <span className="text-blue-400">{totalIcuAvailable}</span>
            <span className="text-sm text-slate-400 font-medium">/ {totalIcuCapacity} open</span>
          </div>
        </div>
        <div className="h-10 w-10 rounded-lg bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400">
          <HospIcon className="h-5 w-5" />
        </div>
      </div>

      {/* 4. Average Response ETA */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-center justify-between">
        <div>
          <div className="text-xs font-semibold text-slate-400">Avg Response ETA</div>
          <div className="text-2xl font-black text-white mt-0.5 flex items-baseline gap-1">
            6.2 <span className="text-xs text-slate-400 font-normal">mins</span>
          </div>
        </div>
        <div className="h-10 w-10 rounded-lg bg-purple-950/60 border border-purple-800/40 flex items-center justify-center text-purple-400">
          <Clock className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
