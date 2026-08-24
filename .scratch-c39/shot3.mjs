import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1600,height:1400}, deviceScaleFactor:3 });
await p.goto('http://localhost:4917/logos/', { waitUntil:'networkidle' });
const r = await p.evaluate(() => {
  const t=[...document.querySelectorAll('title')].find(t=>/Ripple, Sheen/.test(t.textContent));
  if(!t) return null;
  let n=t.closest('svg'); const list=[];
  // climb to the card that holds all the sizes
  let card=n; for(let i=0;i<8 && card;i++){ if(card.querySelectorAll('svg').length>=3) break; card=card.parentElement; }
  const rect=card.getBoundingClientRect();
  card.scrollIntoView();
  const r2=card.getBoundingClientRect();
  return {x:r2.x,y:r2.y,w:r2.width,h:r2.height,svgs:card.querySelectorAll('svg').length};
});
console.log(JSON.stringify(r));
if(r) await p.screenshot({ path:'.scratch-c39/marks.png', clip:{x:Math.max(0,r.x-12),y:Math.max(0,r.y-12),width:Math.min(1600,r.w+24),height:Math.min(1400,r.h+24)} });
await b.close();
