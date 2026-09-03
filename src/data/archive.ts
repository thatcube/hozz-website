/**
 * The navigation of the superseded designs.
 *
 * The concept archive under /w/ and the first live design at /w/v1/ render what
 * was actually built at the time, which is the only reason to keep an archive
 * at all. Their header links point at sections those pages have and the current
 * site does not, so the list lives here rather than in src/data/site.ts — where
 * it read as the live site's navigation long after it had stopped being that.
 *
 * Nothing a visitor can reach from the homepage imports this.
 */
export const ARCHIVE_NAV_LINKS = [
  { href: '#export', label: 'How to export' },
  { href: '#destinations', label: 'Destinations' },
  { href: '#honest', label: 'Honesty' },
  { href: '#status', label: 'Status' },
];
