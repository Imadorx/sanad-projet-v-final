import apiClient from './apiClient';

const aiService = {
  async search(query, patientId) {
    const res = await apiClient.post('/api/ai/search', { query, patient_id: patientId });
    return res.data;
  },
  async explain(model, recordId) {
    const res = await apiClient.post('/api/ai/explain', { model, record_id: recordId });
    return res.data;
  },
  async translate(text, targetLang) {
    const res = await apiClient.post('/api/ai/translate', { text, target_lang: targetLang });
    return res.data;
  },
  async tts(text) {
    const res = await apiClient.post('/api/ai/tts', { text });
    return res.data;
  },
};

export default aiService;
