import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  target: 'node18',
  clean: true,
  shims: true,
  splitting: false,
  banner: {
    js: '#!/usr/bin/env node',
  },
  dts: true,
  sourcemap: true,
  outDir: 'dist',
});
