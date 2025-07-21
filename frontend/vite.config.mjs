import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { execSync } from 'child_process';

const commitHash = execSync('git rev-parse --short HEAD').toString().trim();
const commitDate = execSync('git log -1 --format=%cd --date=format:"%Y-%m-%d"').toString().trim();

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    plugins: [vue()],
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
    define: {
    __APP_COMMIT__: JSON.stringify(commitHash),
    __APP_COMMIT_DATE__: JSON.stringify(commitDate),
  },
  }
})
