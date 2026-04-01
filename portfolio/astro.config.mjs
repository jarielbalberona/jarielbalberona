import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://jarielbalberona.com',
  vite: {
    plugins: [tailwindcss()],
  },
});
