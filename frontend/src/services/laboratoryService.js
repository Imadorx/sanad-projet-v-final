import apiClient from './apiClient';

const laboratoryService = {
  async listRequests(params = {}) {
    const res = await apiClient.get('/api/lab-requests', { params });
    return res.data.lab_requests;
  },
  async getRequest(id) {
    const res = await apiClient.get(`/api/lab-requests/${id}`);
    return res.data.lab_request;
  },
  async createRequest(payload) {
    const res = await apiClient.post('/api/lab-requests', payload);
    return res.data.lab_request;
  },
  async transitionRequest(id, action) {
    const res = await apiClient.post(`/api/lab-requests/${id}/action`, { action });
    return res.data.lab_request;
  },
  async listResults(params = {}) {
    const res = await apiClient.get('/api/lab-results', { params });
    return res.data.lab_results;
  },
  async createResult(payload) {
    const res = await apiClient.post('/api/lab-results', payload);
    return res.data.lab_result;
  },
  async getKpiEvolution(patientId, analysisName) {
    const res = await apiClient.get('/api/lab-results/kpi', {
      params: { patient_id: patientId, analysis_name: analysisName },
    });
    return res.data.evolution;
  },
};

export default laboratoryService;
