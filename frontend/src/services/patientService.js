import apiClient from './apiClient';

const patientService = {
  async list() {
    const res = await apiClient.get('/api/patients');
    return res.data.patients;
  },
  async get(id) {
    const res = await apiClient.get(`/api/patients/${id}`);
    return res.data.patient;
  },
  async me() {
    const res = await apiClient.get('/api/patients/me');
    return res.data.patient;
  },
  async create(payload) {
    const res = await apiClient.post('/api/patients', payload);
    return res.data.patient;
  },
  async update(id, payload) {
    const res = await apiClient.put(`/api/patients/${id}`, payload);
    return res.data.patient;
  },
  async listCareRelationships(patientId) {
    const res = await apiClient.get('/api/care-relationships', { params: { patient_id: patientId } });
    return res.data.relationships;
  },
  async createCareRelationship(payload) {
    const res = await apiClient.post('/api/care-relationships', payload);
    return res.data.relationship;
  },
};

export default patientService;
