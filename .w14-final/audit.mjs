import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';

const browser = await chromium.launch({ headless: true });
const results = [];

for (const width of [1920, 1440, 390]) {
  const context = await browser.newContext({
    viewport: { width, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const external = [];
  page.on('request', (request) => {
    if (new URL(request.url()).origin !== 'http://127.0.0.1:5184') external.push(request.url());
  });
  await page.goto('http://127.0.0.1:5184/w/w14/', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  const metrics = await page.evaluate(() => {
    const icons = [...document.querySelectorAll('.destination-top path')];
    const colors = [...document.querySelectorAll('.destination-top svg')].map(
      (icon) => getComputedStyle(icon).color,
    );
    return {
      overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
      height: document.documentElement.scrollHeight,
      iconCount: icons.length,
      distinctIcons: new Set(icons.map((icon) => icon.getAttribute('d'))).size,
      distinctIconColors: new Set(colors).size,
    };
  });
  await page.locator('.destinations').screenshot({
    path: `.w14-final/${width}-destinations.png`,
    animations: 'disabled',
  });
  await page.screenshot({
    path: `.w14-final/${width}-full.png`,
    fullPage: true,
    animations: 'disabled',
  });
  results.push({ width, external, ...metrics });
  await context.close();
}

await browser.close();
await writeFile('.w14-final/report.json', JSON.stringify(results, null, 2));
console.log(JSON.stringify(results, null, 2));
