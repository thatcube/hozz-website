/**
 * The documentation's shape.
 *
 * One list, in reading order, so the sidebar, the previous/next links and the
 * index page all come from the same place and cannot disagree about what
 * exists. A page missing from here is a page nobody can navigate to.
 */

import { COUNTS, Spell, spell } from './docs';

export type DocPage = {
  /**
   * Path, always with a trailing slash to match Astro's directory routes.
   *
   * Nearly all of these live under /docs/. Privacy is the exception: it sits at
   * /privacy/ because that is where an App Store listing, a repository and the
   * site's own header already point, and a privacy policy that answers on a
   * redirect is a worse answer than one that does not.
   */
  href: string;
  /** Sidebar label — short. */
  nav: string;
  /**
   * The <h1>. Deliberately separate from `title`: search wants the words
   * someone types, and a reader wants a heading that fits on a phone.
   */
  heading: string;
  /** <title>, before the site suffix. */
  title: string;
  /** <meta name="description">. Search is a large part of why this exists. */
  description: string;
  /** The one line under the page heading. */
  lede: string;
};

export type DocSection = {
  title: string;
  pages: DocPage[];
};

export const DOC_SECTIONS: DocSection[] = [
  {
    title: 'Start here',
    pages: [
      {
        href: '/docs/getting-started/',
        heading: 'Getting started',
        nav: 'Getting started',
        title: 'Getting started with Hozz — export your Apple Health data',
        description:
          'Build Hozz, grant Health access, choose a destination, and run your first export.',
        lede: 'Build it, grant access, choose a destination and export.',
      },
      {
        href: '/privacy/',
        heading: 'Privacy',
        nav: 'Privacy',
        title: 'Hozz privacy — what leaves your device, and when',
        description:
          'What leaves your iPhone, where credentials live, what Hozz logs, and where its control ends.',
        lede: 'What leaves your device, when, and where.',
      },
      {
        href: '/docs/open-source/',
        heading: 'Open source',
        nav: 'Open source',
        title: 'Hozz is open source — inspect the privacy claims',
        description:
          'Hozz is GPL-3.0 with an App Store distribution exception. Inspect its privacy claims in source.',
        lede: 'Source, license, and what they let you verify.',
      },
    ],
  },
  {
    title: 'Destinations',
    pages: [
      {
        href: '/docs/destinations/',
        heading: 'Choosing a destination',
        nav: 'Choosing one',
        title: 'Apple Health export destinations — which one to choose',
        description:
          'Compare Hozz destinations: Mac, folder, Home Assistant, InfluxDB, web endpoint and MQTT.',
        lede: `Choose among ${spell(COUNTS.destinations)} destinations.`,
      },
      {
        href: '/docs/destinations/mac/',
        heading: 'Your Mac',
        nav: 'Your Mac',
        title: 'Send Apple Health data to your Mac — the Hozz receiver',
        description:
          'Set up the Hozz Mac receiver, local discovery, authentication and folder fallback.',
        lede: 'Receive, store, chart and query your data on a Mac.',
      },
      {
        href: '/docs/destinations/folder/',
        heading: 'A folder',
        nav: 'Folder',
        title: 'Export Apple Health data to a folder — iCloud, Dropbox, OneDrive',
        description:
          'Write Apple Health batches to any folder the iOS Files app can reach.',
        lede: 'The simplest destination: any folder in Files.',
      },
      {
        href: '/docs/destinations/home-assistant/',
        heading: 'Home Assistant',
        nav: 'Home Assistant',
        title: 'Apple Health to Home Assistant — webhook and REST setup',
        description:
          'Send Apple Health metrics to Home Assistant by webhook or REST API.',
        lede: 'Send Metrics JSON by webhook or REST.',
      },
      {
        href: '/docs/destinations/influxdb/',
        heading: 'InfluxDB',
        nav: 'InfluxDB',
        title: 'Apple Health to InfluxDB — line protocol, no translator needed',
        description:
          'Write Apple Health line protocol to InfluxDB 1.8, 2.x or 3.x.',
        lede: 'Write line protocol directly to InfluxDB.',
      },
      {
        href: '/docs/destinations/web/',
        heading: 'Your own endpoint',
        nav: 'Web address',
        title: 'Apple Health to your own endpoint — POST, headers and idempotency',
        description:
          'POST Apple Health batches to your endpoint with retry and idempotency headers.',
        lede: `POST any of ${spell(COUNTS.deliveryFormats)} delivery formats.`,
      },
      {
        href: '/docs/destinations/mqtt/',
        heading: 'MQTT',
        nav: 'MQTT',
        title: 'Apple Health to MQTT — topics, retained messages and QoS',
        description:
          'Publish Apple Health data to MQTT batch and retained metric topics.',
        lede: 'Publish batches and latest values to MQTT.',
      },
    ],
  },
  {
    title: 'The data',
    pages: [
      {
        href: '/docs/formats/',
        heading: 'Export formats',
        nav: 'Export formats',
        title: 'Apple Health export formats — NDJSON, CSV, JSON, SQLite, Markdown, GPX',
        description:
          'Compare Hozz export formats, including which formats lose detail.',
        lede: `${Spell(COUNTS.exportFormats)} formats; ${spell(COUNTS.lossyExportFormats)} are lossy.`,
      },
      {
        href: '/docs/delivery-schema/',
        heading: 'Delivery schema',
        nav: 'Delivery schema',
        title: 'Hozz delivery schema — Apple Health export JSON reference',
        description:
          'Field reference and examples for every Hozz delivery format.',
        lede: 'Fields, record kinds and payload examples.',
      },
      {
        href: '/docs/data-coverage/',
        heading: 'Data coverage',
        nav: 'Data coverage',
        title: 'What Apple Health data Hozz exports — and what it does not',
        description:
          'What Hozz exports from Apple Health today, its limits, and unsupported data.',
        lede: 'Current coverage, limits and omissions.',
      },
    ],
  },
  {
    title: 'Going further',
    pages: [
      {
        href: '/docs/mcp/',
        heading: 'The MCP server',
        nav: 'The MCP server',
        title: 'Apple Health MCP server — query live Health data from an AI assistant',
        description:
          `Query Hozz's local Mac database through ${spell(COUNTS.mcpTools)} read-only MCP tools.`,
        lede: `${Spell(COUNTS.mcpTools)} read-only tools over your local database.`,
      },
      {
        href: '/docs/switching-from-health-auto-export/',
        heading: 'Switching from Health Auto Export',
        nav: 'Switching from HAE',
        title: 'Switching from Health Auto Export to Hozz — field mapping',
        description:
          'Map Health Auto Export fields to Hozz compatibility mode.',
        lede: 'Field mappings and compatibility limits.',
      },
    ],
  },
  {
    title: 'When something is wrong',
    pages: [
      {
        href: '/docs/background-sync/',
        heading: 'Why your export didn’t run',
        nav: 'Background sync',
        title: 'Why didn’t my Apple Health export run? iOS background limits explained',
        description:
          'Why iOS delays Apple Health background export, and what Hozz guarantees.',
        lede: 'iOS controls timing; Hozz preserves correctness.',
      },
      {
        href: '/docs/troubleshooting/',
        heading: 'Troubleshooting',
        nav: 'Troubleshooting',
        title: 'Hozz troubleshooting — exports, sync and the Mac receiver',
        description:
          'Fix Hozz sync, destination, export and Mac receiver problems.',
        lede: 'Find the message or symptom, then fix it.',
      },
    ],
  },
];

/** Every page, flattened, in reading order. */
export const DOC_PAGES: DocPage[] = DOC_SECTIONS.flatMap((section) => section.pages);

/** The page before and after `href`, for the foot of each page. */
export function neighbours(href: string): { prev?: DocPage; next?: DocPage } {
  const index = DOC_PAGES.findIndex((page) => page.href === href);
  if (index === -1) return {};
  return {
    prev: index > 0 ? DOC_PAGES[index - 1] : undefined,
    next: index < DOC_PAGES.length - 1 ? DOC_PAGES[index + 1] : undefined,
  };
}

/** The entry for `href`, so a page never restates its own title and lede. */
export function page(href: string): DocPage {
  const found = DOC_PAGES.find((entry) => entry.href === href);
  if (!found) throw new Error(`No entry in DOC_SECTIONS for ${href}`);
  return found;
}

/**
 * The section `href` belongs to, for the breadcrumb.
 *
 * Derived rather than passed in by each page: a page that names its own section
 * can be moved in this file and go on claiming the old one, which is a wrong
 * breadcrumb nobody notices until a reader does.
 */
export function sectionOf(href: string): string | undefined {
  return DOC_SECTIONS.find((section) => section.pages.some((entry) => entry.href === href))?.title;
}
