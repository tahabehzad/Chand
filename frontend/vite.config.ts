import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    {
      name: 'chand-ir-rewrite',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const host = req.headers.host || '';
          const url = req.url?.split('?')[0];
          if (url === '/chand.ir' || url === '/chand.ir/') {
            req.url = '/chand.ir/index.html';
          } else if (host.startsWith('chand.ir') && (url === '/' || url === '')) {
            req.url = '/chand.ir/index.html';
          }
          next();
        });
      },
    },
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    allowedHosts: true,
    port: 5273,
    // The API is a separate FastAPI service on loopback. In development the
    // SPA calls `/api/...` on its own origin and Vite forwards it, so the
    // browser never needs a cross-origin credential grant. A deployment that
    // serves the SPA elsewhere sets `VITE_API_BASE_URL` instead.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
    strictPort: false,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    css: false,
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
