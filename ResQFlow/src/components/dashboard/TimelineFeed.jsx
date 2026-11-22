import React from 'react';
import { 
  Activity, 
  ShieldCheck, 
  Layers, 
  Truck, 
  Building2, 
  AlertTriangle, 
  Sliders, 
  CheckCircle,
  Clock
} from 'lucide-react';
import { formatTime } from '../../utils/formatters';

const getEventIcon = (type, severity) => {
  switch (type) {
    case 'AI_VERIFIED':
      return <ShieldCheck className="h-3.5 w-3.5 text-purple-400" />;
    case 'DEDUPLICATED':
      return <Layers className="h-3.5 w-3.5 text-blue-400" />;
    case 'DISPATCHED':
      return <Truck className="h-3.5 w-3.5 text-emerald-400" />;
    case 'HOSPITAL_MATCH':
      return <Building2 className="h-3.5 w-3.5 text-teal-400" />;
    case 'REROUTED':
      return <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />;
    case 'OVERRIDE':
      return <Sliders className="h-3.5 w-3.5 text-orange-400" />;
    case 'STATUS_CHANGE':
    default:
      return <Activity className="h-3.5 w-3.5 text-slate-400" />;
  }
};

const getEventBorder = (severity) => {
  switch (severity) {
    case 'danger':
      return 'border-l-red-500 bg-red-950/20';
    case 'warning':
      return 'border-l-amber-500 bg-amber-950/20';
    case 'success':
      return 'border-l-emerald-500 bg-emerald-950/20';
    case 'info':
    default:
      return 'border-l-blue-500 bg-blue-950/20';
  }
};

export default function TimelineFeed({ logs = [] }) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 flex flex-col h-full">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
        <h3 className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
          <Activity className="h-4 w-4 text-blue-400" />
          <span>Live Operations Audit Timeline</span>
        </h3>
        <span className="text-[10px] text-slate-400">
          Real-time Event Stream
        </span>
      </div>

      <div className="overflow-y-auto space-y-2 flex-1 max-h-48 pr-1 text-xs">
        {logs.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-[11px]">
            No live events recorded yet.
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className={`p-2 rounded-r-lg border border-slate-800/80 border-l-4 ${getEventBorder(log.severity)} flex flex-col gap-1 transition-all`}
            >
              <div className="flex items-center justify-between text-[10px]">
                <span className="font-extrabold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  {getEventIcon(log.event_type, log.severity)}
                  <span>{log.event_type.replace('_', ' ')}</span>
                </span>
                <span className="text-slate-400 flex items-center gap-1 font-mono">
                  <Clock className="h-2.5 w-2.5 text-slate-500" />
                  {formatTime(log.created_at)}
                </span>
              </div>
              <p className="text-[11px] text-slate-300 leading-snug">
                {log.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
