// Helpers the e2e specs share, so each spec quotes the page the same way.
import type { Page } from '@playwright/test';

/** A number as the Oil & Gas posts print it: rounded, with US thousands separators. */
export const us = (v: number) => Math.round(v).toLocaleString('en-US');

/** The day of the month in an ISO date or timestamp, as a number. */
export const dayOf = (iso: string) => Number(iso.slice(8, 10));

/** The text of a post's <article>, whitespace collapsed and typographic quotes made plain, so expectations can use plain ones. */
export async function articleText(page: Page, path: string) {
  await page.goto(path);
  return (await page.locator('article').innerText()).replace(/\s+/g, ' ').replace(/[’‘]/g, "'").replace(/[“”]/g, '"');
}
