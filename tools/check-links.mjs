/**
 * Checks that every internal link in the built site resolves, anchors included.
 *
 *   npm run build && npm run verify:links
 *
 * Documentation is mostly cross-references, and a dead one is invisible to the
 * person who wrote it and obvious to the person reading it. Anchors are checked
 * too, because a heading renamed six pages away is the usual way a fragment
 * quietly stops pointing at anything.
 */
import { readFile, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, relative } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');

if (!existsSync(dist)) {
  console.error('No dist/ — run `npm run build` first.');
  process.exit(1);
}

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map((entry) => {
      const full = join(directory, entry.name);
      return entry.isDirectory() ? walk(full) : Promise.resolve([full]);
    })
  );
  return files.flat();
}

const pages = (await walk(dist)).filter((file) => file.endsWith('.html'));
const cache = new Map();

async function contents(file) {
  if (!cache.has(file)) cache.set(file, await readFile(file, 'utf8'));
  return cache.get(file);
}

let checked = 0;
const problems = [];

for (const page of pages) {
  const html = await contents(page);
  const from = '/' + relative(dist, page);

  for (const match of html.matchAll(/href="(\/[^"#]*)(#[^"]*)?"/g)) {
    const [, href, fragment] = match;
    checked += 1;

    // Astro emits directory-style routes, so /docs/mcp/ is /docs/mcp/index.html.
    const target = href.endsWith('/') ? join(dist, href, 'index.html') : join(dist, href);

    if (!existsSync(target)) {
      problems.push(`${from} → ${href}  (no such page)`);
      continue;
    }

    if (fragment && fragment.length > 1) {
      const targetHtml = await contents(target);
      if (!targetHtml.includes(`id="${fragment.slice(1)}"`)) {
        problems.push(`${from} → ${href}${fragment}  (no such anchor)`);
      }
    }
  }
}

if (problems.length) {
  for (const problem of problems) console.error(`  DEAD  ${problem}`);
  console.error(`\n${problems.length} dead link(s) of ${checked} checked.`);
  process.exit(1);
}

console.log(`${checked} internal links and anchors checked across ${pages.length} pages. None dead.`);
