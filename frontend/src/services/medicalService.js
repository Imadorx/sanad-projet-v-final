import apiClient from './apiClient';

const medicalService = {
  async getMedicalRecord(patientId) {
    const res = await apiClient.get(`/api/medical-records/${patientId}`);
    return res.data.medical_record;
  },
  async listConsultations(patientId) {
    const res = await apiClient.get('/api/consultations', { params: patientId ? { patient_id: patientId } : {} });
    return res.data.consultations;
  },
  async getConsultation(id) {
    const res = await apiClient.get(`/api/consultations/${id}`);
    return res.data.consultation;
  },
  async createConsultation(payload) {
    const res = await apiClient.post('/api/consultations', payload);
    return res.data.consultation;
  },
  async listPrescriptions(patientId) {
    const res = await apiClient.get('/api/prescriptions', { params: patientId ? { patient_id: patientId } : {} });
    return res.data.prescriptions;
  },
  async createPrescription(payload) {
    const res = await apiClient.post('/api/prescriptions', payload);
    return res.data.prescription;
  },
};

export default medicalService;
