import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
const b = await chromium.launch();
for (const [name, dark] of [['light',false],['dark',true]]) {
  const p = await b.newPage({ viewport:{width:1600,height:1400}, deviceScaleFactor:3 });
  await p.goto('http://localhost:4917/logos/', { waitUntil:'networkidle' });
  const r = await p.evaluate((dark) => {
    const sel = 'svg[aria-label*="Ripple, Sheen"]';
    let nodes=[...document.querySelectorAll(sel)];
    // pick the group on the requested ground by looking at nearest bg
    const card = nodes[0].closest('li,article,section,div');
    let up=nodes[0]; for(let i=0;i<10&&up;i++){ if(up.querySelectorAll(sel).length>=4) break; up=up.parentElement; }
    up.scrollIntoView({block:'center'});
    const r2=up.getBoundingClientRect();
    return {x:r2.x,y:r2.y,w:r2.width,h:r2.height,n:up.querySelectorAll(sel).length};
  }, dark);
  console.log(name, JSON.stringify(r));
  await p.screenshot({ path:`.scratch-c39/live-${name}.png`, clip:{x:Math.max(0,r.x-16),y:Math.max(0,r.y-16),width:Math.min(1600-Math.max(0,r.x-16),r.w+32),height:Math.min(1400-Math.max(0,r.y-16),r.h+32)} });
  await p.close();
  break;
}
await b.close();
