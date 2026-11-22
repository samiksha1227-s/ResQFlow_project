import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/common/Header';
import MetricCards from './components/common/MetricCards';
import LiveMap from './components/dashboard/LiveMap';
import IncidentList from './components/dashboard/IncidentList';
import IncidentDetail from './components/dashboard/IncidentDetail';
import TimelineFeed from './components/dashboard/TimelineFeed';
import HumanOverrideModal from './components/dashboard/HumanOverrideModal';
import CitizenPortal from './components/citizen/CitizenPortal';
import AmbulanceHUD from './components/ambulance/AmbulanceHUD';
import HospitalDesk from './components/hospital/HospitalDesk';
import { api } from './services/api';

import WorkflowVisualizer from './components/common/WorkflowVisualizer';

export default function App() {
  const [currentRole, setCurrentRole] = useState('operator');
  const [incidents, setIncidents] = useState([]);
  const [ambulances, setAmbulances] = useState([]);
  const [hospitals, setHospitals] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidentDetail, setIncidentDetail] = useState(null);
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [logs, setLogs] = useState([]);

  // Fetch all core system entities
  const fetchData = useCallback(async () => {
    try {
      const [incs, ambs, hosps] = await Promise.all([
        api.getIncidents(),
        api.getAmbulances(),
        api.getHospitals()
      ]);
      setIncidents(incs);
      setAmbulances(ambs);
      setHospitals(hosps);

      // If no incident is selected yet, select the first active incident
      if (!selectedIncident && incs.length > 0) {
        const active = incs.find(i => !['closed', 'rejected'].includes(i.status)) || incs[0];
        setSelectedIncident(active);
      }
    } catch (err) {
      console.error("Data polling error:", err);
    }
  }, [selectedIncident]);

  // Fetch full details of the selected incident
  const fetchIncidentDetail = useCallback(async () => {
    if (!selectedIncident) return;
    try {
      const detail = await api.getIncidentDetail(selectedIncident.id);
      setIncidentDetail(detail);
      if (detail.logs) {
        setLogs(detail.logs);
      }
    } catch (err) {
      console.error("Detail polling error:", err);
    }
  }, [selectedIncident]);

  // Initial load
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Load detail when selected incident changes
  useEffect(() => {
    if (selectedIncident) {
      fetchIncidentDetail();
    }
  }, [selectedIncident, fetchIncidentDetail]);

  // Periodic polling every 3 seconds for real-time live emergency coordination
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
      if (selectedIncident) {
        fetchIncidentDetail();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [fetchData, fetchIncidentDetail, selectedIncident]);

  const handleRefreshAll = () => {
    fetchData();
    if (selectedIncident) {
      fetchIncidentDetail();
    }
  };

  const handleSelectIncident = (inc) => {
    setSelectedIncident(inc);
  };

  const activeCount = incidents.filter(i => !['closed', 'rejected'].includes(i.status)).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Top Application Bar */}
      <Header
        currentRole={currentRole}
        setRole={setCurrentRole}
        onRefresh={handleRefreshAll}
        activeIncidentsCount={activeCount}
      />

      {/* Main View Container */}
      <main className="flex-1 p-3 md:p-4 max-w-7xl mx-auto w-full">
        {currentRole === 'operator' && (
          <div className="space-y-4">
            
            {/* Top Metric Cards */}
            <MetricCards
              incidents={incidents}
              ambulances={ambulances}
              hospitals={hospitals}
            />

            {/* Core Emergency System Architecture Visualizer */}
            <WorkflowVisualizer
              selectedIncident={selectedIncident}
              activeRoute={incidentDetail?.route}
            />

            {/* Split Screen Dashboard: Queue (3 cols), Map (5 cols), Inspection (4 cols) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              
              {/* Left Column: Active Incidents Queue */}
              <div className="lg:col-span-3">
                <IncidentList
                  incidents={incidents}
                  selectedIncident={selectedIncident}
                  onSelectIncident={handleSelectIncident}
                />
              </div>

              {/* Center Column: Live Tactical Leaflet Map */}
              <div className="lg:col-span-5 flex flex-col gap-4">
                <div className="flex-1 min-h-[440px]">
                  <LiveMap
                    incidents={incidents.filter(i => !['closed', 'rejected'].includes(i.status))}
                    ambulances={ambulances}
                    hospitals={hospitals}
                    activeRoute={incidentDetail?.route}
                    selectedIncident={selectedIncident}
                    onSelectIncident={handleSelectIncident}
                  />
                </div>

                {/* Live Operations Audit Timeline (below map) */}
                <div className="h-44">
                  <TimelineFeed logs={logs} />
                </div>
              </div>

              {/* Right Column: Selected Incident Deep Dive & Rerouting Center */}
              <div className="lg:col-span-4">
                <IncidentDetail
                  incidentDetail={incidentDetail}
                  onRefresh={handleRefreshAll}
                  onOpenOverride={() => setOverrideModalOpen(true)}
                />
              </div>

            </div>

          </div>
        )}

        {/* Citizen SOS View */}
        {currentRole === 'citizen' && (
          <CitizenPortal onIncidentCreated={handleRefreshAll} />
        )}

        {/* Ambulance Driver HUD View */}
        {currentRole === 'ambulance' && (
          <AmbulanceHUD
            ambulances={ambulances}
            incidents={incidents}
            activeRoute={incidentDetail?.route}
            onRefresh={handleRefreshAll}
          />
        )}

        {/* Hospital Intake Desk View */}
        {currentRole === 'hospital' && (
          <HospitalDesk
            hospitals={hospitals}
            incidents={incidents}
            ambulances={ambulances}
            onRefresh={handleRefreshAll}
          />
        )}
      </main>

      {/* Human Operator Override Modal */}
      <HumanOverrideModal
        isOpen={overrideModalOpen}
        onClose={() => setOverrideModalOpen(false)}
        incidentDetail={incidentDetail}
        ambulances={ambulances}
        hospitals={hospitals}
        onSuccess={handleRefreshAll}
      />

    </div>
  );
}
