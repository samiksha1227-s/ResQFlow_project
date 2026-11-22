import React, { useState } from 'react';
import { 
  AlertCircle, 
  Video, 
  Smartphone, 
  Car, 
  Building, 
  Flame, 
  Layers,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { getSeverityStyle, getStatusStyle, formatTime } from '../../utils/formatters';

const getSourceIcon = (source) => {
  switch ((source || '').toLowerCase()) {
    case 'cctv':
      return <Video className="h-3.5 w-3.5 text-blue-400" />;
    case 'citizen':
      return <Smartphone className="h-3.5 w-3.5 text-purple-400" />;
    case 'dashcam':
      return <Car className="h-3.5 w-3.5 text-amber-400" />;
    case 'authority':
    default:
      return <Building className="h-3.5 w-3.5 text-cyan-400" />;
  }
};

export default function IncidentList({ 
  incidents = [], 
  selectedIncident = null, 
  onSelectIncident 
}) {
  const [filterSeverity, setFilterSeverity] = useState('all');

  const filteredIncidents = incidents.filter(inc => {
    if (filterSeverity === 'all') return true;
    return inc.severity === filterSeverity;
  });

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex flex-col h-full max-h-[720px]">
      {/* Header & Filter */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            Incident Queue
          </h2>
          <span className="text-[11px] text-slate-400">
            {incidents.length} total • {incidents.filter(i => !['closed', 'rejected'].includes(i.status)).length} active
          </span>
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-1 text-[10px] bg-slate-950 p-1 rounded-lg border border-slate-800">
          {['all', 'critical', 'high', 'medium'].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-2 py-0.5 rounded capitalize font-semibold transition ${
                filterSeverity === sev
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* List Container */}
      <div className="overflow-y-auto flex-1 mt-2 space-y-2 pr-1">
        {filteredIncidents.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No incidents found in this category.
          </div>
        ) : (
          filteredIncidents.map((inc) => {
            const isSelected = selectedIncident && selectedIncident.id === inc.id;
            const sevStyle = getSeverityStyle(inc.severity);
            const statusClass = getStatusStyle(inc.status);

            return (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-blue-950/40 border-blue-500 ring-1 ring-blue-500/50 shadow-md'
                    : 'bg-slate-950/50 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                }`}
              >
                {/* Top Row: Code, Severity, Time */}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-black text-slate-200 tracking-wider">
                      {inc.incident_code}
                    </span>
                    <span className={`text-[9px] uppercase font-black px-1.5 py-0.5 rounded ${sevStyle.badge}`}>
                      {inc.severity}
                    </span>
                  </div>

                  <span className="text-[10px] text-slate-400 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-500" />
                    {formatTime(inc.created_at)}
                  </span>
                </div>

                {/* Address */}
                <p className="text-xs text-slate-300 font-medium mt-1 line-clamp-1">
                  {inc.address}
                </p>

                {/* Bottom Badges */}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/70 text-[10px]">
                  <div className="flex items-center gap-2">
                    {/* Source Tag */}
                    <span className="flex items-center gap-1 text-slate-300 bg-slate-800/80 px-1.5 py-0.5 rounded border border-slate-700">
                      {getSourceIcon(inc.primary_source)}
                      <span className="uppercase font-semibold text-[9px]">{inc.primary_source}</span>
                    </span>

                    {/* Deduplication Cluster Tag */}
                    {inc.report_count > 1 && (
                      <span className="flex items-center gap-1 text-purple-300 bg-purple-950/70 px-1.5 py-0.5 rounded border border-purple-800/60 font-semibold text-[9px]">
                        <Layers className="h-3 w-3 text-purple-400" />
                        {inc.report_count} Linked (DBSCAN)
                      </span>
                    )}
                  </div>

                  {/* Status Pill */}
                  <span className={`px-2 py-0.5 rounded font-bold uppercase text-[9px] ${statusClass}`}>
                    {inc.status}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
