import React, { useState, useEffect } from 'react';
import { X, Sliders, AlertTriangle, ShieldCheck, Truck, Building2, Check, Ban } from 'lucide-react';
import { api } from '../../services/api';

export default function HumanOverrideModal({ 
  isOpen, 
  onClose, 
  incidentDetail, 
  ambulances = [], 
  hospitals = [], 
  onSuccess 
}) {
  if (!isOpen || !incidentDetail?.incident) return null;

  const { incident, ambulance, hospital } = incidentDetail;

  const [severity, setSeverity] = useState(incident.severity || 'medium');
  const [selectedAmbulanceId, setSelectedAmbulanceId] = useState(incident.assigned_ambulance_id || '');
  const [selectedHospitalId, setSelectedHospitalId] = useState(incident.recommended_hospital_id || '');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setSeverity(incident.severity || 'medium');
    setSelectedAmbulanceId(incident.assigned_ambulance_id || '');
    setSelectedHospitalId(incident.recommended_hospital_id || '');
  }, [incident]);

  const handleApplyOverride = async (action = 'override') => {
    try {
      setSaving(true);
      await api.overrideIncident(incident.id, {
        action: action,
        severity: severity,
        assigned_ambulance_id: selectedAmbulanceId ? parseInt(selectedAmbulanceId) : null,
        recommended_hospital_id: selectedHospitalId ? parseInt(selectedHospitalId) : null,
        notes: notes
      });
      if (onSuccess) onSuccess();
      onClose();
    } catch (e) {
      alert('Override failed: ' + e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <Sliders className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-black text-white">
                Human Operator Override — {incident.incident_code}
              </h3>
              <p className="text-[11px] text-slate-400">
                Manual dispatcher override takes immediate precedence over AI recommendation.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Form Content */}
        <div className="p-5 space-y-4 text-xs">
          
          {/* 1. Confirm / Reject Incident */}
          <div>
            <label className="block text-slate-300 font-bold mb-1.5">
              Incident Validation Status
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleApplyOverride('confirm')}
                className="flex items-center justify-center gap-1.5 p-2.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-700/60 text-emerald-400 font-bold transition"
              >
                <Check className="h-4 w-4" />
                <span>Confirm Incident</span>
              </button>

              <button
                type="button"
                onClick={() => handleApplyOverride('reject')}
                className="flex items-center justify-center gap-1.5 p-2.5 rounded-lg bg-red-950/60 hover:bg-red-900/60 border border-red-700/60 text-red-400 font-bold transition"
              >
                <Ban className="h-4 w-4" />
                <span>Reject / False Alarm</span>
              </button>
            </div>
          </div>

          {/* 2. Change Severity */}
          <div>
            <label className="block text-slate-300 font-bold mb-1.5">
              Override Severity Level
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {['low', 'medium', 'high', 'critical'].map((sev) => (
                <button
                  key={sev}
                  type="button"
                  onClick={() => setSeverity(sev)}
                  className={`py-2 rounded-lg font-bold capitalize transition border text-center ${
                    severity === sev
                      ? 'bg-blue-600 border-blue-400 text-white shadow-md'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>
          </div>

          {/* 3. Change Assigned Ambulance */}
          <div>
            <label className="block text-slate-300 font-bold mb-1.5 flex items-center gap-1.5">
              <Truck className="h-3.5 w-3.5 text-blue-400" />
              <span>Reassign Ambulance Fleet</span>
            </label>
            <select
              value={selectedAmbulanceId}
              onChange={(e) => setSelectedAmbulanceId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">-- Select Ambulance --</option>
              {ambulances.map((amb) => (
                <option key={amb.id} value={amb.id}>
                  {amb.callsign} ({amb.type}) — Status: {amb.status.toUpperCase()} [{amb.base_station}]
                </option>
              ))}
            </select>
          </div>

          {/* 4. Change Recommended Hospital */}
          <div>
            <label className="block text-slate-300 font-bold mb-1.5 flex items-center gap-1.5">
              <Building2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>Redirect Destination Hospital</span>
            </label>
            <select
              value={selectedHospitalId}
              onChange={(e) => setSelectedHospitalId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">-- Select Hospital --</option>
              {hospitals.map((hosp) => (
                <option key={hosp.id} value={hosp.id}>
                  {hosp.name} (Level {hosp.trauma_level} Trauma) — {hosp.available_icu_beds} ICU Beds Open
                </option>
              ))}
            </select>
          </div>

          {/* 5. Dispatcher Notes */}
          <div>
            <label className="block text-slate-300 font-bold mb-1.5">
              Dispatcher Reason / Audit Note
            </label>
            <input
              type="text"
              placeholder="e.g. Traffic surge on Ring Rd; assigned regional clinic instead."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200 placeholder-slate-600 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-slate-800 bg-slate-950/50">
          <button
            type="button"
            onClick={onClose}
            className="px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 font-semibold hover:bg-slate-800 transition text-xs"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={saving}
            onClick={() => handleApplyOverride('override')}
            className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition text-xs shadow-md shadow-blue-900/40"
          >
            {saving ? 'Applying...' : 'Apply & Recalculate Route'}
          </button>
        </div>

      </div>
    </div>
  );
}
