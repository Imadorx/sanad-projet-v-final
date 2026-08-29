import apiClient from './apiClient';

const chatService = {
  async listConversations() {
    const res = await apiClient.get('/api/chat/conversations');
    return res.data.conversations;
  },
  async getOrCreateConversation(otherUserId, conversationType, patientId) {
    const res = await apiClient.post('/api/chat/conversations', {
      other_user_id: otherUserId,
      conversation_type: conversationType,
      patient_id: patientId,
    });
    return res.data.conversation;
  },
  async listMessages(conversationId, afterId) {
    const res = await apiClient.get(`/api/chat/conversations/${conversationId}/messages`, {
      params: afterId ? { after_id: afterId } : {},
    });
    return res.data.messages;
  },
  async postMessage(conversationId, body) {
    const res = await apiClient.post(`/api/chat/conversations/${conversationId}/messages`, { body });
    return res.data.message;
  },
  async poll(sinceId) {
    const res = await apiClient.get('/api/chat/poll', { params: { since_id: sinceId || 0 } });
    return res.data.messages;
  },
};

export default chatService;
