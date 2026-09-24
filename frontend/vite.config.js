import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Vite configuration for the Lunar AI Ice Detection dashboard.
// The dev server proxies API + generated-output requests to the FastAPI backend
// so the frontend can call relative paths (e.g. /api/ice/process).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/outputs": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
