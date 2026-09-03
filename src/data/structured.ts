import { SITE, GITHUB_URL, LICENSE_URL, FAQ, FORMATS } from './site';

/* Shared by `/` and `/w/w12/` so the two can never describe the product
   differently to a crawler. Every value is drawn from site.ts. */
export const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      /* Naming the site as its own entity is what lets Google show "Hozz" as
         the site name in a result rather than guessing it from the hostname —
         which matters more than usual here, because the hostname currently
         belongs to a person rather than to the product. */
      '@type': 'WebSite',
      '@id': `${SITE}/#website`,
      url: SITE,
      name: 'Hozz',
      description:
        'Move health data between the places and platforms you use.',
      publisher: { '@id': `${SITE}/#person` },
      inLanguage: 'en-US',
    },
    {
      '@type': 'Person',
      '@id': `${SITE}/#person`,
      name: 'Brandon Moore',
      url: SITE,
      sameAs: ['https://github.com/thatcube'],
    },
    {
      '@type': 'SoftwareApplication',
      '@id': `${SITE}/#app`,
      name: 'Hozz',
      url: SITE,
      applicationCategory: 'HealthApplication',
      operatingSystem: 'iOS, macOS',
      codeRepository: GITHUB_URL,
      license: LICENSE_URL,
      author: { '@id': `${SITE}/#person` },
      sameAs: [GITHUB_URL],
      description:
        'Reads Apple Health on iPhone and sends it to your Mac or destinations you choose.',
      /* Derived, never typed: if a format is added or dropped in site.ts the
         markup follows, so it cannot claim an export Hozz does not do. */
      featureList: FORMATS.map((format) => `${format.name} export`),
    },
    {
      '@type': 'FAQPage',
      '@id': `${SITE}/#faq`,
      mainEntity: FAQ.map((item) => ({
        '@type': 'Question',
        name: item.q,
        acceptedAnswer: { '@type': 'Answer', text: item.a },
      })),
    },
  ],
};
