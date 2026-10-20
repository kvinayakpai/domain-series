import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://kvinayakpai.github.io',
  base: '/domain-series/',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
