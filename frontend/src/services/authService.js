import apiClient from './apiClient';

const authService = {
  async login(login, password) {
    const res = await apiClient.post('/api/auth/login', { login, password });
    return res.data.user;
  },
  async logout() {
    await apiClient.post('/api/auth/logout', {});
  },
  async getSession() {
    const res = await apiClient.post('/api/auth/session', {});
    return res.data.user;
  },
};

export default authService;
