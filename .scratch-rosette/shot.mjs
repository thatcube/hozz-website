import { chromium } from '/Users/brandon/Development/amazon-subscription-canceller/node_modules/playwright/index.mjs';
import { readFileSync, writeFileSync } from 'node:fs';
import { facePathsAt } from './mark.mjs';
const marks = JSON.parse(readFileSync('.scratch-rosette/marks.json','utf8'));
const SIZES=[96,48,32,24];
const svg=(m,{noFace=false,faceOnly=false}={})=>{
  let s=`<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">`;
  if(!faceOnly) for(const [px,fill] of m.layers)
    s+=`<path fill="${fill}" d="${px.map(([x,y])=>`M${x} ${y}h1v1h-1z`).join('')}"/>`;
  if(!noFace){ const f=m.fit;
    for(const d of facePathsAt({cx:16,cy:f.cy,size:f.size,smile:'wide',gap:f.gap}))
      s+=`<path fill="${faceOnly?'#111':m.face}" d="${d}"/>`; }
  return s+`</svg>`;
};
const cell=(g,s,cls)=>`<td class="${cls}"><div style="width:${s}px;height:${s}px">${g.replace('<svg',`<svg width="${s}" height="${s}"`)}</div></td>`;
let html=`<style>body{margin:0;font:11px ui-monospace}table{border-collapse:collapse}td,th{padding:6px 8px;text-align:center}
.l{background:#fbfbfc}.d{background:#17181c;color:#888}.s{background:#eef0f2}</style><table>`;
html+=`<tr><th></th>${SIZES.map(s=>`<th>${s}</th>`).join('')}${SIZES.map(s=>`<th>${s}d</th>`).join('')}<th>no face</th><th>face only</th></tr>`;
for(const [slug,m] of Object.entries(marks)){
  const g=svg(m);
  html+=`<tr><td>${slug}</td>`;
  for(const s of SIZES) html+=cell(g,s,'l');
  for(const s of SIZES) html+=cell(g,s,'d');
  html+=cell(svg(m,{noFace:true}),72,'s');
  html+=cell(svg(m,{faceOnly:true}),72,'s');
  html+=`</tr>`;
}
html+=`</table>`;
writeFileSync('.scratch-rosette/board.html',html);
const b=await chromium.launch(); const p=await b.newPage({deviceScaleFactor:2});
await p.setContent(html); await p.locator('table').screenshot({path:'.scratch-rosette/board.png'});
await b.close(); console.log('shot');
