import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://jarielbalberona.dev',
  output: 'static',
  integrations: [sitemap()],
  // Avoid Astro dev toolbar (esp. Audit app's MutationObserver) fighting DevTools-driven
  // DOM churn and spamming console.error. Re-enable locally: `astro preferences enable devToolbar`.
  devToolbar: {
    enabled: false,
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
