import fs from 'node:fs/promises';
import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';

const refs = [
  ['Plozz', '/Users/brandon/hozzshots/ref/plozz.svg'],
  ['Mozz', '/Users/brandon/hozzshots/ref/mozz.svg'],
  ['Twozz', '.briefs/twozz-shipped.svg'],
];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

for (const [name, path] of refs) {
  const svg = await fs.readFile(path, 'utf8');
  const result = await page.evaluate(async (source) => {
    const image = new Image();
    image.src = `data:image/svg+xml;base64,${btoa(source)}`;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 32;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    context.imageSmoothingEnabled = false;
    context.drawImage(image, 0, 0, 32, 32);
    const rgba = context.getImageData(0, 0, 32, 32).data;
    const pixels = [];
    for (let i = 0; i < rgba.length; i += 4) {
      pixels.push(rgba.slice(i, i + 4).join(','));
    }
    return pixels;
  }, svg);

  const colours = [...new Set(result)].filter((colour) => !colour.endsWith(',0'));
  const symbols = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const index = new Map(colours.map((colour, i) => [colour, symbols[i]]));

  console.log(`\n${name}: ${colours.length} rendered tones`);
  console.log(colours.map((colour, i) => `${symbols[i]} rgba(${colour})`).join(' · '));
  for (let y = 0; y < 32; y++) {
    const row = result
      .slice(y * 32, y * 32 + 32)
      .map((colour) => index.get(colour) ?? '.')
      .join('');
    console.log(`${String(y).padStart(2)} ${row}`);
  }
}

await browser.close();
