import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:1600,height:1400}, deviceScaleFactor:3 });
await p.goto('http://localhost:4917/logos/', { waitUntil:'networkidle' });
const boxes = await p.evaluate(() => {
  const svgs=[...document.querySelectorAll('svg')].filter(s=>/Ripple, Sheen/.test(s.textContent||''));
  return svgs.map(s=>{const r=s.getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height};});
});
console.log(JSON.stringify(boxes));
if(boxes.length){
  const xs=boxes.map(v=>v.x), ys=boxes.map(v=>v.y);
  const x0=Math.min(...xs)-24, y0=Math.min(...ys)-24;
  const x1=Math.max(...boxes.map(v=>v.x+v.w))+24, y1=Math.max(...boxes.map(v=>v.y+v.h))+24;
  await p.screenshot({ path:'.scratch-c39/marks.png', clip:{x:x0,y:y0,width:x1-x0,height:y1-y0} });
}
await b.close();
