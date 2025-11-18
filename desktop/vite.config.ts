import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
export default defineConfig(async () => ({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  // Electron requires relative paths for production builds
  base: "./",
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
  },

  // Environment variables configuration
  // Vite automatically loads .env files and exposes variables prefixed with VITE_
  // Example: VITE_API_BASE_URL will be available as import.meta.env.VITE_API_BASE_URL
  envPrefix: 'VITE_',
}));
