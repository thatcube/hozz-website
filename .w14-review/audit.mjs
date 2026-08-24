import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';

const widths = [1920, 1440, 1121, 1120, 1024, 901, 900, 701, 700, 431, 430, 390];
const screenshots = new Set([1920, 1440, 390]);
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
    if (new URL(request.url()).origin !== 'http://127.0.0.1:5177') external.push(request.url());
  });
  await page.goto('http://127.0.0.1:5177/w/w14/', { waitUntil: 'networkidle' });
  await page.locator('.hero-copy').waitFor();
  await page.evaluate(() => document.fonts.ready);

  const audit = await page.evaluate(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const box = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && box.width > 0 && box.height > 0;
    };
    const rect = (element) => {
      const box = element.getBoundingClientRect();
      return { x: box.x, y: box.y, right: box.right, bottom: box.bottom };
    };
    const overlap = (a, b) =>
      Math.max(0, Math.min(a.right, b.right) - Math.max(a.x, b.x)) *
      Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.y, b.y));

    const floats = [...document.querySelectorAll('.crossing .float')]
      .filter(visible)
      .map((element) => ({ name: element.className, rect: rect(element) }));
    const fragments = [];
    const walker = document.createTreeWalker(document.querySelector('.hero-copy'), NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      if (!walker.currentNode.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(walker.currentNode);
      for (const box of range.getClientRects()) {
        if (box.width && box.height) {
          fragments.push({
            name: walker.currentNode.textContent.trim(),
            rect: { x: box.x, y: box.y, right: box.right, bottom: box.bottom },
          });
        }
      }
    }

    const collisions = [];
    for (let index = 0; index < floats.length; index += 1) {
      for (let other = index + 1; other < floats.length; other += 1) {
        if (overlap(floats[index].rect, floats[other].rect) > 1) {
          collisions.push(`${floats[index].name} ↔ ${floats[other].name}`);
        }
      }
      for (const fragment of fragments) {
        if (overlap(floats[index].rect, fragment.rect) > 1) {
          collisions.push(`${floats[index].name} ↔ ${fragment.name}`);
        }
      }
    }

    const footholdOrnaments = [...document.querySelectorAll('.foothold')].map((element) => ({
      after: getComputedStyle(element, '::after').content,
      before: getComputedStyle(element, '::before').content,
    }));
    const clippedDecorations = [
      ...document.querySelectorAll('.destination-grid li, .durability-grid li'),
    ].map((element) => ({
      className: element.className,
      overflow: getComputedStyle(element).overflow,
      after: getComputedStyle(element, '::after').content,
    }));

    return {
      overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
      conditions: document.querySelector('.conditions').innerText,
      collisions,
      footholdOrnaments,
      clippedDecorations,
    };
  });

  if (screenshots.has(width)) {
    await page.screenshot({ path: `.w14-review/w14-${width}.png`, animations: 'disabled' });
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
    external: item.external.length,
    conditions: item.conditions.replaceAll('\n', ' / '),
    footholdOrnaments: new Set(item.footholdOrnaments.flatMap(({ after, before }) => [after, before])),
    clippedDecorations: new Set(item.clippedDecorations.map(({ overflow }) => overflow)),
  });
}
