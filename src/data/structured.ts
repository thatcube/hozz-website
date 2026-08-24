import { SITE, GITHUB_URL, LICENSE_URL, FAQ } from './site';

/* Shared by `/` and `/w/w12/` so the two can never describe the product
   differently to a crawler. Every value is drawn from site.ts. */
export const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'SoftwareApplication',
      name: 'Hozz',
      url: SITE,
      applicationCategory: 'HealthApplication',
      operatingSystem: 'iOS, macOS',
      codeRepository: GITHUB_URL,
      license: LICENSE_URL,
      isAccessibleForFree: true,
      description:
        'A free, open-source iPhone app with a companion Mac app that exports Apple Health data to destinations the user owns.',
      offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
    },
    {
      '@type': 'FAQPage',
      mainEntity: FAQ.map((item) => ({
        '@type': 'Question',
        name: item.q,
        acceptedAnswer: { '@type': 'Answer', text: item.a },
      })),
    },
  ],
};
