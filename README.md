# hozz-website

Marketing site for [Hozz](https://github.com/thatcube/hozz) — a free,
open-source iPhone and iPad app for exporting Apple Health data to destinations
you own.

Live at **[hozz.brandomoore.com](https://hozz.brandomoore.com)**.

## Stack

Astro, no client framework, no analytics, no third-party requests. Deployed as
static files on Cloudflare Pages. The site makes exactly zero network calls that
Hozz's own privacy page would have to apologise for — typefaces included, which
is why they are self-hosted rather than pulled from a font CDN.

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # → dist/
npm run preview
```

## Design system

`src/styles/global.css` holds the whole system. The key idea: there is no single
brand accent. Apple Health sorts what it knows about you into categories, and
Hozz keeps those categories intact all the way to the file you end up owning, so
the site borrows the same spectrum. Each section sets one `--tint` and its wash,
eyebrow dot, italic emphasis and selection colour all follow from it.

- **Sentient** — headings only. A humanist serif with softened terminals, warm
  rather than clinical.
- **General Sans** — body copy.
- **IBM Plex Mono** — machine facts only: HealthKit identifiers, coverage
  states, milestone ids. Prose never uses it.

Content lives in `src/data/site.ts`. The identifiers in the hero stream are real
HealthKit names, not invented ones — if a claim on this site cannot be checked,
it should not be on it.

## Images

`public/og-image.png` and `public/apple-touch-icon.png` are generated from the
site's own fonts and colours, and are committed. Regenerate them only when they
change:

```bash
npm i -D playwright && npx playwright install chromium
node tools/build-images.mjs
```

## Deploying

Pushing to `main` triggers the Cloudflare Pages build. To deploy by hand:

```bash
npm run build
npx wrangler pages deploy dist --project-name hozz-website
```

## Licence

Site content and code © Brandon Moore. The Hozz app itself is GPL-3.0 with an
App Store distribution exception.
