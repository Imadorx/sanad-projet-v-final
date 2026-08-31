import apiClient from './apiClient';

const pharmacyService = {
  async listPharmacies() {
    const res = await apiClient.get('/api/pharmacies');
    return res.data.pharmacies;
  },
  async listPrescriptions(status) {
    const res = await apiClient.get('/api/pharmacy/prescriptions', {
      params: status ? { status } : {},
    });
    return res.data.prescriptions;
  },
  async transitionPrescription(id, action) {
    const res = await apiClient.post(`/api/pharmacy/prescriptions/${id}/action`, { action });
    return res.data.prescription;
  },
};

export default pharmacyService;
