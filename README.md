# hozz-website

The website for [Hozz](https://github.com/thatcube/hozz) — a free, open-source
iPhone app that exports Apple Health data to destinations you own.

Plain HTML and CSS with no build step, no framework, and no tracking, so it can
be hosted free on GitHub Pages and audited at a glance.

## Structure

```
index.html        Landing page
docs/index.html   Setup guides, data schema, troubleshooting
assets/style.css  All styling, light and dark
```

## Running it locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Deploying

Enable GitHub Pages on the `main` branch, root folder. There is nothing to
build.
