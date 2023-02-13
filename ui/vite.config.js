import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  build: {
    outDir: '../server/web',
    assetsDir: 'static',
    emptyOutDir: true,
    polyfillDynamicImport: true,
    manifest: true
  },
  plugins: [vue()],
  server: {
    port: 3000
  }
})
