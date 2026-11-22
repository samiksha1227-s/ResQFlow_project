export function getSeverityStyle(severity) {
  switch ((severity || '').toLowerCase()) {
    case 'critical':
      return {
        bg: 'bg-red-950/80',
        text: 'text-red-400',
        border: 'border-red-600/60',
        badge: 'bg-red-500 text-white',
        ring: 'ring-red-500/50'
      };
    case 'high':
      return {
        bg: 'bg-amber-950/80',
        text: 'text-amber-400',
        border: 'border-amber-600/60',
        badge: 'bg-amber-500 text-slate-950 font-bold',
        ring: 'ring-amber-500/50'
      };
    case 'medium':
      return {
        bg: 'bg-yellow-950/70',
        text: 'text-yellow-400',
        border: 'border-yellow-600/50',
        badge: 'bg-yellow-500 text-slate-950 font-medium',
        ring: 'ring-yellow-500/40'
      };
    case 'low':
    default:
      return {
        bg: 'bg-emerald-950/70',
        text: 'text-emerald-400',
        border: 'border-emerald-600/50',
        badge: 'bg-emerald-600 text-white',
        ring: 'ring-emerald-500/40'
      };
  }
}

export function getStatusStyle(status) {
  switch ((status || '').toLowerCase()) {
    case 'dispatched':
      return 'bg-blue-600/20 text-blue-400 border border-blue-500/40';
    case 'verified':
      return 'bg-purple-600/20 text-purple-400 border border-purple-500/40';
    case 'on_scene':
      return 'bg-amber-600/20 text-amber-400 border border-amber-500/40';
    case 'transporting':
      return 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/40';
    case 'arrived':
      return 'bg-teal-600/20 text-teal-400 border border-teal-500/40';
    case 'closed':
      return 'bg-slate-700/40 text-slate-400 border border-slate-600/40';
    case 'rejected':
      return 'bg-red-900/30 text-red-400 border border-red-800/40';
    case 'reported':
    default:
      return 'bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse';
  }
}

export function formatTime(timestamp) {
  if (!timestamp) return 'Just now';
  const d = new Date(timestamp);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
