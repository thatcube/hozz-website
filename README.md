# hozz-website

Marketing site for [Hozz](https://github.com/thatcube/hozz) — a free,
open-source iPhone and iPad app for exporting Apple Health data to destinations
you own.

Live at **[hozz.brando.page](https://hozz.brando.page)**.

## Stack

Astro, no client framework, no analytics, no third-party requests. Deployed as
an assets-only Cloudflare Worker — there is no `main`, so nothing runs
server-side and every request is served from the edge without starting an
isolate. Workers Static Assets rather than Pages, which has been maintenance-only
since early 2025. The site makes exactly zero network calls that Hozz's own
privacy page would have to apologise for — typefaces included, which is why they
are self-hosted rather than pulled from a font CDN.

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

## Documentation

`/docs` is seventeen pages under `src/pages/docs/`. Two data files hold
everything that would otherwise be repeated or go stale:

- **`src/data/docs-nav.ts`** — every page, in reading order, with its `<title>`,
  `<h1>`, description and lede. The sidebar, breadcrumbs, previous/next links
  and the index all read from it. A page missing from this list has no route
  into it.
- **`src/data/docs.ts`** — the facts that live in the app's source: destination
  presets, delivery and export formats, the MCP tool list, the analysis
  thresholds, and the error strings the app actually shows.

### Keeping the docs honest

The site and the app are separate repositories, so the second file can drift.
`verify:facts` reads the enums out of the app's Swift and fails if this
repository disagrees:

```bash
npm run verify:facts                     # against thatcube/hozz@main
npm run verify:facts -- --ref my-branch  # against another ref
HOZZ_REPO=~/Development/hozz npm run verify:facts   # against a local checkout
npm run build && npm run verify:links    # dead internal links and anchors
```

`verify:facts` also holds the four places the site's own hostname is written
down to each other, and checks the counts the pages quote against the lists they
describe — "Seven formats", "Thirteen tools" — so a list can gain an entry
without the sentence beside it going quietly wrong.

A page can be entirely truthful and still be broken, so there is a third check.
`verify:layout` renders every page built on the documentation shell at 390, 768
and 1440 and fails on horizontal overflow, tap targets, a navigation that cannot
be opened on a phone, a missing current-page marker, and links nested inside
links — which is how an anchor inside a card link was caught taking the index
apart without changing a single claim on it.

```bash
npm run build
npm run preview &
SHOOT_BASE=http://localhost:4321 npm run verify:layout
```

It refuses to run against a server that is not serving this build, rather than
measuring whatever answers and reporting the results as this site's.

All three run in CI on every push and once a week, because the app moves without
this repository being touched.

This is a verifier rather than a generator on purpose. Generating prose from
Swift would produce something nobody can maintain, and the prose is most of the
value; generating only the lists would leave them stranded from the sentences
around them. Checking the lists gets the drift protection without either
problem.

## Images

`public/og-image.png` and `public/apple-touch-icon.png` are generated from the
site's own fonts and colours, and are committed. Regenerate them only when they
change:

```bash
npm i -D playwright && npx playwright install chromium
node tools/build-images.mjs
```

## Deploying

**Pushing to `main` deploys the site.** The `deploy` job in
`.github/workflows/site.yml` runs after the fact check and the layout check
have both passed, so the one action here a reader can see is the last one taken
on trust.

This needs one repository secret, `CLOUDFLARE_API_TOKEN` — a token from the
"Edit Cloudflare Workers" template, scoped to the account already named in
`wrangler.jsonc`. The account id is not secret and stays in that file:

```bash
gh secret set CLOUDFLARE_API_TOKEN --repo thatcube/hozz-website
```

Without it the job fails and says so, rather than skipping quietly. The site
used to be published by running wrangler by hand, which is how `main` and the
live site came to be different things for a while without anything saying so.

By hand, when that is what you want:

```bash
npm run deploy        # build, then wrangler deploy
```

The Worker owns `hozz.brando.page` as a custom domain, and still answers on the
former `hozz.brandomoore.com` so old links do not break. Only the first is
canonical — every page declares `hozz.brando.page`, so the two hostnames are not
competing for search results. Declaring any route disables the `workers.dev`
hostname, which is deliberate.

Both hostnames are listed in `wrangler.jsonc`. Wrangler reconciles custom
domains against that list rather than merging with it, so a domain attached by
hand in the dashboard and absent from the file is removed by the next deploy.

## Licence

Site content and code © Brandon Moore. The Hozz app itself is GPL-3.0 with an
App Store distribution exception.
