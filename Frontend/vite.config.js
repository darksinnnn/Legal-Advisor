import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load environment variables from project root and Frontend directory
  const rootEnv = loadEnv(mode, path.resolve(__dirname, '..'), ['REACT_APP_', 'VITE_']);
  const localEnv = loadEnv(mode, __dirname, ['REACT_APP_', 'VITE_']);
  const mergedEnv = { ...rootEnv, ...localEnv };

  // Define process.env definitions for backward compatibility with existing Firebase code
  const processEnvDefines = {};
  for (const [key, val] of Object.entries(mergedEnv)) {
    processEnvDefines[`process.env.${key}`] = JSON.stringify(val);
  }
  processEnvDefines['process.env.NODE_ENV'] = JSON.stringify(mode);

  return {
    plugins: [
      react({
        // Enable JSX in .js files
        babel: {
          plugins: [],
        },
      }),
    ],
    esbuild: {
      loader: 'jsx',
      include: /src\/.*\.jsx?$/,
      exclude: [],
    },
    optimizeDeps: {
      esbuildOptions: {
        loader: {
          '.js': 'jsx',
        },
      },
    },
    define: processEnvDefines,
    server: {
      port: 3000,
      open: false,
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      chunkSizeWarningLimit: 1500,
    },
  };
});
