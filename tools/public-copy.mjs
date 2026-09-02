import { readdir, readFile } from 'node:fs/promises';
import { join, relative } from 'node:path';

const BANNED = [
  {
    label: 'standalone pricing claim using "free"',
    pattern: /(?<![\p{L}\p{N}_-])free(?![\p{L}\p{N}_-])/giu,
  },
  {
    label: 'subscription promise',
    pattern: /\bsubscription\b/giu,
  },
  {
    label: 'tier or paywall promise',
    pattern: /\b(?:paid tier|paid version|pro tier|paywall)\b/giu,
  },
  {
    label: 'future sales promise',
    pattern: /\b(?:nothing to (?:buy|sell|upsell)|future upsell)\b/giu,
  },
  {
    label: 'zero-price schema',
    pattern: /\b(?:isAccessibleForFree|priceCurrency)\b|["']price["']\s*:\s*["']0["']/giu,
  },
  {
    label: 'no-price promise',
    pattern: /\bno price\b/giu,
  },
];

const SOURCE_EXTENSIONS = /\.(?:astro|css|html|js|json|md|mjs|ts)$/;

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map((entry) => {
      const path = join(directory, entry.name);
      return entry.isDirectory() ? walk(path) : Promise.resolve([path]);
    }),
  );
  return files.flat();
}

export async function scanFiles(files, root) {
  const findings = [];

  for (const file of files) {
    const source = await readFile(file, 'utf8');
    for (const { label, pattern } of BANNED) {
      pattern.lastIndex = 0;
      for (const match of source.matchAll(pattern)) {
        const line = source.slice(0, match.index).split('\n').length;
        findings.push({
          file: relative(root, file),
          line,
          text: match[0],
          label,
        });
      }
    }
  }

  return { filesScanned: files.length, findings };
}

export async function scanPublicSource(root) {
  const srcFiles = (await walk(join(root, 'src'))).filter((file) => SOURCE_EXTENSIONS.test(file));
  const standalone = [
    join(root, 'README.md'),
    join(root, 'astro.config.mjs'),
    join(root, 'package.json'),
    join(root, 'tools/build-images.mjs'),
  ];
  return scanFiles([...srcFiles, ...standalone], root);
}
