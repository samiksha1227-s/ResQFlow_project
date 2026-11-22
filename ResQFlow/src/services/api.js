import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Incidents
  getIncidents: async (params = {}) => {
    const res = await client.get('/incidents', { params });
    return res.data;
  },
  
  getIncidentDetail: async (id) => {
    const res = await client.get(`/incidents/${id}`);
    return res.data;
  },

  reportIncident: async (data) => {
    const res = await client.post('/incidents/report', data);
    return res.data;
  },

  overrideIncident: async (id, data) => {
    const res = await client.patch(`/incidents/${id}/override`, data);
    return res.data;
  },

  updateIncidentStatus: async (id, status) => {
    const res = await client.post(`/incidents/${id}/status`, { status });
    return res.data;
  },

  // Ambulances
  getAmbulances: async () => {
    const res = await client.get('/ambulances');
    return res.data;
  },

  updateAmbulanceLocation: async (id, data) => {
    const res = await client.patch(`/ambulances/${id}/location`, data);
    return res.data;
  },

  // Hospitals
  getHospitals: async () => {
    const res = await client.get('/hospitals');
    return res.data;
  },

  updateHospitalCapacity: async (id, data) => {
    const res = await client.patch(`/hospitals/${id}/capacity`, data);
    return res.data;
  },

  // Routing & Blockage Simulation
  simulateRoadBlockage: async (incidentId, blockedSegmentName = "Central Expressway Overpass") => {
    const res = await client.post('/routing/simulate-blockage', {
      incident_id: incidentId,
      blocked_segment_name: blockedSegmentName
    });
    return res.data;
  },

  clearRoadBlockage: async (incidentId) => {
    const res = await client.post(`/routing/clear-blockage/${incidentId}`);
    return res.data;
  },

  getActiveRoute: async (incidentId) => {
    const res = await client.get(`/routing/active/${incidentId}`);
    return res.data;
  },

  // Simulation & Scenarios
  listScenarios: async () => {
    const res = await client.get('/simulation/scenarios');
    return res.data;
  },

  triggerScenario: async (scenarioId) => {
    const res = await client.post(`/simulation/trigger/${scenarioId}`);
    return res.data;
  },

  resetSimulation: async () => {
    const res = await client.post('/simulation/reset');
    return res.data;
  },

  // AI Media Analysis
  analyzeMedia: async (formData) => {
    const res = await client.post('/ai/analyze-media', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  }
};
