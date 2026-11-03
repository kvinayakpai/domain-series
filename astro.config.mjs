import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://kvinayakpai.github.io',
  base: '/domain-series/',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  // KPI 1 was the like-for-like post before the series became one KPI per post.
  redirects: { '/like-for-like/': '/domain-series/sales/' },
  markdown: {
    shikiConfig: { themes: { light: 'github-light', dark: 'github-dark' }, wrap: false },
  },
});
