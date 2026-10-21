import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import offlineShell from './scripts/offline-shell.mjs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), offlineShell()],
  build: { manifest: true },
  test: {
    environment: 'jsdom',
    clearMocks: true,

    coverage: {
      provider: 'v8',
      include: ['src/**/*.{js,jsx}'],
      exclude: ['src/tests/**'],
      reporter: ['text', 'json-summary', 'json', 'lcov', 'html'],
    },
  },
});
