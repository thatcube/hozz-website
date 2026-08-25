/**
 * Renders every documentation page at three widths and checks the things that
 * only show up in a browser.
 *
 *   npm run build
 *   npm run preview &
 *   SHOOT_BASE=http://localhost:4321 npm run verify:layout
 *
 * Writes PNGs to .shots/ (gitignored) and prints a report. Exits non-zero if
 * anything failed, so it can be run the same way a test is.
 *
 * Why a script rather than a careful look
 * --------------------------------------
 * Horizontal overflow on a phone, a tap target too small to hit, and a
 * navigation that cannot be opened are all invisible on a desktop and obvious
 * to the person holding the phone. They are also mechanical, so they are
 * checked mechanically and the screenshots are left for the judgement calls.
 *
 * Why it refuses to start rather than assuming
 * -------------------------------------------
 * This used to take a default address and audit whatever answered there. Run by
 * hand against a forgotten server on the same port, it reported thirty-nine tap
 * target failures — with element names and pixel sizes, entirely real-looking,
 * and about somebody else's site. So the address is printed before anything is
 * measured, and the server is made to prove it is serving *this* build before a
 * single page is opened. A number about the wrong thing is worse than no number.
 */
import puppeteer from 'puppeteer-core';
import { mkdir, writeFile, readFile, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, relative, sep } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const outDir = join(root, '.shots');
const dist = join(root, 'dist');
const base = (process.env.SHOOT_BASE ?? 'http://localhost:4321').replace(/\/$/, '');

const executablePath =
  process.env.CHROME_PATH ??
  `${process.env.HOME}/.cache/puppeteer/chrome/mac_arm-151.0.7922.47/chrome-mac-arm64/` +
    'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';

if (!existsSync(dist)) {
  console.error('No dist/ — run `npm run build` first.');
  process.exit(1);
}

/**
 * Every page built on the documentation shell.
 *
 * Read out of dist rather than imported from src/data/docs-nav.ts, because that
 * module imports a sibling without a file extension — which Vite resolves and
 * plain node does not. Reading the build also means a page added to the site is
 * audited without this list being remembered, and that what is checked is what
 * was actually produced.
 */
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

const built = (await walk(dist)).filter((file) => file.endsWith('index.html'));
const ROUTES = [];
/** route -> the file on disk it was built from, for the preflight below. */
const SOURCE_OF = new Map();
for (const file of built) {
  const html = await readFile(file, 'utf8');
  if (!html.includes('class="docs-shell"')) continue;
  const route = '/' + relative(dist, file).split(sep).slice(0, -1).join('/');
  const href = route === '/' ? '/' : `${route}/`;
  ROUTES.push(href);
  SOURCE_OF.set(href, file);
}
ROUTES.sort();

if (ROUTES.length === 0) {
  console.error('No pages using the documentation shell were found in dist/.');
  process.exit(1);
}

/**
 * Full-page captures are taken at 1x on purpose.
 *
 * A documentation page at 390px can run past 10,000 CSS pixels, and Chrome
 * stitches a full-page shot from tiles: at 2x the image crosses the texture
 * limit and comes back with a band of the page repeated, which reads as a
 * duplication bug that is not in the page. 1x keeps the image honest.
 */
const VIEWPORTS = [
  { name: 'phone', width: 390, height: 844, deviceScaleFactor: 1, mobile: true },
  { name: 'tablet', width: 768, height: 1024, deviceScaleFactor: 1, mobile: true },
  { name: 'desktop', width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false },
];

/**
 * Apple asks for 44pt. A row of chrome links cannot honour that in both axes —
 * "Docs" is 29px wide and padding it to 44 would space a header row out of
 * recognition — so the rule applied here is 44px in the axis a target can grow
 * in, and never below WCAG 2.5.8's 24px in the other. A link 29px wide and 44px
 * tall is comfortable; one 313px wide and 37px tall is not.
 */
const MIN_TAP = 44;
const MIN_CROSS = 24;

const problems = [];
const rows = [];

function fail(route, viewport, message) {
  problems.push(`${route} @ ${viewport}: ${message}`);
}

await mkdir(outDir, { recursive: true });

/**
 * Prove the server is there, and that it is serving this build.
 *
 * `SHOOT_BASE` is the only name this reads. Pass a different variable and the
 * default applies silently, which is how a run once measured a forgotten server
 * on the default port and reported its problems as this site's. Both failures
 * are caught here: nothing answering, and something answering that is not this.
 */
