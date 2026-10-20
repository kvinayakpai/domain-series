# domain-series

A blog series on why domain matters, with one end-to-end demo, "One grocery basket, three domains".

Live site (once Pages is enabled): https://kvinayakpai.github.io/domain-series/

- Posts: `src/content/posts/*.md` (Retail, Logistics, Payments)
- Pages: `src/pages/` (home, one route per post, demo)
- Demo: `src/lib/basket.ts` is a seeded, deterministic one-basket simulation; the demo page drives it. Data is synthetic and not read from the Domain Explorer tables.

## Develop

    npm install
    npm run dev
    npm run build
