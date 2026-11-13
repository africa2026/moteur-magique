import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
    },
  },
  envDir: path.resolve(import.meta.dirname),
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    strictPort: false,
    host: true,
    // Autorise les hosts de prévisualisation (conteneurs, proxys, tunnels).
    // Le serveur étant en écoute sur 0.0.0.0, Vite doit accepter le Host reçu.
    allowedHosts: true,
    // En développement, le frontend appelle des URLs relatives (/api/...).
    // Ce proxy les redirige vers le backend Flask local (port 5000).
    // En production, définir VITE_API_URL vers l'URL du backend déployé.
    proxy: {
      "/api": {
        target: process.env.VITE_DEV_API_TARGET || "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
