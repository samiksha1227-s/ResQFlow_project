import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Helper component to auto-center map when selected incident changes
function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 13, { animate: true });
    }
  }, [center, map]);
  return null;
}

// Custom Leaflet Icons
const createEmergencyIcon = (severity) => {
  const isCritical = severity === 'critical';
  return L.divIcon({
    className: 'custom-emergency-icon',
    html: `
      <div class="relative flex items-center justify-center">
        <span class="${isCritical ? 'beacon-pulse' : 'animate-ping'} absolute inline-flex h-8 w-8 rounded-full bg-red-500 opacity-75"></span>
        <div class="relative flex items-center justify-center h-7 w-7 rounded-full bg-red-600 text-white font-bold text-xs shadow-lg border-2 border-white">
          🚨
        </div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

const createAmbulanceIcon = (callsign, status) => {
  const isDispatched = status === 'dispatched';
  return L.divIcon({
    className: 'custom-ambulance-icon',
    html: `
      <div class="flex flex-col items-center">
        <div class="flex items-center justify-center h-7 w-7 rounded-full ${isDispatched ? 'bg-blue-600 ring-4 ring-blue-400/40' : 'bg-slate-700'} text-white shadow-md border-2 border-white">
          🚑
        </div>
        <span class="bg-slate-900/90 text-[10px] text-blue-300 font-bold px-1.5 py-0.5 rounded border border-slate-700 mt-0.5 whitespace-nowrap shadow">
          ${callsign}
        </span>
      </div>
    `,
    iconSize: [36, 42],
    iconAnchor: [18, 21],
  });
};

const createHospitalIcon = (name, traumaLevel, availableIcu) => {
  return L.divIcon({
    className: 'custom-hospital-icon',
    html: `
      <div class="flex flex-col items-center">
        <div class="flex items-center justify-center h-7 w-7 rounded-lg bg-emerald-600 text-white shadow-md border-2 border-white font-bold">
          🏥
        </div>
        <span class="bg-slate-900/95 text-[9px] text-emerald-300 font-bold px-1.5 py-0.5 rounded border border-slate-700 mt-0.5 whitespace-nowrap shadow">
          L${traumaLevel} • ${availableIcu} ICU
        </span>
      </div>
    `,
    iconSize: [40, 42],
    iconAnchor: [20, 21],
  });
};

const createBlockageIcon = (roadName) => {
  return L.divIcon({
    className: 'custom-blockage-icon',
    html: `
      <div class="flex flex-col items-center">
        <div class="flex items-center justify-center h-8 w-8 rounded-full bg-amber-500 text-slate-950 shadow-xl border-2 border-red-500 font-black text-sm animate-bounce">
          ⛔
        </div>
        <span class="bg-red-950 text-[10px] text-red-300 font-extrabold px-2 py-0.5 rounded-full border border-red-600 mt-1 whitespace-nowrap shadow">
          ROAD BLOCKED
        </span>
      </div>
    `,
    iconSize: [36, 48],
    iconAnchor: [18, 24],
  });
};

export default function LiveMap({ 
  incidents = [], 
  ambulances = [], 
  hospitals = [], 
  activeRoute = null, 
  selectedIncident = null,
  onSelectIncident 
}) {
  const defaultCenter = [12.9719, 77.5937];
  const centerPos = selectedIncident 
    ? [selectedIncident.latitude, selectedIncident.longitude]
    : defaultCenter;

  return (
    <div className="relative w-full h-full min-h-[440px] rounded-xl overflow-hidden border border-slate-800 shadow-xl">
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <MapRecenter center={centerPos} />

        {/* OpenStreetMap Tile Layer without watermarks */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />


        {/* 1. Incident Markers */}
        {incidents.map((inc) => (
          <Marker
            key={`inc-${inc.id}`}
            position={[inc.latitude, inc.longitude]}
            icon={createEmergencyIcon(inc.severity)}
            eventHandlers={{
              click: () => onSelectIncident && onSelectIncident(inc)
            }}
          >
            <Popup>
              <div className="p-1 text-slate-100">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-sm text-red-400">{inc.incident_code}</span>
                  <span className="text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                    {inc.severity}
                  </span>
                </div>
                <div className="text-xs text-slate-300">{inc.address}</div>
                <div className="text-[11px] text-slate-400 mt-1">
                  Source: <span className="font-semibold uppercase text-blue-400">{inc.primary_source}</span> | Victims: {inc.victim_count}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 2. Ambulance Markers */}
        {ambulances.map((amb) => (
          <Marker
            key={`amb-${amb.id}`}
            position={[amb.current_latitude, amb.current_longitude]}
            icon={createAmbulanceIcon(amb.callsign, amb.status)}
          >
            <Popup>
              <div className="p-1 text-slate-100">
                <div className="font-bold text-sm text-blue-400">{amb.callsign}</div>
                <div className="text-xs text-slate-300">Type: <span className="font-semibold">{amb.type}</span></div>
                <div className="text-xs text-slate-300">Status: <span className="uppercase text-emerald-400 font-semibold">{amb.status}</span></div>
                <div className="text-[11px] text-slate-400 mt-1">Base: {amb.base_station}</div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 3. Hospital Markers */}
        {hospitals.map((hosp) => (
          <Marker
            key={`hosp-${hosp.id}`}
            position={[hosp.latitude, hosp.longitude]}
            icon={createHospitalIcon(hosp.name, hosp.trauma_level, hosp.available_icu_beds)}
          >
            <Popup>
              <div className="p-1 text-slate-100">
                <div className="font-bold text-sm text-emerald-400">{hosp.name}</div>
                <div className="text-xs text-slate-300">Trauma Level: <span className="font-semibold">Level {hosp.trauma_level}</span></div>
                <div className="text-xs text-slate-300">ICU Beds: <span className="text-emerald-400 font-bold">{hosp.available_icu_beds} / {hosp.total_icu_beds}</span></div>
                <div className="text-xs text-slate-300">ER Beds: <span className="text-blue-400 font-bold">{hosp.available_er_beds} / {hosp.total_er_beds}</span></div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* 4. Active Route Polylines */}
        {activeRoute && activeRoute.polyline && activeRoute.polyline.length > 1 && (
          <>
            {/* If there is a road blockage, draw the original blocked path in dashed red */}
            {activeRoute.has_blockage && activeRoute.original_polyline && activeRoute.original_polyline.length > 1 && (
              <Polyline
                positions={activeRoute.original_polyline}
                pathOptions={{
                  color: '#ef4444',
                  weight: 4,
                  dashArray: '8, 8',
                  opacity: 0.6
                }}
              />
            )}

            {/* Current or Rerouted Path */}
            <Polyline
              positions={activeRoute.polyline}
              pathOptions={{
                color: activeRoute.has_blockage ? '#10b981' : '#3b82f6',
                weight: 5,
                opacity: 0.9,
              }}
            />

            {/* Road Blockage Marker */}
            {activeRoute.has_blockage && (
              <Marker
                position={[12.9850, 77.5937]} // Central Expressway Overpass coordinate
                icon={createBlockageIcon(activeRoute.blocked_segment)}
              >
                <Popup>
                  <div className="p-1">
                    <div className="font-bold text-red-400 text-xs">⚠️ ACTIVE ROAD BLOCKAGE</div>
                    <div className="text-[11px] text-slate-300">{activeRoute.blocked_segment}</div>
                    <div className="text-[11px] text-emerald-400 font-semibold mt-1">
                      Dynamic Reroute Active (+{activeRoute.eta_minutes - (activeRoute.original_eta_minutes || 0)}m)
                    </div>
                  </div>
                </Popup>
              </Marker>
            )}
          </>
        )}
      </MapContainer>

      {/* Map Legend Overlay */}
      <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur border border-slate-700/80 rounded-lg p-2.5 z-[1000] text-[11px] shadow-xl pointer-events-none">
        <div className="font-bold text-slate-300 mb-1.5 uppercase tracking-wider text-[9px]">Map Legend</div>
        <div className="flex flex-col gap-1 text-slate-300">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500 animate-ping inline-block" />
            <span>Active Incident</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-500 inline-block" />
            <span>Ambulance Unit</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded bg-emerald-500 inline-block" />
            <span>Trauma Center</span>
          </div>
          {activeRoute && activeRoute.has_blockage && (
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <span className="h-2 w-4 bg-emerald-500 inline-block rounded" />
              <span>A* Alternate Reroute</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