console.log(`Auditing ${base}${process.env.SHOOT_BASE ? '' : '  (default — set SHOOT_BASE to change)'}`);

{
  const probe = ROUTES[0];
  let served;
  try {
    const response = await fetch(base + probe);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    served = await response.text();
  } catch (error) {
    console.error(
      `\nNothing usable answered ${base}${probe} — ${error.message}\n\n` +
        '  Start a server for this build first:\n' +
        '    npm run build && npm run preview\n\n' +
        '  Then point this at it with SHOOT_BASE, which is the only variable it\n' +
        '  reads. Note that `astro preview` binds localhost, which may resolve to\n' +
        '  IPv6 — a readiness check against 127.0.0.1 can fail while the server is\n' +
        '  up and answering perfectly well on localhost.'
    );
    process.exit(1);
  }

  // Comparing against the file the route was built from catches both a server
  // that belongs to something else and one still serving a previous build.
  const onDisk = await readFile(SOURCE_OF.get(probe), 'utf8');
  if (served.trim() !== onDisk.trim()) {
    console.error(
      `\n${base}${probe} is not serving this build.\n\n` +
        '  Something is answering, but it does not match dist/. Either it belongs\n' +
        '  to another site or another checkout, or dist/ has been rebuilt since it\n' +
        '  started. Auditing it would produce real-looking numbers about the wrong\n' +
        '  pages, so this stops here.\n\n' +
        '  Rebuild and restart the server, or point SHOOT_BASE somewhere else.'
    );
    process.exit(1);
  }
}
const browser = await puppeteer.launch({ executablePath, headless: true });

