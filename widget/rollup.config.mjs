import resolve from '@rollup/plugin-node-resolve';
import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';

export default {
  input: 'src/index.ts',
  output: [
    {
      file: 'dist/chatbot-widget.js',
      format: 'iife',
      name: 'MakeWebsiteAIReady',
      sourcemap: true,
    },
    {
      file: 'dist/chatbot-widget.esm.js',
      format: 'es',
      sourcemap: true,
    },
  ],
  plugins: [
    resolve(),
    typescript({ tsconfig: './tsconfig.json' }),
    terser(),
  ],
};
