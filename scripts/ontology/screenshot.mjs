// Takes the pictures of the ontology as open-source tools show it: the "Case" class on the documentation
// page pyLODE wrote (public/data/ontology/store-014.html), and the network graph vis-network draws
// (public/data/ontology/store-014-graph.html). check.py writes both pages.
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const data = path.join(root, 'public', 'data', 'ontology');
const outDir = path.join(root, 'public', 'images', 'ontology-in-open-standards');
mkdirSync(outDir, { recursive: true });

// Playwright's own browser in CI; a system Chrome where that is not installed.
let browser;
try {
  browser = await chromium.launch();
} catch {
  browser = await chromium.launch({ executablePath: process.env.CHROME ?? '/usr/bin/google-chrome' });
}

const tab = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 2 });
await tab.goto(`file://${path.join(data, 'store-014.html')}`);
const section = tab.locator('[id="Case"]').first();
const box = await section.boundingBox();
await section.screenshot({ path: path.join(outDir, 'pylode-case.png') });
console.log(`wrote public/images/ontology-in-open-standards/pylode-case.png (${Math.round(box.width * 2)}x${Math.round(box.height * 2)})`);

// The graph settles (a fixed random seed, so the same layout every time), then the buttons are hidden.
const graph = await browser.newPage({ viewport: { width: 1100, height: 1150 }, deviceScaleFactor: 2 });
const errors = [];
graph.on('pageerror', (e) => errors.push(String(e)));
await graph.goto(`file://${path.join(data, 'store-014-graph.html')}`);
await graph.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
if (errors.length) throw new Error(`The graph page failed:\n${errors.join('\n')}`);
await graph.addStyleTag({ content: '.tools { display: none; }' });
const stage = graph.locator('.stage');
const sbox = await stage.boundingBox();
await stage.screenshot({ path: path.join(outDir, 'network-graph.png') });
console.log(`wrote public/images/ontology-in-open-standards/network-graph.png (${Math.round(sbox.width * 2)}x${Math.round(sbox.height * 2)})`);
await browser.close();