for (const route of ROUTES) {
  const slug = route.replace(/^\/|\/$/g, '').replace(/\//g, '-') || 'home';

  for (const viewport of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport(viewport);
    // Without this the second visit to a shared asset answers 304, which is a
    // cache hit rather than a failure but is indistinguishable from one here.
    await page.setCacheEnabled(false);

    let response;
    try {
      response = await page.goto(base + route, { waitUntil: 'networkidle0' });
    } catch (error) {
      // A refused connection means the server is not there, which is a failed
      // check rather than a crash — CI should say so and move on.
      fail(route, viewport.name, `could not be loaded — ${error.message.split('\n')[0]}`);
      await page.close();
      continue;
    }
    const status = response?.status() ?? 0;
    if (status >= 400 || status === 0) {
      fail(route, viewport.name, `HTTP ${status}`);
      await page.close();
      continue;
    }
    await page.evaluate(() => document.fonts.ready);

    const result = await page.evaluate(({ minTap, minCross }) => {
      const doc = document.documentElement;

      // Anything wider than the viewport makes the whole page slide sideways.
      const overflow = doc.scrollWidth - doc.clientWidth;
      const wide = [];
      if (overflow > 1) {
        for (const el of document.querySelectorAll('body *')) {
          if (!el.checkVisibility({ contentVisibilityAuto: true })) continue;
          const rect = el.getBoundingClientRect();
          if (rect.width === 0) continue;
          if (rect.right > doc.clientWidth + 1 || rect.left < -1) {
            const style = getComputedStyle(el);
            // Only report the element itself, not every ancestor stretched by it.
            if (!wide.some((w) => el.contains(w.node))) {
              wide.push({
                node: el,
                tag: el.tagName.toLowerCase(),
                cls: (el.className || '').toString().slice(0, 60),
                right: Math.round(rect.right),
                overflowX: style.overflowX,
              });
            }
          }
        }
      }

      // Tap targets. Inline links inside a paragraph are exempt: making body
      // copy 44px tall is not what the guidance means.
      const small = [];
      for (const el of document.querySelectorAll('a, button, summary, [role="button"]')) {
        // A collapsed <details> keeps its contents in layout under
        // content-visibility, so a rect alone is not proof of being on screen.
        if (!el.checkVisibility({ contentVisibilityAuto: true, opacityProperty: true })) {
          continue;
        }
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;
        const style = getComputedStyle(el);
        const inProse = el.closest('.prose') && el.tagName === 'A' && style.display === 'inline';
        if (inProse) continue;
        const long = Math.max(rect.width, rect.height);
        const short = Math.min(rect.width, rect.height);
        if (long < minTap || short < minCross) {
          small.push({
            tag: el.tagName.toLowerCase(),
            text: (el.textContent || '').trim().slice(0, 28),
            w: Math.round(rect.width),
            h: Math.round(rect.height),
          });
        }
      }

      const sidebar = document.getElementById('docs-sidebar');

      return {
        overflow,
        wide: wide.map(({ tag, cls, right, overflowX }) => ({ tag, cls, right, overflowX })),
        small,
        h1: document.querySelectorAll('h1').length,
        // A link inside a link is not rendered, it is repaired — the parser
        // closes the outer one early and the surrounding block comes apart.
        nestedLinks: document.querySelectorAll('a a').length,
        current: document.querySelectorAll('[aria-current="page"]').length,
        sidebarOpen: sidebar ? sidebar.open : null,
        hasSidebar: Boolean(sidebar),
        title: document.title,
        skipLink: Boolean(document.querySelector('.skip-link')),
      };
    }, { minTap: MIN_TAP, minCross: MIN_CROSS });

    if (result.overflow > 1) {
      const worst = result.wide
        .slice(0, 3)
        .map((w) => `<${w.tag} class="${w.cls}"> right=${w.right}`)
        .join('; ');
      fail(route, viewport.name, `overflows by ${result.overflow}px — ${worst || 'no element found'}`);
    }
    // 44pt is Apple's guidance for a finger, so it is checked where there is
    // one. A mouse is precise and a 34px sidebar row is fine for it.
    if (viewport.mobile && result.small.length) {
      const worst = result.small
        .slice(0, 4)
        .map((s) => `${s.tag}"${s.text}" ${s.w}x${s.h}`)
        .join('; ');
      fail(route, viewport.name, `${result.small.length} tap target(s) below ${MIN_TAP}×${MIN_CROSS}px — ${worst}`);
    }
    if (result.h1 !== 1) fail(route, viewport.name, `${result.h1} <h1> elements, expected 1`);
    if (result.nestedLinks) {
      fail(route, viewport.name, `${result.nestedLinks} link(s) nested inside another link`);
    }
    if (!result.skipLink) fail(route, viewport.name, 'no skip link');

    // The current page has to be marked, or the sidebar is just a list of links.
    if (result.hasSidebar && result.current < 1) {
      fail(route, viewport.name, 'no aria-current="page" in the navigation');
    }

    // The navigation must be operable on a phone: collapsed so it does not bury
    // the page, and openable to reveal real links.
    if (viewport.name === 'phone' && result.hasSidebar) {
      if (result.sidebarOpen) {
        fail(route, viewport.name, 'sidebar starts expanded on a phone, burying the content');
      }
      const opened = await page.evaluate(() => {
        const sidebar = document.getElementById('docs-sidebar');
        const summary = sidebar?.querySelector('summary');
        if (!summary) return { ok: false, reason: 'no summary to tap' };
        // Height is the honest signal. A collapsed <details> keeps its links in
        // layout, so counting them proves nothing; the box growing does.
        const shut = sidebar.getBoundingClientRect().height;
        summary.click();
        if (!sidebar.open) return { ok: false, reason: 'tapping the summary did not open it' };
        const open = sidebar.getBoundingClientRect().height;
        if (open <= shut + 40) {
          return { ok: false, reason: `opened but grew only ${Math.round(open - shut)}px` };
        }
        summary.click();
        if (sidebar.open) return { ok: false, reason: 'tapping again did not close it' };
        if (sidebar.getBoundingClientRect().height > shut + 40) {
          return { ok: false, reason: 'closed but still occupying the open height' };
        }
        return { ok: true };
      });
      if (!opened.ok) fail(route, viewport.name, `navigation: ${opened.reason}`);
    }

    await page.screenshot({
      path: join(outDir, `${slug}-${viewport.name}.png`),
      fullPage: true,
    });

    rows.push({
      route,
      viewport: viewport.name,
      overflow: result.overflow,
      small: result.small.length,
      current: result.current,
    });

    await page.close();
  }
  process.stdout.write(`  shot  ${route}\n`);
}

await browser.close();

await writeFile(join(outDir, 'audit.json'), JSON.stringify({ rows, problems }, null, 2));

console.log(`\n${ROUTES.length} routes × ${VIEWPORTS.length} widths — PNGs in .shots/\n`);

if (problems.length) {
  for (const problem of problems) console.log(`  FAIL  ${problem}`);
  console.log(`\n${problems.length} problem(s).`);
  process.exit(1);
}

console.log('No layout problems found.');
