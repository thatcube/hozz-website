/**
 * Renders the social card and the touch icon from the same fonts and colours
 * the site uses, so they cannot drift from the design system.
 *
 * Playwright is not a dependency of this site — it is only needed when these
 * two images change:
 *
 *   npm i -D playwright && npx playwright install chromium
 *   node tools/build-images.mjs
 *
 * The generated PNGs are committed, so a normal build never needs this.
 */
import { chromium } from 'playwright';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pub = join(root, 'public');

const asDataUrl = async (name) =>
  `data:font/woff2;base64,${(await readFile(join(pub, 'fonts', name))).toString('base64')}`;

const [sentient, sentientItalic, general, mono] = await Promise.all([
  asDataUrl('sentient-500.woff2'),
  asDataUrl('sentient-400-italic.woff2'),
  asDataUrl('general-sans-400.woff2'),
  asDataUrl('ibm-plex-mono-400.woff2'),
]);

const mark = await readFile(join(pub, 'logo.svg'), 'utf8');

const chips = [
  ['#dd6558', 'heartRateVariabilitySDNN'],
  ['#e8863a', 'stepCount'],
  ['#7477cb', 'sleepAnalysis'],
  ['#3f9e9e', 'oxygenSaturation'],
  ['#4a8fc0', 'bodyMass'],
  ['#a173c4', 'mindfulSession'],
  ['#6c9f45', 'walkingSpeed'],
];

const og = `<!doctype html><html><head><meta charset="utf-8"><style>
  @font-face { font-family: 'Sentient'; src: url('${sentient}') format('woff2'); font-weight: 500; }
  @font-face { font-family: 'Sentient'; src: url('${sentientItalic}') format('woff2'); font-weight: 400; font-style: italic; }
  @font-face { font-family: 'General Sans'; src: url('${general}') format('woff2'); font-weight: 400; }
  @font-face { font-family: 'IBM Plex Mono'; src: url('${mono}') format('woff2'); font-weight: 400; }
  * { box-sizing: border-box; margin: 0; }
  body { width: 1200px; height: 630px; background: #fbfcf8; color: #1b2320;
         font-family: 'General Sans', sans-serif; overflow: hidden; }
  .pad { padding: 68px 72px; height: 100%; display: flex; flex-direction: column; }
  .brand { display: flex; align-items: center; gap: 14px; }
  .brand svg { width: 44px; height: 44px; }
  .brand span { font-family: 'Sentient'; font-weight: 500; font-size: 40px; letter-spacing: -0.015em; }
  h1 { font-family: 'Sentient'; font-weight: 500; font-size: 76px; line-height: 1.08;
       letter-spacing: -0.02em; margin-top: 52px; }
  h1 i { font-weight: 400; color: #4b9c5f; }
  .sub { margin-top: 24px; font-size: 25px; color: #4d5a53; max-width: 48ch; }
  /* The row bleeds off the right the same way the stream does on the site, so
     the fade is what makes the crop read as motion rather than as a mistake. */
  .chips { margin-top: auto; padding-top: 44px; display: flex; gap: 10px; flex-wrap: nowrap;
           width: calc(100% + 72px); mask-image: linear-gradient(90deg, #000 78%, transparent); }
  .chip { display: inline-flex; align-items: center; gap: 9px; padding: 11px 18px;
          border-radius: 999px; background: #fff; border: 1px solid #eff2e9;
          font-family: 'IBM Plex Mono'; font-size: 15px; color: #4d5a53; white-space: nowrap; }
  .chip i { width: 8px; height: 8px; border-radius: 50%; }
</style></head><body>
  <div class="pad">
    <div class="brand">${mark}<span>Hozz</span></div>
    <h1>Move your health data<br>where <i>you use it</i>.</h1>
    <p class="sub">Open source. No account, analytics, hosted relay, or default destination.</p>
    <div class="chips">
      ${chips.map(([c, t]) => `<span class="chip"><i style="background:${c}"></i>${t}</span>`).join('')}
    </div>
  </div>
</body></html>`;

const browser = await chromium.launch();

const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.setContent(og, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: join(pub, 'og-image.png') });
await page.close();

// Apple applies its own rounded mask, so the icon is drawn edge to edge.
const icon = await browser.newPage({ viewport: { width: 180, height: 180 } });
await icon.setContent(
  `<!doctype html><html><body style="margin:0">
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="180" height="180">
     <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="64" gradientUnits="userSpaceOnUse">
       <stop offset="0" stop-color="#4ea56a"/><stop offset="1" stop-color="#2b7247"/></linearGradient></defs>
     <rect width="64" height="64" fill="url(#g)"/>
     <circle cx="23" cy="25.5" r="3.7" fill="#fff"/>
     <circle cx="41" cy="25.5" r="3.7" fill="#fff"/>
     <path d="M18.5 35.2c1.9 7.5 7.2 11.1 13.4 11.1 4.6 0 8.5-2.3 10.7-6.3l4.3-7.8"
           fill="none" stroke="#fff" stroke-width="4.6" stroke-linecap="round" stroke-linejoin="round"/>
   </svg></body></html>`,
  { waitUntil: 'load' },
);
await icon.screenshot({ path: join(pub, 'apple-touch-icon.png') });
await icon.close();

await browser.close();
console.log('wrote public/og-image.png and public/apple-touch-icon.png');
