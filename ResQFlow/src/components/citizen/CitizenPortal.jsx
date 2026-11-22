import React, { useState } from 'react';
import { 
  AlertOctagon, 
  MapPin, 
  Video, 
  Smartphone, 
  Car, 
  Building, 
  Camera, 
  ShieldCheck, 
  CheckCircle2, 
  Upload,
  Clock
} from 'lucide-react';
import { api } from '../../services/api';

const LOCATION_PRESETS = [
  { label: "Central Expressway Overpass (Accident Hotspot)", lat: 12.9850, lng: 77.5937, address: "Central Expressway Overpass, Mile Marker 4" },
  { label: "North Ring Interchange & 5th Cross", lat: 12.9969, lng: 77.5937, address: "North Ring Road & Tech Junction" },
  { label: "East Tech Corridor Hub", lat: 12.9720, lng: 77.6250, address: "Tech Boulevard & 100ft Road" },
  { label: "West Metro Commercial Junction", lat: 12.9650, lng: 77.5750, address: "West Metro Junction & 5th Cross" },
];

export default function CitizenPortal({ onIncidentCreated }) {
  const [sourceType, setSourceType] = useState('citizen');
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [customAddress, setCustomAddress] = useState(LOCATION_PRESETS[0].address);
  const [lat, setLat] = useState(LOCATION_PRESETS[0].lat);
  const [lng, setLng] = useState(LOCATION_PRESETS[0].lng);
  const [victimCount, setVictimCount] = useState(2);
  const [vehicleCount, setVehicleCount] = useState(2);
  const [isRollover, setIsRollover] = useState(false);
  const [hasFire, setHasFire] = useState(false);
  const [description, setDescription] = useState('Collision between two vehicles. Passengers trapped.');
  const [callerId, setCallerId] = useState('+1-555-0199');
  
  const [submitting, setSubmitting] = useState(false);
  const [lastSubmission, setLastSubmission] = useState(null);

  const handlePresetChange = (idx) => {
    setSelectedPreset(idx);
    const p = LOCATION_PRESETS[idx];
    setLat(p.lat);
    setLng(p.lng);
    setCustomAddress(p.address);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const res = await api.reportIncident({
        source_type: sourceType,
        source_identifier: callerId,
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        address: customAddress,
        raw_text: description,
        victim_count: parseInt(victimCount),
        vehicle_count: parseInt(vehicleCount),
        is_rollover: isRollover,
        has_fire: hasFire
      });

      setLastSubmission(res);
      if (onIncidentCreated) onIncidentCreated();
    } catch (err) {
      alert('Submission failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">
      {/* Title & Introduction */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-red-600/20 text-red-500 rounded-xl border border-red-500/30">
            <AlertOctagon className="h-7 w-7 animate-pulse" />
          </div>
          <div>
            <h2 className="text-lg font-black text-white">
              Source-Agnostic Emergency Reporting Portal
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Submit accident telemetry or public SOS. The system applies YOLO vision analysis, DBSCAN duplicate filtering, and instant ambulance dispatch.
            </p>
          </div>
        </div>
      </div>

      {/* Submission Card */}
      <form onSubmit={handleSubmit} className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
        
        {/* 1. Ingestion Source Selector */}
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            1. Select Input Source Channel:
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
            {[
              { id: 'citizen', label: 'Citizen SOS App', icon: Smartphone, color: 'text-purple-400' },
              { id: 'cctv', label: 'CCTV Camera Feed', icon: Video, color: 'text-blue-400' },
              { id: 'dashcam', label: 'Vehicle Dashcam', icon: Car, color: 'text-amber-400' },
              { id: 'authority', label: 'Traffic Authority', icon: Building, color: 'text-cyan-400' },
            ].map((src) => {
              const Icon = src.icon;
              const isSelected = sourceType === src.id;
              return (
                <button
                  key={src.id}
                  type="button"
                  onClick={() => setSourceType(src.id)}
                  className={`flex flex-col items-center justify-center p-3 rounded-xl border font-bold transition-all ${
                    isSelected
                      ? 'bg-blue-600/20 border-blue-500 text-white ring-2 ring-blue-500/40 shadow-lg'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  <Icon className={`h-5 w-5 mb-1.5 ${src.color}`} />
                  <span className="text-[11px]">{src.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 2. Source Identifier */}
        <div>
          <label className="block text-xs font-bold text-slate-300 mb-1">
            Source Identifier (Caller ID / Camera Code / Vehicle VIN):
          </label>
          <input
            type="text"
            value={callerId}
            onChange={(e) => setCallerId(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* 3. Location Preset */}
        <div>
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <MapPin className="h-4 w-4 text-red-400" />
            <span>2. Accident Location (Demo Coordinates):</span>
          </label>
          <div className="space-y-2">
            <select
              value={selectedPreset}
              onChange={(e) => handlePresetChange(parseInt(e.target.value))}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              {LOCATION_PRESETS.map((p, idx) => (
                <option key={idx} value={idx}>
                  {p.label} [{p.lat}, {p.lng}]
                </option>
              ))}
            </select>

            <input
              type="text"
              value={customAddress}
              onChange={(e) => setCustomAddress(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="Detailed street description"
            />
          </div>
        </div>

        {/* 4. Incident Details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-300 font-bold mb-1">Injured Victims:</label>
            <input
              type="number"
              min="0"
              max="20"
              value={victimCount}
              onChange={(e) => setVictimCount(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
            />
          </div>

          <div>
            <label className="block text-slate-300 font-bold mb-1">Vehicles Involved:</label>
            <input
              type="number"
              min="1"
              max="10"
              value={vehicleCount}
              onChange={(e) => setVehicleCount(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
            />
          </div>

          <div className="flex items-center gap-2 pt-5">
            <input
              type="checkbox"
              id="rollover"
              checked={isRollover}
              onChange={(e) => setIsRollover(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="rollover" className="text-slate-300 font-bold cursor-pointer">
              Rollover Crash
            </label>
          </div>

          <div className="flex items-center gap-2 pt-5">
            <input
              type="checkbox"
              id="fire"
              checked={hasFire}
              onChange={(e) => setHasFire(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 text-red-600 focus:ring-red-500"
            />
            <label htmlFor="fire" className="text-slate-300 font-bold cursor-pointer">
              Fire / Smoke Risk
            </label>
          </div>
        </div>

        {/* 5. Description */}
        <div>
          <label className="block text-xs font-bold text-slate-300 mb-1">
            Emergency Description / Sensor Context:
          </label>
          <textarea
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3.5 bg-gradient-to-r from-red-600 to-blue-600 hover:from-red-500 hover:to-blue-500 text-white font-black rounded-xl text-sm shadow-xl shadow-red-900/40 transition active:scale-98 flex items-center justify-center gap-2"
        >
          <AlertOctagon className="h-5 w-5" />
          <span>{submitting ? 'PROCESSING EMERGENCY SOS...' : 'TRANSMIT EMERGENCY REPORT'}</span>
        </button>

      </form>

      {/* Mandatory GNSS LOCATION Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-black text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
            <MapPin className="h-4 w-4 text-red-400" />
            GNSS LOCATION
          </span>
          <span className="text-[10px] text-slate-400 font-mono">Real-time Satellite Lock</span>
        </div>
        <div className="grid grid-cols-2 gap-2 bg-slate-950 p-3 rounded-xl font-mono text-xs text-slate-200 border border-slate-800">
          <div>Latitude: <span className="text-emerald-400 font-bold">{parseFloat(lat).toFixed(5)}</span></div>
          <div>Longitude: <span className="text-emerald-400 font-bold">{parseFloat(lng).toFixed(5)}</span></div>
          <div className="col-span-2 text-[10px] text-slate-500 font-sans">
            Timestamp: {new Date().toLocaleTimeString()} | Source: {sourceType.toUpperCase()} GNSS Sensor
          </div>
        </div>
      </div>

      {/* Instant Result Banner */}
      {lastSubmission && (
        <div className="space-y-3">
          {/* SIMULATED LoRa COMMUNICATION Banner */}
          <div className="bg-amber-950/40 border border-amber-500/60 p-3.5 rounded-2xl space-y-2">
            <div className="text-xs font-black text-amber-300 uppercase tracking-wider">
              SIMULATED LoRa COMMUNICATION
            </div>
            <div className="flex items-center justify-between text-[11px] font-bold text-amber-200 bg-slate-950 p-2 rounded-lg border border-amber-900/40">
              <span>Packet Created</span>
              <span>&rarr;</span>
              <span>Packet Sent</span>
              <span>&rarr;</span>
              <span>Packet Received</span>
              <span>&rarr;</span>
              <span className="text-emerald-400 font-extrabold">SUCCESS</span>
            </div>
            <p className="text-[10px] text-slate-400 italic">
              * Note: Software simulation representing longer-range emergency radio communication.
            </p>
          </div>

          <div className={`p-4 rounded-2xl border shadow-xl transition-all ${
            lastSubmission.is_duplicate 
              ? 'bg-purple-950/40 border-purple-600/70' 
              : 'bg-emerald-950/40 border-emerald-600/70'
          }`}>
            <div className="flex items-start gap-3">
              {lastSubmission.is_duplicate ? (
                <ShieldCheck className="h-6 w-6 text-purple-400 shrink-0 mt-0.5" />
              ) : (
                <CheckCircle2 className="h-6 w-6 text-emerald-400 shrink-0 mt-0.5" />
              )}
              <div className="text-xs space-y-1">
                <div className="text-sm font-black text-white flex items-center gap-2">
                  <span>EMERGENCY INFORMATION UPDATED</span>
                  <span className="font-mono bg-slate-900 px-2 py-0.5 rounded text-blue-400">
                    {lastSubmission.incident_code}
                  </span>
                </div>
                <p className="text-slate-300">{lastSubmission.message}</p>
                {!lastSubmission.is_duplicate && (
                  <div className="text-[11px] text-slate-400 pt-1 flex items-center gap-3">
                    <span>Assigned Unit: <strong className="text-blue-300">{lastSubmission.ambulance || 'Assigned'}</strong></span>
                    <span>Hospital: <strong className="text-emerald-300">{lastSubmission.hospital || 'Assigned'}</strong></span>
                    <span>Priority: <strong className="text-red-400 uppercase">{lastSubmission.severity}</strong></span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
