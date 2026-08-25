# Contributor notes — hozz-website

This is the marketing site for Hozz. Hozz's whole argument is that it does not
watch you, so the site must not either.

## Hard rules

- **No third-party requests.** No analytics, tag managers, ad pixels, embedded
  widgets, or font CDNs. Typefaces are self-hosted in `public/fonts`. If a change
  adds a request to another origin, it is the wrong change.
- **No cookies and no client-side storage.**
- **Claims must be checkable.** The HealthKit identifiers on the page are real
  API names. Do not invent metrics, statistics, user counts, or testimonials.
- **No fabricated app screenshots.** Hozz is pre-alpha and has no shipped UI. A
  mocked-up screenshot would be the one dishonest thing on a site about honesty.
- **Keep the status section accurate.** If a milestone in `src/data/site.ts` no
  longer matches the app repository, fix the data, not the wording.

## Design system

Everything lives in `src/styles/global.css`. Before adding a colour, check
whether it already exists as a category hue.

- Sections set a single `--tint`; the wash, eyebrow dot, `.em` italic and
  selection colour all derive from it. Do not hard-code section backgrounds.
- Sentient is for headings, General Sans for prose, IBM Plex Mono for machine
  facts only (identifiers, states, ids). Mono in body copy is a bug.
- `.em` marks the one word in a heading that carries the argument. One per
  heading.
- Type and spacing are fluid via `clamp()`. Prefer adjusting a token over adding
  a breakpoint.

## Quality floor

- Contrast: body and caption text must clear 4.5:1 against every section wash it
  can appear on, not just against `--paper`.
- Keyboard focus must stay visible; the global `:focus-visible` ring is enough.
- Anything that animates must be inert under `prefers-reduced-motion: reduce`.
  The hero stream stops but keeps its content, because the content is
  information.
- Mobile down to 390px, and no horizontal scroll at any width.

## Commands

```bash
npm run dev
npm run build
npm run preview
npm run verify:facts          # docs vs the app's Swift source
npm run verify:links          # dead internal links, after a build
node tools/build-images.mjs   # only when the social card or icon changes
node tools/shoot.mjs /docs/   # screenshots for review; needs `npm run dev`
```

## Documentation pages

- Content lives in `src/pages/docs/`; the page list is `src/data/docs-nav.ts`
  and the checkable facts are `src/data/docs.ts`. Add a page to the nav data or
  it does not exist.
- **Every claim must be checkable in the app's source**, not in its README —
  prose in either repository can be stale. `npm run verify:facts` covers the
  lists; the sentences are on you.
- Where something is built but switched off, or in flight, say so plainly or
  leave it out. Never describe a feature that was true for six hours.
- Mono is for machine facts only: identifiers, formats, states, header names,
  and the app's own error strings. Prose never uses it.
- `<title>` is written for search and `<h1>` for the reader; they are separate
  fields and should stay that way.
- Astro drops the indentation whitespace when an inline element starts a line,
  which silently glues a word to the link after it. Use `{' '}` at the end of
  the previous line, and check the built HTML rather than the source.
