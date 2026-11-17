import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://kvinayakpai.github.io',
  base: '/domain-series/',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  redirects: {
    // KPI 1 was the like-for-like post before the series became one KPI per post.
    '/like-for-like/': '/domain-series/sales/',
    // Season 2's first plan, live for a few hours on 17 November 2026, before the season was repivoted.
    '/every-word/': '/domain-series/what-is-an-ontology/',
    '/glossary-to-graph/': '/domain-series/what-is-an-ontology/',
    '/four-kb-note/': '/domain-series/why-ontology-matters/',
    '/what-is-an-item/': '/domain-series/ontology/',
  },
  markdown: {
    shikiConfig: { themes: { light: 'github-light', dark: 'github-dark' }, wrap: false },
  },
});
