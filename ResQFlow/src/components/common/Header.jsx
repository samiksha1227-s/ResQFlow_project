import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Radio, 
  RotateCcw, 
  Sparkles, 
  Users, 
  Truck, 
  Building2, 
  ChevronDown,
  Activity
} from 'lucide-react';
import { api } from '../../services/api';

export default function Header({ 
  currentRole, 
  setRole, 
  onRefresh, 
  activeIncidentsCount = 0 
}) {
  const [scenarios, setScenarios] = useState([]);
  const [loadingScenario, setLoadingScenario] = useState(false);
  const [showScenarioMenu, setShowScenarioMenu] = useState(false);

  useEffect(() => {
    api.listScenarios().then(setScenarios).catch(console.error);
  }, []);

  const handleTriggerScenario = async (id) => {
    try {
      setLoadingScenario(true);
      setShowScenarioMenu(false);
      await api.triggerScenario(id);
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error(e);
      alert('Failed to trigger scenario: ' + e.message);
    } finally {
      setLoadingScenario(false);
    }
  };

  const handleReset = async () => {
    if (window.confirm('Reset all demo incidents, clear road blockages, and reset ambulances to default base?')) {
      try {
        setLoadingScenario(true);
        await api.resetSimulation();
        if (onRefresh) onRefresh();
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingScenario(false);
      }
    }
  };

  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-50 px-4 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
        
        {/* Left: Brand & Status */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-red-600 to-blue-600 flex items-center justify-center shadow-lg shadow-red-900/30">
            <ShieldAlert className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-black tracking-tight text-white flex items-center gap-1.5">
                ResQFlow <span className="text-blue-400 font-extrabold">AI</span>
              </h1>
              <span className="bg-blue-500/10 text-blue-400 border border-blue-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping" />
                DEMO PROTOTYPE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Source-Agnostic Emergency Coordination System
            </p>
          </div>
        </div>

        {/* Center: Role Switcher Tabs (Supported Actors) */}
        <div className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setRole('operator')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              currentRole === 'operator'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/50'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Radio className="h-3.5 w-3.5" />
            <span>4. OFFICER / ADMIN</span>
            {activeIncidentsCount > 0 && (
              <span className="bg-red-500 text-white text-[10px] px-1.5 py-0.2 rounded-full font-bold">
                {activeIncidentsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setRole('citizen')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              currentRole === 'citizen'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/50'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Users className="h-3.5 w-3.5" />
            <span>1. CITIZEN / USER</span>
          </button>

          <button
            onClick={() => setRole('ambulance')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              currentRole === 'ambulance'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/50'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Truck className="h-3.5 w-3.5" />
            <span>2. AMBULANCE</span>
          </button>

          <button
            onClick={() => setRole('hospital')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              currentRole === 'hospital'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-900/50'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Building2 className="h-3.5 w-3.5" />
            <span>3. HOSPITAL</span>
          </button>
        </div>

        {/* Right: Demo Scenario Triggers & Reset */}
        <div className="flex items-center gap-2 relative">
          <div className="relative">
            <button
              onClick={() => setShowScenarioMenu(!showScenarioMenu)}
              disabled={loadingScenario}
              className="flex items-center gap-1.5 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-medium px-3 py-2 rounded-lg transition"
            >
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              <span>Demo Scenarios</span>
              <ChevronDown className="h-3.5 w-3.5" />
            </button>

            {showScenarioMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-2 z-50">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-2 py-1">
                  Inject Hackathon Demo Case:
                </div>
                {scenarios.map((sc) => (
                  <button
                    key={sc.id}
                    onClick={() => handleTriggerScenario(sc.id)}
                    className="w-full text-left p-2 rounded-lg hover:bg-slate-800 text-xs transition flex flex-col gap-0.5 group"
                  >
                    <span className="font-semibold text-slate-200 group-hover:text-blue-400">
                      {sc.title}
                    </span>
                    <span className="text-[11px] text-slate-400 line-clamp-2">
                      {sc.description}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={handleReset}
            title="Reset Simulation"
            disabled={loadingScenario}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>

      </div>
    </header>
  );
}
