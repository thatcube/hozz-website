import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1600,height:1400}, deviceScaleFactor:3 });
await p.goto('http://localhost:4917/logos/', { waitUntil:'networkidle' });
const info = await p.evaluate(() => {
  const svgs=[...document.getElementsByTagName('svg')];
  const hits=[];
  svgs.forEach((s,i)=>{ const t=s.querySelector('title'); if(t && t.textContent.includes('Sheen')) hits.push([i, t.textContent, s.getBoundingClientRect().width]); });
  return {total:svgs.length, hits, sample: svgs.slice(0,3).map(s=>s.querySelector('title')?.textContent)};
});
console.log(JSON.stringify(info,null,1));
await b.close();
