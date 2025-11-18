import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  // Development server configuration
  server: {
    port: 5173,
    strictPort: false,
    cors: true
  },

  // Production build configuration
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': [
            'react',
            'react-dom',
            'react-hook-form',
          ],
          'ui': [
            '@radix-ui/react-dialog',
            '@radix-ui/react-select',
            'recharts',
          ],
        }
      }
    }
  },

  // Preview server configuration
  preview: {
    port: 4173,
    host: true,
    strictPort: false,
  },

  // Base path for deployment
  base: '/',

  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-hook-form',
      'lucide-react',
      'sonner',
    ]
  }
})