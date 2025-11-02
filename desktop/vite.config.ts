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
}));
