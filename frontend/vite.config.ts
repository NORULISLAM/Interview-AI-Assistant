import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000", // your backend
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react()],
});
