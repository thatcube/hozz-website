import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';

const widths = [1920, 1440, 1121, 1120, 1024, 901, 900, 701, 700, 431, 430, 390];
const screenshotWidths = new Set([1920, 1440, 1024, 390]);
const browser = await chromium.launch({ headless: true });
const report = [];

for (const width of widths) {
  const context = await browser.newContext({
    viewport: { width, height: 900 },
    deviceScaleFactor: 1,
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const external = [];
  page.on('request', (request) => {
    const url = new URL(request.url());
    if (url.origin !== 'http://127.0.0.1:5176') external.push(request.url());
  });
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const response = await page.goto('http://127.0.0.1:5176/w/w14/', { waitUntil: 'networkidle' });
    if (response?.ok() && (await page.locator('.hero-copy').count())) break;
    await page.waitForTimeout(300);
  }
  await page.locator('.hero-copy').waitFor();
  await page.evaluate(() => document.fonts.ready);

  const audit = await page.evaluate(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    };
    const rect = (element) => {
      const value = element.getBoundingClientRect();
      return {
        x: value.x,
        y: value.y,
        right: value.right,
        bottom: value.bottom,
        width: value.width,
        height: value.height,
      };
    };
    const intersection = (a, b) => {
      const width = Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x));
      const height = Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));
      return width * height;
    };

    const floats = [...document.querySelectorAll('.crossing .float')]
      .filter(visible)
      .map((element) => ({
        name: element.className,
        rect: rect(element),
      }));

    const copy = document.querySelector('.hero-copy');
    const textFragments = [];
    const walker = document.createTreeWalker(copy, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!node.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const value of range.getClientRects()) {
        if (value.width === 0 || value.height === 0) continue;
        textFragments.push({
          name: `${node.parentElement.className || node.parentElement.tagName}: ${node.textContent.trim()}`,
          rect: {
            x: value.x,
            y: value.y,
            right: value.right,
            bottom: value.bottom,
            width: value.width,
            height: value.height,
          },
        });
      }
    }

    const collisions = [];
    for (let index = 0; index < floats.length; index += 1) {
      for (let other = index + 1; other < floats.length; other += 1) {
        const area = intersection(floats[index].rect, floats[other].rect);
        if (area > 1) {
          collisions.push({
            a: floats[index].name,
            b: floats[other].name,
            area: Math.round(area),
          });
        }
      }
      for (const fragment of textFragments) {
        const area = intersection(floats[index].rect, fragment.rect);
        if (area > 1) {
          collisions.push({
            a: floats[index].name,
            b: fragment.name,
            area: Math.round(area),
          });
        }
      }
    }

    const visibleAboveFold = floats
      .filter((item) => item.rect.y < innerHeight && item.rect.bottom > 0)
      .map((item) => ({
        name: item.name,
        top: Math.round(item.rect.y),
        bottom: Math.round(item.rect.bottom),
        fullyVisible: item.rect.bottom <= innerHeight,
      }));

    const conditions = document.querySelector('.conditions').innerText.replace(/\s+/g, ' ').trim();
    return {
      overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
      pageHeight: document.documentElement.scrollHeight,
      collisions,
      visibleAboveFold,
      conditions,
    };
  });

  if (screenshotWidths.has(width)) {
    await page.screenshot({
      path: `.w14-review/w14-${width}.png`,
      animations: 'disabled',
    });
  }

  report.push({ width, external, ...audit });
  await context.close();
}

await browser.close();
await writeFile('.w14-review/report.json', JSON.stringify(report, null, 2));
for (const item of report) {
  console.log({
    width: item.width,
    overflow: item.overflow,
    collisions: item.collisions.length,
    aboveFold: item.visibleAboveFold.length,
    external: item.external.length,
    conditions: item.conditions,
  });
}
