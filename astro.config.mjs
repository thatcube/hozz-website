// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import icon from 'astro-icon';

export default defineConfig({
  site: 'https://hozz.brando.page',
  // The privacy page used to live under /docs/ as well as at /privacy/, which
  // meant two pages saying half of the same thing each. There is now one, at
  // the address a store listing and this site's header already point at; the
  // old documentation route keeps answering so nothing that linked to it dies.
  redirects: {
    '/docs/privacy/': '/privacy/',
    '/docs/free-and-open/': '/docs/open-source/',
  },
  integrations: [
    sitemap({
      // The variations and sketches are for review, not for search results. They
      // already carry noindex; keeping them out of the sitemap stops the site
      // from advertising work that is still being decided. /docs/privacy/ is a
      // redirect, and a sitemap should list the destination, not the sign.
      filter: (page) =>
        !/\/(v2|directions|sketch|lab|lab2|logos|w|id|f)\//.test(page) &&
        !/\/docs\/(privacy|free-and-open)\//.test(page),
    }),
    icon(),
  ],
});
