import React, { useState } from 'react';
import { 
  ArrowRight, 
  ArrowDown, 
  Activity, 
  Layers, 
  ShieldAlert, 
  Truck, 
  Building2, 
  Navigation, 
  Radio, 
  CheckCircle2, 
  Smartphone, 
  MapPin, 
  AlertTriangle,
  Server,
  Database,
  Cpu
} from 'lucide-react';

export default function WorkflowVisualizer({ selectedIncident, activeRoute }) {
  const [activeTab, setActiveTab] = useState('primary'); // 'primary' or 'mobile'
  const [simulatingLora, setSimulatingLora] = useState(false);
  const [loraStep, setLoraStep] = useState(0); // 0: None, 1: Created, 2: Sent, 3: Received, 4: Success

  const handleSimulateLoraPacket = () => {
    setSimulatingLora(true);
    setLoraStep(1);
    setTimeout(() => setLoraStep(2), 700);
    setTimeout(() => setLoraStep(3), 1400);
    setTimeout(() => {
      setLoraStep(4);
      setSimulatingLora(false);
    }, 2100);
  };

  const hasBlockage = activeRoute?.has_blockage || false;

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-2xl p-4 md:p-5 shadow-2xl space-y-4">
      {/* Header & Flow Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30">
            <Activity className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center gap-2">
              Core Emergency System Architecture Workflow
            </h3>
            <p className="text-xs text-slate-400">
              End-to-End Primary Response Sequence & Telemetry Dataflow
            </p>
          </div>
        </div>

        {/* Workflow Tab Buttons */}
        <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-bold">
          <button
            onClick={() => setActiveTab('primary')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'primary' 
                ? 'bg-blue-600 text-white shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Primary Incident Workflow
          </button>
          <button
            onClick={() => setActiveTab('mobile')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'mobile' 
                ? 'bg-purple-600 text-white shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Mobile Crash Detection Flow
          </button>
        </div>
      </div>

      {/* 1. PRIMARY EMERGENCY WORKFLOW VIEW */}
      {activeTab === 'primary' && (
        <div className="space-y-4">
          
          {/* Workflow Stage 1 & 2: SOURCE -> DBSCAN -> RISK ANALYZER -> MACHINE CLASSIFIER Banner */}
          <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase text-blue-400 tracking-wider flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-blue-400" />
                Processing Pipeline Stage 1 & 2
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                ACTIVE PIPELINE
              </span>
            </div>

            {/* Mandated Display Sequence */}
            <div className="flex flex-wrap items-center justify-center gap-2 py-2 px-3 bg-slate-900 rounded-lg border border-slate-800 text-xs font-black text-white">
              <span className="px-2.5 py-1 rounded bg-blue-950 text-blue-300 border border-blue-700">SOURCE</span>
              <ArrowRight className="h-4 w-4 text-blue-400" />
              <span className="px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-700">DBSCAN</span>
              <ArrowRight className="h-4 w-4 text-blue-400" />
              <span className="px-2.5 py-1 rounded bg-amber-950 text-amber-300 border border-amber-700">RISK ANALYZER</span>
              <ArrowRight className="h-4 w-4 text-blue-400" />
              <span className="px-2.5 py-1 rounded bg-purple-950 text-purple-300 border border-purple-700">MACHINE CLASSIFIER</span>
            </div>
          </div>

          {/* Core System Flow Pipeline Stepper */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5 text-xs font-bold">
            
            {/* Step 1: INCIDENT SOURCE */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 1</div>
              <div className="text-white flex items-center gap-1.5">
                <Server className="h-4 w-4 text-blue-400" />
                <span>INCIDENT SOURCE</span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal">
                Citizen SOS / CCTV / Crash Sensor telemetry.
              </p>
            </div>

            {/* Step 2: DBSCAN */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 2</div>
              <div className="text-cyan-400 flex items-center gap-1.5">
                <Database className="h-4 w-4 text-cyan-400" />
                <span>DBSCAN</span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal">
                Spatial clustering (&le;250m) deduplication.
              </p>
            </div>

            {/* Step 3: RISK ANALYZER */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 3</div>
              <div className="text-amber-400 flex items-center gap-1.5">
                <ShieldAlert className="h-4 w-4 text-amber-400" />
                <span>RISK ANALYZER</span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal">
                Multi-factor severity scoring (0-100 pts).
              </p>
            </div>

            {/* Step 4: MACHINE CLASSIFIER */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 4</div>
              <div className="text-purple-400 flex items-center gap-1.5">
                <Cpu className="h-4 w-4 text-purple-400" />
                <span>MACHINE CLASSIFIER</span>
              </div>
              <p className="text-[11px] text-slate-400 font-normal">
                YOLOv8 vision & confidence rating.
              </p>
            </div>

            {/* Step 5: SUGGEST AMBULANCE */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 border-l-4 border-l-blue-500">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 5</div>
              <div className="text-blue-300 font-black">SUGGESTED AMBULANCE</div>
              <p className="text-[11px] text-slate-400 font-normal">
                {selectedIncident?.assigned_ambulance_id ? "Matched Unit Dispatched" : "ALS/BLS Proximity Scoring"}
              </p>
            </div>

            {/* Step 6: BLOCK TRAFFIC */}
            <div className={`p-3 bg-slate-950 border rounded-xl space-y-1 border-l-4 ${hasBlockage ? 'border-l-red-500 border-red-900/50' : 'border-slate-800 border-l-amber-500'}`}>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 6</div>
              <div className={hasBlockage ? 'text-red-400 font-black' : 'text-amber-300 font-black'}>
                TRAFFIC BLOCKED / RESTRICTED
              </div>
              <p className="text-[11px] text-slate-400 font-normal">
                {hasBlockage ? "Hazard restriction active" : "Hazard zone monitored"}
              </p>
            </div>

            {/* Step 7: A* REROUTING */}
            <div className={`p-3 bg-slate-950 border rounded-xl space-y-1 border-l-4 ${hasBlockage ? 'border-l-amber-400 bg-amber-950/20' : 'border-slate-800 border-l-emerald-500'}`}>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 7</div>
              <div className="text-emerald-400 font-black">REROUTING USING A* ALGORITHM</div>
              <p className="text-[11px] text-slate-400 font-normal">
                Obstacle-free shortest road graph calculation.
              </p>
            </div>

            {/* Step 8: SUGGEST HOSPITAL */}
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 border-l-4 border-l-emerald-500">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold">Step 8</div>
              <div className="text-emerald-300 font-black">SUGGESTED HOSPITAL</div>
              <p className="text-[11px] text-slate-400 font-normal">
                Matched Level 1 Trauma & open ICU beds.
              </p>
            </div>

          </div>

          {/* LoRa Communication & Information Return Banner */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <h4 className="text-xs font-black text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Radio className="h-4 w-4 text-amber-400" />
                  SIMULATED LoRa COMMUNICATION (LONGER RANGE)
                </h4>
                <p className="text-[11px] text-slate-400">
                  Long-range telemetry fallback simulation for resilient emergency network transmission.
                </p>
              </div>

              <button
                onClick={handleSimulateLoraPacket}
                disabled={simulatingLora}
                className="bg-amber-600 hover:bg-amber-500 text-slate-950 font-black text-xs px-3 py-1.5 rounded-lg transition active:scale-95 shadow shrink-0"
              >
                {simulatingLora ? 'Transmitting Packet...' : 'Simulate LoRa Packet Transmission'}
              </button>
            </div>

            {/* LoRa Transmission Pipeline Diagram */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs font-bold pt-1">
              <div className={`p-2.5 rounded-lg border transition-all ${loraStep >= 1 ? 'bg-amber-500/20 border-amber-500 text-amber-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                Packet Created
              </div>
              <div className={`p-2.5 rounded-lg border transition-all ${loraStep >= 2 ? 'bg-amber-500/20 border-amber-500 text-amber-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                Packet Sent
              </div>
              <div className={`p-2.5 rounded-lg border transition-all ${loraStep >= 3 ? 'bg-amber-500/20 border-amber-500 text-amber-300' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                Packet Received
              </div>
              <div className={`p-2.5 rounded-lg border transition-all ${loraStep >= 4 ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-extrabold' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>
                SUCCESS
              </div>
            </div>

            {/* Final Return Status */}
            <div className="flex items-center justify-between bg-emerald-950/40 border border-emerald-500/40 p-2.5 rounded-lg text-xs font-bold text-emerald-300">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                EMERGENCY INFORMATION UPDATED
              </span>
              <span className="text-[10px] text-slate-400 font-normal">
                Telemetry returned to source, hospital, and ambulance.
              </span>
            </div>
          </div>

        </div>
      )}

      {/* 2. MOBILE CRASH DETECTION FLOW VIEW */}
      {activeTab === 'mobile' && (
        <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-4 space-y-4">
          <div className="flex items-center gap-2">
            <Smartphone className="h-5 w-5 text-purple-400" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">
              Mobile Crash Detection Workflow Architecture
            </h4>
          </div>

          <p className="text-xs text-slate-400">
            Automated sensor-triggered emergency sequence utilizing on-device GNSS location capturing and longer-range LoRa packet dispatch.
          </p>

          {/* Sequence Pipeline */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2 text-xs font-bold">
            
            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 1</div>
              <div className="text-white mt-0.5">MOBILE CRASH DETECTION</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Impact G-force sensor triggered.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 2</div>
              <div className="text-white mt-0.5">INCIDENT INFO</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Vehicle telemetry payload assembled.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 3</div>
              <div className="text-white mt-0.5">GNSS</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Satellite positioning lock.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 4</div>
              <div className="text-white mt-0.5">LATITUDE + LONGITUDE</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Exact GNSS coordinates obtained.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 5</div>
              <div className="text-white mt-0.5">INCIDENT DETECTION</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Ingested into ResQFlow AI system.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 6</div>
              <div className="text-white mt-0.5">HOSPITAL + AMBULANCE</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Matched and dispatched dual teams.</div>
            </div>

            <div className="p-3 bg-purple-950/30 border border-purple-800/60 rounded-xl">
              <div className="text-purple-400 text-[10px] uppercase font-black">Stage 7</div>
              <div className="text-white mt-0.5">LoRa COMMUNICATION</div>
              <div className="text-[11px] text-slate-400 font-normal mt-1">Long-range radio transmission.</div>
            </div>

            <div className="p-3 bg-emerald-950/40 border border-emerald-500/60 rounded-xl">
              <div className="text-emerald-400 text-[10px] uppercase font-black">Stage 8</div>
              <div className="text-emerald-300 mt-0.5">INFORMATION SOURCE</div>
              <div className="text-[11px] text-slate-300 font-normal mt-1">Confirmation returned to handset.</div>
            </div>

          </div>

          {/* Mandatory GNSS Display Card */}
          <div className="p-3.5 bg-slate-900 border border-slate-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div>
              <div className="font-extrabold text-white flex items-center gap-1.5">
                <MapPin className="h-4 w-4 text-red-400" />
                GNSS LOCATION TELEMETRY
              </div>
              <div className="text-slate-400 font-mono text-[11px] mt-1">
                Latitude: {selectedIncident ? selectedIncident.latitude.toFixed(5) : '12.98500'} | Longitude: {selectedIncident ? selectedIncident.longitude.toFixed(5) : '77.59370'}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Timestamp: {new Date().toISOString()} | Accuracy: &plusmn; 4.2 meters
              </div>
            </div>

            <span className="bg-purple-500/10 text-purple-300 border border-purple-500/30 font-bold px-2.5 py-1 rounded-lg text-center shrink-0">
              MOBILE GNSS SYNCED
            </span>
          </div>

        </div>
      )}
    </div>
  );
}
