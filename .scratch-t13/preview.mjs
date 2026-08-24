/**
 * Pull marks out of the built gallery and lay them out at the sizes that
 * matter, on both grounds. Scratch — deleted when the mark is done.
 */
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('dist/logos/index.html', 'utf8');

function grab(label) {
  const i = html.indexOf(`aria-label="${label}"`);
  if (i < 0) throw new Error(`no mark labelled ${label}`);
  const start = html.lastIndexOf('<svg', i);
  const end = html.indexOf('</svg>', i) + 6;
  return html
    .slice(start, end)
    .replace(/width="\d+"/, 'width="SIZE"')
    .replace(/height="\d+"/, 'height="SIZE"');
}

const marks = [
  ['t13', grab('Twozz — Glass, cast')],
  ['c45 (chosen Hozz)', grab('Hozz — Ripple, Lens')],
  ['t10 (a plain sibling)', grab('Twozz — Calm')],
];

const shipped = readFileSync('.briefs/twozz-shipped.svg', 'utf8')
  .replace(/width="\d+"/, 'width="SIZE"')
  .replace(/height="\d+"/, 'height="SIZE"');
marks.push(['twozz shipped', shipped]);

const SIZES = [96, 48, 24, 16];
const rows = marks
  .map(
    ([name, svg]) => `<tr><th>${name}</th>${SIZES.map(
      (s) => `<td>${svg.replaceAll('SIZE', String(s))}</td>`,
    ).join('')}</tr>`,
  )
  .join('\n');

writeFileSync(
  'dist/t13-preview.html',
  `<!doctype html><meta charset="utf-8"><title>t13</title>
<style>
  body { font: 13px ui-sans-serif, system-ui; margin: 24px; background: #fbfbfd; color: #222; }
  table { border-collapse: collapse; margin-bottom: 28px; }
  th { text-align: right; padding-right: 14px; font-weight: 500; white-space: nowrap; }
  td { padding: 12px 16px; vertical-align: middle; }
  .dark { background: #14121a; color: #eee; }
  .dark td, .dark th { color: #eee; }
</style>
<table>${rows}</table>
<table class="dark">${rows}</table>
`,
);
console.log('wrote dist/t13-preview.html');
