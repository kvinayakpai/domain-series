# Why Domain Matters

A blog series on why domain knowledge matters. Each post takes one real operational failure from Indian grocery retail, follows it through the people who see it differently, and ships with a demo scenario, downloadable records, a slide deck and a captioned video.

Live site: https://kvinayakpai.github.io/domain-series/

## Layout

- `src/content/posts/*.md`: one file per post. Front matter holds the title, the "record says" and "what actually happened" lines, dates and draft status.
- `src/pages/`: home (audit table of the posts), one route per post, the demo, RSS (`rss.xml`). The sitemap is generated at build time.
- `src/styles/global.css`: design tokens. Blue monospace is what a system records, serif ink is what happened, yellow marks the gap.
- `public/og/`: link-preview images, rendered by `npm run og` from the post front matter.
- `tests/e2e/`: Playwright tests run on desktop and mobile in CI before every deploy.

## Data

Demo data comes from the India grocery world in the Domain Explorer project (`synthetic-data/india_grocery/`, seed 42). A small, static slice is exported into this repo, so the site has no runtime dependency on Domain Explorer.

## Develop

    npm install
    npm run dev          # local server
    npm run build        # static build into dist/
    npm run og           # re-render link-preview images
    npm run test:e2e     # build first; runs the Playwright suite against the built site
