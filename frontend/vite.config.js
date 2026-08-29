import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev server proxies /api to the Odoo backend so the React app can be
// developed standalone without CORS configuration on the Odoo side.
// In production, /api is served by the same Nginx host as the built
// static files (see docker/nginx.conf), so no proxy is needed there.
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_ODOO_URL || 'http://localhost:8069',
        changeOrigin: true,
      },
    },
  },
});
