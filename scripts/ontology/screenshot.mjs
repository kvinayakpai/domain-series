// Takes the picture of the ontology as an open-source tool shows it: the "Case" class on the
// documentation page pyLODE wrote (public/data/ontology/store-014.html, from check.py).
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const page = path.join(root, 'public', 'data', 'ontology', 'store-014.html');
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
await tab.goto(`file://${page}`);
const section = tab.locator('[id="Case"]').first();
const box = await section.boundingBox();
await section.screenshot({ path: path.join(outDir, 'pylode-case.png') });
console.log(`wrote public/images/ontology-in-open-standards/pylode-case.png (${Math.round(box.width * 2)}x${Math.round(box.height * 2)})`);
await browser.close();
