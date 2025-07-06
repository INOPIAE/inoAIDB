import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [
      vue(),
      vuetify({ autoImport: true }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    server: {
      host: env.VITE_HOST || '0.0.0.0',
      port: parseInt(env.VITE_FRONTEND_PORT) || 5173,
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      manifest: true,
      outDir: 'dist',
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/setupTests.js',
      mockReset: true,
      css: true, // neu: verhindert CSS-Fehler

  // wichtige Ergänzung:
      resolveSnapshotPath: true,
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
      files: ['**/*.spec.js'],
      transformMode: {
        web: [/\.vue$/, /\.js$/]
      },
      deps: {
        optimizer: {
          web: {
            include: ['vuetify'],
          },
        },
      },
    },
  }
})
