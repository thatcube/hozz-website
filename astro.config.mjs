// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import icon from 'astro-icon';

export default defineConfig({
  site: 'https://hozz.brandomoore.com',
  integrations: [
    sitemap({
      // The variations and sketches are for review, not for search results. They
      // already carry noindex; keeping them out of the sitemap stops the site
      // from advertising work that is still being decided.
      filter: (page) => !/\/(v2|directions|sketch|lab|lab2|logos|w|id|f)\//.test(page),
    }),
    icon(),
  ],
});
