/**
 * Screenshot helper for reviewing pages during development.
 *
 * Not part of the build. Point it at a running dev server:
 *
 *   node tools/shoot.mjs /docs/ /docs/mcp/
 *
 * Writes desktop and phone PNGs to .shots/ (gitignored).
 */
import puppeteer from 'puppeteer-core';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const outDir = join(root, '.shots');
const base = process.env.SHOOT_BASE ?? 'http://localhost:4321';
const executablePath =
  process.env.CHROME_PATH ??
  `${process.env.HOME}/.cache/puppeteer/chrome/mac_arm-151.0.7922.47/chrome-mac-arm64/` +
    'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';

const paths = process.argv.slice(2);
if (paths.length === 0) {
  console.error('usage: node tools/shoot.mjs <path> [<path>...]');
  process.exit(1);
}

const viewports = [
  { name: 'desktop', width: 1440, height: 1000, deviceScaleFactor: 1 },
  { name: 'phone', width: 390, height: 844, deviceScaleFactor: 2 },
];

await mkdir(outDir, { recursive: true });

const browser = await puppeteer.launch({ executablePath, headless: true });

for (const path of paths) {
  const slug = path.replace(/^\/|\/$/g, '').replace(/\//g, '-') || 'home';
  for (const viewport of viewports) {
    const page = await browser.newPage();
    await page.setViewport(viewport);
    const response = await page.goto(base + path, { waitUntil: 'networkidle0' });
    if (!response?.ok()) {
      console.error(`  !! ${path} → HTTP ${response?.status()}`);
    }
    // Fonts have to be in before anything is measured or captured.
    await page.evaluate(() => document.fonts.ready);

    const file = join(outDir, `${slug}-${viewport.name}.png`);
    await page.screenshot({ path: file, fullPage: process.env.SHOOT_FULL !== '0' });

    // A horizontal scrollbar at phone width is a bug, so report it here rather
    // than hoping it is noticed in a tall screenshot.
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth
    );
    console.log(
      `  ${file.replace(root + '/', '')}${overflow > 0 ? `  OVERFLOW +${overflow}px` : ''}`
    );
    await page.close();
  }
}

await browser.close();
