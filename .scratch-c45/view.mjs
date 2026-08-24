import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('.scratch-c45/dist/logos/index.html', 'utf8');
const svgs = html.match(/<svg[^>]*aria-label="Hozz[^"]*"[\s\S]*?<\/svg>/g) ?? [];
const byLabel = new Map();
for (const s of svgs) {
  const label = s.match(/aria-label="([^"]*)"/)[1];
  if (!byLabel.has(label)) byLabel.set(label, s);
}
console.log([...byLabel.keys()].join('\n'));

const pick = (label, size) => {
  const s = byLabel.get(label);
  if (!s) throw new Error(`missing ${label}`);
  return s.replace(/width="\d+"/, `width="${size}"`).replace(/height="\d+"/, `height="${size}"`);
};

const row = (label, sizes) => `
  <div class="row"><h2>${label}</h2>
    ${sizes.map((s) => `<div class="cell"><div class="light">${pick(label, s)}</div><span>${s}</span></div>`).join('')}
    ${sizes.map((s) => `<div class="cell"><div class="dark">${pick(label, s)}</div><span>${s}</span></div>`).join('')}
  </div>`;

const zoom = (label, size, scale) => `
  <div class="cell"><div class="light zoom" style="--s:${scale}">${pick(label, size * scale)}</div><span>${label} @${size} ×${scale}</span></div>`;

writeFileSync('.scratch-c45/view.html', `<!doctype html><meta charset="utf-8">
<style>
 body{background:#faf8f5;font:12px/1.4 ui-sans-serif,system-ui;margin:24px;color:#333}
 .row{display:flex;align-items:flex-end;gap:18px;margin:0 0 22px;flex-wrap:wrap}
 h2{font-size:12px;width:130px;margin:0;font-weight:600}
 .cell{display:flex;flex-direction:column;align-items:center;gap:5px}
 .light{background:#fff;padding:8px;border:1px solid #e6e2dc}
 .dark{background:#14161a;padding:8px;border:1px solid #14161a}
 .zoom svg{image-rendering:pixelated}
</style>
${row('Hozz — Ripple, Lens', [96, 48, 24, 16])}
${row('Hozz — Ripple, Centred', [96, 48, 24, 16])}
${row('Hozz — Ripple', [96, 48, 24, 16])}
<div class="row"><h2>zoom</h2>
${zoom('Hozz — Ripple, Lens', 96, 4)}
${zoom('Hozz — Ripple, Lens', 24, 12)}
${zoom('Hozz — Ripple, Centred', 24, 12)}
</div>`);
