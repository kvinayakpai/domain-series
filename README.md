# Why Domain Matters

A blog series on why domain knowledge matters. Each post takes one real operational failure from Indian grocery retail, follows it through the people who see it differently, and ships with a demo scenario, downloadable records, a slide deck and a captioned video.

Live site: https://kvinayakpai.github.io/domain-series/

## Layout

- `src/content/posts/`: one file per post (`.mdx` when the post uses figure components, `.md` otherwise). Front matter holds the title, the "record says" and "what actually happened" lines, dates and draft status.
- `src/pages/`: home (audit table of the posts), one route per post, the demo, the downloadable records (`data/`), RSS (`rss.xml`). The sitemap is generated at build time.
- `src/components/`: the retail and logistics demos and the post figures. Figures are static SVG with a table view, so they read without JavaScript.
- `src/styles/global.css`: design tokens. Blue monospace is what a system records, serif ink is what happened, yellow marks the gap.
- `public/og/`: link-preview images, rendered by `npm run og` from the post front matter.
- `tests/e2e/`: Playwright tests run on desktop and mobile in CI before every deploy.

## Media

- `public/media/<post>-short.mp4` (1080x1920, about a minute) and `<post>-walkthrough.mp4` (1920x1080, about two minutes), for each published post: captioned, no narration, rendered from the built site by `npm run video` (`scripts/video/render.py`, needs Python Playwright and ffmpeg; `npm run video -- logistics` renders one post). Captions read their numbers from the world data. `.srt` files sit beside them.
- `public/media/<post>-slides.pdf`: each post's deck as a PDF (the editable decks are Slides artifacts).

## Data

Demo data comes from the India grocery world in the Domain Explorer project (`synthetic-data/india_grocery/`, seed 42). A small, static slice is exported into this repo, so the site has no runtime dependency on Domain Explorer: `src/data/retail.json` and `src/data/logistics.json` drive the demos and figures, and `public/data/india-grocery/` holds the June records offered for download. To refresh it, run this from the Domain Explorer repo:

    python synthetic-data/india_grocery/export_blog.py --out ../domain-series

The Playwright suite checks the numbers quoted in each post against the exported data, so a re-export that changes the story fails the build until the prose is updated. The videos and the deck are not checked this way: if the story numbers change, re-render the videos with `npm run video` and update the decks and their PDFs by hand.

## Develop

    npm install
    npm run dev          # local server
    npm run build        # static build into dist/
    npm run og           # re-render link-preview images
    npm run test:e2e     # build first; runs the Playwright suite against the built site
    npm run video        # build first; re-renders the captioned videos
