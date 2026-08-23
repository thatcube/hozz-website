import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1000, height: 820 }, deviceScaleFactor: 1 });
await page.goto('http://127.0.0.1:4783/logos/', { waitUntil: 'networkidle' });

const marks = await page.evaluate(() =>
  ['c31', 'c32', 'c33', 'c34'].map((slug) => {
    const card = document.querySelector(`#${slug}`);
    return {
      slug,
      name: card.querySelector('.tag span').textContent,
      svg: card.querySelector('.ground--light svg').outerHTML,
    };
  })
);

const sized = (svg, size) => svg
  .replace(/width="\\d+"/, `width="${size}"`)
  .replace(/height="\\d+"/, `height="${size}"`);

await page.setContent(`<!doctype html>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; padding: 30px; background: #e9ebee; color: #15171b; font: 14px system-ui; }
  main { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  article { background: white; border-radius: 16px; padding: 18px; }
  h2 { margin: 0 0 14px; font-size: 16px; }
  .grounds { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .ground { min-height: 140px; border-radius: 12px; display: flex; align-items: center;
    justify-content: center; gap: 24px; }
  .light { background: #fbfbfc; border: 1px solid #e5e7ea; }
  .dark { background: #17181c; }
  .sample { display: grid; justify-items: center; gap: 8px; }
  span { color: #666b73; font: 11px ui-monospace, monospace; }
  .dark span { color: #a0a5ad; }
</style>
<main>
${marks.map(({ slug, name, svg }) => `<article>
  <h2>${slug} · ${name}</h2>
  <div class="grounds">
    <div class="ground light">
      <div class="sample">${sized(svg, 96)}<span>96px</span></div>
      <div class="sample">${sized(svg, 24)}<span>24px</span></div>
    </div>
    <div class="ground dark">
      <div class="sample">${sized(svg, 96)}<span>96px</span></div>
      <div class="sample">${sized(svg, 24)}<span>24px</span></div>
    </div>
  </div>
</article>`).join('')}
</main>`);

await page.screenshot({ path: 'scratch-concentric/pass1.png', fullPage: true });
await browser.close();
