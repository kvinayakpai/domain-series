import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://kvinayakpai.github.io',
  base: '/domain-series/',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
});
