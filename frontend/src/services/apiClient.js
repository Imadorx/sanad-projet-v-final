import axios from 'axios';

/**
 * Central axios instance for all SANAD API calls.
 *
 * withCredentials: true is required because authentication is Odoo's
 * native session cookie (set by /api/auth/login via request.session.
 * authenticate on the backend) - not a bearer token. Every request
 * below automatically carries that cookie.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_ODOO_URL || '',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Odoo's `type='json'` routes expect JSON-RPC-shaped bodies in the
// strictest sense, but our controllers read raw request.httprequest.data
// as plain JSON, so a plain JSON body (not JSON-RPC envelope) is correct
// here and matches every controller written in Phases 1-6 API layer.

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalize error shape so every caller can rely on error.apiMessage
    // and error.apiCode regardless of whether Odoo returned our JSON
    // error envelope, a network failure, or an unexpected HTML error page.
    if (error.response && error.response.data && typeof error.response.data === 'object') {
      error.apiMessage = error.response.data.message || 'Request failed.';
      error.apiCode = error.response.data.code || 'error';
      error.apiStatus = error.response.status;
    } else if (error.request) {
      error.apiMessage = 'Cannot reach the SANAD server. Check your connection.';
      error.apiCode = 'network_error';
      error.apiStatus = 0;
    } else {
      error.apiMessage = error.message || 'Unexpected error.';
      error.apiCode = 'client_error';
      error.apiStatus = 0;
    }
    return Promise.reject(error);
  }
);

export default apiClient;
