import { readFileSync, writeFileSync } from 'node:fs';
const html = readFileSync(new URL('../dist/logos/index.html', import.meta.url), 'utf8');
const want = process.argv.slice(2);
const svgs = [...html.matchAll(/<svg[\s\S]*?<\/svg>/g)].map((m) => m[0]);
const pick = {};
for (const s of svgs) {
  const t = /aria-label="([^"]*)"/.exec(s);
  if (!t) continue;
  for (const w of want) if (t[1].includes(w) && !pick[w]) pick[w] = s;
}
const SIZES = [400, 96, 48, 28, 16];
const rows = want.map((w) => {
  const svg = (pick[w] || '').replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
  return `{ name: ${JSON.stringify(w)}, svg: ${JSON.stringify(svg)} }`;
}).join(',\n');
writeFileSync(new URL('../dist/t13-preview.html', import.meta.url), `<!doctype html>
<meta charset="utf-8">
<style>
 body{background:#fff;margin:0;font:12px ui-monospace,monospace;color:#333}
 .row{display:flex;align-items:flex-end;gap:18px;padding:10px 14px;border-bottom:1px solid #eee}
 canvas{image-rendering:pixelated}
 .lbl{width:120px}
</style>
<div id="out"></div>
<script>
const MARKS=[\n${rows}\n];
const SIZES=${JSON.stringify(SIZES)};
const out=document.getElementById('out');
(async()=>{
 for(const m of MARKS){
  const row=document.createElement('div');row.className='row';
  const lbl=document.createElement('div');lbl.className='lbl';lbl.textContent=m.name;row.appendChild(lbl);
  const img=new Image();img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(m.svg);
  await img.decode();
  for(const s of SIZES){
   const c=document.createElement('canvas');c.width=s;c.height=s;
   const g=c.getContext('2d');g.imageSmoothingEnabled=false;g.drawImage(img,0,0,s,s);
   row.appendChild(c);
  }
  out.appendChild(row);
 }
 document.title='ready';
})();
</script>`);
console.log('preview written for', want.join(', '));
